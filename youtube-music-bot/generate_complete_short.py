import sys
from pathlib import Path

# Add current dir to sys.path
sys.path.append(str(Path.cwd()))

import video_build
import thumbnail_make

def main():
    # 1. Config
    slug = "binauralmind"
    genre = {
        "slug": slug,
        "title": "Deep Sleep Binaural Beats - {duration} Hours Study Music"
    }
    duration_min = 60 # placeholder for thumbnail text
    
    # Paths to real test assets
    audio_path = Path("test_assets/audio/dummy60.mp3")
    bg_dir = Path("test_assets/backgrounds")
    
    print(f"--- Starting Complete Short Generation for {slug} ---")
    
    # 2. Generate Vertical Thumbnail
    print("Generating vertical thumbnail...")
    v_thumb = thumbnail_make.make_vertical(genre, duration_min)
    print(f"Thumbnail created: {v_thumb}")
    
    # 3. Generate Short Video
    # We first need a 'long' video as base, but for test we can just use the audio directly if we want.
    # However, create_short expects a long_video path to cut from.
    # So we'll build a long video first (cached if exists).
    print("Ensuring long video exists (cached)...")
    long_video = video_build.run(audio_path, slug=slug, bg_dir=bg_dir)
    
    print("Generating short video with edge-tts voiceover...")
    short_video = video_build.create_short(long_video, slug=slug)
    
    print(f"\n--- SUCCESS ---")
    print(f"Vertical Thumbnail: {v_thumb}")
    print(f"Short Video: {short_video}")
    print(f"Voiceover used: AriaNeural (Edge-TTS)")
    print(f"Background: {video_build._pick_background(slug, bg_dir)}")

if __name__ == "__main__":
    main()
