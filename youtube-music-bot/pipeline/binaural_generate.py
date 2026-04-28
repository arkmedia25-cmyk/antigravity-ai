"""
Binaural beats generator — mathematically generated with numpy.
Left and right ear receive different frequencies; the brain perceives the difference as a beat.

Frequency table:
  Delta  1-4 Hz  -> deep sleep
  Theta  4-8 Hz  -> meditation, dreaming
  Alpha  8-13 Hz -> focus, relaxation
  Beta  13-30 Hz -> energy, concentration
  Gamma 30-50 Hz -> creativity, peak awareness
"""
import sys
import numpy as np
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = Path("output/audio")
SAMPLE_RATE = 44100
BASE_FREQ = 200  # Left ear base frequency (Hz)

PRESETS = {
    "delta-sleep":       {"beat_hz": 2,  "label": "Delta 2Hz — Deep Sleep"},
    "theta-meditation":  {"beat_hz": 6,  "label": "Theta 6Hz — Meditation"},
    "alpha-focus":       {"beat_hz": 10, "label": "Alpha 10Hz — Focus"},
    "beta-energy":       {"beat_hz": 20, "label": "Beta 20Hz — Energy"},
    "gamma-creativity":  {"beat_hz": 40, "label": "Gamma 40Hz — Creativity"},
}


def generate(slug: str, duration_sec: int, volume: float = 0.35) -> Path:
    """
    Generate binaural beat .wav in chunks (low RAM usage).
    volume: 0.0-1.0, 0.35 is ideal for mixing with ambient music.
    """
    import wave

    preset = PRESETS.get(slug, {"beat_hz": 10, "label": "Alpha 10Hz"})
    beat_hz = preset["beat_hz"]

    print(f"[binaural] {preset['label']} | {duration_sec}s | base={BASE_FREQ}Hz beat={beat_hz}Hz")

    total_samples = int(SAMPLE_RATE * duration_sec)
    fade_sec = min(60, duration_sec // 6)
    fade_len = int(fade_sec * SAMPLE_RATE)
    chunk_size = SAMPLE_RATE * 10  # 10-second chunks

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dest = OUTPUT_DIR / f"binaural_{slug}.wav"

    with wave.open(str(dest), "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)

        written = 0
        while written < total_samples:
            n = min(chunk_size, total_samples - written)
            t = (np.arange(written, written + n, dtype=np.float32)) / SAMPLE_RATE

            left  = np.sin(2 * np.pi * BASE_FREQ * t, dtype=np.float32)
            right = np.sin(2 * np.pi * (BASE_FREQ + beat_hz) * t, dtype=np.float32)

            # Fade in
            if written < fade_len:
                fi_end = min(n, fade_len - written)
                ramp = np.linspace(written / fade_len, min((written + fi_end) / fade_len, 1.0), fi_end, dtype=np.float32)
                left[:fi_end]  *= ramp
                right[:fi_end] *= ramp

            # Fade out
            fade_start = total_samples - fade_len
            if written + n > fade_start:
                fo_start = max(0, fade_start - written)
                fo_len   = n - fo_start
                pos_start = written + fo_start - fade_start
                ramp = np.linspace(1.0 - pos_start / fade_len, 1.0 - (pos_start + fo_len) / fade_len, fo_len, dtype=np.float32)
                left[fo_start:]  *= ramp
                right[fo_start:] *= ramp

            stereo = (np.stack([left * volume, right * volume], axis=1) * 32767).astype(np.int16)
            wf.writeframes(stereo.tobytes())
            written += n

    print(f"[binaural] Generated: {dest} ({dest.stat().st_size // 1_048_576} MB)")
    return dest


def mix_with_ambient(binaural_path: Path, ambient_path: Path, out_path: Path) -> Path:
    """
    Mix binaural .wav + ambient .mp3 -> final .mp3.
    Binaural is the base layer, ambient sits on top.
    """
    import subprocess

    cmd = [
        "ffmpeg", "-y",
        "-i", str(binaural_path),
        "-i", str(ambient_path),
        "-filter_complex",
        "[0:a]volume=0.4[bin];[1:a]volume=0.7[amb];[bin][amb]amix=inputs=2:duration=longest[out]",
        "-map", "[out]",
        "-b:a", "192k",
        str(out_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"[binaural] Mix complete: {out_path}")
    return out_path
