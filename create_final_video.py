"""
create_final_video.py
Timestamp-synced Reels video using outputs/timestamps.json + outputs/audio_final.mp3
"""
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip, AudioFileClip

_W, _H = 1080, 1920
_CX = _W // 2

_BLACK = (0,   0,   0)
_NAVY  = (10,  10,  46)
_WHITE = (255, 255, 255)
_TURQ  = (0,   212, 255)
_YELL  = (255, 235, 60)
_BLUE  = (0,   150, 255)

_FONT_BOLD  = "C:/Windows/Fonts/arialbd.ttf"
_FONT_EMOJI = "C:/Windows/Fonts/seguiemj.ttf"
_FADE       = 0.20   # fade-in / fade-out seconds


# ── Helpers ────────────────────────────────────────────────────────────────────

def _font(size, emoji=False):
    for p in ([_FONT_EMOJI] if emoji else []) + [_FONT_BOLD]:
        try:
            return ImageFont.truetype(p, size)
        except IOError:
            pass
    return ImageFont.load_default()


def _sz(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]


def _center(draw, text, font, cy, color):
    w, h = _sz(draw, text, font)
    draw.text((_CX - w // 2, cy - h // 2), text, font=font, fill=color)


def _wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        if _sz(draw, test, font)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _multiline(draw, lines, font, center_y, color, spacing=26):
    _, lh = _sz(draw, "Ag", font)
    total_h = len(lines) * (lh + spacing) - spacing
    y = center_y - total_h // 2
    for line in lines:
        w, _ = _sz(draw, line, font)
        draw.text((_CX - w // 2, y), line, font=font, fill=color)
        y += lh + spacing


# ── Frame builders ─────────────────────────────────────────────────────────────

def _frame_hook() -> np.ndarray:
    """Black bg — warning + hook text."""
    img  = Image.new("RGB", (_W, _H), _BLACK)
    draw = ImageDraw.Draw(img)

    f_em   = _font(160, emoji=True)
    f_main = _font(90)

    # ⚠️ emoji
    em = "\u26a0\ufe0f"
    ew, eh = _sz(draw, em, f_em)
    draw.text((_CX - ew // 2, 620), em, font=f_em, fill=(255, 140, 0))

    # Hook text
    _multiline(draw, ["DIT WIST JE NOG NIET...", "over je brein!"],
               f_main, center_y=1000, color=_WHITE, spacing=28)

    return np.array(img)


def _frame_sentence(text: str) -> np.ndarray:
    """Navy bg — single sentence centered."""
    img  = Image.new("RGB", (_W, _H), _NAVY)
    draw = ImageDraw.Draw(img)

    f_body = _font(72)

    lines = _wrap(draw, text, f_body, max_w=900)
    _multiline(draw, lines, f_body, center_y=_H // 2, color=_WHITE, spacing=28)

    # Subtle bottom divider
    draw.line([(80, _H - 120), (_W - 80, _H - 120)], fill=(*_TURQ, ), width=2)
    f_sm = _font(42)
    _center(draw, "Meer info? Link in bio", f_sm, cy=_H - 72, color=_TURQ)

    return np.array(img)


def _frame_cta() -> np.ndarray:
    """Navy bg — CTA with social buttons."""
    img  = Image.new("RGB", (_W, _H), _NAVY)
    draw = ImageDraw.Draw(img)

    f_q    = _font(80)
    f_em   = _font(62, emoji=True)
    f_btn  = _font(56)
    f_link = _font(48)

    # Question
    _multiline(draw, ["Wat doe jij", "voor je brein?"],
               f_q, center_y=820, color=_WHITE, spacing=24)

    # 💬 emoji below question
    em = "\U0001f4ac"
    ew, _ = _sz(draw, em, f_em)
    draw.text((_CX - ew // 2, 970), em, font=f_em, fill=_WHITE)

    # Social buttons box
    bx0, by0, bx1, by1 = 60, 1100, _W - 60, 1360
    draw.rectangle([bx0, by0, bx1, by1], outline=_BLUE, width=3)
    draw.rectangle([bx0 - 4, by0 - 4, bx1 + 4, by1 + 4], outline=(0, 80, 180), width=2)

    # Icons
    icons = "\U0001f44d   \U0001f4be   \U0001f465"
    iw, _ = _sz(draw, icons, f_em)
    draw.text((_CX - iw // 2, by0 + 30), icons, font=f_em, fill=_WHITE)

    # Labels
    labels = "Like        Bewaar        Volg ons"
    lw, _ = _sz(draw, labels, f_btn)
    draw.text((_CX - lw // 2, by0 + 130), labels, font=f_btn, fill=_YELL)

    # Link in bio
    link = "\U0001f447 Link in bio"
    llw, _ = _sz(draw, link, f_link)
    draw.text((_CX - llw // 2, _H - 130), link, font=f_link, fill=_TURQ)

    return np.array(img)


# ── Video sections ─────────────────────────────────────────────────────────────

def _build_sections(ts: list, total: float) -> list:
    """
    Returns list of {start, end, frame_arr} sorted by start time.
    Uses exact timestamps from timestamps.json.
    """
    sent = {s["sentence"]: s for s in ts}

    hook_ts  = ts[0]                   # "Dit wist je nog NIET..."
    cta_ts   = ts[4]                   # "Wat doe jij vandaag..."
    body_ts  = ts[1:4]                 # sentences 2-4

    sections = []

    # HOOK
    sections.append({
        "name": "HOOK",
        "start": hook_ts["start"],
        "end":   hook_ts["end"],
        "frame": _frame_hook(),
    })

    # CONTENT — one frame per sentence
    for s in body_ts:
        sections.append({
            "name": f"CONTENT({s['sentence'][:20]})",
            "start": s["start"],
            "end":   s["end"],
            "frame": _frame_sentence(s["sentence"]),
        })

    # CTA — runs to end of audio
    sections.append({
        "name": "CTA",
        "start": cta_ts["start"],
        "end":   total,
        "frame": _frame_cta(),
    })

    return sections


# ── Alpha ──────────────────────────────────────────────────────────────────────

def _alpha(t_local: float, dur: float) -> float:
    if dur <= 0:
        return 1.0
    if t_local < _FADE:
        return max(0.0, t_local / _FADE)
    if t_local > dur - _FADE:
        return max(0.0, (dur - t_local) / _FADE)
    return 1.0


# ── Main ───────────────────────────────────────────────────────────────────────

def create_final_video(
    timestamps_path: str = "outputs/timestamps.json",
    audio_path:      str = "outputs/audio_final.mp3",
    output_path:     str = "outputs/final_video.mp4",
):
    with open(timestamps_path, encoding="utf-8") as f:
        ts = json.load(f)

    audio = AudioFileClip(audio_path)
    total = audio.duration

    sections = _build_sections(ts, total)
    _BLACK_F  = np.zeros((_H, _W, 3), dtype=np.uint8)

    print(f"\nSes suresi : {total:.2f}s")
    print(f"Toplam bolum: {len(sections)}\n")
    for s in sections:
        print(f"  {s['name'][:30]:30s}  {s['start']:.2f}s - {s['end']:.2f}s")
    print()

    def make_frame(t: float) -> np.ndarray:
        for sec in sections:
            if sec["start"] <= t < sec["end"]:
                t_local = t - sec["start"]
                dur     = sec["end"] - sec["start"]
                a       = _alpha(t_local, dur)
                if a >= 0.9999:
                    return sec["frame"]
                return (sec["frame"] * a).astype(np.uint8)
        return _BLACK_F

    clip = VideoClip(make_frame, duration=total).with_audio(audio)
    clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", logger=None)

    audio.close()
    clip.close()

    import os
    size_mb = os.path.getsize(output_path) / 1_000_000
    print(f"Kaydedildi: {output_path} ({size_mb:.1f} MB)")
    return output_path


if __name__ == "__main__":
    create_final_video()
