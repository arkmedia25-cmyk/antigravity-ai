import os
import subprocess
from pathlib import Path

# Ensure required dirs exist
audio_dir = Path('test_assets/audio')
bg_dir = Path('test_assets/backgrounds')
audio_dir.mkdir(parents=True, exist_ok=True)
bg_dir.mkdir(parents=True, exist_ok=True)

# 1️⃣ Create a dummy silent audio (1 sec) if none exists
audio_file = audio_dir / 'dummy.wav'
if not audio_file.exists():
    subprocess.run([
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-t', '1', str(audio_file)
    ], check=True, capture_output=True)

# Convert to mp3 (ffmpeg will handle conversion)
audio_mp3 = audio_dir / 'dummy.mp3'
if not audio_mp3.exists():
    subprocess.run([
        'ffmpeg', '-y', '-i', str(audio_file), str(audio_mp3)
    ], check=True, capture_output=True)

# 2️⃣ Create a dummy background video (5 sec solid color)
bg_video = bg_dir / 'bg_binauralmind.mp4'
if not bg_video.exists():
    subprocess.run([
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=0x001122:s=1920x1080:d=5',
        '-c:v', 'libx264', '-t', '5', str(bg_video)
    ], check=True, capture_output=True)

# 3️⃣ Run the pipeline (build both long and short videos)
import video_build
results = video_build.build_montage_with_shorts(
    audio_dir=audio_dir,
    slug='binauralmind',
    bg_dir=bg_dir,
    repeat_factor=1,
    group_size=10,
)

print('Long videos:')
for p in results['long']:
    print('  ', p)
print('Short videos:')
for p in results['short']:
    print('  ', p)
print('Montages:')
for p in results['montage']:
    print('  ', p)
