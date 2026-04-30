"""
pipeline/reels_builder.py
─────────────────────────
Full pipeline: binaural audio + HTML animation → 35s Reels MP4.

Usage:
    from pipeline.reels_builder import build
    mp4 = build(preset="delta-sleep", duration=35)
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

OUTPUT_DIR  = Path("output")
REELS_HTML  = Path("output/binaural_reels_35s.html")   # pre-built HTML


def build(
    preset:   str   = "delta-sleep",
    duration: int   = 35,
    fps:      int   = 30,
    html_path: Path | None = None,
    out_mp4:   Path | None = None,
) -> Path:
    """
    1. Generate binaural WAV audio.
    2. Render HTML animation → MP4 frames via Playwright.
    3. Mux audio into final MP4.
    Returns path to finished MP4.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)

    # ── Step 1: Audio ────────────────────────────────────────────────────────
    from pipeline.binaural_generate import generate as gen_audio
    print(f"\n[reels] Step 1/2 — Generating binaural audio ({preset}, {duration}s)...")
    audio_path = gen_audio(preset, duration, volume=0.55)

    # ── Step 2: HTML → MP4 ──────────────────────────────────────────────────
    from pipeline.html_to_video import render
    src_html = Path(html_path) if html_path else REELS_HTML
    dst_mp4  = Path(out_mp4)   if out_mp4  else OUTPUT_DIR / f"reels_{preset}_{duration}s.mp4"

    if not src_html.exists():
        raise FileNotFoundError(
            f"HTML not found: {src_html}\n"
            "Run make_reels.py first or pass html_path explicitly."
        )

    print(f"\n[reels] Step 2/2 — Rendering HTML → MP4 ({fps}fps, {duration}s)...")
    mp4 = render(
        html_path  = src_html,
        out_mp4    = dst_mp4,
        audio_path = audio_path,
        duration   = float(duration),
        fps        = fps,
        width      = 405,
        height     = 720,
    )

    print(f"\n[reels] ✓ Done: {mp4.resolve()}")
    return mp4
