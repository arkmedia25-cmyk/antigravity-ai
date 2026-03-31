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

# ── Health & Brand Themes ─────────────────────────────────────────────────────
THEMES = {
    "glow": {
        "bg": (254, 245, 238),    # Soft Peach/Coral BG
        "accent": (255, 112, 86), # GlowUp Coral
        "accent2": (255, 180, 160),
        "text": (62, 44, 40),     # Warm Charcoal
        "font_title": "body",     # GlowUp uses vibrant sans-serif focus
        "font_body": "body",
        "brand_name": "@GlowUpNL",
        "icons": (255, 112, 86)
    },
    "holisti": {
        "bg": (247, 243, 240),    # Earthy Beige/Cream
        "accent": (130, 150, 120), # Sage Green
        "accent2": (210, 205, 245),# Lavender
        "text": (40, 44, 45),     # Deep Charcoal
        "font_title": "title",    # Holisti uses elegant serif focus
        "font_body": "body",
        "brand_name": "@HolistiGlow",
        "icons": (130, 150, 120)
    }
}

# ── Typography Management ─────────────────────────────────────────────────────
_FONTS = {
    "title": "PlayfairDisplay-Bold.ttf",
    "body":  "Montserrat-Medium.ttf"
}

_FONT_URLS = {
    "title": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay-Bold.ttf",
    "body":  "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Medium.ttf"
}

def _ensure_fonts():
    for name, path in _FONTS.items():
        if not os.path.exists(path):
            print(f"[video_skill] Downloading {name} font...")
            try:
                urllib.request.urlretrieve(_FONT_URLS[name], path)
            except Exception as e:
                print(f"[video_skill] Warning: Failed to download {name}: {e}")

_ensure_fonts()

_GAP      = 0.20   # black gap between sections (seconds)
_FADE_IN  = 0.30   # fade-in duration
_FADE_OUT = 0.30   # fade-out duration

# ── Font & drawing helpers ─────────────────────────────────────────────────────

def _font(size: int, type: str = "body") -> ImageFont.FreeTypeFont:
    # Use the script's directory to find the root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    font_filename = _FONTS.get(type, "Montserrat-Medium.ttf")
    path = os.path.join(base_dir, font_filename)
    
    # Scale up size for 1080x1920 canvas (High Visibility)
    final_size = size + 200 if size < 120 else size + 250
    
    try:
        if os.path.exists(path):
            return ImageFont.truetype(path, final_size)
    except IOError:
        pass
        
    # CRITICAL FALLBACK: If TTF fails, we MUST still have large text.
    # PIL's load_default() doesn't support size, so we try system fonts
    for fallback in ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]:
        try:
            return ImageFont.truetype(fallback, final_size)
        except:
            continue
            
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

# ── Frame builders (Premium Redesign) ─────────────────────────────────────────

def _draw_rounded_rect(draw, coords, radius, fill):
    x0, y0, x1, y1 = coords
    draw.pieslice([x0, y0, x0 + radius * 2, y0 + radius * 2], 180, 270, fill=fill)
    draw.pieslice([x1 - radius * 2, y0, x1, y0 + radius * 2], 270, 360, fill=fill)
    draw.pieslice([x1 - radius * 2, y1 - radius * 2, x1, y1], 0, 90, fill=fill)
    draw.pieslice([x0, y1 - radius * 2, x0 + radius * 2, y1], 90, 180, fill=fill)
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)

def _build_hook(theme) -> str:
    img  = Image.new("RGB", (_W, _H), theme["bg"])
    draw = ImageDraw.Draw(img)
    
    # Decorative Circle
    draw.ellipse([_CX - 400, 300, _CX + 400, 1100], outline=theme["accent2"] if "accent2" in theme else theme["accent"], width=4)
    
    # Stylized Warning Triangle
    draw.polygon([(_CX, 600), (_CX-60, 720), (_CX+60, 720)], fill=theme["accent"])
    
    f_hook = _font(110, theme["font_title"])
    _multiline(draw, ["DIT WIST JE NOG NIET...", "over dit onderwerp!"], f_hook, center_y=1000, color=theme["text"], spacing=40)
    
    path = os.path.join(_OUTPUT_DIR, f"frame_{theme['brand_name']}_0_hook.png")
    img.save(path)
    return path

