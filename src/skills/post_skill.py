import os
import json
from PIL import Image, ImageDraw, ImageFont
from src.skills.ai_client import generate_image

# Bu beceri, Instagram icin markali statik icerikler (Post & Story) uretir.

def _draw_rounded_rect(draw, coords, radius, fill):
    x0, y0, x1, y1 = coords
    draw.ellipse([x0, y0, x0 + radius * 2, y0 + radius * 2], fill=fill)
    draw.ellipse([x1 - radius * 2, y0, x1, y0 + radius * 2], fill=fill)
    draw.ellipse([x1 - radius * 2, y1 - radius * 2, x1, y1], fill=fill)
    draw.ellipse([x0, y1 - radius * 2, x0 + radius * 2, y1], fill=fill)
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)

def _add_link_sticker(image_path, brand="glow"):
    """Gorsele 'Link in Bio' sticker'i ekler."""
    try:
        img = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        # Marka Renkleri
        accent = (255, 112, 86, 230) if brand == "glow" else (130, 150, 120, 230)
        
        # Buton Boyutlari ve Konumu (Daha Belirgin)
        bw, bh = 600, 140
        bx0, by0 = (w - bw) // 2, h - 550
        bx1, by1 = bx0 + bw, by0 + bh
        
        # Sticker Cizimi (Modern Yuvarlak)
        _draw_rounded_rect(draw, [bx0, by0, bx1, by1], 70, fill=accent)
        
        # Profesyonel Font Yukleme (Montserrat)
        try:
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            font_path = os.path.join(base, "Montserrat-Medium.ttf")
            if not os.path.exists(font_path):
                 font = ImageFont.load_default()
            else:
                 font = ImageFont.truetype(font_path, 60)
            
            text = "LINK IN BIO"
            # Text bbox matching for centering
            bb = draw.textbbox((0, 0), text, font=font)
            tw = bb[2] - bb[0]
            th = bb[3] - bb[1]
            draw.text(((bx0 + bx1 - tw) // 2, by0 + (bh - th) // 2 - 10), text, fill="white", font=font)
        except Exception as e:
             print(f"Font error: {e}")
             draw.text((bx0 + 80, by0 + 40), "LINK IN BIO", fill="white")

        # Save back
        img = img.convert("RGB")
        img.save(image_path)
        print(f"✨ 'Link in Bio' sticker added to {image_path}")
        return image_path
    except Exception as e:
        print(f"⚠️ Sticker error: {e}")
        return image_path

def create_static_post(brand="glow", topic="wellness", prompt_override=None):
    """Kare (1:1) formatta statik gorsel post uretir."""
    print(f"🎨 Creating static post for @{brand.capitalize()}NL | Topic: {topic}")
    brand_style = "Energetic, coral tones" if brand == "glow" else "Calm, sage tones"
    final_prompt = prompt_override or f"A high-end, aesthetic square 1:1 Instagram post for @{brand.capitalize()}NL. {topic}. {brand_style}."
    try:
        path = generate_image(final_prompt + " (Ensure Square 1:1 format)")
        if path: return path
    except Exception as e: print(f"❌ Post error: {e}")
    return None

def create_static_story(brand="glow", topic="wellness", prompt_override=None):
    """Dikey (9:16) formatta statik story gorseli uretir + Markali Sticker."""
    print(f"📱 Creating branded story for @{brand.capitalize()}NL | Topic: {topic}")
    brand_style = "Energetic vibe" if brand == "glow" else "Zen atmosphere"
    final_prompt = prompt_override or f"A high-end 9:16 Instagram Story for @{brand.capitalize()}NL. {topic}. {brand_style}."
    try:
        image_path = generate_image(final_prompt + " (Ensure Vertical 9:16 aspect ratio)")
        if image_path:
            # OTOMATIK STICKER EKLE
            fixed_path = _add_link_sticker(image_path, brand=brand)
            return fixed_path
    except Exception as e:
        print(f"❌ Story error: {e}")
    return None
