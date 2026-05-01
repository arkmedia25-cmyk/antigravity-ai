import subprocess
import json
import hashlib
from pathlib import Path

OUTPUT_VIDEO = Path("output/final_video.mp4")


def _get_duration(path: Path) -> float:
    import time
    for _ in range(3):
        if not path.exists():
            time.sleep(1)
            continue
        try:
            result = subprocess.run([
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(path)
            ], capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except subprocess.CalledProcessError:
            time.sleep(1)
    raise FileNotFoundError(f"Could not probe duration for {path}")


def _pick_background(slug: str, bg_dir: Path) -> Path:
    """Select niche-specific background bg_<slug>.mp4 if exists; otherwise fallback to background_1084p.mp4 or first MP4 file."""
    niche_bg = bg_dir / f"bg_{slug}.mp4"
    if niche_bg.exists():
        return niche_bg
    fallback = bg_dir / "background_1080p.mp4"
    if fallback.exists():
        return fallback
    backgrounds = list(bg_dir.glob("*.mp4"))
    if not backgrounds:
        raise FileNotFoundError(f"Backgrounds not found: {bg_dir}")
    return backgrounds[0]


def run(audio_path: Path, slug: str = "", bg_dir: Path | None = None) -> Path:
    """Background MP4 + audio → YouTube video (1920x1080)."""
    resolved_bg_dir = bg_dir or Path("backgrounds")
    bg = _pick_background(slug, resolved_bg_dir)
    audio_dur = _get_duration(audio_path)

    OUTPUT_VIDEO.parent.mkdir(parents=True, exist_ok=True)

    # Compute a cache key based on background, audio and duration
    import hashlib
    cache_dir = Path("output/cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    hash_input = f"{bg.resolve()}|{audio_path.resolve()}|{audio_dur}".encode()
    cache_key = hashlib.sha256(hash_input).hexdigest()[:12]
    cached_video = OUTPUT_VIDEO.parent / f"video_{cache_key}.mp4"
    # Only trust the cache if the file is larger than 1MB (prevents using 0-byte broken files from Ctrl+C)
    if cached_video.exists() and cached_video.stat().st_size > 1_000_000:
        print(f"[video] Cache hit: {cached_video}")
        return cached_video
    elif cached_video.exists():
        cached_video.unlink() # delete broken cache
    filter_chain = (
        "[0:v]scale=1920:1080[bg];"
        "[1:a]showwaves=s=1920x250:mode=cline:colors=0x00FFFF@0.8|0xFF00FF@0.5[wave];"
        "[bg][wave]overlay=0:H-250[outv]"
    )
    # If not cached, run ffmpeg to generate new video
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", str(bg),
        "-i", str(audio_path),
        "-filter_complex", filter_chain,
        "-map", "[outv]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(audio_dur),
        "-shortest",
        str(cached_video)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"[video] Created: {cached_video}")
    return cached_video

# ---------------------------------------------------------------------------
# Helper: Text‑to‑Speech using edge-tts (dynamic and energetic voice)
# ---------------------------------------------------------------------------
def synthesize_speech(text: str, out_path: Path) -> None:
    """Generate an English young‑female voice narration.
    Uses edge-tts for a more energetic and dynamic voice.
    Falls back to a silent placeholder if edge-tts fails or is not available.
    """
    try:
        # en-US-AriaNeural or en-US-JennyNeural are good dynamic female voices
        subprocess.run([
            "edge-tts", "--voice", "en-US-AriaNeural", "--text", text, "--write-media", str(out_path)
        ], check=True, capture_output=True)
    except Exception as e:
        print(f"[tts] edge-tts failed ({e}), creating a silent placeholder.")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-t", "1", "-q:a", "9", "-acodec", "aac",
            str(out_path)
        ], check=True, capture_output=True)

