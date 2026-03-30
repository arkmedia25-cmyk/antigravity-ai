import os
import io
import json
import subprocess
import urllib.request
import platform
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_OUTPUT_DIR = "outputs"
_W, _H = 1080, 1920
_CX = _W // 2

_BLACK  = (0,   0,   0)
_NAVY   = (10,  10,  46)
_WHITE  = (255, 255, 255)
_TURQ   = (0,   212, 255)
_YELLOW = (255, 235, 60)
_ORANGE = (255, 140, 0)
_BLUE   = (0,   150, 255)

_FONT_PATH = "Roboto-Bold.ttf"
if not os.path.exists(_FONT_PATH):
    print("[video_skill] Downloading Roboto font...")
    try:
        urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf", _FONT_PATH)
    except Exception as e:
        print(f"[video_skill] Warning: Failed to download font: {e}")

_GAP      = 0.20   # black gap between sections (seconds)
_FADE_IN  = 0.30   # fade-in duration
_FADE_OUT = 0.30   # fade-out duration

# ── Font & drawing helpers ─────────────────────────────────────────────────────

def _font(size: int, emoji: bool = False) -> ImageFont.FreeTypeFont:
    try:
        if os.path.exists(_FONT_PATH):
            return ImageFont.truetype(_FONT_PATH, size)
    except IOError:
        pass
    return ImageFont.load_default()

def _sz(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]

