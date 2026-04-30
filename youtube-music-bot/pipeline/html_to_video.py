"""
pipeline/html_to_video.py
─────────────────────────
Renders an animated HTML file to MP4 using Playwright + FFmpeg.

Strategy (frame-file approach — most reliable on Windows):
  1. Open the HTML in headless Chromium with a fake clock.
  2. Advance the clock by 1000/fps ms per frame → drives rAF deterministically.
  3. Save each frame as a numbered PNG to a temp folder.
  4. Call FFmpeg once with the image sequence → H.264 MP4.
  5. Mux optional audio file.
  6. Clean up temp frames.

Requirements:
    pip install playwright
    playwright install chromium
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_FPS      = 30
DEFAULT_DURATION = 35.0
DEFAULT_WIDTH    = 405
DEFAULT_HEIGHT   = 720


def _bar(frame: int, total: int, fps: int) -> None:
    pct    = frame / total * 100
    filled = int(30 * frame / total)
    bar    = "█" * filled + "░" * (30 - filled)
    print(f"\r[html2mp4] [{bar}] {pct:5.1f}%  {frame/fps:5.1f}s / {total/fps:.1f}s",
          end="", flush=True)


def render(
    html_path:  Path,
    out_mp4:    Path,
    audio_path: Path | None = None,
    *,
    duration: float = DEFAULT_DURATION,
    fps:      int   = DEFAULT_FPS,
    width:    int   = DEFAULT_WIDTH,
    height:   int   = DEFAULT_HEIGHT,
    crf:      int   = 18,
    preset:   str   = "fast",
) -> Path:
    """Render html_path → out_mp4 (optionally mux audio_path)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError(
            "Run: pip install playwright && playwright install chromium"
        )

    html_path = Path(html_path).resolve()
    out_mp4   = Path(out_mp4).resolve()
    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    total_frames = int(duration * fps)
    frame_ms     = 1000.0 / fps

    print(f"[html2mp4] {html_path.name}  →  {out_mp4.name}")
    print(f"[html2mp4] {width}×{height} @ {fps}fps  {duration}s  ({total_frames} frames)")

    # ── Temp folder for frames ────────────────────────────────────────────────
    tmp_dir = Path(tempfile.mkdtemp(prefix="html2mp4_"))
    print(f"[html2mp4] Frames → {tmp_dir}")

    try:
        # ── Step 1: Capture frames ────────────────────────────────────────────
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--disable-gpu", "--no-sandbox"])
            ctx  = browser.new_context(
                viewport={"width": width, "height": height},
                device_scale_factor=1,
            )
            page = ctx.new_page()

            # Freeze real-time clock BEFORE navigating
            page.clock.install(time=0)
            page.goto(html_path.as_uri(), wait_until="load")

            # Tick 50ms so fonts.ready resolves and first rAF fires
            page.clock.run_for(50)

            stage = page.locator(".stage")

            print(f"[html2mp4] Capturing {total_frames} frames...")
            for i in range(total_frames):
                page.clock.run_for(int(frame_ms))
                frame_path = tmp_dir / f"frame_{i:06d}.png"
                stage.screenshot(path=str(frame_path), type="png")
                _bar(i + 1, total_frames, fps)

            print()  # newline after progress bar
            browser.close()

        # ── Step 2: Verify frames ─────────────────────────────────────────────
        frames_written = sorted(tmp_dir.glob("frame_*.png"))
        print(f"[html2mp4] Frames on disk: {len(frames_written)}")
        if not frames_written:
            raise RuntimeError("No frames were captured — check Playwright setup")

        # Write a filelist (most reliable across OS/FFmpeg versions)
        filelist = tmp_dir / "filelist.txt"
        with filelist.open("w", encoding="utf-8") as fl:
            for fp in frames_written:
                # FFmpeg filelist needs forward slashes and escaped single quotes
                safe = fp.as_posix().replace("'", "\\'")
                fl.write(f"file '{safe}'\n")
                fl.write(f"duration {1/fps:.6f}\n")

        # ── Step 2: Encode with FFmpeg (concat demuxer) ───────────────────────
        print("[html2mp4] Encoding MP4...")
        has_audio = audio_path and Path(audio_path).exists()

        cmd = [
            "ffmpeg", "-y",
            "-f",  "concat",
            "-safe", "0",
            "-i",  str(filelist),
        ]

        if has_audio:
            cmd += ["-i", str(audio_path)]

        cmd += [
            "-c:v",     "libx264",
            "-preset",  preset,
            "-crf",     str(crf),
            "-pix_fmt", "yuv420p",
            "-t",       str(duration),
            "-r",       str(fps),
        ]

        if has_audio:
            cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]

        cmd.append(str(out_mp4))

        res = subprocess.run(cmd, capture_output=True, text=True,
                             encoding="utf-8", errors="replace")
        if res.returncode != 0:
            print(res.stderr[-2000:], file=sys.stderr)
            raise RuntimeError("FFmpeg encoding failed")

    finally:
        # Always remove temp frames
        shutil.rmtree(tmp_dir, ignore_errors=True)

    mb = out_mp4.stat().st_size / 1_048_576
    print(f"[html2mp4] ✓ {out_mp4}  ({mb:.1f} MB)")
    return out_mp4
