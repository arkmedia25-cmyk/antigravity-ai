from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Animated HTML thumbnail generator (Binaural Mind / Sleep Wave Music)
try:
    from thumbnail_animated import make as _make_animated
    _ANIMATED_AVAILABLE = True
except ImportError:
    _ANIMATED_AVAILABLE = False

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


def _draw_glow(draw, xy, radius, color):
    """Draw a soft glowing circle."""
    x, y = xy
    for i in range(radius, 0, -1):
        alpha = int(color[3] * (1 - (i / radius)**2))
        draw.ellipse([x - i, y - i, x + i, y + i], fill=(color[0], color[1], color[2], alpha))

def make(genre: dict, video_duration_min: int) -> Path:
    # Use RGBA for transparency effects
    img = Image.new("RGBA", (WIDTH, HEIGHT), color=(10, 15, 40, 255))
    draw = ImageDraw.Draw(img)
    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

    out_path = THUMBNAILS_DIR / f"{genre['slug']}.jpg"

    # 1. Background: Vibrant Gradient (Deep Blue to Royal Purple)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(10 + 60 * ratio)
        g = int(15 + 10 * ratio)
        b = int(40 + 120 * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    # 2. Ambient Glows (Vibrant Neon)
    glow_draw = ImageDraw.Draw(img, "RGBA")
    _draw_glow(glow_draw, (WIDTH * 0.8, HEIGHT * 0.2), 450, (0, 255, 255, 60)) # Neon Cyan
    _draw_glow(glow_draw, (WIDTH * 0.1, HEIGHT * 0.8), 500, (255, 0, 255, 50)) # Neon Magenta
    _draw_glow(glow_draw, (WIDTH * 0.5, HEIGHT * 0.5), 600, (100, 100, 255, 40)) # Electric Blue

    # 3. Modern Glass Panel
    panel_margin = 80
    panel_rect = [panel_margin, panel_margin, WIDTH - panel_margin, HEIGHT - panel_margin]
    glow_draw.rounded_rectangle(panel_rect, radius=50, fill=(255, 255, 255, 20), outline=(255, 255, 255, 60), width=3)

    # 4. Content
    title_raw = genre["title"].format(duration=video_duration_min, year=2025).upper()
    lines = _wrap_text(title_raw, max_chars=22)

    # Standard Windows Font Paths
    f_bold = "C:/Windows/Fonts/arialbd.ttf"
    f_reg = "C:/Windows/Fonts/arial.ttf"

    try:
        font_main = ImageFont.truetype(f_bold, 95)
        font_sub = ImageFont.truetype(f_reg, 45)
    except IOError:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    y_cursor = 200
    for line in lines[:2]:
        bbox = draw.textbbox((0, 0), line, font=font_main)
        w = bbox[2] - bbox[0]
        # Stronger Text Shadow
        draw.text(((WIDTH - w) // 2 + 5, y_cursor + 5), line, font=font_main, fill=(0, 0, 0, 150))
        draw.text(((WIDTH - w) // 2, y_cursor), line, font=font_main, fill=(255, 255, 255, 255))
        y_cursor += 120

    # Modern Cyan Separator
    draw.rectangle([(WIDTH // 2 - 200, y_cursor + 30), (WIDTH // 2 + 200, y_cursor + 35)], fill=(0, 255, 255, 255))

    # Sub label
    label = f"{video_duration_min} HOURS  •  ULTRA RELAXING  •  {genre['slug'].replace('-', ' ').upper()}"
    bbox = draw.textbbox((0, 0), label, font=font_sub)
    w = bbox[2] - bbox[0]
    draw.text(((WIDTH - w) // 2, 540), label, font=font_sub, fill=(200, 220, 255, 255))

    final_img = img.convert("RGB")
    final_img.save(out_path, "JPEG", quality=95)
    print(f"[thumbnail-vibrant] Created: {out_path}")
    return out_path


def make_vertical(genre: dict, video_duration_min: int) -> Path:
    V_WIDTH, V_HEIGHT = 720, 1280
    img = Image.new("RGBA", (V_WIDTH, V_HEIGHT), color=(10, 15, 40, 255))
    draw = ImageDraw.Draw(img)
    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

    out_path = THUMBNAILS_DIR / f"{genre['slug']}_vertical.jpg"

    # 1. Background
    for y in range(V_HEIGHT):
        ratio = y / V_HEIGHT
        r = int(10 + 70 * ratio)
        g = int(15 + 15 * ratio)
        b = int(40 + 130 * ratio)
        draw.line([(0, y), (V_WIDTH, y)], fill=(r, g, b, 255))

    # 2. Ambient Glows
    glow_draw = ImageDraw.Draw(img, "RGBA")
    _draw_glow(glow_draw, (V_WIDTH * 0.5, V_HEIGHT * 0.3), 500, (0, 255, 255, 70))
    _draw_glow(glow_draw, (V_WIDTH * 0.8, V_HEIGHT * 0.8), 450, (255, 0, 255, 60))

    # 3. Glass Panel
    glow_draw.rounded_rectangle([30, 250, V_WIDTH - 30, 1030], radius=60, fill=(255, 255, 255, 15), outline=(255, 255, 255, 50), width=3)

    # 4. Content
    title_raw = genre["title"].format(duration=video_duration_min, year=2025).upper()
    lines = _wrap_text(title_raw, max_chars=14)

    f_bold = "C:/Windows/Fonts/arialbd.ttf"
    f_reg = "C:/Windows/Fonts/arial.ttf"

    try:
        font_large = ImageFont.truetype(f_bold, 100)
        font_small = ImageFont.truetype(f_reg, 50)
    except IOError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    y_start = 380
    for line in lines[:3]:
        bbox = draw.textbbox((0, 0), line, font=font_large)
        w = bbox[2] - bbox[0]
        draw.text(((V_WIDTH - w) // 2 + 4, y_start + 4), line, font=font_large, fill=(0, 0, 0, 150))
        draw.text(((V_WIDTH - w) // 2, y_start), line, font=font_large, fill=(255, 255, 255, 255))
        y_start += 130

    # Sub label
    label = genre['slug'].replace('-', ' ').upper()
    bbox = draw.textbbox((0, 0), label, font=font_small)
    w = bbox[2] - bbox[0]
    draw.text(((V_WIDTH - w) // 2, 900), label, font=font_small, fill=(0, 255, 255, 255))

    final_img = img.convert("RGB")
    final_img.save(out_path, "JPEG", quality=95)
    print(f"[thumbnail-vertical-vibrant] Created: {out_path}")
    return out_path




def run(
    genre: dict,
    duration_min: int,
    channel: str = "binaural",
    animated: bool = True,
) -> dict:
    """
    Generate both a static JPG thumbnail and an animated HTML thumbnail.

    Args:
        genre:        genre dict with 'slug' and 'title' keys
        duration_min: video duration in minutes
        channel:      'binaural' | 'sleep' — controls brand colours
        animated:     if True, also produce the animated HTML file

    Returns:
        dict with keys:
            'jpg'  -> Path to static JPEG thumbnail
            'html' -> Path to animated HTML thumbnail (or None)
    """
    jpg_path = make(genre, duration_min)

    html_path = None
    if animated and _ANIMATED_AVAILABLE:
        result = _make_animated(
            genre,
            channel=channel,
            video_duration_min=duration_min,
            render=False,          # set render=True to also export PNG via Playwright
        )
        html_path = result["html"]

    return {"jpg": jpg_path, "html": html_path}

