# -*- coding: utf-8 -*-
"""
amarenl.com Reel Maker v2
- ElevenLabs Hollandaca TTS seslendirme
- PIL glassmorphism text overlay (transparan PNG)
- Pexels konu-eslesik portrait video arka plan
- FFmpeg assembly: video + transparan overlay + ses

Kullanim:
  python amarenl_reel_maker.py "Magnesium en Slaap"
  python amarenl_reel_maker.py  (son WP makalesini alir)
"""
import os, sys, json, requests, subprocess
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_DIR  = Path(__file__).parent
_ROOT = _DIR.parent.parent.parent  # src/agents/cmo/ → antigravity-ai/
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

PEXELS_KEY  = os.getenv("PEXELS_API_KEY")
OPENAI_KEY  = os.getenv("OPENAI_API_KEY")
WP_AUTH     = ("shoppingbest41", "QmdY FAML WPzu IiK4 jewG lSD7")
WP_BASE    = "https://amarenl.com"
OUTPUT_DIR = _ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

W, H = 1080, 1920

DEFAULT_BRAND = "holistiglow"
STYLE_STATE   = _ROOT / ".video_style_state.json"
_BRANDS_DIR   = _DIR / "brands"  # src/agents/cmo/brands/

# ── Brand config lader — leest uit brands/<brand>/reel_config.py ──────────────

def load_brand_config(brand: str):
    """Importeer brands/<brand>/reel_config.py en geef module terug."""
    import importlib.util
    cfg_path = _BRANDS_DIR / brand / "reel_config.py"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Brand config niet gevonden: {cfg_path}")
    spec = importlib.util.spec_from_file_location(f"brand_{brand}", cfg_path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def get_next_style(brand: str = DEFAULT_BRAND) -> dict:
    cfg    = load_brand_config(brand)
    styles = cfg.STYLES
    key    = f"last_{brand}"
    try:
        state = json.loads(STYLE_STATE.read_text()) if STYLE_STATE.exists() else {}
    except Exception:
        state = {}
    idx = (state.get(key, -1) + 1) % len(styles)
    state[key] = idx
    STYLE_STATE.write_text(json.dumps(state))
    return styles[idx]

# ── Fonts ─────────────────────────────────────────────────────────────────────

def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    paths = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

# ── PIL Helpers ────────────────────────────────────────────────────────────────

def _rounded_rect(draw: ImageDraw.ImageDraw, xy, r: int, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    draw.ellipse([x0, y0, x0 + 2*r, y0 + 2*r], fill=fill)
    draw.ellipse([x1 - 2*r, y0, x1, y0 + 2*r], fill=fill)
    draw.ellipse([x0, y1 - 2*r, x0 + 2*r, y1], fill=fill)
    draw.ellipse([x1 - 2*r, y1 - 2*r, x1, y1], fill=fill)

def _text_wh(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]

def _center_text(draw, text, font, cy, color, shadow=True):
    w, h = _text_wh(draw, text, font)
    x = (W - w) // 2
    y = cy - h // 2
    if shadow:
        draw.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0, 100))
    draw.text((x, y), text, font=font, fill=color)

