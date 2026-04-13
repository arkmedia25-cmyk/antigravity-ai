import os
import sys
import json

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.skills.video_skill import _build_hook, _build_content, _build_cta

# Set outputs dir manually if needed
if not os.path.exists("outputs"):
    os.makedirs("outputs")

# Mock timestamp data
mock_ts = [
    {"sentence": "DIT WIST JE NOG NIET...", "start": 0.0, "end": 2.0},
    {"sentence": "Gezonde voeding is essentieel voor je energie.", "start": 2.0, "end": 4.0},
    {"sentence": "Slaap tekort kan je hormonen verstoren.", "start": 4.0, "end": 6.0},
    {"sentence": "Blijf hydrateren gedurende de dag.", "start": 6.0, "end": 8.0},
    {"sentence": "Wat ga jij vandaag doen?", "start": 8.0, "end": 10.0},
]

print("Generating Hook frame...")
hook_path = _build_hook()
print(f"Saved: {hook_path}")

print("Generating Content frame...")
content_path = _build_content(mock_ts)
print(f"Saved: {content_path}")

print("Generating CTA frame...")
cta_path = _build_cta()
print(f"Saved: {cta_path}")
