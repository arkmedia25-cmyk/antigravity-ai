import sys
from PIL import Image, ImageFilter

try:
    img_path = r"C:\Users\mus-1\.gemini\antigravity\brain\7d982953-869f-46e8-b2eb-8e9dfb1a1d2c\healingflow_banner_base_1777237830954.png"
    out_path = r"d:\OneDrive\Bureaublad\HealingFlow_Banner_Fixed.png"
    
    img = Image.open(img_path)
    
    # YouTube tam banner boyutu
    bg_w, bg_h = 2560, 1440
    # YouTube mobil/her cihaz güvenli alanı
    safe_w, safe_h = 1546, 423
    
    # Arka planı oluştur (orijinali büyütüp çok fazla bulanıklaştırıyoruz)
    bg = img.resize((bg_w, bg_h), Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=40))
    
    # Ana görseli güvenli alana (1546x423) sığacak şekilde küçült
    ratio = min(safe_w / img.width, safe_h / img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    
    fg = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Ana görseli tam ortaya yerleştir
    offset_x = (bg_w - new_w) // 2
    offset_y = (bg_h - new_h) // 2
    
    bg.paste(fg, (offset_x, offset_y))
    
    bg.save(out_path)
    print("Basariyla kaydedildi.")
except Exception as e:
    print("Hata:", e)
