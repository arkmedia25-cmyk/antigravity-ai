import sys, os, json
sys.path.append(os.path.join(os.getcwd(), "src"))

from skills.video_skill import THEMES, _build_hook, _build_sentence_frame, _build_cta

theme = THEMES["glow"]

# Test cases for character mapping: emojis, bullets, numbers should all become '* '
test_sentences = [
    "🌿 1. Drink elke ochtend een glas lauw water.", 
    "• Dit helpt je lichaam om giftstoffen af te voeren.",
    "- Probeer ook 10 minuten te wandelen.",
    "✨ 3. Je zult merken dat je energie stijgt!"
]

os.makedirs("outputs", exist_ok=True)

print("--- FINAL VISUAL VERIFICATION START ---")

print("Generating frames...")
for i, s in enumerate(test_sentences):
    p = _build_sentence_frame(s, theme, i)
    print(f"Frame {i} saved ({s[:20]}...): {p}")

print("--- FINAL VISUAL VERIFICATION END ---")
