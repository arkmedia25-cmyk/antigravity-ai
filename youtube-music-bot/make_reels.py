"""
make_reels.py — 35s Binaural Mind Reels MP4 uretici
Usage: python make_reels.py [--preset delta-sleep] [--duration 35]
"""
import sys
import subprocess
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
from pipeline.binaural_generate import generate as gen_binaural

OUTPUT_DIR = Path("output")
W, H = 405, 720
FPS  = 30

# Windows font paths — fallback zinciri
FONTS = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/verdana.ttf",
]

def _find_font() -> str:
    for f in FONTS:
        if Path(f).exists():
            # FFmpeg icin : karakterini escape et
            return f.replace(":", "\\:")
    return ""


def _dt(text: str, x: str, y: str, size: int, color: str,
        t_start: float, t_end: float, font: str) -> str:
    """
    Tek bir drawtext filtresi uret.
    - text icindeki ozel karakterleri escape et
    - enable ile goster/gizle (alpha yok — Windows uyumlu)
    """
    safe = (text
            .replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace(":", "\\:")
            .replace("[", "\\[")
            .replace("]", "\\]"))
    enable = f"between(t\\,{t_start}\\,{t_end})"
    parts = [
        f"drawtext=fontfile='{font}'",
        f"text='{safe}'",
        f"x={x}",
        f"y={y}",
        f"fontsize={size}",
        f"fontcolor={color}",
        f"enable='{enable}'",
    ]
    return ":".join(parts)


def build_video(audio_path: Path, out_path: Path, duration: float = 35.0) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    font = _find_font()
    cx   = "(w-text_w)/2"

    # ── Timeline
    T = dict(hook=3.5, intro=7.0, title=12.0, main=29.0, end=duration)

    texts = [
        # HOOK (0 – 3.5s)
        _dt("Can't sleep?",          cx, "h/2-80",  48, "white",       0,        T["hook"],  font),
        _dt("Brain won't stop?",     cx, "h/2-20",  34, "0xaa88ff",   0,        T["hook"],  font),
        _dt("Keep watching...",      cx, "h/2+50",  18, "0x7766cc",   0.5,      T["hook"],  font),

        # INTRO (3.5 – 7s)
        _dt("BINAURAL MIND",         cx, "h/2-25",  30, "white",       T["hook"],  T["intro"], font),
        _dt("Neural Audio",          cx, "h/2+20",  16, "0x8866ff",   T["hook"],  T["intro"], font),

        # TITLE (7 – 12s)
        _dt("Deep Focus",            cx, "h/2-70",  54, "white",       T["intro"], T["title"], font),
        _dt("and Sleep",             cx, "h/2+8",   54, "0x9966ff",   T["intro"], T["title"], font),
        _dt("Binaural Frequencies",  cx, "h/2+85",  15, "0x6655aa",   T["intro"], T["title"], font),

        # MAIN VIS (12 – 29s)
        _dt("BINAURAL MIND",         cx, "38",       13, "0x6644cc",   T["title"], T["main"],  font),
        _dt("Deep Focus and Sleep",  cx, "h-105",   27, "white",       T["title"], T["main"],  font),
        _dt("Binaural Frequencies",  cx, "h-72",    13, "0x6655aa",   T["title"], T["main"],  font),
        _dt("a 8-12Hz  t 4-8Hz  d 1-4Hz", cx, "h-48", 11, "0x5588ff", T["title"], T["main"], font),

        # CTA (29 – 35s)
        _dt("Like what you hear?",   cx, "h/2-90",  17, "0xaa88ff",   T["main"],  T["end"],   font),
        _dt("Subscribe and Like",    cx, "h/2-40",  46, "white",       T["main"],  T["end"],   font),
        _dt("New sessions every day", cx, "h/2+35", 15, "0x8866ff",   T["main"],  T["end"],   font),
        _dt(">> SUBSCRIBE NOW <<",   cx, "h/2+90",  21, "0x9966ff",   T["main"],  T["end"],   font),
    ]

    # ── filter_complex
    # Katman 1: showwaves (ses dalgasi) + showfreqs (frekans barlar)
    # Katman 2: Tum drawtext zinciri
    vf_chain = ",".join(texts)

    filter_complex = (
        # ses dalgasi katmani
        f"[1:a]showwaves=s={W}x160:mode=cline:colors=0x6644ff@0.50:rate={FPS}:scale=sqrt[wave];"
        f"[1:a]showfreqs=s={W}x70:mode=bar:ascale=log:colors=0x4477ff@0.55:rate={FPS}[freq];"
        # arka plan
        f"color=c=0x020008:size={W}x{H}:rate={FPS}[bg];"
        f"[bg][wave]overlay=0:{H//2+30}:format=auto[bw];"
        f"[bw][freq]overlay=0:{H-155}:format=auto[bwf];"
        # text zinciri
        f"[bwf]{vf_chain}[out]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f",  "lavfi",
        "-i",  f"color=c=0x020008:size={W}x{H}:rate={FPS}",
        "-i",  str(audio_path),
        "-filter_complex", filter_complex,
        "-map",   "[out]",
        "-map",   "1:a",
        "-c:v",   "libx264", "-preset", "fast", "-crf", "22",
        "-c:a",   "aac",     "-b:a",    "192k",
        "-t",     str(duration),
        "-pix_fmt", "yuv420p",
        str(out_path),
    ]

    print(f"[reels] FFmpeg calistiriliyor — {duration}s video...")
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        # Son 2000 karakter yeterli hata bilgisi verir
        print("[reels] HATA (stderr son kisim):")
        print(res.stderr[-2000:])
        raise RuntimeError("FFmpeg basarisiz")

    mb = out_path.stat().st_size / 1_048_576
    print(f"[reels] Video hazir: {out_path}  ({mb:.1f} MB)")
    return out_path


def main(preset: str = "delta-sleep", duration: int = 35) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"[reels] Preset={preset}  Sure={duration}s")

    # 1. Binaural ses
    audio = gen_binaural(preset, duration, volume=0.55)

    # 2. Video
    out = OUTPUT_DIR / "binaural_reels_35s.mp4"
    build_video(audio, out, float(duration))

    print(f"\n[reels] Tamam: {out.resolve()}")
    # Otomatik ac
    subprocess.Popen(["start", "", str(out.resolve())], shell=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset",   default="delta-sleep",
                    choices=["delta-sleep","theta-meditation","alpha-focus",
                             "beta-energy","gamma-creativity"])
    ap.add_argument("--duration", type=int, default=35)
    a = ap.parse_args()
    main(a.preset, a.duration)
