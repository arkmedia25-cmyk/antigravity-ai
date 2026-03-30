"""
video_skill.py — 3-section Reels with fade-in/out, synced to audio.

Timeline (auto-calculated from audio duration):
  Section 1  20% of total  → HOOK
  <0.2s black gap>
  Section 2  60% of total  → CONTENT
  <0.2s black gap>
  Section 3  20% of total  → CTA

Each section: 0.3s fade-in → full display → 0.3s fade-out
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip, AudioFileClip

_OUTPUT_DIR = "outputs"
_W, _H = 1080, 1920

_BLACK  = (0,   0,   0)
_NAVY   = (10,  10,  46)
_TURQ   = (0,   212, 255)
_WHITE  = (255, 255, 255)
_YELLOW = (255, 235, 60)
_ORANGE = (255, 140, 0)
_BLUE   = (0,   150, 255)

import platform
import os
import urllib.request

_FONT_PATH = "Roboto-Bold.ttf"
if not os.path.exists(_FONT_PATH):
    print("[video_skill] Downloading Roboto font...")
    try:
        urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf", _FONT_PATH)
    except Exception as e:
        print(f"[video_skill] Warning: Failed to download font: {e}")

_GAP      = 0.20   # black gap between sections (seconds)
_FADE_IN  = 0.30   # fade-in duration
_FADE_OUT = 0.30   # fade-out duration

# ── Font & drawing helpers ─────────────────────────────────────────────────────

def _font(size: int, emoji: bool = False) -> ImageFont.FreeTypeFont:
    try:
        if os.path.exists(_FONT_PATH):
            return ImageFont.truetype(_FONT_PATH, size)
    except IOError:
        pass
    return ImageFont.load_default()


def _sz(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]


def _center_text(draw, text, font, y, color):
    w, h = _sz(draw, text, font)
    draw.text((_W // 2 - w // 2, y), text, font=font, fill=color)
    return h


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


def _multiline_centered(draw, lines, font, start_y, color, spacing=22):
    y = start_y
    for line in lines:
        w, h = _sz(draw, line, font)
        draw.text((_W // 2 - w // 2, y), line, font=font, fill=color)
        y += h + spacing
    return y


# ── Static frame builders (return numpy RGB arrays) ───────────────────────────

def _build_hook() -> np.ndarray:
    img  = Image.new("RGB", (_W, _H), _BLACK)
    draw = ImageDraw.Draw(img)

    f_em   = _font(180, emoji=True)
    f_main = _font(82)

    # ⚠️ emoji
    em = "\u26a0\ufe0f"
    ew, _ = _sz(draw, em, f_em)
    draw.text((_W // 2 - ew // 2, 570), em, font=f_em, fill=_ORANGE)

    # Hook text (two lines)
    _multiline_centered(
        draw,
        ["Dit wist je nog NIET", "over je brein..."],
        f_main,
        start_y=920,
        color=_WHITE,
        spacing=24,
    )

    return np.array(img)


def _build_content() -> np.ndarray:
    img  = Image.new("RGB", (_W, _H), _NAVY)
    draw = ImageDraw.Draw(img)

    f_title = _font(82)
    f_em    = _font(74, emoji=True)
    f_body  = _font(66)
    f_link  = _font(46)

    # Header
    title = "DID YOU KNOW?"
    tw, _ = _sz(draw, title, f_title)
    tx = _W // 2 - tw // 2
    draw.text((tx, 110), title, font=f_title, fill=_TURQ)
    draw.text((tx + tw + 14, 118), "\U0001f9e0", font=f_em, fill=_WHITE)

    # Divider
    draw.line([(_W // 2 - 380, 248), (_W // 2 + 380, 248)], fill=_TURQ, width=3)

    # Body — auto-wrapped, vertically centered
    body = (
        "Stress vermindert je geheugen met 40%. "
        "Je brein heeft dagelijks de juiste "
        "voeding en rust nodig."
    )
    lines = _wrap(draw, body, f_body, max_w=920)
    _, lh = _sz(draw, "Ag", f_body)
    sp = 26
    total_h = len(lines) * (lh + sp) - sp
    start_y = _H // 2 - total_h // 2 - 40
    _multiline_centered(draw, lines, f_body, start_y=start_y, color=_WHITE, spacing=sp)

    # Bottom link
    link = "\U0001f447 Meer tips? Link in bio"
    lw, _ = _sz(draw, link, f_link)
    draw.text((_W // 2 - lw // 2, _H - 110), link, font=f_link, fill=_TURQ)

    return np.array(img)


def _build_cta() -> np.ndarray:
    img  = Image.new("RGB", (_W, _H), _NAVY)
    draw = ImageDraw.Draw(img)

    f_em   = _font(60, emoji=True)
    f_btn  = _font(54)
    f_link = _font(48)

    # Icons row
    icons = "\U0001f44d   \U0001f4be   \U0001f465"
    iw, _ = _sz(draw, icons, f_em)
    draw.text((_W // 2 - iw // 2, 810), icons, font=f_em, fill=_WHITE)

    # Labels row
    labels = "Like        Bewaar        Volg ons"
    lw, _ = _sz(draw, labels, f_btn)
    draw.text((_W // 2 - lw // 2, 920), labels, font=f_btn, fill=_YELLOW)

    # Border box around icons + labels
    bx0, by0, bx1, by1 = 60, 778, _W - 60, 1020
    draw.rectangle([bx0, by0, bx1, by1], outline=_BLUE, width=3)
    draw.rectangle([bx0 - 4, by0 - 4, bx1 + 4, by1 + 4], outline=(0, 80, 180), width=2)

    # Bottom link
    link_text = "\U0001f447 Link in bio"
    llw, _ = _sz(draw, link_text, f_link)
    draw.text((_W // 2 - llw // 2, _H - 130), link_text, font=f_link, fill=_TURQ)

    return np.array(img)


# ── Section timing ─────────────────────────────────────────────────────────────

def _calc_sections(total: float):
    """
    Returns list of section dicts:
      {frame, start, end, dur}
    Timeline accounts for two 0.2s black gaps.
    """
    available = total - 2 * _GAP
    s1_dur = available * 0.20
    s2_dur = available * 0.60
    s3_dur = available * 0.20

    s1_start = 0.0
    s1_end   = s1_start + s1_dur
    s2_start = s1_end + _GAP
    s2_end   = s2_start + s2_dur
    s3_start = s2_end + _GAP
    s3_end   = s3_start + s3_dur   # should equal total

    return [
        {"name": "HOOK",    "start": s1_start, "end": s1_end,   "dur": s1_dur},
        {"name": "CONTENT", "start": s2_start, "end": s2_end,   "dur": s2_dur},
        {"name": "CTA",     "start": s3_start, "end": s3_end,   "dur": s3_dur},
    ]


# ── Alpha calculator ────────────────────────────────────────────────────────────

def _section_alpha(t_local: float, dur: float) -> float:
    """Returns 0..1 opacity for time t_local within a section of length dur."""
    if t_local < _FADE_IN:
        return t_local / _FADE_IN
    if t_local > dur - _FADE_OUT:
        return max(0.0, (dur - t_local) / _FADE_OUT)
    return 1.0


# ── Public API ─────────────────────────────────────────────────────────────────

def create_reel(audio_path: str, output_filename: str = "reel.mp4") -> str:
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(_OUTPUT_DIR, output_filename)

    # Measure audio
    audio = AudioFileClip(audio_path)
    total = audio.duration
    print(f"\n[video_skill] Audio duration : {total:.2f}s")

    # Calculate sections
    sections = _calc_sections(total)
    frames   = [_build_hook(), _build_content(), _build_cta()]
    _BLACK_FRAME = np.zeros((_H, _W, 3), dtype=np.uint8)

    for s in sections:
        print(f"[video_skill] {s['name']:8s}  {s['start']:.2f}s - {s['end']:.2f}s  "
              f"(dur={s['dur']:.2f}s)")
    print()

    def make_frame(t: float) -> np.ndarray:
        for i, sec in enumerate(sections):
            if sec["start"] <= t < sec["end"]:
                t_local = t - sec["start"]
                alpha   = _section_alpha(t_local, sec["dur"])
                if alpha >= 0.9999:
                    return frames[i]
                return (frames[i] * alpha).astype(np.uint8)
        return _BLACK_FRAME   # gap periods

    clip = VideoClip(make_frame, duration=total)
    clip = clip.with_audio(audio)
    clip.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        logger=None,
        ffmpeg_params=["-pix_fmt", "yuv420p"],
    )

    audio.close()
    clip.close()

    size_mb = os.path.getsize(output_path) / 1_000_000
    print(f"[video_skill] Saved: {output_path} ({size_mb:.1f} MB)")
    return output_path


if __name__ == "__main__":
    path = create_reel(
        audio_path="outputs/test_audio_v3.mp3",
        output_filename="test_video_v6.mp4",
    )
    print(f"[video_skill] Done: {path}")
