import os
import json
import subprocess
import urllib.request
import time
import uuid
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.core.brand_manager import BrandManager

_OUTPUT_DIR = "outputs"
_W, _H = 1080, 1920
_CX = _W // 2

brand_manager = BrandManager()

import os, urllib.request
from PIL import ImageFont

_FONTS = {
    "title": "PlayfairDisplay-Bold.ttf",
    "body":  "Montserrat-Medium.ttf",
}
_FONT_URLS = {
    "title": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay-Bold.ttf",
    "body":  "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Medium.ttf",
}

def _get_project_root():
    # Garantili olarak ana proje kök dizinini (Antigravity/) bulur
    current = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(current))

def _ensure_fonts():
    root = _get_project_root()
    for name, filename in _FONTS.items():
        full_path = os.path.join(root, filename)
        if not os.path.exists(full_path):
            print(f"Downloading font {filename} to {full_path}")
            try:
                urllib.request.urlretrieve(_FONT_URLS[name], full_path)
            except Exception as e:
                print(f"Font download failed: {e}")

_ensure_fonts()

def _font(size: int, font_type: str = "body") -> ImageFont.FreeTypeFont:
    root = _get_project_root()
    filename = _FONTS.get(font_type, "Montserrat-Medium.ttf")
    path = os.path.join(root, filename)
    try:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    except Exception as e: 
        print(f"Font load error: {e}")
    # Sistemde yüklü standart bir fonta fallback dene
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

# ── Drawing & Text Helpers ───────────────────────────────────────────────────

def _sz(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]