# ---------------------------------------------------------------------------
# Helper: Detect the most energetic segment (hook) of an audio track
# ---------------------------------------------------------------------------
def _detect_hook(audio_path: Path, window_sec: int = 5) -> float:
    """Return start time (seconds) of the highest-energy window using astats filter."""
    try:
        cmd = [
            "ffprobe", "-hide_banner", "-loglevel", "error",
            "-f", "lavfi",
            "-i", f"amovie={audio_path.as_posix()},astats=metadata=1:reset=1",
            "-show_entries", "frame_tags=lavfi.astats.Overall.RMS_level:frame=pkt_pts_time",
            "-of", "json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout or "{}")
        frames = data.get("frames", [])
        if not frames:
            return 0.0
            
        frame_data = []
        for f in frames:
            val = f.get("tags", {}).get("lavfi.astats.Overall.RMS_level", "-91")
            pts_time = f.get("pkt_pts_time", "0.0")
            try:
                frame_data.append((float(pts_time), float(val)))
            except ValueError:
                pass
                
        if not frame_data:
            return 0.0

        best_start = 0.0
        best_sum = float("-inf")
        
        # O(N^2) sliding window over variable frame rate is okay since N is small
        for i in range(len(frame_data)):
            start_time = frame_data[i][0]
            end_time = start_time + window_sec
            
            # Sum RMS for frames within the window
            current_sum = 0
            count = 0
            for j in range(i, len(frame_data)):
                if frame_data[j][0] > end_time:
                    break
                current_sum += frame_data[j][1]
                count += 1
                
            if count > 0 and current_sum > best_sum:
                best_sum = current_sum
                best_start = start_time
                
        # Cap the start time so it leaves at least window_sec at the end if possible
        duration = frame_data[-1][0]
        if best_start > max(0, duration - window_sec):
            best_start = max(0, duration - window_sec)
            
        return best_start
    except Exception as e:
        print(f"[hook] detection failed: {e}, using start=0")
        return 0.0

# make_vertical is now handled by thumbnail_make.py

# ---------------------------------------------------------------------------
# Core: Create short (YouTube Shorts) from a long video
# ---------------------------------------------------------------------------
def create_short(
    long_video: Path,
    slug: str,
    start: float | None = None,
    max_len: int = 59,
) -> Path:
    """Generate a vertical short (<=59 s) with voice‑over, waveform, CTA.
    - Detects hook start if not supplied.
    - Adds a young‑female English TTS narration.
    - Overlays waveform visualisation.
    - Adds a CTA text overlay for the full video.
    - Caches result under output/shorts/<slug>_<hash>.mp4.
    """
    cache_dir = Path("output/shorts")
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Determine hook start time
    if start is None:
        # Extract temporary audio
        tmp_audio = cache_dir / f"{slug}_tmp.wav"
        subprocess.run([
            "ffmpeg", "-y", "-i", str(long_video), "-vn", "-ac", "1", str(tmp_audio)
        ], check=True, capture_output=True)
        start = _detect_hook(tmp_audio)
        tmp_audio.unlink(missing_ok=True)

    # Cache key based on video path + start + length
    print("START IS:", start)
    h = hashlib.sha256(f"{long_video}|{start}|{max_len}".encode()).hexdigest()[:12]
    out_path = cache_dir / f"{slug}_{h}.mp4"
    if out_path.exists():
        print(f"[short] Cache hit: {out_path}")
        return out_path

    # 1 Cut & resize to portrait (720×1280)
    short_tmp = cache_dir / f"{slug}_{h}_raw.mp4"
    cmd1 = [
        "ffmpeg", "-y",
        "-ss", str(start), "-t", str(max_len),
        "-i", str(long_video),
        "-vf", "scale=720:1280,setsar=1",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        str(short_tmp)
    ]
    print("RUNNING FFMPEG CMD:", " ".join(cmd1))
    r = subprocess.run(cmd1, check=True, capture_output=True)
    print("FFMPEG STDOUT:", r.stdout.decode('utf-8'))
    print("FFMPEG STDERR:", r.stderr.decode('utf-8'))

    # 2 Generate voice‑over (English young female)
    voice_text = (
        f"{slug.replace('_', ' ').title()} – enjoy {max_len} seconds of relaxing binaural beats. "
        "For the full experience, subscribe and like the channel."
    )
    voice_path = cache_dir / f"{slug}_{h}_voice.mp3"
    synthesize_speech(voice_text, voice_path)

    # 3 Create waveform overlay image (720×120)
    waveform_png = cache_dir / f"{slug}_{h}_wave.png"
    # Added -vn to ignore video stream for faster audio processing
    # Using lowercase 'white' and aformat for better compatibility
    # Generate waveform image from the audio of the short video.
    # Removed the '-update' flag and aformat conversion for broader FFmpeg compatibility.
    subprocess.run([
        "ffmpeg", "-y", "-vn",
        "-i", str(short_tmp),
        "-filter_complex", "[0:a]showwavespic=s=720x120:colors=white",
        "-frames:v", "1",
        str(waveform_png)
    ], check=True, capture_output=True)

    # 4 Assemble final short with audio mix and overlays
    final_tmp = cache_dir / f"{slug}_{h}_final.mp4"
    # Filter chain: overlay waveform at bottom, draw CTA text at end
    delay_ms = max(0, max_len - 10) * 1000
    text_start = max_len - 6
    text_end = max_len - 1
    filter_chain = (
        "[0:v][2:v]overlay=0:H-120[vidw];"
        f"[vidw]drawtext=text='Subscribe & Like!':fontcolor=white@0.9:fontsize=48:x=(w-text_w)/2:y=h-70:enable='between(t,{text_start},{text_end})'[outv];"
        f"[1:a]adelay={delay_ms}|{delay_ms}[delayed_voice];"
        "[0:a][delayed_voice]amix=inputs=2:duration=first:dropout_transition=2[outa]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", str(short_tmp),          # 0: video (with background music)
        "-i", str(voice_path),          # 1: voice audio
        "-i", str(waveform_png),        # 2: waveform image
        "-filter_complex", filter_chain,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        str(final_tmp),
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    # Rename to final output path
    final_tmp.rename(out_path)
    # Cleanup temporary files
    short_tmp.unlink(missing_ok=True)
    voice_path.unlink(missing_ok=True)
    waveform_png.unlink(missing_ok=True)

    print(f"[short] Created: {out_path}")
    return out_path

# ---------------------------------------------------------------------------
# Updated montage builder – now also creates Shorts
# ---------------------------------------------------------------------------
def build_montage_with_shorts(
    audio_dir: Path,
    slug: str,
    bg_dir: Path | None = None,
    repeat_factor: int = 1,
    group_size: int = 10,
) -> dict:
    """Generate long videos, Shorts, and 10‑video montages.
    Returns dict with keys: 'long', 'short', 'montage'.
    """
    long_videos = []
    short_videos = []
    audio_files = sorted(audio_dir.glob("*.mp3"))
    bg_path = _pick_background(slug, bg_dir or Path("backgrounds"))

    for audio in audio_files:
        # Long video (existing pipeline)
        long = run(audio, slug=slug, bg_dir=bg_dir)
        long_videos.append(long)
        # Short video (new pipeline)
        short = create_short(long, slug=slug)
        short_videos.append(short)

    # Optional repeat for long videos (same as before)
    if repeat_factor > 1:
        long_videos = long_videos * repeat_factor
        short_videos = short_videos * repeat_factor

    # Build montages for long videos (10‑block concat)
    montage_paths = []
    tmp_dir = Path("tmp")
    tmp_dir.mkdir(exist_ok=True)
    for i in range(0, len(long_videos), group_size):
        block = long_videos[i : i + group_size]
        list_file = tmp_dir / f"list_{i // group_size}.txt"
        list_file.write_text("\n".join([f"file '{p.resolve()}'" for p in block]))
        out_path = Path("output") / f"montage_{i // group_size}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i",
            str(list_file), "-c", "copy", str(out_path)
        ], check=True, capture_output=True)
        montage_paths.append(out_path)

    return {"long": long_videos, "short": short_videos, "montage": montage_paths}

# ---------------------------------------------------------------------------
# Hashtag helper (static list – can be expanded later)
# ---------------------------------------------------------------------------
def generate_hashtags() -> str:
    tags = [
        "#BinauralBeats", "#RelaxMusic", "#StudyMusic", "#SleepSounds",
        "#Mindfulness", "#Meditation", "#Ambient",
        "#Shorts", "#YouTubeShorts"
    ]
    return " ".join(tags)
