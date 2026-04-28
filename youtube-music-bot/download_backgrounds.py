"""
Her kanal için Pexels'dan uygun background video indir.
Kullanım: python download_backgrounds.py
.env'deki PEXELS_API_KEY kullanılır.
"""
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

CHANNEL_QUERIES = {
    "neonpulse": {
        "epic-cinematic":    "cinematic landscape mountains fog dramatic",
        "electronic-focus":  "abstract neon particles technology dark",
        "dark-cinematic":    "dark storm clouds night dramatic fog",
        "energy-edm":        "colorful abstract energy particles music",
        "futuristic-ambient":"galaxy nebula space stars universe",
    },
    "sleepwave": {
        "deep-sleep-432hz":  "night sky stars peaceful sleeping nature",
        "rain-sleep":        "rain window night calm cozy",
        "delta-waves-sleep": "dark ocean waves moonlight night",
        "piano-sleep":       "soft candlelight peaceful bedroom night",
        "nature-sleep":      "forest night fireflies peaceful nature",
    },
    "healingflow": {
        "528hz-healing":     "golden light sunrise nature healing",
        "tibetan-bowls":     "buddhist temple meditation candles peaceful",
        "alpha-focus":       "calm water lake reflection nature morning",
        "chakra-healing":    "colorful light mandala spiritual meditation",
        "spa-relaxation":    "spa water flowers zen stones peaceful",
    },
    "binauralmind": {
        "delta-sleep":       "dark deep ocean underwater peaceful",
        "theta-meditation":  "abstract purple cosmos meditation space",
        "alpha-focus":       "soft blue particles abstract calm mind",
        "beta-energy":       "bright energy particles sunrise morning",
        "gamma-creativity":  "colorful abstract geometric creativity art",
    },
}


def search_video(query: str) -> dict | None:
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 5, "size": "large", "orientation": "landscape"}
    resp = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    videos = resp.json().get("videos", [])
    if not videos:
        return None
    best = None
    for video in videos:
        for file in video.get("video_files", []):
            if file.get("quality") in ("hd", "uhd") and file.get("width", 0) >= 1280:
                if best is None or video["duration"] > best["duration"]:
                    best = {"url": file["link"], "duration": video["duration"]}
    return best


def download(url: str, dest: Path) -> None:
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 512):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    print(f"\r  {downloaded/total*100:.0f}%", end="", flush=True)
        print()


def main():
    if not PEXELS_API_KEY:
        print("HATA: PEXELS_API_KEY .env'de yok")
        return

    for channel, queries in CHANNEL_QUERIES.items():
        bg_dir = Path(f"channels/{channel}/backgrounds")
        bg_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n{'='*40}\n{channel.upper()}\n{'='*40}")

        for slug, query in queries.items():
            dest = bg_dir / f"bg_{slug}.mp4"
            if dest.exists():
                print(f"[{slug}] Zaten var, atlanıyor")
                continue
            print(f"[{slug}] Aranıyor: '{query}'")
            video = search_video(query)
            if not video:
                print(f"[{slug}] Bulunamadı")
                continue
            download(video["url"], dest)
            print(f"  Kaydedildi: {dest.name}")
            time.sleep(1)

    print("\n✅ Tüm backgroundlar indirildi.")


if __name__ == "__main__":
    main()