def _center(draw, text, font, cy, color):
    w, h = _sz(draw, text, font)
    draw.text((_CX - w // 2, cy - h // 2), text, font=font, fill=color)

def _wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        if _sz(draw, test, font)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def _multiline(draw, lines, font, center_y, color, spacing=26):
    _, lh = _sz(draw, "Ag", font)
    total_h = len(lines) * (lh + spacing) - spacing
    y = center_y - total_h // 2
    for line in lines:
        w, _ = _sz(draw, line, font)
        draw.text((_CX - w // 2, y), line, font=font, fill=color)
        y += lh + spacing

# ── Frame builders ─────────────────────────────────────────────────────────────

def _build_hook() -> str:
    img  = Image.new("RGB", (_W, _H), _BLACK)
    draw = ImageDraw.Draw(img)
    f_em   = _font(160, emoji=True)
    f_main = _font(90)
    em = "\u26a0\ufe0f" # Warning emoji
    ew, eh = _sz(draw, em, f_em)
    draw.text((_CX - ew // 2, 620), em, font=f_em, fill=_ORANGE)
    _multiline(draw, ["DIT WIST JE NOG NIET...", "over dit onderwerp!"], f_main, center_y=1000, color=_WHITE, spacing=28)
    path = os.path.join(_OUTPUT_DIR, "frame_0_hook.png")
    img.save(path)
    return path

def _build_content(ts_data: list) -> str:
    img  = Image.new("RGB", (_W, _H), _NAVY)
    draw = ImageDraw.Draw(img)
    f_body = _font(72)
    # Combine sentences for content
    content_text = " ".join([s["sentence"] for s in ts_data[1:4]]) if len(ts_data) >= 4 else "Belangrijke informatie..."
    lines = _wrap(draw, content_text, f_body, max_w=900)
    _multiline(draw, lines, f_body, center_y=_H // 2, color=_WHITE, spacing=28)
    draw.line([(80, _H - 120), (_W - 80, _H - 120)], fill=_TURQ, width=2)
    f_sm = _font(42)
    _center(draw, "Meer info? Link in bio", f_sm, cy=_H - 72, color=_TURQ)
    path = os.path.join(_OUTPUT_DIR, "frame_1_content.png")
    img.save(path)
    return path

def _build_cta() -> str:
    img  = Image.new("RGB", (_W, _H), _NAVY)
    draw = ImageDraw.Draw(img)
    f_q    = _font(80)
    f_em   = _font(62, emoji=True)
    f_btn  = _font(56)
    f_link = _font(48)
    _multiline(draw, ["Wat ga jij", "vandaag doen?"], f_q, center_y=820, color=_WHITE, spacing=24)
    em = "\U0001f4ac"
    ew, _ = _sz(draw, em, f_em)
    draw.text((_CX - ew // 2, 970), em, font=f_em, fill=_WHITE)
    bx0, by0, bx1, by1 = 60, 1100, _W - 60, 1360
    draw.rectangle([bx0, by0, bx1, by1], outline=_BLUE, width=3)
    draw.rectangle([bx0 - 4, by0 - 4, bx1 + 4, by1 + 4], outline=(0, 80, 180), width=2)
    icons = "\U0001f44d   \U0001f4be   \U0001f465"
    iw, _ = _sz(draw, icons, f_em)
    draw.text((_CX - iw // 2, by0 + 30), icons, font=f_em, fill=_WHITE)
    labels = "Like        Bewaar        Volg ons"
    lw, _ = _sz(draw, labels, f_btn)
    draw.text((_CX - lw // 2, by0 + 130), labels, font=f_btn, fill=_YELLOW)
    link = "\U0001f447 Link in bio"
    llw, _ = _sz(draw, link, f_link)
    draw.text((_CX - llw // 2, _H - 130), link, font=f_link, fill=_TURQ)
    path = os.path.join(_OUTPUT_DIR, "frame_2_cta.png")
    img.save(path)
    return path

# ── Main FFmpeg execution ────────────────────────────────────────────────────────

def create_reel(
    audio_path: str = "outputs/audio_final.mp3",
    output_filename: str = "final_video.mp4",
) -> str:
    """
    Creates the video by generating flat PNGs and stitching them via FFmpeg process.
    Uses 0% RAM compared to MoviePy. Resolves DigitalOcean Droplet Broken Pipe.
    """
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(_OUTPUT_DIR, output_filename)
    if os.path.exists(output_path):
        os.remove(output_path)

    # 1. Provide minimal fake timestamps if timestamps.json missing
    ts_path = os.path.join(_OUTPUT_DIR, "timestamps.json")
    if os.path.exists(ts_path):
        try:
            with open(ts_path, encoding="utf-8") as f:
                ts = json.load(f)
        except:
            ts = []
    else:
        ts = []

    if len(ts) < 5:
        # Generate dummy 15s segments placeholder
        ts = [{"sentence": f"Deel {i}", "start": i*3.0, "end": (i+1)*3.0} for i in range(5)]

    # 2. Extract durations
    d_hook = max(0.5, ts[0]["end"] - ts[0]["start"])
    d_content = max(0.5, ts[4]["start"] - ts[1]["start"])
    d_cta = 5.0 # Let audio length determine the rest. We use a static 5.0 or determine from audio.

    # 3. Create static images (uses negligible memory)
    img_hook = _build_hook()
    img_content = _build_content(ts)
    img_cta = _build_cta()

    print(f"[video_skill] Natively generating video with FFmpeg. Resolutions: 1080x1920")

    # 4. Construct FFmpeg command
    # Filtergraph: Fade in/out each image, pad with black gaps in between
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "24", "-t", str(d_hook), "-i", img_hook,
        "-f", "lavfi", "-t", str(_GAP), "-i", "color=c=black:s=1080x1920:r=24",
        "-loop", "1", "-framerate", "24", "-t", str(d_content), "-i", img_content,
        "-f", "lavfi", "-t", str(_GAP), "-i", "color=c=black:s=1080x1920:r=24",
        "-loop", "1", "-framerate", "24", "-t", "10", "-i", img_cta, # cta is long, audio will cut it
        "-i", audio_path,
        "-filter_complex",
        (
            f"[0:v]fade=t=in:st=0:d={_FADE_IN},fade=t=out:st={d_hook - _FADE_OUT}:d={_FADE_OUT}[v0];"
            f"[2:v]fade=t=in:st=0:d={_FADE_IN},fade=t=out:st={d_content - _FADE_OUT}:d={_FADE_OUT}[v2];"
            f"[4:v]fade=t=in:st=0:d={_FADE_IN}[v4];"
            f"[v0][1:v][v2][3:v][v4]concat=n=5:v=1:a=0[outv]"
        ),
        "-map", "[outv]",
        "-map", "5:a",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path
    ]

    print("[video_skill] Running FFmpeg command...")
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("[video_skill] FFmpeg failed!")
        print(e.stderr.decode("utf-8", errors="ignore"))
        raise RuntimeError(f"FFmpeg error: {e.stderr.decode('utf-8', errors='ignore')}")

    size_mb = os.path.getsize(output_path) / 1_000_000
    print(f"[video_skill] Video saved instantly: {output_path} ({size_mb:.1f} MB)")
    return output_path

if __name__ == "__main__":
    _path = create_reel()
    print("Test video:", _path)
