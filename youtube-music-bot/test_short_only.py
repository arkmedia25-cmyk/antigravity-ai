import os
import subprocess
from pathlib import Path
import video_build

def main():
    audio_dir = Path('test_assets/audio')
    bg_dir = Path('test_assets/backgrounds')
    audio_dir.mkdir(parents=True, exist_ok=True)
    bg_dir.mkdir(parents=True, exist_ok=True)

    # 1. 60 sec dummy audio
    audio_file = audio_dir / 'dummy60.wav'
    if not audio_file.exists():
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=60',
            '-c:a', 'pcm_s16le', str(audio_file)
        ], check=True, capture_output=True)

    # Convert to mp3
    audio_mp3 = audio_dir / 'dummy60.mp3'
    if not audio_mp3.exists():
        subprocess.run([
            'ffmpeg', '-y', '-i', str(audio_file), str(audio_mp3)
        ], check=True, capture_output=True)

    # 2. 60 sec dummy background
    bg_video = bg_dir / 'bg_binauralmind.mp4'
    if not bg_video.exists():
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=0x001122:s=1920x1080:d=60',
            '-c:v', 'libx264', '-t', '60', str(bg_video)
        ], check=True, capture_output=True)

    print("Generating long video...")
    long_video = video_build.run(audio_path=audio_mp3, slug='binauralmind', bg_dir=bg_dir)

    print("Generating short video...")
    short_video = video_build.create_short(long_video=long_video, slug='binauralmind')

    print(f"\\n--- TEST SUCCESS ---\\nShort video is ready at: {short_video}\\n")

if __name__ == '__main__':
    main()