def _build_content(ts_data: list, theme) -> str:
    img  = Image.new("RGB", (_W, _H), theme["bg"])
    draw = ImageDraw.Draw(img)
    
    # Soft background border
    draw.rectangle([40, 40, _W - 40, _H - 40], outline=theme["accent"], width=2)
    
    f_body = _font(80, theme["font_body"])
    content_text = " ".join([s["sentence"] for s in ts_data[1:4]]) if len(ts_data) >= 4 else "Belangrijke informatie..."
    lines = _wrap(draw, content_text, f_body, max_w=850)
    
    _multiline(draw, lines, f_body, center_y=_H // 2, color=theme["text"], spacing=35)
    
    # Decorative line
    draw.line([_CX - 150, _H - 250, _CX + 150, _H - 250], fill=theme["accent"], width=6)
    
    path = os.path.join(_OUTPUT_DIR, f"frame_{theme['brand_name']}_1_content.png")
    img.save(path)
    return path

def _build_cta(theme) -> str:
    img  = Image.new("RGB", (_W, _H), theme["bg"])
    draw = ImageDraw.Draw(img)
    
    f_q   = _font(90, theme["font_title"])
    f_btn = _font(54, theme["font_body"])
    
    _multiline(draw, ["Wat ga jij", "vandaag doen?"], f_q, center_y=800, color=theme["text"], spacing=30)
    
    # Custom drawn social buttons
    bx0, by0, bx1, by1 = 150, 1050, _W - 150, 1350
    _draw_rounded_rect(draw, [bx0, by0, bx1, by1], 40, fill=theme["accent"])
    
    labels = ["Like & Save", f"Volg {theme['brand_name']}"]
    y_pos = by0 + 100
    for label in labels:
        _center(draw, label, f_btn, cy=y_pos, color=(255, 255, 255))
        y_pos += 120
        
    f_link = _font(50, theme["font_body"])
    _center(draw, "Klik op de link in bio voor meer hulp", f_link, cy=_H - 150, color=theme["accent"])
    
    path = os.path.join(_OUTPUT_DIR, f"frame_{theme['brand_name']}_2_cta.png")
    img.save(path)
    return path

# ── Main FFmpeg execution ────────────────────────────────────────────────────────

def create_reel(
    audio_path: str = "outputs/audio_final.mp3",
    output_filename: str = "final_video.mp4",
    brand: str = "holisti"
) -> str:
    """
    Creates the video with brand-specific themes.
    """
    theme = THEMES.get(brand, THEMES["holisti"])
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(_OUTPUT_DIR, output_filename)
    if os.path.exists(output_path):
        os.remove(output_path)

    ts_path = os.path.join(_OUTPUT_DIR, "timestamps.json")
    try:
        with open(ts_path, encoding="utf-8") as f:
            ts = json.load(f)
    except:
        ts = [{"sentence": f"Deel {i}", "start": i*3.0, "end": (i+1)*3.0} for i in range(5)]
    if len(ts) < 5:
        ts = [{"sentence": f"Deel {i}", "start": i*3.0, "end": (i+1)*3.0} for i in range(5)]

    # Calculate dynamic durations based on audio
    # But since we use -shortest, we can just set long buffers for segments 2 and 3
    d_hook = 5.0
    d_content = 30.0 # Plenty of space for tips
    d_cta = 15.0     # Plenty of space for CTA

    print(f"[video_skill] Natively generating frames for brand: {brand}...")
    img_hook = _build_hook(theme)
    img_content = _build_content(ts, theme)
    img_cta = _build_cta(theme)

    def make_clip(img_path, dur, out_name):
        clip_path = os.path.join(_OUTPUT_DIR, out_name)
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-t", str(dur),
            "-i", img_path, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
            "-preset", "ultrafast", clip_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return clip_path

    def make_black(dur, out_name):
        clip_path = os.path.join(_OUTPUT_DIR, out_name)
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-t", str(dur),
            "-i", "color=c=black:s=1080x1920:r=24", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "23", "-preset", "ultrafast", clip_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return clip_path

    print("[video_skill] Encoding lightweight segments (ZERO Memory Mode)...")
    v1 = make_clip(img_hook, d_hook, "v1.mp4")
    b1 = make_black(_GAP, "b1.mp4")
    v2 = make_clip(img_content, d_content, "v2.mp4")
    b2 = make_black(_GAP, "b2.mp4")
    v3 = make_clip(img_cta, d_cta, "v3.mp4")

    list_path = os.path.join(_OUTPUT_DIR, "concat.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        f.write(f"file 'v1.mp4'\nfile 'b1.mp4'\nfile 'v2.mp4'\nfile 'b2.mp4'\nfile 'v3.mp4'\n")

    print("[video_skill] Assembling final pipeline...")
    cmd_final = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
        "-i", audio_path, "-c:v", "copy", "-c:a", "aac", "-shortest", output_path
    ]

    try:
        subprocess.run(cmd_final, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("[video_skill] Concat failed!")
        raise RuntimeError(f"FFmpeg error: {e.stderr.decode('utf-8', errors='ignore')}")

    size_mb = os.path.getsize(output_path) / 1_000_000
    print(f"[video_skill] Video assembled flawlessly: {output_path} ({size_mb:.1f} MB)")
    return output_path

if __name__ == "__main__":
    _path = create_reel()
    print("Test video:", _path)
