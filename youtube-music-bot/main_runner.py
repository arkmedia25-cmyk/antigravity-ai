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
from pipeline.suno_generate import InsufficientCreditsError
from core import notifier as notify

# Animated thumbnail generator (genre-aware, vertical + horizontal)
try:
    from thumbnail_animated import make as make_animated_thumbs
    _ANIMATED = True
except ImportError:
    _ANIMATED = False

OUTPUT_DIR = Path("output")


def _load_channel(slug: str) -> dict:
    path = Path(f"channels/{slug}/channel.json")
    if not path.exists():
        raise FileNotFoundError(f"Channel not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_genre(slug: str) -> dict:
    channel_dir = Path(f"channels/{slug}")
    genres_path = channel_dir / "genres.json"

    if not genres_path.exists():
        genres_path = Path("genres.json")

    state_file = channel_dir / ".rotation_state.json"

    with open(genres_path, encoding="utf-8") as f:
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
            bin_path = binaural_generate.generate(preset, dur_sec)
            # Ambient layer via Suno (optional — requires credits)
            try:
                suno_generate.check_credits()
                ambient_tracks = suno_generate.run(genre)
                ambient_audio  = audio_process.run(ambient_tracks * 5)
                mix_path    = Path("output/audio/binaural_mix.mp3")
                final_audio = binaural_generate.mix_with_ambient(bin_path, ambient_audio, mix_path)
                print("[runner] Binaural + ambient mix complete")
            except InsufficientCreditsError:
                print("[runner] No Suno credits — using pure binaural audio (no ambient layer)")
                final_audio = bin_path
        else:
            track_paths = suno_generate.run(genre)
            # Loop tracks to double duration at half the API cost
            final_audio = audio_process.run(track_paths * 5)

        # 2. Build video
        video_path = video_build.run(final_audio, genre.get("slug", ""), bg_dir)

        # 3. Build Short video
        short_path = video_build.create_short(video_path, slug=genre.get("slug", ""))
        print(f"[runner] Short: {short_path}")

        # 4. Thumbnails — static JPG + animated HTML (vertical 9:16 + horizontal 16:9)
        thumbs = thumbnail_make.run(genre, duration_min, channel_slug=channel_slug)
        thumbnail_path    = thumbs["jpg"]          # static JPEG for long video
        short_thumb_path  = thumbs.get("vertical") or thumbs["jpg"]   # animated 9:16 or fallback
        print(f"[runner] Thumbnail JPG:      {thumbnail_path}")
        print(f"[runner] Thumbnail vertical: {short_thumb_path}")

        # 4. Save local copy before cleanup
        channel_out_dir = Path(f"channels/{channel_slug}/output")
        channel_out_dir.mkdir(parents=True, exist_ok=True)
        saved_video = channel_out_dir / f"{genre['slug']}.mp4"
        shutil.copy2(video_path, saved_video)
        print(f"[runner] Saved: {saved_video}")

        # 5. Upload to YouTube
        if not no_upload:
            # Upload long video
            video_url = youtube_upload.upload(
                video_path, thumbnail_path, genre, duration_min, token_file, schedule=True
            )
            # Upload Short
            short_url = youtube_upload.upload_short(
                short_path, short_thumb_path, genre, token_file, schedule=True
            )
            title = genre["title"].format(duration=duration_min, year=date.today().year)
            notify.send(
                f"New video uploaded — {channel['name']}\n{title}\n{duration_min} min\n{video_url}\nShort: {short_url}",
                chat_id
            )
            print(f"[runner] Long: {video_url} | Short: {short_url}")

    except InsufficientCreditsError as e:
        print(f"[runner] SKIPPED: {e}")
        notify.send(f"[{channel['name']}] Skipped — kie.ai credits empty. Top up to resume.", chat_id)
        # Exit cleanly, no re-raise — scheduler will retry tomorrow
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
