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
        
        # Buton Boyutlari ve Konumu (Orta-Alt)
        bw, bh = 450, 100
        bx0, by0 = (w - bw) // 2, h - 450
        bx1, by1 = bx0 + bw, by0 + bh
        
        # Sticker Cizimi (Modern Yuvarlak)
        _draw_rounded_rect(draw, [bx0, by0, bx1, by1], 40, fill=accent)
        
        # Yazi Ekleme (Basit Font Fallback)
        try:
            # Try to find a font or use default
            font = ImageFont.load_default()
            text = "LINK IN BIO"
            # Calculate text size manually for default font
            tw = len(text) * 10
            draw.text(((bx0 + bx1 - tw) // 2, by0 + 35), text, fill="white", font=font)
        except:
             draw.text((bx0 + 50, by0 + 35), "LINK IN BIO", fill="white")

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
