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
        "glass":      (255, 255, 255, 190),
        "brand_name": "@GlowUpNL",
    },
    "holisti": {
        "accent":     (130, 150, 120),
        "text":       (40, 44, 45),
        "glass":      (255, 255, 255, 190),
        "brand_name": "@HolistiGlow",
    }
}

# ── Font helpers ──────────────────────────────────────────────────────────────
def _font(size: int):
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base, "Montserrat-Medium.ttf")
    try:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    except: pass
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
    return lines

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
        # Cleaning and wrapping text
        clean_text = re.sub(r'[^\x00-\x7F\xC0-\xFF\.,!?\'\":\* ]+', '', text).strip()
        
        f_size = 55 if is_story else 45
        font = _font(f_size)
        max_w = W - 200
        lines = _wrap(draw_ov, clean_text, font, max_w)
        
        # Calculate plate height
        _, lh = _sz(draw_ov, "Ag", font)
        spacing = 20
        total_text_h = len(lines) * lh + (len(lines) - 1) * spacing
        
        # Plate positioning
        pad = 60
        bx0, bx1 = 100, W - 100
        by0 = (H // 2) - (total_text_h // 2) - pad
        by1 = by0 + total_text_h + (pad * 2)
        
        # Draw Glass Plate
        _draw_rounded_rect(draw_ov, [bx0, by0, bx1, by1], 50, fill=theme["glass"])
        # Accent side-bar
        draw_ov.rectangle([bx0, by0 + 30, bx0 + 12, by1 - 30], fill=theme["accent"])
        
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
            # Sticker button
            sw, sh = 550, 110
            sx0, sy0 = (W - sw) // 2, H - 450
            sx1, sy1 = sx0 + sw, sy0 + sh
            _draw_rounded_rect(draw_final, [sx0, sy0, sx1, sy1], 55, fill=theme["accent"])
            
            s_text = "LINK IN BIO"
            s_font = _font(50)
            stw, sth = _sz(draw_final, s_text, s_font)
            draw_final.text(((W - stw) // 2, sy0 + (sh - sth) // 2 - 5), s_text, font=s_font, fill="white")

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
