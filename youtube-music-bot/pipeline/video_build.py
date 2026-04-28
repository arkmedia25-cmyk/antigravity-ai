import sys
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_VIDEO = Path("output/final_video.mp4")


def _get_duration(path: Path) -> float:
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path)
    ], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def _pick_background(slug: str, bg_dir: Path) -> Path:
    """Use bg_<slug>.mp4 if available, fall back to background_1080p.mp4, then first MP4."""
    niche_bg = bg_dir / f"bg_{slug}.mp4"
    if niche_bg.exists():
        return niche_bg
    fallback = bg_dir / "background_1080p.mp4"
    if fallback.exists():
        return fallback
    backgrounds = list(bg_dir.glob("*.mp4"))
    if not backgrounds:
        raise FileNotFoundError(f"No backgrounds found in: {bg_dir}")
    return backgrounds[0]


def run(audio_path: Path, slug: str = "", bg_dir: Path | None = None) -> Path:
    """Background MP4 + audio -> YouTube video (1920x1080)."""
    resolved_bg_dir = bg_dir or Path("backgrounds")
    bg = _pick_background(slug, resolved_bg_dir)
    audio_dur = _get_duration(audio_path)

    OUTPUT_VIDEO.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", str(bg),
        "-i", str(audio_path),
        "-filter_complex",
        (
            "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1[bg];"
            "[1:a]showwaves=s=1920x200:mode=cline:colors=white@0.6[wave];"
            "[bg][wave]overlay=0:880[out]"
        ),
        "-map", "[out]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(audio_dur),
        "-shortest",
        str(OUTPUT_VIDEO)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"[video] Created: {OUTPUT_VIDEO}")
    return OUTPUT_VIDEO
