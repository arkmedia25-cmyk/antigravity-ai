"""
Daily YouTube music video pipeline — multi-channel.
Usage: python main_runner.py --channel neonpulse
Cron example:
  0 1 * * * cd /path/to/youtube-music-bot && python -u queue_runner.py >> logs/queue.log 2>&1
"""
import sys
import argparse
import json
import shutil
import traceback
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from pipeline import suno_generate, audio_process, video_build, thumbnail_make, youtube_upload, binaural_generate
from core import notifier as notify

OUTPUT_DIR = Path("output")


def _load_channel(slug: str) -> dict:
    path = Path(f"channels/{slug}/channel.json")
    if not path.exists():
        raise FileNotFoundError(f"Channel not found: {path}")
    return json.loads(path.read_text())


def _load_genre(slug: str) -> dict:
    channel_dir = Path(f"channels/{slug}")
    genres_path = channel_dir / "genres.json"

    if not genres_path.exists():
        genres_path = Path("genres.json")

    state_file = channel_dir / ".rotation_state.json"

    with open(genres_path) as f:
        genres = json.load(f)

    state = {}
    if state_file.exists():
        state = json.loads(state_file.read_text())

    last_index = state.get("last_index", -1)
    next_index = (last_index + 1) % len(genres)

    state_file.write_text(json.dumps({"last_index": next_index, "last_date": str(date.today())}))

    genre = genres[next_index]
    print(f"[runner] Genre: {genre['slug']}")
    return genre


def _cleanup() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()
    print("[runner] Output cleared")


def main(channel_slug: str, no_upload: bool = False, publish_hour: int | None = None) -> None:
    Path("logs").mkdir(exist_ok=True)
    print(f"[runner] Channel: {channel_slug} | Date: {date.today()}")

    channel = _load_channel(channel_slug)
    genre = _load_genre(channel_slug)
    duration_min = genre["duration_min"]
    chat_id = channel.get("telegram_chat_id", "")

    bg_dir     = Path(f"channels/{channel_slug}/backgrounds")
    token_file = Path(channel["token_file"])
    is_binaural = channel.get("type") == "binaural"

    try:
        # 1. Generate music
        if is_binaural:
            preset  = genre.get("binaural_preset", genre["slug"])
            dur_sec = duration_min * 60
            bin_path       = binaural_generate.generate(preset, dur_sec)
            ambient_tracks = suno_generate.run(genre)
            ambient_audio  = audio_process.run(ambient_tracks + ambient_tracks)
            mix_path    = Path("output/audio/binaural_mix.mp3")
            final_audio = binaural_generate.mix_with_ambient(bin_path, ambient_audio, mix_path)
        else:
            track_paths = suno_generate.run(genre)
            # Loop tracks to double duration at half the API cost
            final_audio = audio_process.run(track_paths + track_paths)

        # 2. Build video
        video_path = video_build.run(final_audio, genre.get("slug", ""), bg_dir)

        # 3. Thumbnail
        thumbnail_path = thumbnail_make.run(genre, duration_min, channel_slug)

        # 4. Save local copy before cleanup
        channel_out_dir = Path(f"channels/{channel_slug}/output")
        channel_out_dir.mkdir(parents=True, exist_ok=True)
        saved_video = channel_out_dir / f"{genre['slug']}.mp4"
        shutil.copy2(video_path, saved_video)
        print(f"[runner] Saved: {saved_video}")

        # 5. Upload to YouTube
        if not no_upload:
            video_url = youtube_upload.run(video_path, thumbnail_path, genre, duration_min, token_file, publish_hour)
            title = genre["title"].format(duration=duration_min, year=date.today().year)
            notify.send(
                f"New video uploaded — {channel['name']}\n{title}\n{duration_min} min\n{video_url}",
                chat_id
            )
            print(f"[runner] Done: {video_url}")

    except Exception as e:
        detail = traceback.format_exc()
        print(f"[runner] ERROR: {e}\n{detail}")
        notify.error(type(e).__name__, str(e), chat_id)
        raise

    finally:
        _cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", required=True, help="Channel slug (neonpulse, sleepwave, healingflow, binauralmind)")
    parser.add_argument("--no-upload", action="store_true", help="Skip YouTube upload (test mode)")
    parser.add_argument("--publish-hour", type=int, default=None, help="Publish hour override (0-23, Amsterdam time)")
    args = parser.parse_args()
    main(args.channel, no_upload=args.no_upload, publish_hour=args.publish_hour)
