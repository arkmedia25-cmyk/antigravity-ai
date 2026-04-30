"""
render_reels.py — One-command Reels producer
Usage:
    python render_reels.py
    python render_reels.py --preset theta-meditation --duration 35 --fps 30
    python render_reels.py --html output/binaural_reels_35s.html --out output/my_reel.mp4
"""
import sys
import argparse
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

PRESETS = ["delta-sleep", "theta-meditation", "alpha-focus", "beta-energy", "gamma-creativity"]


def main():
    ap = argparse.ArgumentParser(description="Render Binaural Mind Reels MP4")
    ap.add_argument("--preset",   default="delta-sleep", choices=PRESETS)
    ap.add_argument("--duration", type=int,   default=35)
    ap.add_argument("--fps",      type=int,   default=30)
    ap.add_argument("--html",     default=None, help="Override HTML source path")
    ap.add_argument("--out",      default=None, help="Override output MP4 path")
    ap.add_argument("--open",     action="store_true", help="Auto-open MP4 when done")
    args = ap.parse_args()

    print("=" * 55)
    print("  Binaural Mind — Reels Renderer")
    print(f"  Preset  : {args.preset}")
    print(f"  Duration: {args.duration}s  |  FPS: {args.fps}")
    print("=" * 55)

    from pipeline.reels_builder import build
    mp4 = build(
        preset    = args.preset,
        duration  = args.duration,
        fps       = args.fps,
        html_path = Path(args.html) if args.html else None,
        out_mp4   = Path(args.out)  if args.out  else None,
    )

    if args.open:
        subprocess.Popen(["start", "", str(mp4.resolve())], shell=True)
        print("[render_reels] Opened in default player.")


if __name__ == "__main__":
    main()
