"""
test_html2mp4.py — Pipeline smoke test
Renders the first 5 seconds of binaural_reels_35s.html → test_render.mp4
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.html_to_video import render

html = Path("output/binaural_reels_35s.html")
out  = Path("output/test_render_5s.mp4")

if not html.exists():
    print(f"[ERROR] HTML not found: {html}")
    sys.exit(1)

print(f"Testing 5s render of: {html}")
mp4 = render(
    html_path  = html,
    out_mp4    = out,
    audio_path = None,   # no audio for quick test
    duration   = 5.0,
    fps        = 30,
    width      = 405,
    height     = 720,
    crf        = 23,
    preset     = "ultrafast",
)
print(f"\n✓ Test render OK: {mp4}")
import subprocess
subprocess.Popen(["start", "", str(mp4.resolve())], shell=True)
