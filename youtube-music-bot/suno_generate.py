import os
import time
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

KIE_API_KEY = os.getenv("KIE_API_KEY")
OUTPUT_DIR = Path("output/audio")
BASE_URL = "https://api.kie.ai/api/v1"


def generate_tracks(prompt: str) -> list[str]:
    """kie.ai Suno API ile müzik üret, MP3 URL listesi döndür."""
    headers = {
        "Authorization": f"Bearer {KIE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "model": "V4_5",
        "instrumental": True,
        "customMode": False,
        "callBackUrl": "http://134.209.80.233/callback",
    }

    resp = requests.post(f"{BASE_URL}/generate", headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    if data.get("data") is None:
        raise RuntimeError(f"kie.ai API hatasi (code={data.get('code')}): {data.get('msg')}")

    task_id = data["data"]["taskId"]
    print(f"[suno] Task ID: {task_id}")
    return _poll_task(task_id, headers)


def _poll_task(task_id: str, headers: dict, max_wait: int = 900) -> list[str]:
    """Üretim tamamlanana kadar bekle, MP3 URL'lerini döndür."""
    elapsed = 0
    while elapsed < max_wait:
        resp = requests.get(f"{BASE_URL}/generate/record-info", headers=headers,
                            params={"taskId": task_id}, timeout=30)
        resp.raise_for_status()
        raw = resp.json()
        data = raw.get("data") or {}

        status = data.get("status", "")
        print(f"[suno] Status: {status} ({elapsed}s)")

        tracks = (data.get("response") or {}).get("sunoData") or []
        # audioUrl dolunca tamamdır
        ready = [t for t in tracks if t.get("audioUrl")]
        if ready:
            urls = [t["audioUrl"] for t in ready]
            print(f"[suno] {len(urls)} parca hazir")
            return urls

        if status in ("failed", "error"):
            raise RuntimeError(f"Suno task basarisiz: {data}")

        time.sleep(20)
        elapsed += 20

    raise TimeoutError("Suno task zaman aşımına uğradı")


def download_tracks(urls: list[str]) -> list[Path]:
    """MP3 URL'lerini output/audio/ klasörüne indir."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = []

    for i, url in enumerate(urls):
        dest = OUTPUT_DIR / f"track_{i:02d}.mp3"
        resp = requests.get(url, timeout=60, stream=True)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[suno] İndirildi: {dest.name}")
        paths.append(dest)

    return paths


def run(genre: dict) -> list[Path]:
    prompt = genre["prompt"]
    duration_min = genre.get("duration_min", 60)
    # Her parça ~3 dk, her API çağrısı 2 parça üretiyor
    target_tracks = max(4, duration_min // 3)
    calls_needed = (target_tracks + 1) // 2

    print(f"[suno] Prompt: {prompt}")
    print(f"[suno] Hedef: {target_tracks} parça / {duration_min} dk — {calls_needed} API çağrısı")

    all_urls: list[str] = []
    for call_num in range(calls_needed):
        print(f"[suno] Çağrı {call_num + 1}/{calls_needed}...")
        urls = generate_tracks(prompt)
        all_urls.extend(urls)
        if len(all_urls) >= target_tracks:
            break

    return download_tracks(all_urls[:target_tracks])


if __name__ == "__main__":
    with open("genres.json") as f:
        genres = json.load(f)
    paths = run(genres[0])
    print(f"Indirilen dosyalar: {[str(p) for p in paths]}")
