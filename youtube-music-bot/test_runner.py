"""
60 saniyelik test videosu — tek kanal, kısa süre.
Kullanım: python test_runner.py --channel neonpulse
"""
import argparse
import json
import shutil
import traceback
from datetime import date
from pathlib import Path

from pipeline import suno_generate, audio_process, video_build, thumbnail_make, youtube_upload, binaural_generate
from core import notifier as notify

OUTPUT_DIR = Path("output")

TEST_GENRES = {
    "neonpulse": {
        "slug": "epic-cinematic",
        "title": "TEST Epic Cinematic | 1 Min | {year}",
        "prompt": "epic orchestral cinematic trailer music, powerful emotional strings, dramatic percussion, no lyrics, hollywood style, inspirational",
        "duration_min": 1,
        "hook": "TEST VIDEO — 60 second cinematic test.",
    },
    "sleepwave": {
        "slug": "deep-sleep-432hz",
        "title": "TEST 432Hz Sleep Music | 1 Min | {year}",
        "prompt": "432hz healing frequency, deep sleep ambient, soft piano, no vocals, very slow, relaxing",
        "duration_min": 1,
        "hook": "TEST VIDEO — 60 second sleep music test.",
    },
    "healingflow": {
        "slug": "528hz-healing",
        "title": "TEST 528Hz Healing | 1 Min | {year}",
        "prompt": "528hz solfeggio frequency, healing music, soft bells, meditation tones, no vocals",
        "duration_min": 1,
        "hook": "TEST VIDEO — 60 second healing frequency test.",
    },
    "binauralmind": {
        "slug": "alpha-focus",
        "binaural_preset": "alpha-focus",
        "title": "TEST Alpha Binaural Beats | 1 Min | {year}",
        "prompt": "calm focus ambient, gentle electronic, minimal synth, no vocals",
        "duration_min": 1,
        "hook": "TEST VIDEO — 60 second binaural beats test.",
    },
}


def _load_channel(slug: str) -> dict:
    path = Path(f"channels/{slug}/channel.json")
    if not path.exists():
        raise FileNotFoundError(f"Kanal bulunamadı: {path}")
    return json.loads(path.read_text())


def _cleanup() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()


def main(channel_slug: str) -> None:
    Path("logs").mkdir(exist_ok=True)
    print(f"\n[TEST] Kanal: {channel_slug} | Süre: 1 dakika")

    channel = _load_channel(channel_slug)
    genre = TEST_GENRES.get(channel_slug)
    if not genre:
        raise ValueError(f"Test genre bulunamadı: {channel_slug}")

    bg_dir = Path(f"channels/{channel_slug}/backgrounds")
    token_file = Path(channel["token_file"])
    is_binaural = channel.get("type") == "binaural"
    chat_id = channel.get("telegram_chat_id", "")

    try:
        if is_binaural:
            preset = genre.get("binaural_preset", genre["slug"])
            bin_path = binaural_generate.generate(preset, 60)
            ambient_tracks = suno_generate.run(genre)
            ambient_audio = audio_process.run(ambient_tracks)
            mix_path = Path("output/audio/binaural_mix.mp3")
            final_audio = binaural_generate.mix_with_ambient(bin_path, ambient_audio, mix_path)
        else:
            track_paths = suno_generate.run(genre)
            final_audio = audio_process.run(track_paths)

        video_path = video_build.run(final_audio, genre.get("slug", ""), bg_dir)
        thumbnail_path = thumbnail_make.run(genre, 1)

        # Test videoları private yükle
        genre_upload = dict(genre)
        genre_upload["force_private"] = True
        genre_upload["title"] = genre["title"].format(year=date.today().year)

        video_url = youtube_upload.run(video_path, thumbnail_path, genre_upload, 1, token_file)

        print(f"\n[TEST] ✅ Tamamlandı: {video_url}")
        notify.send(f"🧪 <b>TEST video — {channel['name']}</b>\n🔗 {video_url}", chat_id)

    except Exception as e:
        print(f"[TEST] ❌ HATA: {e}\n{traceback.format_exc()}")
        raise
    finally:
        _cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", required=True)
    args = parser.parse_args()
    main(args.channel)
