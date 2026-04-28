import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

THUMBNAILS_DIR = Path("thumbnails")  # fallback only
WIDTH, HEIGHT = 1280, 720

CHANNEL_COLORS = {
    "neonpulse":    {"top": (20, 30, 120),   "bottom": (5, 10, 60),    "accent": (100, 150, 255), "text": (255, 255, 255)},
    "sleepwave":    {"top": (10, 20, 100),    "bottom": (5, 10, 50),    "accent": (80, 130, 220),  "text": (210, 230, 255)},
    "healingflow":  {"top": (10, 80, 50),     "bottom": (5, 40, 20),    "accent": (60, 200, 130),  "text": (210, 255, 230)},
    "binauralmind": {"top": (60, 10, 120),    "bottom": (30, 5, 70),    "accent": (170, 80, 255),  "text": (230, 210, 255)},
}

FONT_PATHS = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "arial.ttf",
    "DejaVuSans-Bold.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def _wrap_text(text: str, max_chars: int = 28) -> list[str]:
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


def make(genre: dict, video_duration_min: int, channel_slug: str = "neonpulse") -> Path:
    out_dir = Path(f"channels/{channel_slug}/thumbnails")
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = genre.get("slug", "")
    colors = CHANNEL_COLORS.get(channel_slug, CHANNEL_COLORS["neonpulse"])

    top        = colors["top"]
    bottom     = colors["bottom"]
    accent     = colors["accent"]
    text_color = colors["text"]

    img = Image.new("RGB", (WIDTH, HEIGHT), color=bottom)
    draw = ImageDraw.Draw(img)

    # Gradient top to bottom
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top[0] * (1 - ratio) + bottom[0] * ratio)
        g = int(top[1] * (1 - ratio) + bottom[1] * ratio)
        b = int(top[2] * (1 - ratio) + bottom[2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Top accent line
    draw.rectangle([(0, 0), (WIDTH, 6)], fill=accent)

    # Title — take only the part before the first "|"
    title_raw   = genre["title"].format(duration=video_duration_min, year=2026)
    title_short = title_raw.split("|")[0].strip()
    lines = _wrap_text(title_short, max_chars=28)

    font_large = _load_font(80)
    font_small = _load_font(40)
    font_label = _load_font(32)

    y_start = 160
    for line in lines[:2]:
        bbox = draw.textbbox((0, 0), line, font=font_large)
        w = bbox[2] - bbox[0]
        x = (WIDTH - w) // 2
        draw.text((x + 3, y_start + 3), line, font=font_large, fill=(0, 0, 0))  # shadow
        draw.text((x, y_start), line, font=font_large, fill=text_color)
        y_start += 100

    # Middle accent line
    draw.rectangle([(160, y_start + 10), (WIDTH - 160, y_start + 14)], fill=accent)
    y_start += 40

    # Duration + quality label
    label = f"  {video_duration_min} MIN   |   AI MUSIC"
    bbox = draw.textbbox((0, 0), label, font=font_small)
    w = bbox[2] - bbox[0]
    draw.text(((WIDTH - w) // 2, y_start), label, font=font_small, fill=accent)

    # Bottom genre label
    niche_label = slug.upper().replace("-", " ")
    bbox = draw.textbbox((0, 0), niche_label, font=font_label)
    w = bbox[2] - bbox[0]
    draw.text(((WIDTH - w) // 2, HEIGHT - 60), niche_label, font=font_label, fill=(*accent, 180))

    # Bottom accent line
    draw.rectangle([(0, HEIGHT - 6), (WIDTH, HEIGHT)], fill=accent)

    out = out_dir / f"{slug}.jpg"
    img.save(out, "JPEG", quality=95)
    print(f"[thumbnail] Created: {out}")
    return out


def run(genre: dict, duration_min: int, channel_slug: str = "neonpulse") -> Path:
    return make(genre, duration_min, channel_slug)
