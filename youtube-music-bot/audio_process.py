import subprocess
from pathlib import Path

OUTPUT_DIR = Path("output/audio")
FINAL_AUDIO = Path("output/final.mp3")


def normalize(path: Path) -> Path:
    out = path.with_suffix(".norm.mp3")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(path),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        str(out)
    ], check=True, capture_output=True)
    return out


def concat_with_crossfade(tracks: list[Path], crossfade_sec: int = 3) -> Path:
    """Parçaları crossfade ile birleştir, tek MP3 üret."""
    normalized = [normalize(t) for t in tracks]
    FINAL_AUDIO.parent.mkdir(parents=True, exist_ok=True)

    # Tek parça: filter_complex gereksiz, direkt kopyala
    if len(normalized) == 1:
        import shutil
        shutil.copy(normalized[0], FINAL_AUDIO)
        print(f"[audio] Tek parça kopyalandı: {FINAL_AUDIO}")
        return FINAL_AUDIO

    inputs = []
    for t in normalized:
        inputs += ["-i", str(t)]

    # Zincir crossfade filtresi
    filter_parts = []
    prev = "0:a"
    for i in range(1, len(normalized)):
        label = f"cf{i}"
        filter_parts.append(
            f"[{prev}][{i}:a]acrossfade=d={crossfade_sec}:c1=tri:c2=tri[{label}]"
        )
        prev = label

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", ";".join(filter_parts),
        "-map", f"[{prev}]",
        "-b:a", "192k",
        str(FINAL_AUDIO)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"[audio] Birleştirildi: {FINAL_AUDIO}")
    return FINAL_AUDIO


def run(track_paths: list[Path]) -> Path:
    print(f"[audio] {len(track_paths)} parça işleniyor...")
    return concat_with_crossfade(track_paths)
