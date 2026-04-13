import sys, os, json
sys.path.append(os.path.join(os.getcwd(), "src"))

from skills.tts_skill import generate_dutch_audio
from skills.video_skill import THEMES, create_reel

# Test sentences with tags for Zero-Delay Flow
test_fragments = [
    {"sentence": "DIT WIST JE NOG NIET... Over deze routine!", "tag": "hook"},
    {"sentence": "Drink elke ochtend een glas lauw water met citroen.", "tag": "content"},
    {"sentence": "Dit helpt je lichaam om giftstoffen sneller af te voeren.", "tag": "content"},
    {"sentence": "Wat ga jij vandaag doen? Volg ons voor meer!", "tag": "cta"}
]

os.makedirs("outputs", exist_ok=True)

print("--- ZERO-DELAY SYNC TEST START ---")

fragment_data = []
for i, frag in enumerate(test_fragments):
    f_name = f"zero_frag_{i}.mp3"
    # Nova 1.15x speed for energy
    f_path = generate_dutch_audio(frag["sentence"], filename=f_name, voice="nova", speed=1.15)
    fragment_data.append({"sentence": frag["sentence"], "audio": f_path, "tag": frag["tag"]})

# Save fragments.json
with open("outputs/fragments.json", "w", encoding="utf-8") as f:
    json.dump(fragment_data, f, ensure_ascii=False, indent=2)

print("Rendering Zero-Delay Reel...")
v_path = create_reel(brand="glow", output_filename="test_zero_delay.mp4")

print(f"--- TEST COMPLETE: {v_path} ---")
