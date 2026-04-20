#!/usr/bin/env python3
"""
article_writer_amarenl.py — Schrijft Nederlandstalige SEO-artikelen over voedingsstoffen
en Amare-ingrediënten. Publiceert op amarenl.com. Doel: organisch verkeer + e-mailleads.
"""

import os
import sys
import base64
import re
import requests
from dotenv import load_dotenv

_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_FILE_DIR)
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

if _PROJECT_ROOT not in sys.path:
    sys.path.append(_PROJECT_ROOT)

from src.skills.ai_client import ask_ai

# ─── Config ────────────────────────────────────────────────────────────────────
WP_URL      = "https://amarenl.com/wp-json/wp/v2/posts"
WP_USER     = os.getenv("WP_USERNAME", "shoppingbest41")
WP_APP_PASS = os.getenv("WP_APP_PASSWORD", "QmdY FAML WPzu IiK4 jewG lSD7")
AFFILIATE_BASE = "https://www.amare.com/2075008/nl-nl"

# ─── Artikel Onderwerpen ────────────────────────────────────────────────────────
# Nutriënten/ingrediënten gerelateerd aan Amare-producten — voor SEO-verkeer
ARTICLES = {
    "magnesium_slaap": {
        "title": "Magnesium en Slaap: Waarom Nederlanders Tekort Hebben (2026)",
        "slug": "magnesium-slaap-supplement-nederland",
        "keywords": ["magnesium slaap", "magnesium tekort nederland", "magnesium supplement slaap"],
        "focus_product": "Amare Ignite for Her / MentaBiotics",
        "affiliate_slug": "ignite-for-her",
        "nutrient": "magnesium",
        "topic": "de relatie tussen magnesiumtekort en slaapproblemen bij Nederlanders, oplossingen via voeding en supplementen",
    },
    "omega3_hersenen": {
        "title": "Omega-3 en Hersengezondheid: Wat Niemand Je Vertelt (2026)",
        "slug": "omega-3-hersenen-supplement-nederland",
        "keywords": ["omega 3 hersenen", "omega 3 supplement nederland", "omega 3 focus"],
        "focus_product": "Amare Sunset",
        "affiliate_slug": "sunset",
        "nutrient": "omega-3 vetzuren",
        "topic": "hoe omega-3 vetzuren (EPA en DHA) de hersenfunctie, focus en stemming beïnvloeden",
    },
    "vitamine_d_tekort": {
        "title": "Vitamine D Tekort Nederland: Symptomen & Beste Aanvulling 2026",
        "slug": "vitamine-d-tekort-nederland-supplement",
        "keywords": ["vitamine d tekort nederland", "vitamine d supplement", "vitamine d symptomen"],
        "focus_product": "Amare Sunset",
        "affiliate_slug": "sunset",
        "nutrient": "vitamine D3",
        "topic": "vitamine D-tekort in Nederland (weinig zon), symptomen, risico's en hoe je het aanvult",
    },
    "vitamine_e_huid": {
        "title": "Vitamine E voor Huid en Haar: Werkt Het Echt? (2026)",
        "slug": "vitamine-e-huid-haar-supplement",
        "keywords": ["vitamine e huid", "vitamine e supplement haar", "antioxidant huid nederland"],
        "focus_product": "Amare Sunset / HL5 Collageen",
        "affiliate_slug": "hl5-peach",
        "nutrient": "vitamine E",
        "topic": "de werking van vitamine E als antioxidant voor huidgezondheid, haargroei en celbescherming",
    },
    "vitamine_b_energie": {
        "title": "B-Vitamines en Energie: Welke Heb Jij Nodig? Complete Gids 2026",
        "slug": "b-vitamines-energie-supplement-nederland",
        "keywords": ["b vitamines energie", "vitamine b12 tekort", "b complex supplement nederland"],
        "focus_product": "Amare ON Shots / Sunrise",
        "affiliate_slug": "amareedge-plus-mango",
        "nutrient": "B-vitaminecomplex (B1, B2, B3, B6, B12)",
        "topic": "hoe B-vitamines (B1, B2, B3, B6, B12) vermoeidheid bestrijden en energie geven",
    },
    "vitamine_c_immuun": {
        "title": "Vitamine C en Immuunsysteem: Meer Dan Alleen Verkoudheid (2026)",
        "slug": "vitamine-c-immuunsysteem-supplement",
        "keywords": ["vitamine c immuunsysteem", "vitamine c supplement nederland", "vitamine c huid"],
        "focus_product": "Amare Sunrise",
        "affiliate_slug": "triangle-of-wellness-xtreme",
        "nutrient": "vitamine C",
        "topic": "de rol van vitamine C bij het immuunsysteem, collageen aanmaak, en energieniveau",
    },
    "collageen_huid": {
        "title": "Collageen Supplement: Werkt Het Voor Huid, Haar en Gewrichten? (2026)",
        "slug": "collageen-supplement-huid-haar-gewrichten",
        "keywords": ["collageen supplement huid", "collageen kopen nederland", "collageen ervaringen"],
        "focus_product": "Amare HL5 Collageen",
        "affiliate_slug": "hl5-peach",
        "nutrient": "gehydrolyseerd collageen Type I en III",
        "topic": "hoe collageen supplementen (Type I en III peptiden) de huid elasticiteit, haargroei en gewrichten verbeteren",
    },
    "probiotica_darm": {
        "title": "Probiotica voor Darmen: Welke Bacteriën Heb Je Nodig? (2026)",
        "slug": "probiotica-darmen-supplement-nederland",
        "keywords": ["probiotica darmen", "beste probiotica nederland", "probiotica darmflora supplement"],
        "focus_product": "Amare MentaBiotics / Restore",
        "affiliate_slug": "mentabiotics",
        "nutrient": "probiotica (Lactobacillus en Bifidobacterium stammen)",
        "topic": "welke probiotische bacteriestammen de darmflora herstellen, het immuunsysteem versterken en de darm-hersenverbinding verbeteren",
    },
    "adaptogenen_stress": {
        "title": "Adaptogenen tegen Stress: Ashwagandha, Rhodiola & Co (2026)",
        "slug": "adaptogenen-stress-supplement-nederland",
        "keywords": ["adaptogenen stress", "ashwagandha supplement nederland", "rhodiola stress"],
        "focus_product": "Amare ON Shots / Ignite for Him",
        "affiliate_slug": "amareedge-plus-mango",
        "nutrient": "adaptogenen (Ashwagandha, Rhodiola Rosea, Bacopa Monnieri)",
        "topic": "hoe adaptogenen zoals Ashwagandha en Rhodiola stresshormonen reguleren en veerkracht verhogen",
    },
    "gut_brain_stemming": {
        "title": "Darm-Hersen Verbinding: Hoe Je Darmen Je Stemming Sturen (2026)",
        "slug": "darm-hersen-verbinding-stemming-supplement",
        "keywords": ["darm hersen verbinding", "gut brain axis nederland", "darmen stemming serotonine"],
        "focus_product": "Amare Happy Juice / MentaBiotics",
        "affiliate_slug": "amareedge-plus-mango",
        "nutrient": "probiotica, prebiotica, GABA, 5-HTP, magnesium",
        "topic": "de wetenschappelijke basis van de darm-hersenverbinding (gut-brain axis), serotonine aanmaak in darmen, en hoe supplementen helpen",
    },
    "zink_testosteron": {
        "title": "Zink en Testosteron: Wat Is de Verbinding? (2026)",
        "slug": "zink-testosteron-supplement-nederland",
        "keywords": ["zink testosteron", "zink supplement man", "zink tekort symptomen"],
        "focus_product": "Amare Ignite for Him",
        "affiliate_slug": "ignite-for-him",
        "nutrient": "zink",
        "topic": "de rol van zink bij testosteronproductie, vruchtbaarheid en immuunfunctie bij mannen",
    },
    "calcium_botten": {
        "title": "Calcium voor Sterke Botten: Meer Dan Melk Drinken (2026)",
        "slug": "calcium-botten-supplement-nederland",
        "keywords": ["calcium botten supplement", "calcium tekort nederland", "botontkalking voorkomen"],
        "focus_product": "Amare Origin / Sunset",
        "affiliate_slug": "triangle-of-wellness-xtreme",
        "nutrient": "calcium en vitamine D3",
        "topic": "hoe calcium samen met vitamine D3 en K2 de botdichtheid ondersteunt en osteoporose voorkomt",
    },
    "mct_energie": {
        "title": "MCT Olie voor Energie en Gewicht: Wat Zegt de Wetenschap? (2026)",
        "slug": "mct-olie-energie-gewicht-supplement",
        "keywords": ["mct olie energie", "mct supplement nederland", "mct keto energie"],
        "focus_product": "Amare Origin Chocolate",
        "affiliate_slug": "amareedge-plus-mango",
        "nutrient": "MCT (Medium Chain Triglycerides)",
        "topic": "hoe MCT-vetten snelle energie geven, de vetverbranding ondersteunen en hersenfunctie verbeteren",
    },
    "ijzer_vermoeidheid": {
        "title": "IJzer Tekort en Vermoeidheid: Herken de Signalen (2026)",
        "slug": "ijzer-tekort-vermoeidheid-supplement-nederland",
        "keywords": ["ijzer tekort vermoeidheid", "ijzer supplement vrouw", "anemie nederland"],
        "focus_product": "Amare Sunrise / Ignite for Her",
        "affiliate_slug": "ignite-for-her",
        "nutrient": "ijzer en vitamine C",
        "topic": "ijzertekort als meest voorkomende voedingsstofdeficiëntie bij Nederlandse vrouwen — symptomen, oorzaken, aanvullen",
    },
    "prebiotica_vezels": {
        "title": "Prebiotica vs Probiotica: Wat Is het Verschil? (Volledige Gids 2026)",
        "slug": "prebiotica-probiotica-verschil-nederland",
        "keywords": ["prebiotica probiotica verschil", "prebiotica supplement", "inuline vezels darmen"],
        "focus_product": "Amare Happy Juice / Restore",
        "affiliate_slug": "amareedge-plus-mango",
        "nutrient": "prebiotische vezels (inuline) en probiotica",
        "topic": "het verschil tussen prebiotica en probiotica, hoe ze samenwerken voor een gezonde darmflora",
    },
}

