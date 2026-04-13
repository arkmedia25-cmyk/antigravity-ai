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
    learned = load_json(os.path.join(memory_dir, "learned.json"))
    competitor_strategy = load_json(os.path.join(memory_dir, "competitor_strategy.json"))
    return brand, audience, products, learned, competitor_strategy

def run_content(task):
    """Voert content generatie uit"""
    try:
        brand, audience, products, learned, competitor_strategy = load_memory()

        # Rakip strateji boşluklarını çıkar
        competitor_gaps = ""
        content_rules_extra = ""
        priority_formats = ""
        if competitor_strategy:
            bonusan = competitor_strategy.get("competitors", {}).get("bonusan", {})
            strategy = competitor_strategy.get("content_strategy", {})
            competitor_gaps = "\n".join(
                f"- {g}" for g in bonusan.get("creative_weaknesses", [])
            )
            content_rules_extra = "\n".join(
                f"- {r}" for r in strategy.get("messaging_rules", [])
            )
            priority_formats = json.dumps(
                strategy.get("priority_formats", []), ensure_ascii=False, indent=2
            )

        system_prompt = f"""
Je bent een social media content specialist en video content creator voor Amare Global Brand Partner in Nederland.

MERK INFO:
{json.dumps(brand, ensure_ascii=False, indent=2)}

DOELGROEPEN:
{json.dumps(audience, ensure_ascii=False, indent=2)}

PRODUCTEN:
{json.dumps(products, ensure_ascii=False, indent=2)}

GOEDGEKEURDE HOOKS:
{json.dumps(learned.get('approved_hooks', []), ensure_ascii=False)}

AFGEWEZEN STIJLEN:
{json.dumps(learned.get('rejected_styles', []), ensure_ascii=False)}

---
CONCURRENTIE INTELLIGENTIE — BONUSAN ANALYSE (april 2026):
Bonusan is onze grootste concurrent. Hun creatieve zwakheden zijn onze kansen:
{competitor_gaps}

KERN STRATEGIE: "Bonusan verkoopt aan features. Wij verkopen aan emoties, resultaten en echte mensen."

CONTENT & MESSAGING REGELS (verplicht voor alle content):
- Schrijf altijd in het Nederlands tenzij anders gevraagd
- Nooit medische claims maken
- Altijd authentiek en persoonlijk
- Focus op lifestyle, energie, moederschap
- Gebruik storytelling
- Altijd een zachte CTA
{content_rules_extra}

PRIORITAIRE CONTENT FORMATS (in volgorde van prioriteit):
{priority_formats}

---
CONTENT TYPES:
1. UGC video script (30-45 seconden, verticaal 9:16) — HOOGSTE PRIORITEIT
2. Instagram Reels script (60-90 seconden)
3. Instagram carousel (5 slides — dag 1/dag 3/dag 7/dag 30/CTA structuur)
4. Testimonial statische advertentie (screenshot-stijl met sterren + review tekst)
5. Instagram story serie (5 stories)
6. Caption voor foto post
7. LinkedIn artikel
8. Email nieuwsbrief
9. Blog artikel (SEO-geoptimaliseerd, jargonvrij, 600-900 woorden)

Voor elk content stuk geef:
- De volledige tekst / script
- Hook (eerste 2-3 seconden apart uitgelicht)
- Hashtags (15-20 stuks)
- Beste tijdstip om te posten
- Thumbnail/cover tip
- CTA suggestie
- Format notitie (waarom dit format werkt vs. Bonusan)
"""

        full_prompt = (
            f"{system_prompt}\n\n"
            f"TAAK: {task}\n\n"
            f"Maak professionele, engaging content die past bij de doelgroep en de concurrentiestrategie."
        )

        response = ask_ai(full_prompt)
        return response

    except Exception as e:
        return f"Content agent fout: {e}"
