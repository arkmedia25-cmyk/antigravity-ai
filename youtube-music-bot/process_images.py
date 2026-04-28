import sys
import shutil
from PIL import Image, ImageFilter

try:
    # Use existing banner image
    img_path = r"d:\OneDrive\Bureaublad\Antigravity\youtube-music-bot\SleepWave_Banner_3.png"
    out_banner_path = r"d:\OneDrive\Bureaublad\SleepWave_Banner_Final.png"
    
    img = Image.open(img_path)
    
    # YouTube full banner size
    bg_w, bg_h = 2560, 1440
    # YouTube mobile/safe area
    safe_w, safe_h = 1546, 423
    
    # Create background by resizing and blurring heavily
    bg = img.resize((bg_w, bg_h), Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=40))
    
    # Let's resize the width to 1546
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
    print(f"Banner basariyla {out_banner_path} konumuna kaydedildi.")
    
    # Copy the generated logo to Desktop
    logo_src = r"C:\Users\mus-1\.gemini\antigravity\brain\de74af8e-afe3-413c-91f8-508b8b32cf2a\sleep_wave_logo_1777273811846.png"
    logo_dest = r"d:\OneDrive\Bureaublad\SleepWave_Logo_Final.png"
    shutil.copy2(logo_src, logo_dest)
    print(f"Logo basariyla {logo_dest} konumuna kopyalandi.")
    
except Exception as e:
    print("Hata:", e)
