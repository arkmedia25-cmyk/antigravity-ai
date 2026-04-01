import os
import json
import re
import urllib.request
from PIL import Image, ImageDraw, ImageFont
from src.skills.ai_client import generate_image

# ── Brand Themes ──────────────────────────────────────────────────────────────
THEMES = {
    "glow": {
        "accent":     (255, 112, 86),
        "text":       (62, 44, 40),
        "glass":      (255, 255, 255, 205), # Slightly more opaque glass for readability
        "brand_name": "@GlowUpNL",
    },
    "holisti": {
        "accent":     (130, 150, 120),
        "text":       (40, 44, 45),
        "glass":      (255, 255, 255, 205),
        "brand_name": "@HolistiGlow",
    }
}

# ── Font management ───────────────────────────────────────────────────────────
_FONTS = {
    "body":  "Montserrat-Medium.ttf",
    "fallback": "Roboto-Bold.ttf",
}
_FONT_URLS = {
    "body":  "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Medium.ttf",
}

def _ensure_fonts():
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for name, filename in _FONT_URLS.items():
        full_path = os.path.join(base, _FONTS[name])
        if not os.path.exists(full_path):
            try:
                print(f"[post_skill] Downloading {name} font...")
                urllib.request.urlretrieve(_FONT_URLS[name], full_path)
            except Exception as e:
                print(f"[post_skill] Warning: Could not download {name}: {e}")

_ensure_fonts()

def _font(size: int):
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Try Montserrat
    path1 = os.path.join(base, "Montserrat-Medium.ttf")
    # Try Roboto
    path2 = os.path.join(base, "Roboto-Bold.ttf")
    # Try Windows System
    path3 = "C:/Windows/Fonts/arial.ttf"
    
    for p in [path1, path2, path3]:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except: pass
    
    # Final desperate fallback for Windows
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

def _sz(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]

def _wrap(draw, text, font, max_w):
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

def _draw_rounded_rect(draw, coords, radius, fill):
    x0, y0, x1, y1 = coords
    draw.ellipse([x0, y0, x0 + radius * 2, y0 + radius * 2], fill=fill)
    draw.ellipse([x1 - radius * 2, y0, x1, y0 + radius * 2], fill=fill)
    draw.ellipse([x1 - radius * 2, y1 - radius * 2, x1, y1], fill=fill)
    draw.ellipse([x0, y1 - radius * 2, x0 + radius * 2, y1], fill=fill)
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)

# ── Core Visual Engine ────────────────────────────────────────────────────────

def _apply_narrator_plate(image_path, text, brand="glow", is_story=False):
    """Adds a premium glassmorphic plate with the description text."""
    try:
        img = Image.open(image_path).convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0,0,0,0))
        draw_ov = ImageDraw.Draw(overlay)
        theme = THEMES.get(brand, THEMES["glow"])
        
        W, H = img.size
        # Cleaning text
        clean_text = re.sub(r'[^\x00-\x7F\xC0-\xFF\.,!?\'\":\* ]+', '', text).strip()
        
        # HUGE fonts for visibility
        f_size = 90 if is_story else 80
        font = _font(f_size)
        max_w = W - 300
        lines = _wrap(draw_ov, clean_text, font, max_w)
        
        # Calculate plate height
        _, lh = _sz(draw_ov, "Ag", font)
        spacing = 40
        total_text_h = len(lines) * lh + (len(lines) - 1) * spacing
        
        # Plate positioning
        pad = 100
        bx0, bx1 = 80, W - 80
        by0 = (H // 2) - (total_text_h // 2) - pad
        by1 = by0 + total_text_h + (pad * 2)
        
        # Draw Glass Plate
        _draw_rounded_rect(draw_ov, [bx0, by0, bx1, by1], 60, fill=theme["glass"])
        # Accent side-bar
        draw_ov.rectangle([bx0, by0 + 40, bx0 + 20, by1 - 40], fill=theme["accent"])
        
        img.paste(overlay, (0, 0), overlay)
        draw_final = ImageDraw.Draw(img)
        
        # Draw Text
        y = by0 + pad
        for line in lines:
            lw, _ = _sz(draw_final, line, font)
            draw_final.text(((W - lw) // 2, y), line, font=font, fill=theme["text"])
            y += lh + spacing

        # --- If Story, add the Link in Bio Sticker ---
        if is_story:
            # Huge Sticker button
            sw, sh = 700, 180
            sx0, sy0 = (W - sw) // 2, H - 450
            sx1, sy1 = sx0 + sw, sy0 + sh
            _draw_rounded_rect(draw_final, [sx0, sy0, sx1, sy1], 90, fill=theme["accent"])
            
            s_text = "LINK IN BIO"
            s_font = _font(72)
            stw, sth = _sz(draw_final, s_text, s_font)
            draw_final.text(((W - stw) // 2, sy0 + (sh - sth) // 2 - 10), s_text, font=s_font, fill="white")

        img = img.convert("RGB")
        img.save(image_path)
        return image_path
    except Exception as e:
        print(f"⚠️ Narrator Error: {e}")
        return image_path

def create_static_post(brand="glow", topic="wellness", description=""):
    """Kare (1:1) formatta metinli post uretir."""
    print(f"🎨 Creating Narrator Post for @{brand.capitalize()}NL...")
    prompt = f"Professional wellness photography, {topic}, clean aesthetic, cinematic lighting."
    try:
        path = generate_image(prompt + " (Square 1:1)")
        if path:
            return _apply_narrator_plate(path, description or topic, brand=brand, is_story=False)
    except Exception as e: print(f"❌ Post error: {e}")
    return None

def create_static_story(brand="glow", topic="wellness", description=""):
    """Dikey (9:16) formatta metinli story uretir."""
    print(f"📱 Creating Narrator Story for @{brand.capitalize()}NL...")
    prompt = f"Professional lifestyle wellness photography, {topic}, high-end aesthetic."
    try:
        path = generate_image(prompt + " (Vertical 9:16)")
        if path:
            return _apply_narrator_plate(path, description or topic, brand=brand, is_story=True)
    except Exception as e: print(f"❌ Story error: {e}")
    return None