def _create_gradient_bg(width, height, color1, color2):
    """Estetik dikey renk geçişi (gradient) ve Aura arka plan oluşturur."""
    # Zemini açık renkle başlat
    base = Image.new('RGB', (width, height), color1)
    
    # Modern Aura / Gradient Mesh efekti için arka plan katmanı
    aura_layer = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(aura_layer)
    
    # GlowUp stili enerjik, organik, asimetrik renk lekeleri (Auralar)
    # 1. Sol üstte büyük leke
    c2_rgba = color2 + (180,) if len(color2) == 3 else color2
    draw.ellipse([-500, -500, 800, 800], fill=c2_rgba)
    # 2. Sağ altta detay lekesi
    draw.ellipse([width - 600, height - 600, width + 400, height + 400], fill=c2_rgba)
    # 3. Ortada çok hafif bir sıcaklık geçişi
    draw.ellipse([-200, height//2 - 400, width + 200, height//2 + 400], fill=color2 + (60,) if len(color2) == 3 else color2)

    # Kuvvetli bir bulanıklaştırma (Gaussian Blur) organik bir görünüm verir
    aura_blur = aura_layer.filter(ImageFilter.GaussianBlur(150))
    base.paste(aura_blur, (0,0), aura_blur)
    
    return base

def _wrap(draw, text: str, font, max_w: int) -> list:
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        w, _ = _sz(draw, test, font)
        if w <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = word
    if cur: lines.append(cur)
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
    text = re.sub(r'\[HOOK\]|\[CONTENT\]|\[CTA\]|\[TITLE\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\s*[•🌿✨\-1234567890\.\*\/]+\s*', '', text)
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

def _fit_lines(draw, text: str, font_type: str, max_w: int, max_h: int) -> tuple:
    # Modern Reels stili için font boyutunu oldukça büyük alıyoruz
    sizes = [150, 130, 110, 90, 70] if font_type == "title" else [120, 100, 85, 70, 55]
    total_h = 0
    for sz in sizes:
        f = _font(sz, font_type)
        lines = _wrap(draw, text, f, max_w)
        _, lh = _sz(draw, "Ag", f)
        total_h = len(lines) * lh + (len(lines) - 1) * 25
        if total_h <= max_h: return lines, f, total_h
    return _wrap(draw, text, _font(sizes[-1], font_type), max_w), _font(sizes[-1], font_type), total_h

def _center(draw, text: str, font, cy: int, color):
    text = _clean_text(text)
    tw, _ = _sz(draw, text, font)
    _, lh = _sz(draw, "Ag", font)
    draw.text((_CX - tw // 2, cy - lh // 2), text, font=font, fill=color)

# ── Main video assembly (The Fixed Part) ────────────────────────────────────

def create_reel(fragments=None, image_path=None, output_filename=None, brand="glowup", watermark_icon=None):
    theme = brand_manager.get_theme_for_video(brand)
    if not theme:
        theme = {"bg": (254, 245, 238), "accent": (255, 112, 86), "text": (62, 44, 40), 
                 "glass": (255, 255, 255, 215), "font_title": "title", "font_body": "body", 
                 "brand_name": brand.capitalize(), "watermark": "✨"}

    session_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    
    if not output_filename:
        output_filename = f"reels_{brand}_{time.strftime('%Y%m%d_%H%M%S')}.mp4"
    output_path = os.path.join(_OUTPUT_DIR, output_filename)

    if not fragments: return ""

    def get_duration(p):
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", p]
            return float(subprocess.check_output(cmd, text=True).strip())
        except: return 3.0

    all_video_clips = []
    all_audio_files = []

    print(f"[video_skill] Rendering {len(fragments)} fragments for @{brand}...")

    for i, frag in enumerate(fragments):
        a_path = frag.get("audio") or frag.get("path")
        if not a_path: continue
        
        # FIX: Ensure absolute paths for audio
        a_path = os.path.abspath(a_path)
        dur = get_duration(a_path)
        tag = frag.get("tag", "content")
        text = frag.get("sentence") or frag.get("text", "")
        
        # Premium Gradient background using theme colors
        color1 = tuple(theme["bg"]) if isinstance(theme["bg"], (list, tuple)) else (254, 245, 238)
        color2 = tuple(theme["accent"]) if isinstance(theme["accent"], (list, tuple)) else (255, 112, 86)
        img = _create_gradient_bg(_W, _H, color1, color2)
        # (Image pasting logic here - simplified for space)
        
        overlay_img = Image.new("RGBA", (_W, _H), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay_img)
        draw = ImageDraw.Draw(img)
        text_color = theme["text"]
        
        # Render visual according to tag (hook/content/cta)
        if tag == "hook":
            lines, f, total_h = _fit_lines(draw, text, theme["font_title"], 850, 1000)
            bx0, by0, bx1, by1 = 80, 220, _W - 80, 220 + total_h + 220
            _draw_rounded_rect(overlay_draw, [bx0, by0, bx1, by1], 60, theme["glass"])
            img.paste(overlay_img, (0, 0), overlay_img)
            draw = ImageDraw.Draw(img)
            y = by0 + 110
            for line in lines:
                lw, _ = _sz(draw, line, f)
                # Drop shadow for premium pop effect
                draw.text(((_W - lw) // 2 + 5, y + 5), line, font=f, fill=(0,0,0, 100))
                # Main text
                draw.text(((_W - lw) // 2, y), line, font=f, fill=text_color)
                y += (_sz(draw, "Ag", f)[1] + 25)
        elif tag == "cta":
            # CTA Ekranı - "Volg voor meer!" (Hollandaca)
            cta_text = "Volg voor meer!"
            lines, f, total_h = _fit_lines(draw, cta_text, theme["font_title"], 850, 400)
            
            bx0, by0, bx1, by1 = 100, (_H // 2) - 200, _W - 100, (_H // 2) + 200
            _draw_rounded_rect(overlay_draw, [bx0, by0, bx1, by1], 60, theme["glass"])
            img.paste(overlay_img, (0, 0), overlay_img)
            draw = ImageDraw.Draw(img)
            
            y = by0 + 80
            for line in lines:
                lw, _ = _sz(draw, line, f)
                # Text shadow
                draw.text(((_W - lw) // 2 + 5, y + 5), line, font=f, fill=(0,0,0, 100))
                # Main Text
                draw.text(((_W - lw) // 2, y), line, font=f, fill=text_color)
                y += (_sz(draw, "Ag", f)[1] + 25)
            
            # Alt tarafa buton izlenimi
            _draw_rounded_rect(draw, [bx0 + 100, y + 50, bx1 - 100, y + 170], 40, theme["accent"])
            
            display_brand = "GlowUpNL" if brand == "glow" else "HolistiGlow"
            btn_text = f"@{display_brand}"
            btw, _ = _sz(draw, btn_text, _font(60, "body"))
            draw.text(((_W - btw) // 2, y + 85), btn_text, font=_font(60, "body"), fill=(255,255,255))
        else:
            lines, f, total_h = _fit_lines(draw, text, theme["font_body"], 850, 1050)
            bx0, by0, bx1, by1 = 80, (_H // 2) - (total_h // 2) - 100, _W - 80, (_H // 2) + (total_h // 2) + 100
            _draw_rounded_rect(overlay_draw, [bx0, by0, bx1, by1], 60, theme["glass"])
            img.paste(overlay_img, (0, 0), overlay_img)
            draw = ImageDraw.Draw(img)
            y = by0 + 100
            for line in lines:
                lw, _ = _sz(draw, line, f)
                draw.text(((_W - lw) // 2, y), line, font=f, fill=text_color)
                y += (_sz(draw, "Ag", f)[1] + 25)

        img_p = os.path.abspath(os.path.join(_OUTPUT_DIR, f"f_{session_id}_{i}.png"))
        img.save(img_p)
        
        clip_p = os.path.abspath(os.path.join(_OUTPUT_DIR, f"v_{session_id}_{i}.mp4"))
        subprocess.run(["ffmpeg", "-y", "-loop", "1", "-t", f"{dur:.2f}", "-i", img_p, "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast", clip_p], capture_output=True)
        
        all_video_clips.append(clip_p)
        all_audio_files.append(a_path)

    # ── THE ULTIMATE PATH FIX ────────────────────────────────────────────────
    
    def write_list(p, files):
        # Important: use forward slashes for FFmpeg on Windows list files
        with open(p, "w", encoding="utf-8") as f:
            for file in files:
                f.write(f"file '{file.replace(os.sep, '/')}'\n")

    v_list = os.path.abspath(os.path.join(_OUTPUT_DIR, f"v_list_{session_id}.txt"))
    a_list = os.path.abspath(os.path.join(_OUTPUT_DIR, f"a_list_{session_id}.txt"))
    
    write_list(v_list, all_video_clips)
    write_list(a_list, all_audio_files)

    final_audio = os.path.abspath(os.path.join(_OUTPUT_DIR, f"audio_{session_id}.mp3"))
    
    # Concat Audio (Check if list matches)
    print(f"[video_skill] Concatenating audio using list: {a_list}")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", a_list.replace(os.sep, '/'), "-c:a", "libmp3lame", final_audio], check=True)

    # Final Composite
    print(f"[video_skill] Assembling final reel: {output_path}")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", v_list.replace(os.sep, '/'), "-i", final_audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", os.path.abspath(output_path)], check=True)

    return output_path
