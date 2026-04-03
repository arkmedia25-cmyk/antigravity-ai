import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from autonomous_producer import run_production_line
from src.skills.video_skill import create_reel
from src.skills.ai_client import generate_image

def test_luna_flow():
    print("🚀 Testing Luna Content Pipeline...")
    brand = "glow"
    topic = "Morning energy and skincare routine"
    
    # 1. Run Production Line (Generates scripts/fragments)
    print("--- [1/3] Generating Scripts ---")
    pack = run_production_line(topic=topic, brand=brand)
    print(f"Fragments generated: {len(pack.get('fragments', []))}")
    print(f"Image Prompt: {pack.get('image_prompt', 'N/A')}")
    
    # 2. Generate Background Image (DALL-E 3)
    print("--- [2/3] Generating Background Image ---")
    bg_path = generate_image(pack['image_prompt'])
    if not bg_path:
        print("❌ Image generation failed.")
        return
    print(f"Background saved to: {bg_path}")
    
    # 3. Create Reel (FFmpeg with Montserrat Typography)
    print("--- [3/3] Rendering Video ---")
    output_filename = f"test_luna_{int(time.time())}.mp4"
    video_path = create_reel(
        fragments=pack["fragments"],
        image_path=bg_path,
        output_filename=output_filename,
        brand=brand
    )
    
    if video_path and os.path.exists(video_path):
        print(f"✅ SUCCESS! Luna Video rendered at: {video_path}")
    else:
        print("❌ Video rendering failed.")

if __name__ == "__main__":
    test_luna_flow()
