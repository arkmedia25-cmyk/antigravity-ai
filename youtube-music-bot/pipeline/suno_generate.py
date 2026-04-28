import os
import sys
import time
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()

KIE_API_KEY = os.getenv("KIE_API_KEY")
OUTPUT_DIR = Path("output/audio")
BASE_URL = "https://api.kie.ai/api/v1"


def generate_tracks(prompt: str) -> list[str]:
    """Generate tracks via kie.ai Suno API, return list of MP3 URLs."""
    headers = {
        "Authorization": f"Bearer {KIE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "model": "V4_5",
        "instrumental": True,
        "customMode": False,
        "callBackUrl": "https://httpbin.org/post",
    }

    last_error: Exception = RuntimeError("No attempts made")
    for attempt in range(3):
        try:
            print(f"[suno] Sending request (attempt {attempt + 1}/3)...")
            resp = requests.post(f"{BASE_URL}/generate", headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            if data.get("data") is None:
                raise RuntimeError(f"kie.ai API error (code={data.get('code')}): {data.get('msg')}")

            task_id = data["data"]["taskId"]
            print(f"[suno] Task ID: {task_id}")
            return _poll_task(task_id, headers)
        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt >= 2:
                break
            print(f"[suno] Request failed: {e}, retrying...")
            time.sleep(5 * (attempt + 1))
    raise last_error


def _poll_task(task_id: str, headers: dict, max_wait: int = 1800) -> list[str]:
    """Poll until generation is complete, return MP3 URLs."""
    elapsed = 0
    fail_count = 0
    while elapsed < max_wait:
        try:
            resp = requests.get(f"{BASE_URL}/generate/record-info", headers=headers,
                                params={"taskId": task_id}, timeout=30)
            resp.raise_for_status()
            raw = resp.json()
            data = raw.get("data") or {}
            fail_count = 0

            status = data.get("status", "")
            response = data.get("response") or {}
            tracks = response.get("sunoData") or []
            ready = [t for t in tracks if t.get("audioUrl")]

            print(f"[suno] Status: {status} | tracks: {len(tracks)} | ready: {len(ready)} ({elapsed}s)")

            if ready:
                urls = [t["audioUrl"] for t in ready]
                print(f"[suno] {len(urls)} tracks ready")
                return urls

            if status in ("FAILED", "GENERATE_AUDIO_FAILED"):
                fail_count += 1
                if fail_count >= 3:
                    raise RuntimeError(f"Suno task failed: {status}")
                print(f"[suno] Task failed, retrying... ({fail_count}/3)")
                time.sleep(15)
                elapsed += 15
                continue

            time.sleep(30)
            elapsed += 30
        except requests.exceptions.RequestException as e:
            fail_count += 1
            if fail_count >= 3:
                raise RuntimeError(f"Network error after 3 attempts: {e}")
            print(f"[suno] Network error, retrying... ({fail_count}/3)")
            time.sleep(15)
            elapsed += 15

    raise TimeoutError("Suno task timed out after 30 min")


def download_tracks(urls: list[str]) -> list[Path]:
    """Download MP3 URLs to output/audio/."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = []

    for i, url in enumerate(urls):
        dest = OUTPUT_DIR / f"track_{i:02d}.mp3"
        resp = requests.get(url, timeout=60, stream=True)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[suno] Downloaded: {dest.name}")
        paths.append(dest)

    return paths


def run(genre: dict) -> list[Path]:
    prompt = genre["prompt"]
    duration_min = genre.get("duration_min", 60)
    # Half the tracks — main_runner doubles them via loop (50% cost saving)
    target_tracks = max(2, duration_min // 6)
    calls_needed = (target_tracks + 1) // 2

    print(f"[suno] Prompt: {prompt}")
    print(f"[suno] Target: {target_tracks} tracks / {duration_min} min — {calls_needed} API calls")

    all_urls: list[str] = []
    for call_num in range(calls_needed):
        print(f"[suno] Call {call_num + 1}/{calls_needed}...")
        urls = generate_tracks(prompt)
        all_urls.extend(urls)
        if len(all_urls) >= target_tracks:
            break

    return download_tracks(all_urls[:target_tracks])


if __name__ == "__main__":
    with open("genres.json") as f:
        genres = json.load(f)
    paths = run(genres[0])
    print(f"Downloaded: {[str(p) for p in paths]}")
