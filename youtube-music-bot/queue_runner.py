"""
Runs all channels sequentially — one after the other.
Scheduled nightly at 01:00 via Task Scheduler or cron.
"""
import subprocess
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

CHANNEL_DIR = Path("channels")
LOG_DIR = Path("logs")


def _all_channels() -> list[str]:
    """Return active channel slugs in sorted order, skipping inactive or token-less channels."""
    slugs = []
    for d in sorted(CHANNEL_DIR.iterdir()):
        cfg_file = d / "channel.json"
        if not d.is_dir() or not cfg_file.exists():
            continue
        cfg = json.loads(cfg_file.read_text())
        if cfg.get("active", True) is False:
            print(f"[queue] {d.name} inactive, skipping")
            continue
        token = Path(cfg.get("token_file", ""))
        if not token.exists():
            print(f"[queue] {d.name} no token, skipping")
            continue
        slugs.append(d.name)
    return slugs


def run_channel(slug: str, publish_hour: int | None = None) -> bool:
    """Run single channel pipeline. Returns True on success."""
    log_file = LOG_DIR / f"{slug}.log"
    LOG_DIR.mkdir(exist_ok=True)

    print(f"\n[queue] {'='*50}")
    print(f"[queue] Starting: {slug} — {datetime.now().strftime('%H:%M:%S')}")
    print(f"[queue] Log: {log_file}")

    start = time.time()

    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n\n--- {datetime.now()} ---\n")
        cmd = [sys.executable, "-u", "main_runner.py", "--channel", slug]
        if publish_hour is not None:
            cmd += ["--publish-hour", str(publish_hour)]
        result = subprocess.run(cmd, stdout=log, stderr=log)

    elapsed = int(time.time() - start)
    mins = elapsed // 60
    secs = elapsed % 60

    if result.returncode == 0:
        print(f"[queue] OK  {slug} — {mins}m {secs}s")
        return True
    else:
        print(f"[queue] ERR {slug} (exit {result.returncode}) — {mins}m {secs}s")
        return False


def main(publish_hour: int | None = None) -> None:
    channels = _all_channels()

    if not channels:
        print("[queue] No active channels found. Exiting.")
        return

    print(f"[queue] Order: {' -> '.join(channels)}")
    print(f"[queue] Start: {datetime.now().strftime('%H:%M:%S')}\n")

    results = {}
    for slug in channels:
        results[slug] = "OK " if run_channel(slug, publish_hour=publish_hour) else "ERR"

    print(f"\n[queue] {'='*50}")
    print(f"[queue] All done — {datetime.now().strftime('%H:%M:%S')}")
    for slug, status in results.items():
        print(f"  {status}  {slug}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish-hour", type=int, default=None, help="Publish hour override (0-23, Amsterdam)")
    args = parser.parse_args()
    main(publish_hour=args.publish_hour)
