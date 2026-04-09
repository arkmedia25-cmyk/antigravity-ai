import os
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
    "title":   "Montserrat-Bold.ttf",
    "body":    "Montserrat-Regular.ttf",
    "medium":  "Montserrat-Medium.ttf",
    "display": "PlayfairDisplay-Bold.ttf",
}

def _get_project_root():
    return os.getcwd()

def _ensure_fonts():
    root = _get_project_root()
    font_dir = os.path.join(root, "assets", "fonts")
    os.makedirs(font_dir, exist_ok=True)

    urls = {
        "title":   "https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Bold.ttf",
        "body":    "https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Regular.ttf",
        "medium":  "https://fonts.gstatic.com/s/montserrat/v31/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCtZ6Ew-.ttf",
        "display": "https://fonts.gstatic.com/s/playfairdisplay/v40/nuFvD-vYSZviVYUb_rj3ij__anPXJzDwcbmjWBN2PKeiukDQ.ttf",
    }

    for name, filename in _FONTS.items():
        full_path = os.path.join(font_dir, filename)
        if not os.path.exists(full_path):
            print(f"[video_skill] Downloading font: {filename}...")
            try:
                urllib.request.urlretrieve(urls[name], full_path)
            except Exception as e:
                print(f"[video_skill] Font download failed: {e}")

_ensure_fonts()

def _font(size: int, font_type: str = "body") -> ImageFont.FreeTypeFont:
    root = _get_project_root()
    filename = _FONTS.get(font_type, "Montserrat-Regular.ttf")
    path = os.path.join(root, "assets", "fonts", filename)
    try:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    except: pass
    # Fallback to bold if display not found
    if font_type == "display":
        return _font(size, "title")
    try:
        import platform
        if platform.system() == "Windows":
            return ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()

