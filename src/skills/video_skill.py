import os
import json
import subprocess
import urllib.request
from PIL import Image, ImageDraw, ImageFont

_OUTPUT_DIR = "outputs"
_W, _H = 1080, 1920
_CX = _W // 2

# ── Brand Themes ──────────────────────────────────────────────────────────────
THEMES = {
    "glow": {
        "bg":         (254, 245, 238),
        "accent":     (255, 112, 86),
        "accent2":    (255, 185, 165),
        "text":       (62, 44, 40),
        "glass":      (255, 255, 255, 180), # Soft white glass
        "font_title": "title",
        "font_body":  "body",
        "brand_name": "@GlowUpNL",
    },
    "holisti": {
        "bg":         (247, 243, 240),
        "accent":     (130, 150, 120),
        "accent2":    (210, 220, 200),
        "text":       (40, 44, 45),
        "glass":      (255, 255, 255, 180), # Soft white glass
        "font_title": "title",
        "font_body":  "body",
        "brand_name": "@HolistiGlow",
    }
}

# ── Font management ───────────────────────────────────────────────────────────
_FONTS = {
    "title": "PlayfairDisplay-Bold.ttf",
    "body":  "Montserrat-Medium.ttf",
}
_FONT_URLS = {
    "title": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay-Bold.ttf",
    "body":  "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Medium.ttf",
}

def _ensure_fonts():
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for name, filename in _FONTS.items():
        full_path = os.path.join(base, filename)
        if not os.path.exists(full_path):
            try:
                print(f"[video_skill] Downloading {name} font...")
                urllib.request.urlretrieve(_FONT_URLS[name], full_path)
            except Exception as e:
                print(f"[video_skill] Warning: Could not download {name}: {e}")

_ensure_fonts()

def _font(size: int, font_type: str = "body") -> ImageFont.FreeTypeFont:
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    filename = _FONTS.get(font_type, "Montserrat-Medium.ttf")
    path = os.path.join(base, filename)
    try:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    except Exception:
        pass
    # Fallback: try system fonts
    for fallback in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                     "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(fallback):
            try:
                return ImageFont.truetype(fallback, size)
            except Exception:
                pass
    return ImageFont.load_default()

# ── Drawing helpers ───────────────────────────────────────────────────────────

def _sz(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]

def _wrap(draw, text: str, font, max_w: int) -> list:
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        w, _ = _sz(draw, test, font)
        if w <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines if lines else [text]