# ─── Lead Capture CTA Blok ──────────────────────────────────────────────────────
LEAD_CTA = """<div style="background:linear-gradient(135deg,#2A5C45,#4a9470);color:#fff;padding:32px;border-radius:16px;text-align:center;margin:40px 0;">
<h3 style="color:#fff;margin-top:0;font-size:1.4em;">🎁 Ontvang €8 Korting op Je Eerste Amare Bestelling</h3>
<p style="color:#e8f5ee;margin:8px 0 20px;">Vul je e-mailadres in en ontvang direct een exclusieve kortingscode + gratis wellness tips.</p>
<a href="https://amarenl.com/#lead" style="background:#fff;color:#2A5C45;padding:14px 32px;border-radius:50px;text-decoration:none;font-weight:700;font-size:1em;display:inline-block;">✉️ Claim Mijn €8 Korting →</a>
<p style="color:#c8e6d4;font-size:0.8em;margin:12px 0 0;">🔒 Geen spam. Uitschrijven kan altijd.</p>
</div>"""

GARANTIE_BLOK = """<div style="background:#f0faf4;border-left:5px solid #2A5C45;padding:20px 24px;margin:32px 0;border-radius:8px;">
<h3 style="color:#2A5C45;margin-top:0;">🛡️ 30 dagen niet-goed-geld-terug garantie</h3>
<p>Amare staat volledig achter hun producten. Geen resultaat na 30 dagen? <strong>Volledig geld terug</strong> — zelfs op lege verpakkingen. Volledig risicoverloos proberen.</p>
</div>"""


