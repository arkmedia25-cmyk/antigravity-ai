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
    
    # Refined size for 1080x1920 canvas (Not too huge, not too small)
    final_size = size + 20
    
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

def _multiline(draw, lines, font, center_y, color, spacing=45):
    _, lh = _sz(draw, "Ag", font)
    # Correct total height calculation for centering jumbo fonts
    total_h = len(lines) * (lh + spacing) - spacing
    y = center_y - total_h // 2
    for line in lines:
        w, _ = _sz(draw, line, font)
        # Vertical centering within each line's slot
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
    
    f_hook = _font(120, theme["font_title"]) # Uniform size
    lines = ["DIT WIST JE NOG NIET...", "Over deze routine!"]
    _multiline(draw, lines, f_hook, center_y=1100, color=theme["text"], spacing=50)
    
    path = os.path.join(_OUTPUT_DIR, f"frame_{theme['brand_name']}_0_hook.png")
    img.save(path)
    return path

def _build_sentence_frame(text: str, theme, index: int) -> str:
    img  = Image.new("RGB", (_W, _H), theme["bg"])
    draw = ImageDraw.Draw(img)
    
    # Premium Accent: Subtle glow
    draw.ellipse([_CX - 400, _H // 2 - 350, _CX + 400, _H // 2 + 350], fill=theme["accent2"])
    
    f_body = _font(110, theme["font_body"])
    lines = _wrap(draw, text, f_body, max_w=900)
    _multiline(draw, lines, f_body, center_y=_H // 2, color=theme["text"], spacing=50)
    
    path = os.path.join(_OUTPUT_DIR, f"frame_content_{index}.png")
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
    # Calculate dynamic durations based on audio duration
    audio_duration = 15.0
    try:
        import subprocess
        res = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path], 
                             capture_output=True, text=True)
        audio_duration = float(res.stdout.strip())
    except:
        pass

    # Split script into sentences for dynamic flow
    # Since we don't have word-level timestamps, we estimate based on sentence length
    sentences = [s.strip() for s in ts[1:-1]] if len(ts) > 2 else ["Blijf kijken voor meer wellness tips!"]
    total_chars = sum(len(s) for s in sentences)
    content_duration = audio_duration - 10.0 # Reserve 5s for hook and 5s for CTA
    if content_duration < 5.0: content_duration = 10.0
    
    print(f"[video_skill] Generating dynamic frames for brand: {brand}...")
    img_hook = _build_hook(theme)
    img_cta = _build_cta(theme)
    
    # Clip generation helpers
    def make_clip(img_path, dur, out_name):
        clip_path = os.path.join(_OUTPUT_DIR, out_name)
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-t", str(dur),
            "-i", img_path, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
            "-preset", "ultrafast", clip_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return clip_path

    # Build individual clips for each sentence
    content_clips = []
    for i, text in enumerate(sentences):
        # Calculate proportional duration
        sent_dur = (len(text) / total_chars) * content_duration
        img_p = _build_sentence_frame(text, theme, i)
        c_p = make_clip(img_p, sent_dur, f"c_{i}.mp4")
        content_clips.append(c_p)

    print("[video_skill] Assembling final dynamic pipeline...")
    v1 = make_clip(img_hook, 5.0, "v1.mp4")
    v3 = make_clip(img_cta, 10.0, "v3.mp4")
    
    list_path = os.path.join(_OUTPUT_DIR, "concat.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        f.write("file 'v1.mp4'\n")
        for i in range(len(content_clips)):
            f.write(f"file 'c_{i}.mp4'\n")
        f.write("file 'v3.mp4'\n")

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
    print(f"[video_skill] Dynamic Video assembled: {output_path} ({size_mb:.1f} MB)")
    return output_path

if __name__ == "__main__":
    _path = create_reel()
    print("Test video:", _path)
