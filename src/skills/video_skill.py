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
    "title": "Montserrat-Bold.ttf",
    "body":  "Montserrat-Regular.ttf",
}

def _get_project_root():
    # Proje ana dizinini bulur
    return os.getcwd()

def _ensure_fonts():
    root = _get_project_root()
    font_dir = os.path.join(root, "assets", "fonts")
    if not os.path.exists(font_dir):
        os.makedirs(font_dir)
    
    # Montserrat Font URL'leri (GitHub üzerinden ham dosyalar)
    urls = {
        "title": "https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Bold.ttf",
        "body":  "https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Regular.ttf"
    }
    
    for name, filename in _FONTS.items():
        full_path = os.path.join(font_dir, filename)
        if not os.path.exists(full_path):
            print(f"[video_skill] İndiriliyor: {filename}...")
            try:
                import urllib.request
                urllib.request.urlretrieve(urls[name], full_path)
            except Exception as e:
                print(f"[video_skill] Font indirilemedi: {e}")

_ensure_fonts()

def _font(size: int, font_type: str = "body") -> ImageFont.FreeTypeFont:
    root = _get_project_root()
    filename = _FONTS.get(font_type, "Montserrat-Regular.ttf")
    path = os.path.join(root, "assets", "fonts", filename)
    try:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    except: pass
    
    # Standart Sistem Fallback (Windows & Linux)
    try:
        import platform
        if platform.system() == "Windows":
            return ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", size)
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
    # 1. Tag'leri temizle
    text = re.sub(r'\[HOOK\]|\[CONTENT\]|\[CTA\]|\[TITLE\]', '', text, flags=re.IGNORECASE)
    # 2. Madde işaretlerini ve numaraları temizle
    text = re.sub(r'^\s*[•🌿✨\-1234567890\.\*\/]+\s*', '', text)
    # 3. KESİN ÇÖZÜM: Emojileri ve garip kutu karakterlerini (non-latin/non-printable) tamamen sil
    # Sadece standart Latin harfleri, sayılar ve noktalama işaretlerine izin ver
    clean = re.sub(r'[^\x20-\x7E\xC1-\xFF\.,!?\'\":\* ]+', '', text)
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
    # "Baştan sona aynı punto olsun" ve "taşmasın" kuralı.
    sizes = [90, 80, 70, 60, 50, 40]
    total_h = 0
    for sz in sizes:
        f = _font(sz, font_type)
        lines = _wrap(draw, text, f, max_w)
        _, lh = _sz(draw, "Ag", f)
        total_h = len(lines) * lh + (len(lines) - 1) * 20
        # Hem genişlik (wrap sayesinde garanti) hem yükseklik kontrolü
        if total_h <= max_h: return lines, f, total_h
    
    final_f = _font(sizes[-1], font_type)
    return _wrap(draw, text, final_f, max_w), final_f, total_h

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
        
        # Pexels (veya harici) bir stock görsel geldiyse arka plana harmanla
        if image_path and os.path.exists(image_path):
            try:
                bg_pic = Image.open(image_path).convert("RGBA")
                # Resize and crop to fill screen using aspect ratio
                bg_w, bg_h = bg_pic.size
                ratio = max(_W / bg_w, _H / bg_h)
                new_w, new_h = int(bg_w * ratio), int(bg_h * ratio)
                bg_pic = bg_pic.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                # Crop center
                left = (new_w - _W) // 2
                top = (new_h - _H) // 2
                bg_pic = bg_pic.crop((left, top, left + _W, top + _H))
                
                # Siyah opak bir filtre ile karartma (yazılar okunsun diye)
                dark_layer = Image.new("RGBA", (_W, _H), (0, 0, 0, 110))
                bg_pic = Image.alpha_composite(bg_pic, dark_layer)
                
                # Gradyanla alttan blend etme
                img.paste(bg_pic, (0, 0), bg_pic)
            except Exception as e:
                print(f"[video_skill] Gorsel eklenemedi: {e}")
        
        overlay_img = Image.new("RGBA", (_W, _H), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay_img)
        draw = ImageDraw.Draw(img)
        text_color = theme["text"]
        
        # Render visual according to tag (hook/content/cta)
        padding = 70 # Safe Zone Padding inside the glass box
        
        if tag == "hook":
            # 1. Text fitting inside a stricter max_w (box_w - 2*padding)
            lines, f, total_h = _fit_lines(draw, text, theme["font_title"], 780, 1000)
            
            # 2. Dynamic Box Sizing
            bx0, bx1 = 80, _W - 80
            by0 = 220
            by1 = by0 + total_h + (padding * 2)
            
            _draw_rounded_rect(overlay_draw, [bx0, by0, bx1, by1], 60, theme["glass"])
            img.paste(overlay_img, (0, 0), overlay_img)
            draw = ImageDraw.Draw(img)
            
            y = by0 + padding
            for line in lines:
                lw, _ = _sz(draw, line, f)
                draw.text(((_W - lw) // 2 + 5, y + 5), line, font=f, fill=(0,0,0, 100))
                draw.text(((_W - lw) // 2, y), line, font=f, fill=text_color)
                y += (_sz(draw, "Ag", f)[1] + 25)
                
        elif tag == "cta":
            # CTA Ekranı - "Volg voor meer!"
            cta_text = "Volg voor meer!"
            lines, f, total_h = _fit_lines(draw, cta_text, theme["font_title"], 780, 400)
            
            bx0, bx1 = 80, _W - 80
            by0, by1 = (_H // 2) - 250, (_H // 2) + 250
            
            _draw_rounded_rect(overlay_draw, [bx0, by0, bx1, by1], 60, theme["glass"])
            img.paste(overlay_img, (0, 0), overlay_img)
            draw = ImageDraw.Draw(img)
            
            y = by0 + padding
            for line in lines:
                lw, _ = _sz(draw, line, f)
                draw.text(((_W - lw) // 2 + 5, y + 5), line, font=f, fill=(0,0,0, 100))
                draw.text(((_W - lw) // 2, y), line, font=f, fill=text_color)
                y += (_sz(draw, "Ag", f)[1] + 25)
            
            # Button inside CTA
            _draw_rounded_rect(draw, [bx0 + 100, y + 30, bx1 - 100, y + 150], 40, theme["accent"])
            display_brand = "GlowUpNL" if brand == "glow" else "HolistiGlow"
            btn_text = f"@{display_brand}"
            btw, _ = _sz(draw, btn_text, _font(60, "body"))
            draw.text(((_W - btw) // 2, y + 85), btn_text, font=_font(60, "body"), fill=(255,255,255))
            
        else:
            # CONTENT
            lines, f, total_h = _fit_lines(draw, text, theme["font_body"], 780, 1050)
            
            bx0, bx1 = 80, _W - 80
            by0 = 180
            by1 = by0 + total_h + (padding * 2)
            
            _draw_rounded_rect(overlay_draw, [bx0, by0, bx1, by1], 60, theme["glass"])
            img.paste(overlay_img, (0, 0), overlay_img)
            draw = ImageDraw.Draw(img)
            
            y = by0 + padding
            for line in lines:
                lw, _ = _sz(draw, line, f)
                # Profesyonel Soft Shadow (Opaklık 100 -> 45, Mesafe 5 -> 3)
                draw.text(((_W - lw) // 2 + 3, y + 3), line, font=f, fill=(0, 0, 0, 45))
                # Main text
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
