import os
import json
from src.skills.ai_client import generate_image

# Bu beceri, Instagram feed icin yuksek kaliteli kare postlar uretir.

def create_static_post(brand="glow", topic="wellness", prompt_override=None):
    """Kare (1:1) formatta statik gorsel post uretir."""
    print(f"🎨 Creating static post for @{brand.capitalize()}NL | Topic: {topic}")
    
    brand_style = (
        "Energetic, bright coral and peach tones, morning light, active wellness" 
        if brand == "glow" else 
        "Calm beige and sage green tones, soft afternoon light, mindfulness and zen"
    )

    final_prompt = prompt_override or f"A high-end, aesthetic square 1:1 Instagram post for @{brand.capitalize()}NL. {topic}. {brand_style}, professional photography style, minimal and clean."
    
    try:
        # We use the generate_image from ai_client (DALL-E 3)
        image_path = generate_image(final_prompt + " (Ensure Square 1:1 aspect ratio)")
        if image_path:
            print(f"✅ Static post generated: {image_path}")
            return image_path
    except Exception as e:
        print(f"❌ Static post generation failed: {e}")
    return None
