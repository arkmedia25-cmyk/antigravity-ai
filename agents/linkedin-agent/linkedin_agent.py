import os
import json
from ai_client import ask_ai
 
def load_json(filepath):
    """Laadt JSON bestand"""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
 
def load_memory():
    """Laadt memory bestanden"""
    current_dir = os.path.dirname(__file__)
    memory_dir = os.path.abspath(os.path.join(current_dir, "../../memory"))
 
    # Als memory map niet bestaat, probeer alternatief pad
    if not os.path.exists(memory_dir):
        memory_dir = r"C:\Users\mus-1\OneDrive\Bureaublad\Antigravity\memory"
 
    brand = load_json(os.path.join(memory_dir, "brand.json"))
    audience = load_json(os.path.join(memory_dir, "audience.json"))
    products = load_json(os.path.join(memory_dir, "products.json"))
 
    return brand, audience, products
 
def run_linkedin(task):
    """Voert LinkedIn bericht generatie uit"""
    try:
        brand, audience, products = load_memory()
 
        system_prompt = f"""
Je bent een LinkedIn specialist voor Amare Global Brand Partner in Nederland.
 
MERK INFO:
{json.dumps(brand, ensure_ascii=False, indent=2)}
 
DOELGROEPEN:
{json.dumps(audience, ensure_ascii=False, indent=2)}
 
PRODUCTEN:
{json.dumps(products, ensure_ascii=False, indent=2)}
 
LINKEDIN REGELS:
- Schrijf altijd in het Nederlands tenzij anders gevraagd
- Nooit agressieve verkooptaal
- Altijd persoonlijk en warm
- Focus op waarde geven, niet verkopen
- Maximum 300 woorden per bericht
- Gebruik geen MLM taal
- Altijd een duidelijke maar zachte CTA
 
BERICHTTYPEN:
1. Connectieverzoek (max 300 tekens)
2. Welkomstbericht na connectie
3. Opvolgbericht (follow-up)
4. Waardebericht (gratis tip)
5. Zacht aanbod bericht
 
Voor elk bericht geef:
- Het bericht zelf
- Waarom deze aanpak werkt
- Beste tijdstip om te sturen
"""
 
        full_prompt = (
            f"{system_prompt}\n\n"
            f"TAAK: {task}\n\n"
            f"Geef een volledig uitgewerkt LinkedIn bericht of strategie."
        )
 
        response = ask_ai(full_prompt)
        return response
 
    except Exception as e:
        return f"LinkedIn agent fout: {e}"