import json
import re
from src.skills.ai_client import ask_ai

def simulate_dirty_json():
    # Example that would trigger "Extra data" error
    # It has valid JSON but also extra text at the end.
    dirty_text = """{
  "title": "Healthy Smoothie",
  "hook": "Wait until you see this!",
  "content": "Banana, berries, and some spinach.",
  "cta": "Check the link in bio!"
}
Extra data: line 23 column 1 (char 599)"""

    print("--- SIMULATING DIRTY JSON RESPONSE ---")
    print(dirty_text)
    
    # We monkey-patch ask_ai for this specific test case
    # or better, just test the internal logic.
    
    # Internal logic simulation
    clean_text = dirty_text.strip()
    try:
        data = json.loads(clean_text)
        print("Success: Straight JSON parse.")
    except json.JSONDecodeError as e:
        print(f"Caught expected JSON error: {e}")
        if "Extra data" in str(e):
             # Extraction logic from ask_ai
             match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
             if match:
                  content = match.group(1)
                  print(f"Regex found: {content[:100]}...")
                  parsed = False
                  for i in range(len(content), 0, -1):
                      if content[i-1] == '}':
                          try:
                              data = json.loads(content[:i])
                              print(f"Recovered JSON at index {i}: {data['title']}")
                              parsed = True
                              break
                          except:
                              continue
                  if not parsed:
                      print("FAILURE: Could not recover JSON.")
             else:
                  print("FAILURE: Regex did not match.")

if __name__ == "__main__":
    simulate_dirty_json()
