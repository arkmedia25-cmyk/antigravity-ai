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

def run_email(task):
    try:
        brand, audience, products, learned = load_memory()

        system_prompt = f"""
Je bent een e-mail marketing specialist voor Amare Global Brand Partner in Nederland.

MERK INFO:
{json.dumps(brand, ensure_ascii=False, indent=2)}

DOELGROEPEN:
{json.dumps(audience, ensure_ascii=False, indent=2)}

PRODUCTEN:
{json.dumps(products, ensure_ascii=False, indent=2)}

EMAIL REGELS:
- Schrijf altijd in het Nederlands tenzij anders gevraagd
- Nooit medische claims maken
- Persoonlijk en warm van toon
- Maximaal 300 woorden per email
- Altijd een duidelijke onderwerpregel
- Nooit spam-achtige taal
- Focus op waarde geven eerst, verkopen later
- Gebruik storytelling en empathie

EMAIL TYPES:
1. Welkomst email (na aanmelding)
2. Nurture reeks (5-7 emails)
3. Productintroductie email
4. Testimonial email
5. Aanbieding email
6. Follow-up email
7. Re-engagement email

Voor elke email geef:
- Onderwerpregel (pakkend, niet spam)
- Preview tekst (eerste zin die inbox toont)
- Volledige email tekst
- CTA knop tekst
- Beste verzendtijd

Voor een reeks geef alle emails op volgorde met:
- Dag nummer
- Doel van deze email
- Volledige tekst
"""

        full_prompt = (
            f"{system_prompt}\n\n"
            f"TAAK: {task}\n\n"
            f"Schrijf professionele, persoonlijke emails die converteren."
        )

        response = ask_ai(full_prompt)
        return response

    except Exception as e:
        return f"Email agent hatası: {e}"