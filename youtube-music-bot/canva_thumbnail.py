"""
Canva-based thumbnail generator.
Uses pre-exported Canva base images per channel, overlays dynamic title text.
Canva design IDs (for re-export when needed):
  sleepwave:    DAHIDjZkxtc
  healingflow:  DAHIDkzrCjQ
  binauralmind: DAHIDvj_Nvg
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

THUMBNAILS_DIR = Path("thumbnails")
CANVA_BASE_DIR = Path("thumbnails/canva")
WIDTH, HEIGHT = 1280, 720

CHANNEL_BASES = {
    "sleepwave":    CANVA_BASE_DIR / "sleepwave_base.png",
    "healingflow":  CANVA_BASE_DIR / "healingflow_base.png",
    "binauralmind": CANVA_BASE_DIR / "binauralmind_base.png",
    # NeonPulse kullanmaya devam ediyor eski thumbnail_make.py'ı
}

# Kanal başına metin rengi ve gölge
CHANNEL_STYLE = {
    "sleepwave":    {"color": (255, 255, 255), "shadow": (0, 0, 60, 180)},
    "healingflow":  {"color": (255, 255, 220), "shadow": (20, 60, 0, 180)},
    "binauralmind": {"color": (200, 230, 255), "shadow": (0, 10, 50, 180)},
}


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for name in ["arialbd.ttf", "Arial Bold.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except IOError:
            continue
    return ImageFont.load_default()


def _wrap(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        w = draw.textlength(test, font=font)
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def make(genre: dict, video_duration_min: int, channel_slug: str = "sleepwave") -> Path:
    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

    base_path = CHANNEL_BASES.get(channel_slug)
    if base_path and base_path.exists():
        img = Image.open(base_path).convert("RGBA")
    else:
        # Fallback: koyu arka plan
        img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 12, 30, 255))

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    title_raw = genre["title"].format(duration=video_duration_min, year=2026)
    style = CHANNEL_STYLE.get(channel_slug, {"color": (255, 255, 255), "shadow": (0, 0, 0, 160)})

    # Yarı saydam koyu bant — metin okunabilirliği için
    band_top, band_bottom = HEIGHT // 4, (HEIGHT * 3) // 4
    for y in range(band_top, band_bottom):
        alpha = int(150 * abs(y - (band_top + band_bottom) // 2) / ((band_bottom - band_top) // 2 + 1))
        alpha = max(0, 140 - alpha)
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))

    font_title = _load_font(72)
    font_label = _load_font(34)

    max_w = WIDTH - 120
    lines = _wrap(title_raw, font_title, max_w, draw)[:3]

    total_h = len(lines) * 88
    y = (HEIGHT - total_h) // 2 - 20

    for line in lines:
        w = draw.textlength(line, font=font_title)
        x = (WIDTH - w) // 2
        # Gölge
        draw.text((x + 3, y + 3), line, font=font_title, fill=(*style["shadow"][:3], 180))
        # Asıl metin
        draw.text((x, y), line, font=font_title, fill=style["color"])
        y += 88

    # Alt etiket
    label = f"{video_duration_min} HOURS  •  NO ADS  •  AI MUSIC"
    lw = draw.textlength(label, font=font_label)
    draw.text(((WIDTH - lw) // 2 + 2, 622), label, font=font_label, fill=(0, 0, 0, 160))
    draw.text(((WIDTH - lw) // 2, 620), label, font=font_label, fill=(200, 220, 255, 230))

    # Birleştir
    result = Image.alpha_composite(img, overlay).convert("RGB")

    out_path = THUMBNAILS_DIR / f"{channel_slug}_{genre['slug']}.jpg"
    result.save(out_path, "JPEG", quality=95)
    return out_path


if __name__ == "__main__":
    import json

    for channel_slug in ["sleepwave", "healingflow", "binauralmind"]:
        genres_path = Path(f"channels/{channel_slug}/genres.json")
        if not genres_path.exists():
            print(f"genres.json yok: {channel_slug}")
            continue
        genres = json.loads(genres_path.read_text())
        for genre in genres:
            out = make(genre, genre["duration_min"], channel_slug)
            print(f"[{channel_slug}] {genre['slug']} -> {out}")
