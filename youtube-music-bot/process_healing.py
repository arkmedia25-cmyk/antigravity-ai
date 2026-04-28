import sys
import shutil
from PIL import Image, ImageFilter

try:
    # Use existing banner image found in brain
    img_path = r"C:\Users\mus-1\.gemini\antigravity\brain\7d982953-869f-46e8-b2eb-8e9dfb1a1d2c\healingflow_banner_base_1777237830954.png"
    out_banner_path = r"d:\OneDrive\Bureaublad\HealingFlow_Banner_Final.png"
    
    img = Image.open(img_path)
    
    # YouTube full banner size
    bg_w, bg_h = 2560, 1440
    # YouTube mobile/safe area
    safe_w, safe_h = 1546, 423
    
    # Create background by resizing and blurring heavily
    bg = img.resize((bg_w, bg_h), Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=40))
    
    # Resize width to 1546
    new_w = 1546
    new_h = int(img.height * (1546 / img.width)) 
    fg_temp = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Crop the center 423 pixels vertically
    top = (new_h - 423) // 2
    bottom = top + 423
    fg = fg_temp.crop((0, top, 1546, bottom))
    
    # Paste the foreground perfectly in the center of the background
    offset_x = (bg_w - 1546) // 2
    offset_y = (bg_h - 423) // 2
    bg.paste(fg, (offset_x, offset_y))
    
    bg.save(out_banner_path)
    print(f"Healing Flow Banner basariyla {out_banner_path} konumuna kaydedildi.")
    
except Exception as e:
    print("Hata:", e)
