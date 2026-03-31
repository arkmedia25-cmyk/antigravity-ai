import sys
import os
sys.path.append(os.getcwd())

import json
from openai import OpenAI
from dotenv import load_dotenv
from src.skills import tts_skill, video_skill

load_dotenv()

SYSTEM_PROMPT = """You are a viral social media strategist for @GlowUpNL. 
Your audience is Dutch women interested in Wellness, Health, and Beauty. 
They value 'Gezelligheid' (coziness) and practical tips.
The tone should be like a wise best friend: warm, direct, and slightly energetic.

IMPORTANT: All text (hook, content, cta, dutch_script) MUST BE IN DUTCH ONLY. NO ENGLISH EVER.
SADECE HOLLANDACA (Nederlands) yazmalısın.

Generate a JSON object with:
1. 'title': A short, punchy title for the video (in Dutch).
2. 'hook': A short attention-grabbing sentence for the entrance (in Dutch, <3s).
3. 'content': 2-3 relatable sentences about a health/wellness tip (in Dutch).
4. 'cta': A clear call-to-action (in Dutch, e.g., Like & Sla Op, Volg @GlowUpNL).
5. 'instagram_caption': An engaging Instagram caption with emojis (in Dutch).
6. 'hashtags': 5-8 strategic Dutch hashtags (Space separated).
7. 'image_prompt': A DALL-E 3 prompt for a WARM, NATURAL background image (in English).
8. 'dutch_script': The exact text to be spoken by AI Nova (IN DUTCH).
"""

USER_PROMPT = "Generate a 'Gezellig' Wellness tip for @GlowUpNL NL audience."

def generate_autonomous_content(topic=None):
    print(f"🤖 Asking GPT-4o for '{topic or 'Gezellig'}' Wellness content...")
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        user_prompt = f"Generate a 'Gezellig' Wellness tip for @GlowUpNL. Topic: {topic or 'Random Wellness Tip'}"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = json.loads(response.choices[0].message.content)
        print("✅ Content Generated!")
        return content
    except Exception as e:
        print(f"❌ Error calling OpenAI: {e}")
        return None

def run_production_line(topic=None, output_name=None):
    # 1. Generate Content
    data = generate_autonomous_content(topic)
    if not data: return None

    # 2. Image Prompt from GPT
    image_prompt = data["image_prompt"]
    print(f"🎨 Visual Plan: {image_prompt}")
    
    # 3. Create Audio Fragments
    print("🎙️ Producing Vocal Elements (Nova 1.15x)...")
    fragments = [
        {"tag": "hook", "text": data["hook"]},
        {"tag": "content", "text": data["content"]},
        {"tag": "cta", "text": data["cta"]}
    ]
    
    for i, frag in enumerate(fragments):
        # We use a unique prefix to avoid collisions if multiple productions run
        import time
        ts = int(time.time())
        filename = f"autonorm_{ts}_frag_{i}_{frag['tag']}.mp3"
        path = tts_skill.generate_dutch_audio(
            text=frag["text"],
            filename=filename,
            voice="nova",
            speed=1.15
        )
        frag["audio"] = path

    # 4. Success - Return the full production package
    return {
        "gpt_data": data,
        "fragments": fragments,
        "image_prompt": image_prompt
    }

if __name__ == "__main__":
    # Local Test for a SINGLE otonom video
    run_production_line()

if __name__ == "__main__":
    run_production_line()
