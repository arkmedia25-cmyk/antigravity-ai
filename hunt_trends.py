import os
import json
import datetime
from src.skills.ai_client import ask_ai

# Bu betik her sabah calistirilabilir (veya manuel)
# Hollanda wellness pazarini tarayip trendleri gunceller.

def hunt_trends():
    print("🔍 Hunting for latest Dutch Wellness trends (2026 Context)...")
    
    # In a real scenario, we use search_web tool, but here as a script 
    # we ask GPT to summarize current knowledge of trends for the brand.
    prompt = (
        "Analyze the current 2026 Dutch Wellness and Health market. "
        "What are the top 10 viral buzzwords or themes on Instagram/TikTok for Dutch women? "
        "Provide a JSON list with 'trends' (array of strings) and 'last_update' (YYYY-MM-DD)."
    )
    
    try:
        response = ask_ai(prompt, is_json=True)
        if response:
            os.makedirs("memory", exist_ok=True)
            with open("memory/current_trends.json", "w", encoding="utf-8") as f:
                json.dump(response, f, ensure_ascii=False, indent=2)
            print("✅ Market trends updated in memory/current_trends.json")
            return True
    except Exception as e:
        print(f"❌ Trend hunt failed: {e}")
    return False

if __name__ == "__main__":
    hunt_trends()
