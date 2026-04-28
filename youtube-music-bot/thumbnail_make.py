from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

THUMBNAILS_DIR = Path("thumbnails")
WIDTH, HEIGHT = 1280, 720


def _wrap_text(text: str, max_chars: int = 35) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = f"{current} {word}".strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def make(genre: dict, video_duration_min: int) -> Path:
    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), color=(8, 12, 30))
    draw = ImageDraw.Draw(img)

    # Gradient efekti — koyu mavi → siyah
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(8 * (1 - ratio))
        g = int(12 * (1 - ratio))
        b = int(30 + 20 * (1 - ratio))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Büyük başlık metni
    title_raw = genre["title"].format(duration=video_duration_min, year=2025)
    lines = _wrap_text(title_raw, max_chars=30)

    try:
        font_large = ImageFont.truetype("arial.ttf", 72)
        font_small = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    y_start = 180
    for line in lines[:3]:
        bbox = draw.textbbox((0, 0), line, font=font_large)
        w = bbox[2] - bbox[0]
        draw.text(((WIDTH - w) // 2, y_start), line, font=font_large, fill=(255, 255, 255))
        y_start += 90

    # Alt etiket
    label = f"{video_duration_min} HOURS  •  NO ADS  •  {genre['slug'].upper()}"
    bbox = draw.textbbox((0, 0), label, font=font_small)
    w = bbox[2] - bbox[0]
    draw.text(((WIDTH - w) // 2, 580), label, font=font_small, fill=(150, 180, 255))

    # Frekans dalgası dekoratif çizgisi
    draw.rectangle([(200, 560), (WIDTH - 200, 562)], fill=(100, 130, 255, 128))

    out = THUMBNAILS_DIR / f"{genre['slug']}.jpg"
    img.save(out, "JPEG", quality=95)
    print(f"[thumbnail] Oluşturuldu: {out}")
    return out


def run(genre: dict, duration_min: int) -> Path:
    return make(genre, duration_min)