def _add_vignette(img: Image.Image) -> Image.Image:
    """Radyal vignette efekti — kenarları karartır, merkezi aydınlatır."""
    w, h = img.size
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(vignette)
    # Kenarlardan merkeze doğru gradyan halkalar çiz
    steps = 40
    for s in range(steps):
        alpha = int(180 * (s / steps) ** 2)
        margin = int(s * min(w, h) / (2 * steps))
        draw.rectangle([margin, margin, w - margin, h - margin],
                       outline=(0, 0, 0, alpha), width=int(min(w, h) / steps) + 1)
    vignette = vignette.filter(ImageFilter.GaussianBlur(30))
    result = img.convert("RGBA")
    result = Image.alpha_composite(result, vignette)
    return result.convert("RGB")

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

    display_brand = "GlowUpNL" if brand in ("glow", "glowup") else "HolistiGlow"
    accent_rgb = tuple(theme["accent"]) if isinstance(theme["accent"], (list, tuple)) else (255, 112, 86)
    total_frags = len([f for f in fragments if f.get("audio") or f.get("path")])

    for i, frag in enumerate(fragments):
        a_path = frag.get("audio") or frag.get("path")
        if not a_path: continue

        a_path = os.path.abspath(a_path)
        dur = get_duration(a_path)
        tag = frag.get("tag", "content")
        text = frag.get("sentence") or frag.get("text", "")

        # ── Background ──────────────────────────────────────────────────────
        color1 = tuple(theme["bg"]) if isinstance(theme["bg"], (list, tuple)) else (254, 245, 238)
        color2 = tuple(theme["accent"]) if isinstance(theme["accent"], (list, tuple)) else (255, 112, 86)
        img = _create_gradient_bg(_W, _H, color1, color2)

        if image_path and os.path.exists(image_path):
            try:
                bg_pic = Image.open(image_path).convert("RGBA")
                bg_w, bg_h = bg_pic.size
                ratio = max(_W / bg_w, _H / bg_h)
                new_w, new_h = int(bg_w * ratio), int(bg_h * ratio)
                bg_pic = bg_pic.resize((new_w, new_h), Image.Resampling.LANCZOS)
                left = (new_w - _W) // 2
                top = (new_h - _H) // 2
                bg_pic = bg_pic.crop((left, top, left + _W, top + _H))
                dark_layer = Image.new("RGBA", (_W, _H), (0, 0, 0, 130))
                bg_pic = Image.alpha_composite(bg_pic, dark_layer)
                img.paste(bg_pic, (0, 0), bg_pic)
            except Exception as e:
                print(f"[video_skill] Gorsel eklenemedi: {e}")

        # Vignette efekti
        img = _add_vignette(img)

        # ── Overlays layer ──────────────────────────────────────────────────
        overlay_img = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay_img)
        padding = 65

        # ── TOP BRAND BAR ────────────────────────────────────────────────────
        bar_h = 110
        bar_color = accent_rgb + (200,)
        overlay_draw.rectangle([0, 0, _W, bar_h], fill=bar_color)
        img.paste(overlay_img, (0, 0), overlay_img)

        draw = ImageDraw.Draw(img)
        f_brand = _font(44, "title")
        brand_label = f"@{display_brand}"
        bw, _ = _sz(draw, brand_label, f_brand)
        draw.text(((_W - bw) // 2 + 2, 32 + 2), brand_label, font=f_brand, fill=(0, 0, 0, 80))
        draw.text(((_W - bw) // 2, 32), brand_label, font=f_brand, fill=(255, 255, 255))

        # ── BOTTOM PROGRESS BAR ──────────────────────────────────────────────
        prog_h = 10
        prog_y = _H - prog_h
        draw.rectangle([0, prog_y, _W, _H], fill=(0, 0, 0, 90))
        filled_w = int(_W * (i + 1) / max(total_frags, 1))
        draw.rectangle([0, prog_y, filled_w, _H], fill=accent_rgb + (220,))

        # Reset overlay for glass boxes
        overlay_img2 = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
        overlay_draw2 = ImageDraw.Draw(overlay_img2)

        # ── CONTENT RENDERING ────────────────────────────────────────────────
        if tag == "hook":
            lines, f, total_h = _fit_lines(draw, text, "display", 820, 900)
            bx0, bx1 = 60, _W - 60
            by0 = bar_h + 80
            by1 = by0 + total_h + padding * 2
            glass = (255, 255, 255, 210) if not image_path else (0, 0, 0, 150)
            _draw_rounded_rect(overlay_draw2, [bx0, by0, bx1, by1], 50, glass)
            img.paste(overlay_img2, (0, 0), overlay_img2)
            draw = ImageDraw.Draw(img)
            tc = tuple(theme["text"]) if not image_path else (255, 255, 255)
            y = by0 + padding
            for line in lines:
                lw, lh = _sz(draw, line, f)
                draw.text(((_W - lw) // 2 + 3, y + 3), line, font=f, fill=(0, 0, 0, 120))
                draw.text(((_W - lw) // 2, y), line, font=f, fill=tc)
                y += lh + 22

        elif tag == "cta":
            # Full-width CTA block (Instagram stili)
            cta_main = "Volg voor meer tips!"
            cta_sub = f"@{display_brand}"
            cy_center = _H // 2

            # Background block
            block_y0, block_y1 = cy_center - 320, cy_center + 320
            _draw_rounded_rect(overlay_draw2, [60, block_y0, _W - 60, block_y1], 50, (255, 255, 255, 220))
            img.paste(overlay_img2, (0, 0), overlay_img2)
            draw = ImageDraw.Draw(img)

            # Main CTA text
            f_cta = _font(80, "display")
            lines_cta = _wrap(draw, cta_main, f_cta, 820)
            y = block_y0 + 80
            for line in lines_cta:
                lw, lh = _sz(draw, line, f_cta)
                draw.text(((_W - lw) // 2 + 3, y + 3), line, font=f_cta, fill=(0, 0, 0, 80))
                draw.text(((_W - lw) // 2, y), line, font=f_cta, fill=tuple(theme["text"]))
                y += lh + 18

            # Follow button
            btn_y0, btn_y1 = y + 40, y + 160
            _draw_rounded_rect(draw, [120, btn_y0, _W - 120, btn_y1], 40, accent_rgb)
            f_btn = _font(62, "title")
            btw, _ = _sz(draw, cta_sub, f_btn)
            draw.text(((_W - btw) // 2, btn_y0 + 46), cta_sub, font=f_btn, fill=(255, 255, 255))

        else:
            # CONTENT frame
            lines, f, total_h = _fit_lines(draw, text, "body", 820, 1000)
            bx0, bx1 = 60, _W - 60
            by0 = bar_h + 120
            by1 = by0 + total_h + padding * 2
            glass = (255, 255, 255, 205) if not image_path else (0, 0, 0, 145)
            _draw_rounded_rect(overlay_draw2, [bx0, by0, bx1, by1], 50, glass)
            img.paste(overlay_img2, (0, 0), overlay_img2)
            draw = ImageDraw.Draw(img)
            tc = tuple(theme["text"]) if not image_path else (255, 255, 255)
            y = by0 + padding
            for line in lines:
                lw, lh = _sz(draw, line, f)
                draw.text(((_W - lw) // 2 + 3, y + 3), line, font=f, fill=(0, 0, 0, 90))
                draw.text(((_W - lw) // 2, y), line, font=f, fill=tc)
                y += lh + 22

        img_p = os.path.abspath(os.path.join(_OUTPUT_DIR, f"f_{session_id}_{i}.png"))
        img.save(img_p)

        clip_p = os.path.abspath(os.path.join(_OUTPUT_DIR, f"v_{session_id}_{i}.mp4"))
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-t", f"{dur:.2f}", "-i", img_p,
            "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-preset", "superfast", "-vsync", "cfr", clip_p
        ], capture_output=True)

        all_video_clips.append(clip_p)
        all_audio_files.append(a_path)

    # ── Concatenate & Mix ────────────────────────────────────────────────────

    def write_list(p, files):
        with open(p, "w", encoding="utf-8") as f:
            for file in files:
                # Normaliseer paden en ontsnap enkelvoudige aanhalingstekens voor FFmpeg concat
                safe_p = file.replace(os.sep, '/').replace("'", "'\\''")
                f.write(f"file '{safe_p}'\n")

    v_list = os.path.abspath(os.path.join(_OUTPUT_DIR, f"v_list_{session_id}.txt"))
    a_list = os.path.abspath(os.path.join(_OUTPUT_DIR, f"a_list_{session_id}.txt"))
    write_list(v_list, all_video_clips)
    write_list(a_list, all_audio_files)

    final_vo = os.path.abspath(os.path.join(_OUTPUT_DIR, f"vo_{session_id}.mp3"))
    print(f"[video_skill] Concatenating voiceover...")
    
    vo_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", a_list.replace(os.sep, '/'),
        "-af", "aresample=async=1", "-ar", "44100",
        "-c:a", "libmp3lame", "-b:a", "192k", final_vo
    ]
    res_vo = subprocess.run(vo_cmd, capture_output=True, text=True)
    if res_vo.returncode != 0:
        print(f"[video_skill] Voiceover Concat Error (Code {res_vo.returncode})")
        # Bekende fallback: Gebruik het eerste audiobestand als concat faalt
        final_vo = all_audio_files[0] if all_audio_files else final_vo

    # Check for optional background music file
    music_path = os.path.join(_get_project_root(), "assets", "music", "background.mp3")
    brand_music = os.path.join(_get_project_root(), "assets", "music", f"background_{brand}.mp3")
    if os.path.exists(brand_music):
        music_path = brand_music

    print(f"[video_skill] Assembling final reel: {output_path}")
    if os.path.exists(music_path):
        # Mix voiceover (full volume) + background music (15%)
        print(f"[video_skill] Mixing with background music: {music_path}")
        final_audio = os.path.abspath(os.path.join(_OUTPUT_DIR, f"audio_{session_id}.mp3"))
        mix_res = subprocess.run([
            "ffmpeg", "-y",
            "-i", final_vo, "-i", music_path,
            "-filter_complex", "[0:a]volume=1.4[vo];[1:a]volume=0.15,aloop=loop=-1:size=2e+09[bg];[vo][bg]amix=inputs=2:duration=first[aout]",
            "-map", "[aout]", "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "192k", final_audio
        ], capture_output=True)
        if mix_res.returncode != 0:
            print(f"[video_skill] Music Mix Error: {mix_res.stderr[-500:]}")
    else:
        final_audio = final_vo

    final_res = subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", v_list.replace(os.sep, '/'),
        "-i", final_audio,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-af", "aresample=async=1", "-shortest",
        os.path.abspath(output_path)
    ], capture_output=True)
    if final_res.returncode != 0:
        print(f"[video_skill] Final Assembly Error: {final_res.stderr[-500:]}")

    return output_path

    return output_path
