import os
import json
import subprocess
import urllib.request
from PIL import Image, ImageDraw, ImageFont

_OUTPUT_DIR = "outputs"
_W, _H = 1080, 1920
_CX = _W // 2

# ── Brand Themes ──────────────────────────────────────────────────────────────
THEMES = {
    "glow": {
        "bg":         (254, 245, 238),
        "accent":     (255, 112, 86),
        "accent2":    (255, 185, 165),
        "text":       (62, 44, 40),
        "font_title": "title",
        "font_body":  "body",
        "brand_name": "@GlowUpNL",
    },
    "holisti": {
        "bg":         (247, 243, 240),
        "accent":     (130, 150, 120),
        "accent2":    (210, 220, 200),
        "text":       (40, 44, 45),
        "font_title": "title",
        "font_body":  "body",
        "brand_name": "@HolistiGlow",
    }
}

# ── Font management ───────────────────────────────────────────────────────────
_FONTS = {
    "title": "PlayfairDisplay-Bold.ttf",
    "body":  "Montserrat-Medium.ttf",
}
_FONT_URLS = {
    "title": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay-Bold.ttf",
    "body":  "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Medium.ttf",
}

def _ensure_fonts():
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for name, filename in _FONTS.items():
        full_path = os.path.join(base, filename)
        if not os.path.exists(full_path):
            try:
                print(f"[video_skill] Downloading {name} font...")
                urllib.request.urlretrieve(_FONT_URLS[name], full_path)
            except Exception as e:
                print(f"[video_skill] Warning: Could not download {name}: {e}")

_ensure_fonts()

def _font(size: int, font_type: str = "body") -> ImageFont.FreeTypeFont:
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    filename = _FONTS.get(font_type, "Montserrat-Medium.ttf")
    path = os.path.join(base, filename)
    try:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    except Exception:
        pass
    # Fallback: try system fonts
    for fallback in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                     "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(fallback):
            try:
                return ImageFont.truetype(fallback, size)
            except Exception:
                pass
    return ImageFont.load_default()

# ── Drawing helpers ───────────────────────────────────────────────────────────

def _sz(draw, text, font):
    """Return (width, height) of a text string."""
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]

