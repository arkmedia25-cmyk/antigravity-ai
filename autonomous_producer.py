import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# SYSTEM_PROMPT - Dutch Language and Professional Tone
SYSTEM_PROMPT = """
You are the Creative Director for @GlowUpNL (Energetic) and @HolistiGlow (Calm), premium Dutch wellness brands.
Your task is to generate highly engaging, viral-ready video content for Instagram Reels and TikTok.
Language: Dutch (Nederlands). Tone: Professional, Inspiring, Warm, Gezellig.

PROMPT ENGINEERING SECRETS (APPLY TO ALL IMAGE_PROMPTS):
- For HUMANS: Use "Candid photograph shot on iPhone 16 Pro, realistic skin texture, natural pores visible, no retouching, handheld feel, authentic moment".
- AVOID: "Hasselblad", "Editorial", "Fashion Film", "4K", "Masterpiece" - these keywords increase AI look.
- LIGHTING: Prefer "Natural window light", "Soft outdoor backlight", "Golden hour sunset".
- MOVEMENTS: Always specify a camera motion like "Slow dolly-in", "Macro orbit around product", "Tracking shot", "Panning across landscape".
- COLORS: GlowUp = Warm peach/coral/white. HolistiGlow = Sage green/beige/natural wood.

OUTPUT FORMAT MUST BE JSON:
{
  "dutch_script": "The 2-3 sentence tip in Dutch",
  "image_prompt": "Descriptive English prompt applying the SECRETS above",
  "instagram_caption": "Engaging Dutch caption with hashtags",
  "hashtags": "#wellness #glowup #gezellig #nederland",
  "plates": [
    {"text": "Hook line in Dutch", "duration": 3, "tag": "hook"},
    {"text": "Value line in Dutch", "duration": 4, "tag": "content"},
    {"text": "Call to action in Dutch", "duration": 3, "tag": "cta"}
  ]
}
"""

def generate_autonomous_content(topic=None, brand="glow"):
    print(f"🤖 Asking GPT-4o for '@{brand.capitalize()}NL' {topic or ''} content...")
    try:
        # Load Brand-Specific Trends
        trends_context = ""
        trends_path = os.path.join(os.getcwd(), "memory", f"current_trends_{brand}.json")
        if not os.path.exists(trends_path):
             trends_path = os.path.join(os.getcwd(), "memory", "current_trends.json")
             
        if os.path.exists(trends_path):
            with open(trends_path, "r", encoding="utf-8") as f:
                trends_data = json.load(f)
                trends_context = f"\nCURRENT BRAND-SPECIFIC TRENDS: {', '.join(trends_data['trends'])}\n"

        brand_persona = "Energetic, coral/peach colors, fitness results" if brand == "glow" else "Calm, sage/beige colors, holistic health"

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        user_prompt = (
            f"Generate a Wellness tip for @{brand.capitalize()}NL. "
            f"Persona: {brand_persona}. Topic: {topic or 'Trending Wellness'}. {trends_context}"
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.replace("@GlowUpNL", f"@{brand.capitalize()}NL")},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ Content generation error: {e}")
        return None

def run_production_line(topic=None, brand="glow"):
    """Complete production for a specific brand."""
    data = generate_autonomous_content(topic, brand=brand)
    if not data:
        return None

    # Prepare fragments for video_skill
    fragments = []
    for plate in data.get("plates", []):
        fragments.append({
            "text": plate["text"],
            "duration": plate["duration"],
            "tag": plate.get("tag", "content")
        })
    
    return {
        "fragments": fragments,
        "image_prompt": data["image_prompt"],
        "gpt_data": data
    }

if __name__ == "__main__":
    # Test run
    print("🚀 Starting test production...")
    result = run_production_line()
    if result:
        print(f"✅ Production Pack Ready: {result['gpt_data']['dutch_script']}")
