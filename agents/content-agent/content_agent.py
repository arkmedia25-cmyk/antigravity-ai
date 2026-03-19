import os
import json
from ai_client import ask_ai

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_memory():
    current_dir = os.path.dirname(__file__)
    memory_dir = os.path.abspath(os.path.join(current_dir, "../../memory"))
    brand = load_json(os.path.join(memory_dir, "brand.json"))
    audience = load_json(os.path.join(memory_dir, "audience.json"))
    products = load_json(os.path.join(memory_dir, "products.json"))
    learned = load_json(os.path.join(memory_dir, "learned.json"))
    return brand, audience, products, learned

def run_content(task):
    try:
        brand, audience, products, learned = load_memory()

        system_prompt = f"""
Je bent een social media content specialist voor Amare Global Brand Partner in Nederland.

MERK INFO:
{json.dumps(brand, ensure_ascii=False, indent=2)}

DOELGROEPEN:
{json.dumps(audience, ensure_ascii=False, indent=2)}

PRODUCTEN:
{json.dumps(products, ensure_ascii=False, indent=2)}

GOEDGEKEURDE HOOKS:
{learned.get('approved_hooks', [])}

AFGEWEZEN STIJLEN:
{learned.get('rejected_styles', [])}

CONTENT REGELS:
- Schrijf altijd in het Nederlands tenzij anders gevraagd
- Nooit medische claims maken
- Altijd authentiek en persoonlijk
- Focus op lifestyle, energie, moederschap
- Gebruik storytelling
- Altijd een zachte CTA

CONTENT TYPES:
1. Instagram Reels script (60-90 seconden)
2. Instagram carousel (5-7 slides)
3. Instagram story serie (5 stories)
4. Caption voor foto post
5. LinkedIn artikel
6. Email nieuwsbrief

Voor elk content stuk geef:
- De volledige tekst
- Hashtags (15-20 stuks)
- Beste tijdstip om te posten
- Thumbnail/cover tip
- CTA suggestie
"""

        full_prompt = (
            f"{system_prompt}\n\n"
            f"TAAK: {task}\n\n"
            f"Maak professionele, engaging content die past bij de doelgroep."
        )

        response = ask_ai(full_prompt)
        return response

    except Exception as e:
        return f"Content agent hatası: {e}"