def _wrap(text: str, font, draw, max_w: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if _text_wh(draw, test, font)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [text]

def _draw_lines(draw, lines, font, cy, color, spacing=12):
    _, lh = _text_wh(draw, "A", font)
    total = len(lines) * lh + (len(lines) - 1) * spacing
    y = cy - total // 2
    for line in lines:
        _center_text(draw, line, font, y + lh // 2, color)
        y += lh + spacing

# ── Overlay Frame Renderer ─────────────────────────────────────────────────────

def make_overlay(tag: str, line1: str, line2: str, progress: float,
                 style: dict | None = None,
                 brand_handle: str = "@HolistiGlow") -> Image.Image:
    """Transparan RGBA overlay PNG: brand bar + text card + progress bar."""
    s = style or load_brand_config(DEFAULT_BRAND).STYLES[0]
    AC  = s["accent"]
    CH  = s["card_hook"]
    CC  = s["card_content"]

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_brand = _font(44)
    f_hook  = _font(72)
    f_sub   = _font(58)
    f_body  = _font(56)
    f_small = _font(46, bold=False)
    f_cta   = _font(54)

    # Üst marka barı
    draw.rectangle([0, 0, W, 108], fill=(*AC, 245))
    _center_text(draw, brand_handle, f_brand, 54, (255, 255, 255, 255), shadow=False)

    # Alt progress bar
    bar_y = H - 12
    draw.rectangle([0, bar_y, W, H], fill=(255, 255, 255, 40))
    draw.rectangle([0, bar_y, int(W * progress), H], fill=(*AC, 220))

    if tag == "hook":
        card_h = 340
        card_y = (H - card_h) // 2
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        _rounded_rect(sd, [54, card_y + 8, W - 54, card_y + card_h + 8], 28, (0, 0, 0, 80))
        shadow = shadow.filter(ImageFilter.GaussianBlur(14))
        img = Image.alpha_composite(img, shadow)
        draw = ImageDraw.Draw(img)
        _rounded_rect(draw, [60, card_y, W - 60, card_y + card_h], 28, (*CH, 230))
        draw.rectangle([80, card_y + 4, W - 80, card_y + 7], fill=(255, 255, 255, 60))
        lines1 = _wrap(line1, f_hook, draw, 860)
        _draw_lines(draw, lines1, f_hook, card_y + card_h // 2 - 44, (255, 255, 255, 255))
        lines2 = _wrap(line2, f_sub, draw, 860)
        _draw_lines(draw, lines2, f_sub, card_y + card_h // 2 + 72, (220, 220, 220, 255))

    elif tag == "content":
        card_h = 280
        card_y = (H - card_h) // 2
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        _rounded_rect(sd, [54, card_y + 6, W - 54, card_y + card_h + 6], 24, (0, 0, 0, 70))
        shadow = shadow.filter(ImageFilter.GaussianBlur(12))
        img = Image.alpha_composite(img, shadow)
        draw = ImageDraw.Draw(img)
        _rounded_rect(draw, [60, card_y, W - 60, card_y + card_h], 24, (*CC, 185))
        draw.rectangle([80, card_y + 4, W - 80, card_y + 7], fill=(255, 255, 255, 45))
        lines1 = _wrap(line1, f_body, draw, 860)
        _draw_lines(draw, lines1, f_body, card_y + card_h // 2 - 34, (255, 255, 255, 255))
        lines2 = _wrap(line2, f_small, draw, 860)
        _draw_lines(draw, lines2, f_small, card_y + card_h // 2 + 68, (200, 200, 200, 255))

    else:  # cta
        draw.rectangle([0, 1670, W, H - 14], fill=(*AC, 245))
        draw.rectangle([0, 1670, W, 1674], fill=(255, 255, 255, 50))
        _center_text(draw, line1, f_cta, 1730, (255, 255, 255, 255))
        _center_text(draw, line2, f_small, 1800, (220, 220, 220, 255), shadow=False)

    return img

# ── OpenAI TTS ────────────────────────────────────────────────────────────────

def tts(text: str, out_path: Path, voice: str = "nova") -> bool:
    if not OPENAI_KEY:
        return False
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            speed=1.0,
            input=text,
        )
        response.write_to_file(str(out_path))
        return True
    except Exception as e:
        print(f"  TTS fout: {e}")
        return False

def audio_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 4.0

# ── Pexels Video ──────────────────────────────────────────────────────────────

def fetch_pexels_video(query: str, out_path: Path) -> bool:
    r = requests.get(
        "https://api.pexels.com/videos/search",
        params={"query": query, "per_page": 8, "orientation": "portrait", "size": "medium"},
        headers={"Authorization": PEXELS_KEY},
        timeout=15,
    )
    if r.ok:
        for vid in r.json().get("videos", []):
            for f in vid.get("video_files", []):
                if (f.get("quality") in ("hd", "sd")
                        and f.get("width", 999) <= f.get("height", 0)
                        and vid.get("duration", 0) >= 10):
                    data = requests.get(f["link"], timeout=40).content
                    out_path.write_bytes(data)
                    print(f"  Pexels video: {vid['id']} ({len(data)//1024}KB, {vid['duration']}s)")
                    return True
    return False

# ── FFmpeg Assembly ───────────────────────────────────────────────────────────

def build_reel(sections: list, bg_video: Path, output: Path) -> bool:
    """
    sections: [(tag, line1, line2, tts_text, audio_path, overlay_png, duration)]
    """
    total = sum(s[6] for s in sections)
    n = len(sections)

    # Inputs bouwen
    cmd = ["ffmpeg", "-y",
           "-stream_loop", "-1", "-i", str(bg_video)]
    for s in sections:
        cmd += ["-i", str(s[5])]   # overlay PNG per sectie
    for s in sections:
        cmd += ["-i", str(s[4])]   # audio per sectie

    filter_parts = []

    # Achtergrond schalen
    filter_parts.append(
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,setsar=1,fps=25[bg]"
    )

    # Overlay PNGs schalen
    for i in range(n):
        filter_parts.append(f"[{i+1}:v]scale=1080:1920[ov{i}]")

    # Sequentieel overlays toepassen met tijdsvensters
    t = 0.0
    prev = "[bg]"
    for i, s in enumerate(sections):
        dur = s[6]
        enable = f"between(t\\,{t:.2f}\\,{t+dur:.2f})"
        out = f"[vout{i}]"
        filter_parts.append(
            f"{prev}[ov{i}]overlay=x=0:y=0:enable='{enable}'{out}"
        )
        prev = out
        t += dur

    # Audio aaneenschakelen
    audio_inputs = "".join(f"[{n+1+i}:a]" for i in range(n))
    filter_parts.append(f"{audio_inputs}concat=n={n}:v=0:a=1[aout]")

    cmd += [
        "-t", str(total),
        "-filter_complex", ";".join(filter_parts),
        "-map", prev,
        "-map", "[aout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(output),
    ]

    r = subprocess.run(cmd, capture_output=True, timeout=180)
    if r.returncode != 0:
        print("FFmpeg hata:", r.stderr.decode()[-800:])
        return False
    return True

# ── Per-merk topic queues ─────────────────────────────────────────────────────

def get_next_topic(brand: str) -> str:
    topics = load_brand_config(brand).TOPIC_QUEUE
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        state = json.loads(STYLE_STATE.read_text()) if STYLE_STATE.exists() else {}
    except Exception:
        state = {}

    if state.get("today_date") != today:
        state["today_date"] = today
        state["today_runs"] = {}

    today_runs: dict = state.get("today_runs", {})
    already_today = set(today_runs.values())
    idx = state.get(f"topic_idx_{brand}", -1)
    candidate = topics[(idx + 1) % len(topics)]  # default: next in queue

    for _ in range(len(topics)):
        idx = (idx + 1) % len(topics)
        if topics[idx] not in already_today:
            candidate = topics[idx]
            break

    state[f"topic_idx_{brand}"] = idx
    today_runs[brand] = candidate
    state["today_runs"] = today_runs
    STYLE_STATE.write_text(json.dumps(state))
    return candidate


# ── Main ──────────────────────────────────────────────────────────────────────

def run(topic_key: str | None = None, title: str | None = None,
        brand: str = DEFAULT_BRAND, force_style: str | None = None):
    brand_cfg    = load_brand_config(brand)
    brand_handle = brand_cfg.HANDLE
    brand_voice  = brand_cfg.VOICE

    print("\n" + "=" * 55)
    print(f"  Reel Maker v2  —  {brand_handle}")
    print("=" * 55)

    # Topic: expliciet meegegeven of automatisch volgende in de queue
    if not topic_key:
        topic_key = get_next_topic(brand)
        print(f"  Topic (auto)  : {topic_key}")
    else:
        print(f"  Topic (opgeg.): {topic_key}")

    # Stijl: geforceerd of rouleren
    if force_style:
        style = next((s for s in brand_cfg.STYLES if s["name"] == force_style),
                     brand_cfg.STYLES[0])
    else:
        style = get_next_style(brand)
    print(f"  Stijl vandaag : {style['name']}  |  Stem: {brand_voice}")

    scripts = brand_cfg.DEMO_SCRIPTS
    script  = scripts.get(topic_key) or scripts.get(
        brand_cfg.TOPIC_QUEUE[0], list(scripts.values())[0]
    )
    if title:
        # Pas pexels query aan op basis van meegegeven titel
        script = dict(script)
        script["pexels_query"] = title.lower().replace(" ", " ")

    stamp  = datetime.now().strftime("%Y%m%d_%H%M")
    tmp    = OUTPUT_DIR / f"_tmp_{stamp}"
    tmp.mkdir(exist_ok=True)

    # 1. Pexels video
    bg_path = tmp / "bg.mp4"
    print(f"\nPexels video: {script['pexels_query']}")
    if not fetch_pexels_video(script["pexels_query"], bg_path):
        print("  Pexels mislukt, fallback kleur achtergrond")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "color=c=0x0a1a1a:size=1080x1920:rate=25",
            "-t", "60", "-c:v", "libx264", str(bg_path)
        ], capture_output=True)

    # 2. TTS + overlay per sectie
    sections_built = []
    total_sections = len(script["sections"])
    print("\nSectie rendering:")

    for i, (tag, l1, l2, tts_text) in enumerate(
        [(t, a.replace("{handle}", brand_handle), b, tx)
         for t, a, b, tx in script["sections"]]
    ):
        print(f"  [{i+1}/{total_sections}] {tag}: {l1[:40]}")

        # TTS audio
        audio_path = tmp / f"audio_{i}.mp3"
        ok = tts(tts_text, audio_path, voice=brand_voice)
        if not ok:
            # Stille audio fallback (4 seconden)
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", "anullsrc=r=44100:cl=mono",
                "-t", "4", "-acodec", "libmp3lame", str(audio_path)
            ], capture_output=True)

        dur = audio_duration(audio_path)
        progress = (i + 1) / total_sections

        # Overlay PNG (stijl + merk doorgeven)
        overlay_img = make_overlay(tag, l1, l2, progress, style=style, brand_handle=brand_handle)
        overlay_path = tmp / f"overlay_{i}.png"
        overlay_img.save(str(overlay_path))

        sections_built.append((tag, l1, l2, tts_text, audio_path, overlay_path, dur))
        print(f"     audio={dur:.1f}s  overlay={overlay_path.name}")

    # 3. Video samenstellen
    output = OUTPUT_DIR / f"reel_{brand}_{stamp}.mp4"
    print(f"\nVideo samenstellen...")
    ok = build_reel(sections_built, bg_path, output)

    if ok:
        sz = output.stat().st_size // 1024
        total_dur = sum(s[6] for s in sections_built)
        print(f"\nKlaar: {output.name}")
        print(f"  Grootte  : {sz} KB")
        print(f"  Duur     : {total_dur:.1f} seconden")
        print(f"  Locatie  : {output}")
    else:
        print("\nMislukt")

    # Tmp opruimen
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)

    if not ok:
        return None, {}

    # Meta voor Telegram notificatie
    hook_secs    = [s for s in script["sections"] if s[0] == "hook"]
    content_secs = [s for s in script["sections"] if s[0] == "content"]
    title_text   = f"{hook_secs[0][1]} {hook_secs[0][2]}" if hook_secs else topic_key.replace("_", " ").title()
    desc_text    = "  ".join(f"{s[1]} {s[2]}" for s in content_secs[:3])
    tags_text    = getattr(brand_cfg, "CTA_HASHTAGS", "#wellness #nl")

    return str(output), {"title": title_text, "description": desc_text, "tags": tags_text}


if __name__ == "__main__":
    # Kullanım: python amarenl_reel_maker.py [topic_key] [brand]
    # Örnek: python amarenl_reel_maker.py magnesium glowup
    # Kullanım: python amarenl_reel_maker.py [topic_key] [brand] [force_style]
    # Örnek: python amarenl_reel_maker.py magnesium glowup navy
    _topic = sys.argv[1] if len(sys.argv) > 1 else "magnesium"
    _brand = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_BRAND
    _style = sys.argv[3] if len(sys.argv) > 3 else None
    run(_topic, brand=_brand, force_style=_style)