def generate_article(article_key: str) -> str:
    a = ARTICLES[article_key]
    affiliate_url = f"{AFFILIATE_BASE}/{a['affiliate_slug']}"

    btn = (
        f'<div style="text-align:center;margin:32px 0;">'
        f'<a href="{affiliate_url}" rel="sponsored" '
        f'style="background:#2A5C45;color:#fff;padding:16px 36px;border-radius:10px;'
        f'text-decoration:none;font-weight:700;font-size:17px;">'
        f'✅ Bekijk {a["focus_product"]} bij Amare →</a></div>'
    )

    prompt = f"""Schrijf een uitgebreid, betrouwbaar Nederlandstalig SEO-artikel over het onderwerp:
"{a['topic']}"

Kernnutriënt(en): {a['nutrient']}
Gerelateerd Amare-product: {a['focus_product']}

Gebruik PRECIES deze HTML-structuur (geen markdown, alleen HTML-tags):

<h2>Wat Is {a['nutrient']} en Waarom Hebben We Het Nodig?</h2>
[150 woorden: wetenschappelijke uitleg, dagelijkse behoefte, rol in het lichaam]

<h2>Symptomen van {a['nutrient']} Tekort</h2>
[150 woorden: herkenbare symptomen, prevalentie in Nederland, risicogroepen]

{LEAD_CTA}

<h2>Hoe Verhoog Je Je {a['nutrient']} Inname?</h2>
[150 woorden: voedingsbronnen, wanneer supplementen nodig zijn, absorptietips]

<h2>{a['focus_product']} en {a['nutrient']}: De Verbinding</h2>
[150 woorden: hoe dit Amare-product helpt bij dit nutriënt, ingrediënten, werking]
{GARANTIE_BLOK}
{btn}

<h2>Veelgestelde Vragen over {a['nutrient']}</h2>
<h3>Hoeveel {a['nutrient']} heb ik per dag nodig?</h3>
[60 woorden]
<h3>Kan ik te veel {a['nutrient']} innemen?</h3>
[60 woorden]
<h3>Wanneer merk ik verschil na het starten met {a['nutrient']}?</h3>
[60 woorden]

<h2>Conclusie</h2>
[100 woorden eindconclusie, noem het Amare-product, benadruk risicovrij proberen]
{GARANTIE_BLOK}
{btn}

STRIKTE REGELS:
- ALLEEN Nederlands — geen enkel Engels woord
- Wetenschappelijk onderbouwd maar begrijpelijk voor gewone lezer
- Verwerk deze zoekwoorden NATUURLIJK: {', '.join(a['keywords'])}
- Totaal 800–1000 woorden
- Geef ALLEEN pure HTML terug, GEEN ```html blokken, GEEN markdown
- Toon: informatief, betrouwbaar, empathisch (niet schreeuwerig)"""

    text = ask_ai(prompt)
    text = re.sub(r'^```[a-z]*\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n?```$', '', text, flags=re.MULTILINE)
    return text.strip()