def _multiline(draw, lines: list, font, center_y: int, color, spacing: int = 20):
    _, lh = _sz(draw, "Ag", font)
    total_h = len(lines) * lh + (len(lines) - 1) * spacing
    y = center_y - total_h // 2
    for line in lines:
        w, _ = _sz(draw, line, font)
        draw.text((_CX - w // 2, y), line, font=font, fill=color)
        y += lh + spacing

def _clean_text(text: str) -> str:
    import re
    if not text: return ""
    text = re.sub(r'^\s*[•🌿✨\-1234567890\.\*\/]+\s*', '* ', text)
    clean = re.sub(r'[^\x00-\x7F\xC0-\xFF\.,!?\'\":\* ]+', '', text)
    return clean.strip()

def _draw_rounded_rect(draw, coords, radius: int, fill):
    x0, y0, x1, y1 = coords
    draw.ellipse([x0, y0, x0 + radius * 2, y0 + radius * 2], fill=fill)
    draw.ellipse([x1 - radius * 2, y0, x1, y0 + radius * 2], fill=fill)
    draw.ellipse([x1 - radius * 2, y1 - radius * 2, x1, y1], fill=fill)
    draw.ellipse([x0, y1 - radius * 2, x0 + radius * 2, y1], fill=fill)
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)

def _center(draw, text: str, font, cy: int, color):
    text = _clean_text(text)
    w, h = _sz(draw, "Ag", font)
    tw, _ = _sz(draw, text, font)
    draw.text((_CX - tw // 2, cy - h // 2), text, font=font, fill=color)

# ── Frame builders ────────────────────────────────────────────────────────────

def _build_sentence_frame(text: str, theme: dict, index: int) -> str:
    img  = Image.new("RGB", (_W, _H), theme["bg"])
    draw = ImageDraw.Draw(img)
    text = _clean_text(text)
    
    card_x0, card_x1 = 80, _W - 80
    card_y0, card_y1 = _H // 2 - 380, _H // 2 + 380
    
    # Modern Rounded Plate
    _draw_rounded_rect(draw, [card_x0, card_y0, card_x1, card_y1], 40, fill=theme["accent2"])
    
    # Accent Bar
    draw.rectangle([card_x0, card_y0 + 60, card_x0 + 10, card_y1 - 60], fill=theme["accent"])
    
    f = _font(72, theme["font_body"])
    lines = _wrap(draw, text, f, max_w=870)
    _multiline(draw, lines, f, center_y=_H // 2, color=theme["text"], spacing=22)
    
    path = os.path.join(_OUTPUT_DIR, f"frame_content_{index}.png")
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    img.save(path)
    return path

# ── Main video assembly ───────────────────────────────────────────────────────

def create_reel(
    fragments: list = None,
    image_path: str = None,
    output_filename: str = "final_video.mp4",
    brand: str = "glow",
    font_path: str = None
) -> str:
    theme = THEMES.get(brand, THEMES["glow"])
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(_OUTPUT_DIR, output_filename)
    if os.path.exists(output_path):
        try: os.remove(output_path)
        except: pass

    if fragments is None:
        frag_path = os.path.join(_OUTPUT_DIR, "fragments.json")
        try:
            if os.path.exists(frag_path):
                with open(frag_path, encoding="utf-8") as f:
                    fragments = json.load(f)
        except Exception: pass

    if not fragments:
        print("[video_skill] ERROR: No fragments provided or found.")
        return ""

    def get_duration(p: str) -> float:
        try:
            res = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", p],
                capture_output=True, text=True
            )
            return float(res.stdout.strip())
        except: return 3.0

    def make_clip(img_path: str, dur: float, out_name: str) -> str:
        clip_path = os.path.join(_OUTPUT_DIR, out_name)
        # Stable Fast Rendering (Static Background)
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-t", f"{dur:.2f}", "-i", img_path,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-preset", "ultrafast", clip_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return clip_path

    all_video_clips = []
    all_audio_files = []

    print(f"[video_skill] Rendering {len(fragments)} fragments...")

    for i, frag in enumerate(fragments):
        a_path = frag.get("audio") or frag.get("path")
        if not a_path: continue
        
        dur = get_duration(a_path)
        tag = frag.get("tag", "content")
        text = frag.get("sentence") or frag.get("text", "")
        
        # Combine background and glass plate
        img = Image.new("RGB", (_W, _H), theme["bg"])
        if image_path and os.path.exists(image_path):
            try:
                bg_img = Image.open(image_path).convert("RGB")
                ratio = max(_W/bg_img.width, _H/bg_img.height)
                bg_img = bg_img.resize((int(bg_img.width*ratio), int(bg_img.height*ratio)), Image.Resampling.LANCZOS)
                left = (bg_img.width - _W) // 2
                top = (bg_img.height - _H) // 2
                bg_img = bg_img.crop((left, top, left + _W, top + _H))
                img.paste(bg_img, (0, 0))
            except Exception as e:
                print(f"[video_skill] Warning background wrap: {e}")

        # Create Overlay Layer for Glassmorphism
        overlay_img = Image.new("RGBA", (_W, _H), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay_img)
        
        draw = ImageDraw.Draw(img) # Draw on the main image for measuerement first
        text_color = theme["text"]
        
        if tag == "hook":
            f = _font(85, theme["font_title"])
            lines = _wrap(draw, _clean_text(text), f, max_w=850)
            _, lh = _sz(draw, "Ag", f)
            total_h = len(lines) * lh + (len(lines) - 1) * 25
            
            # Header Plate (Glass) - Dynamic Height
            bx0, by0, bx1, by1 = 80, 200, _W - 80, 200 + total_h + 100
            _draw_rounded_rect(overlay_draw, [bx0, by0, bx1, by1], 60, fill=theme["glass"])
            
            img.paste(overlay_img, (0, 0), overlay_img)
            draw = ImageDraw.Draw(img)
            _multiline(draw, lines, f, center_y=(by0 + by1) // 2, color=text_color, spacing=25)
            
            img_p = os.path.join(_OUTPUT_DIR, f"f_hook_{i}.png")
            img.save(img_p)
        elif tag == "cta":
            f_q = _font(82, theme["font_title"])
            lines_q = _wrap(draw, _clean_text(text), f_q, max_w=820)
            _, lh_q = _sz(draw, "Ag", f_q)
            total_h_q = len(lines_q) * lh_q + (len(lines_q) - 1) * 25
            
            # Quote/CTA Plate (Glass) - Dynamic Height
            p_cy = 650
            bx0, by0, bx1, by1 = 100, p_cy - total_h_q//2 - 50, _W - 100, p_cy + total_h_q//2 + 50
            _draw_rounded_rect(overlay_draw, [bx0, by0, bx1, by1], 60, fill=theme["glass"])
            
            # Action Button Plate
            btn_bx0, btn_by0, btn_bx1, btn_by1 = 120, _H - 550, _W - 120, _H - 270
            _draw_rounded_rect(overlay_draw, [btn_bx0, btn_by0, btn_bx1, btn_by1], 60, fill=theme["accent"])
            
            img.paste(overlay_img, (0, 0), overlay_img)
            draw = ImageDraw.Draw(img)
            _multiline(draw, lines_q, f_q, center_y=(by0 + by1) // 2, color=text_color, spacing=25)
            
            f_btn = _font(55, theme["font_body"])
            _center(draw, "Like & Sla Op", f_btn, cy=btn_by0 + 85, color=(255, 255, 255))
            _center(draw, f"Volg {theme['brand_name']}", f_btn, cy=btn_by0 + 185, color=(255, 255, 255))
            
            f_link = _font(44, theme["font_body"])
            _center(draw, "Bekijk de link in bio", f_link, cy=_H - 160, color=theme["accent"])
            
            img_p = os.path.join(_OUTPUT_DIR, f"f_cta_{i}.png")
            img.save(img_p)
        else:
            f = _font(72, theme["font_body"])
            lines = _wrap(draw, _clean_text(text), f, max_w=850)
            _, lh = _sz(draw, "Ag", f)
            total_h = len(lines) * lh + (len(lines) - 1) * 25
            
            # Main Content Plate (Glass) - Dynamic Height
            bx0, by0, bx1, by1 = 80, _H//2 - total_h//2 - 60, _W - 80, _H//2 + total_h//2 + 60
            _draw_rounded_rect(overlay_draw, [bx0, by0, bx1, by1], 60, fill=theme["glass"])
            
            # Accent bar on glass
            overlay_draw.rectangle([bx0, by0 + 40, bx0 + 15, by1 - 40], fill=theme["accent"])
            
            img.paste(overlay_img, (0, 0), overlay_img)
            draw = ImageDraw.Draw(img)
            _multiline(draw, lines, f, center_y=_H // 2, color=text_color, spacing=25)
            
            img_p = os.path.join(_OUTPUT_DIR, f"f_content_{i}.png")
            img.save(img_p)

        c_p = make_clip(img_p, dur, f"v_frag_{i}.mp4")
        all_video_clips.append(c_p)
        all_audio_files.append(a_path)

    v_list = os.path.join(_OUTPUT_DIR, "v_list.txt")
    with open(v_list, "w", encoding="utf-8") as f:
        for i in range(len(all_video_clips)):
            f.write(f"file 'v_frag_{i}.mp4'\n")

    a_list = os.path.join(_OUTPUT_DIR, "a_list.txt")
    with open(a_list, "w", encoding="utf-8") as f:
        for i, a_p in enumerate(all_audio_files):
            local_a = os.path.join(_OUTPUT_DIR, f"tmp_a_{i}.mp3")
            import shutil
            shutil.copy2(a_p, local_a)
            f.write(f"file 'tmp_a_{i}.mp3'\n")

    final_audio = os.path.join(_OUTPUT_DIR, "audio_full.mp3")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", a_list, "-c", "copy", final_audio],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Mixed Final Assembly (Voice + Background Music with Ducking)
    bg_music = os.path.join("audio_assets", "wellness_bg.mp3")
    if os.path.exists(bg_music):
        print("[video_skill] Mixing background music with ducking...")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", v_list,
            "-i", final_audio, "-i", bg_music,
            "-filter_complex", 
            "[2:a]volume=0.15[bg];" # Constant music volume 15%
            "[1:a]volume=1.0[voice];" # Voice at 100%
            "[bg][voice]amix=inputs=2:duration=first[outa]", # Mix them
            "-map", "0:v", "-map", "[outa]", "-c:v", "copy", "-c:a", "aac", "-shortest", output_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", v_list,
            "-i", final_audio, "-c:v", "copy", "-c:a", "aac", "-shortest", output_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return output_path

if __name__ == "__main__":
    p = create_reel()
    print("Video:", p)