def _wrap(draw, text: str, font, max_w: int) -> list:
    """Break text into lines that fit within max_w pixels."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        w, _ = _sz(draw, test, font)
        if w <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines if lines else [text]

def _multiline(draw, lines: list, font, center_y: int, color, spacing: int = 20):
    """Draw centered multi-line text around center_y."""
    _, lh = _sz(draw, "Ag", font)
    total_h = len(lines) * lh + (len(lines) - 1) * spacing
    y = center_y - total_h // 2
    for line in lines:
        w, _ = _sz(draw, line, font)
        draw.text((_CX - w // 2, y), line, font=font, fill=color)
        y += lh + spacing

def _clean_text(text: str) -> str:
    """Removes unsupported characters and maps markers (bullets/emojis)
    to a standard '*' for better visual list alignment."""
    import re
    if not text: return ""
    # Map common list/emoji markers to '*' to maintain list structure
    text = re.sub(r'^\s*[•🌿✨\-1234567890\.\*\/]+\s*', '* ', text)
    # Filter for standard characters supported by the font, plus our '*'
    clean = re.sub(r'[^\x00-\x7F\xC0-\xFF\.,!?\'\":\* ]+', '', text)
    return clean.strip()

def _draw_rounded_rect(draw, coords, radius: int, fill):
    """Draw a truly solid rounded rectangle to avoid rendering artifacts."""
    x0, y0, x1, y1 = coords
    # Use 4 solid circles for corners and 2 rectangles for the body
    draw.ellipse([x0, y0, x0 + radius * 2, y0 + radius * 2], fill=fill)
    draw.ellipse([x1 - radius * 2, y0, x1, y0 + radius * 2], fill=fill)
    draw.ellipse([x1 - radius * 2, y1 - radius * 2, x1, y1], fill=fill)
    draw.ellipse([x0, y1 - radius * 2, x0 + radius * 2, y1], fill=fill)
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)

def _center(draw, text: str, font, cy: int, color):
    """Draw a single horizontally centered line at cy."""
    text = _clean_text(text)
    w, _ = _sz(draw, text, font)
    draw.text((_CX - w // 2, cy - _sz(draw, "Ag", font)[1] // 2), text, font=font, fill=color)

# ── Frame builders ────────────────────────────────────────────────────────────

def _build_hook(theme: dict) -> str:
    img  = Image.new("RGB", (_W, _H), theme["bg"])
    draw = ImageDraw.Draw(img)

    # Decorative circle
    draw.ellipse([_CX - 380, 280, _CX + 380, 1080],
                 outline=theme["accent2"], width=4)
    # Small accent triangle
    draw.polygon([(_CX, 560), (_CX - 55, 680), (_CX + 55, 680)],
                 fill=theme["accent"])

    # Hook text — always wrapped so nothing overflows
    f = _font(82, theme["font_title"])
    lines = _wrap(draw, "DIT WIST JE NOG NIET... Over deze routine!", f, max_w=950)
    _multiline(draw, lines, f, center_y=1130, color=theme["text"], spacing=22)

    path = os.path.join(_OUTPUT_DIR, f"frame_{theme['brand_name']}_0_hook.png")
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    img.save(path)
    return path


def _build_sentence_frame(text: str, theme: dict, index: int) -> str:
    img  = Image.new("RGB", (_W, _H), theme["bg"])
    draw = ImageDraw.Draw(img)

    # Sanitization
    text = _clean_text(text)

    # Card background — solid, clean
    card_x0, card_x1 = 80, _W - 80
    card_y0, card_y1 = _H // 2 - 380, _H // 2 + 380
    _draw_rounded_rect(draw, [card_x0, card_y0, card_x1, card_y1], 40, fill=theme["accent2"])

    # Left accent bar
    draw.rectangle([card_x0, card_y0 + 60, card_x0 + 10, card_y1 - 60], fill=theme["accent"])

    f = _font(72, theme["font_body"])
    lines = _wrap(draw, text, f, max_w=870)
    _multiline(draw, lines, f, center_y=_H // 2, color=theme["text"], spacing=22)

    path = os.path.join(_OUTPUT_DIR, f"frame_content_{index}.png")
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    img.save(path)
    return path


def _build_cta(theme: dict) -> str:
    img  = Image.new("RGB", (_W, _H), theme["bg"])
    draw = ImageDraw.Draw(img)

    # Main CTA question
    f_q = _font(82, theme["font_title"])
    lines_q = _wrap(draw, _clean_text("Wat ga jij vandaag doen?"), f_q, max_w=950)
    _multiline(draw, lines_q, f_q, center_y=750, color=theme["text"], spacing=20)

    # Rounded action button
    bx0, by0, bx1, by1 = 120, 1000, _W - 120, 1280
    _draw_rounded_rect(draw, [bx0, by0, bx1, by1], 40, fill=theme["accent"])

    f_btn = _font(52, theme["font_body"])
    y_btn = by0 + 75
    for label in ["Like & Save", f"Volg {theme['brand_name']}"]:
        _center(draw, label, f_btn, cy=y_btn, color=(255, 255, 255))
        y_btn += 95

    # Bottom link
    f_link = _font(44, theme["font_body"])
    lines_link = _wrap(draw, _clean_text("Klik op de link in bio voor meer hulp"), f_link, max_w=950)
    _multiline(draw, lines_link, f_link, center_y=_H - 160, color=theme["accent"], spacing=10)

    path = os.path.join(_OUTPUT_DIR, f"frame_{theme['brand_name']}_2_cta.png")
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    img.save(path)
    return path


# ── Main video assembly ───────────────────────────────────────────────────────

def create_reel(
    audio_path: str = "outputs/audio_final.mp3",
    output_filename: str = "final_video.mp4",
    brand: str = "holisti"
) -> str:
    theme = THEMES.get(brand, THEMES["holisti"])
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(_OUTPUT_DIR, output_filename)
    if os.path.exists(output_path):
        os.remove(output_path)

    # ── 1. Check for Fragmented Mode (Perfect Sync) ──
    frag_path = os.path.join(_OUTPUT_DIR, "fragments.json")
    fragments = []
    if os.path.exists(frag_path):
        try:
            with open(frag_path, encoding="utf-8") as f:
                fragments = json.load(f)
            print(f"[video_skill] Fragmented mode active: {len(fragments)} fragments found.")
        except Exception:
            pass

    # ── 2. Utility for duration ──
    def get_duration(p: str) -> float:
        try:
            res = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", p],
                capture_output=True, text=True
            )
            return float(res.stdout.strip())
        except Exception:
            return 3.0

    # ── 3. Encode clips ──
    def make_clip(img_path: str, dur: float, out_name: str) -> str:
        clip_path = os.path.join(_OUTPUT_DIR, out_name)
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-t", f"{dur:.2f}",
            "-i", img_path, "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "23", "-preset", "ultrafast", clip_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return clip_path

    # Step A: Build Fixed Hook & CTA
    img_hook = _build_hook(theme)
    img_cta  = _build_cta(theme)
    v_hook = make_clip(img_hook, 5.0, "v_hook.mp4")
    v_cta  = make_clip(img_cta,  8.0, "v_cta.mp4")

    # Step B: Build Content Fragments
    content_video_clips = []
    all_audio_files = [] # We will concatenate these later
    
    if fragments:
        print("[video_skill] Encoding fragments for 100% sync...")
        for i, frag in enumerate(fragments):
            dur = get_duration(frag["audio"])
            img_p = _build_sentence_frame(frag["sentence"], theme, i)
            c_p = make_clip(img_p, dur, f"v_c{i}.mp4")
            content_video_clips.append(c_p)
            all_audio_files.append(frag["audio"])
    else:
        # Fallback to old linear/weighted logic if no fragments
        print("[video_skill] Fallback to weighted sync...")
        sentences = ["Kusursuz biyo-hacker rutini!"] # Mock
        weights = [1.2 + (len(s.split()) / 2.5) for s in sentences]
        total_w = sum(weights) or 1.0
        for i, s in enumerate(sentences):
            img_p = _build_sentence_frame(s, theme, i)
            c_p = make_clip(img_p, 3.0, f"v_c{i}.mp4") # Mock dur
            content_video_clips.append(c_p)

    # ── 4. Final Assembly ──
    # Join video clips
    list_path = os.path.join(_OUTPUT_DIR, "concat_v.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        f.write("file 'v_hook.mp4'\n")
        for i in range(len(content_video_clips)):
            f.write(f"file 'v_c{i}.mp4'\n")
        f.write("file 'v_cta.mp4'\n")

    # Join audio clips (Hook silence + fragments + CTA silence)
    # We create a silent 5s hook and 8s cta audio if none exist
    silence_hook = os.path.join(_OUTPUT_DIR, "silence_5.mp3")
    silence_cta  = os.path.join(_OUTPUT_DIR, "silence_8.mp3")
    for s_path, s_dur in [(silence_hook, 5.0), (silence_cta, 8.0)]:
        if not os.path.exists(s_path):
            subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo", "-t", str(s_dur), s_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    audio_list_path = os.path.join(_OUTPUT_DIR, "concat_a.txt")
    with open(audio_list_path, "w", encoding="utf-8") as f:
        f.write(f"file 'silence_5.mp3'\n")
        for af in all_audio_files:
            # Must write relative or absolute path correctly
            f.write(f"file '{os.path.basename(af)}'\n")
        f.write(f"file 'silence_8.mp3'\n")

    # Concatenate Audio
    final_audio = os.path.join(_OUTPUT_DIR, "audio_combined.mp3")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", audio_list_path, "-c", "copy", final_audio],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Concatenate Video + Audio Merge
    print("[video_skill] Merging final Reel...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
        "-i", final_audio, "-c:v", "copy", "-c:a", "aac", "-shortest", output_path
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    size_mb = os.path.getsize(output_path) / 1_000_000
    print(f"[video_skill] Completed Fragmented Reel: {output_path} ({size_mb:.1f} MB)")
    return output_path


if __name__ == "__main__":
    path = create_reel()
    print("Test video:", path)