def post_to_wordpress(article_key: str, content: str) -> str:
    a = ARTICLES[article_key]
    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "title":   a["title"],
        "content": content,
        "status":  "publish",
        "slug":    a["slug"],
        "meta": {
            "yoast_wpseo_metadesc": f"{a['title']} — Ontdek alles over {a['nutrient']}, symptomen van tekort en de beste supplementen voor Nederland.",
            "yoast_wpseo_focuskw":  a["keywords"][0],
        },
    }

    # Bestaand artikel? Update dan
    search = requests.get(f"{WP_URL}?slug={a['slug']}", headers=headers, timeout=15)
    existing = search.json()
    if existing and isinstance(existing, list) and len(existing) > 0:
        post_id = existing[0]["id"]
        print(f"⚠️  Bestaand artikel gevonden (ID:{post_id}), wordt bijgewerkt…")
        r = requests.post(f"{WP_URL}/{post_id}", headers=headers, json=payload, timeout=30)
        return r.json().get("link", "")

    r = requests.post(WP_URL, headers=headers, json=payload, timeout=30)
    if r.status_code in (200, 201):
        return r.json().get("link", "")

    raise RuntimeError(f"WordPress API fout {r.status_code}: {r.text[:300]}")


def write_and_publish(article_key: str) -> str:
    if article_key not in ARTICLES:
        raise ValueError(f"Onbekend artikel: '{article_key}'. Beschikbaar: {list(ARTICLES.keys())}")

    a = ARTICLES[article_key]
    print(f"📝 Artikel schrijven: {a['title']}")
    content = generate_article(article_key)

    print(f"📤 Uploaden naar WordPress (amarenl.com): {a['title']}")
    url = post_to_wordpress(article_key, content)
    print(f"✅ Gepubliceerd → {url}")
    return url


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "magnesium_slaap"
    try:
        write_and_publish(key)
    except Exception as e:
        print(f"❌ Fout: {e}", file=sys.stderr)
        sys.exit(1)
