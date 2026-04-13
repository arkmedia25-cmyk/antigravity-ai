#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv(".env")

from wellness_producer import compose_reel

avatar = "C:/Users/mus-1/AppData/Local/Temp/drpriya_1775734174.mp4"
vis_dir = "C:/Users/mus-1/AppData/Local/Temp/visuals"

scenes = [
    {"text": "73 procent van de Nederlanders ervaart dagelijks werkstress.", "image_path": f"{vis_dir}/scene_0.jpg"},
    {"text": "Je lichaam maakt dan tot twee keer zoveel cortisol aan als normaal.", "image_path": f"{vis_dir}/scene_1.jpg"},
    {"text": "Dit verhoogt je risico op burn-out met 60 procent.", "image_path": f"{vis_dir}/scene_2.jpg"},
    {"text": "Maar drie minuten ademhaling per dag reset je zenuwstelsel volledig.", "image_path": f"{vis_dir}/scene_3.jpg"},
    {"text": "Sla dit op en probeer het vanavond.", "image_path": f"{vis_dir}/scene_4.jpg"},
]

result = compose_reel(avatar, scenes, "Werkstress: De Stille Epidemie")
print(f"\nOUTPUT: {result}")
