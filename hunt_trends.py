import os
import json
import datetime

# Bu betik her marka icin pazar analizi yapar.
# Hollanda wellness pazarini tarayip markaya ozel trendleri gunceller.

def hunt_trends(brand="glow"):
    print(f"🔍 Hunting for latest Dutch Wellness trends for @{brand.capitalize()}NL (2026 Context)...")
    
    brand_context = "Energetic, fitness, and result-oriented" if brand == "glow" else "Calm, holistic, and mindfulness-oriented"

    prompt = (
        f"Analyze the current 2026 Dutch Wellness and Health market for a brand with this persona: {brand_context}.\n"
        "What are the top 10 viral buzzwords or themes on Instagram/TikTok for Dutch women in this specific niche?\n"
        "Provide a JSON list with 'trends' (array of strings) and 'last_update' (YYYY-MM-DD)."
    )
    
    try:
        from src.skills.ai_client import ask_ai
        response = ask_ai(prompt, is_json=True)
        if response:
            os.makedirs("memory", exist_ok=True)
            # Store brand-specific trends
            filename = f"current_trends_{brand}.json"
            trends_path = os.path.join("memory", filename)
            with open(trends_path, "w", encoding="utf-8") as f:
                json.dump(response, f, ensure_ascii=False, indent=2)
            
            # Also update the generic one for fallback
            with open("memory/current_trends.json", "w", encoding="utf-8") as f:
                json.dump(response, f, ensure_ascii=False, indent=2)

            print(f"✅ Market trends updated in {trends_path}")
            return True
    except Exception as e:
        print(f"❌ Trend hunt failed: {e}")
    return False

if __name__ == "__main__":
    hunt_trends()
