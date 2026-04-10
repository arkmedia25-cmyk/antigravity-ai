#!/usr/bin/env python3
"""
article_writer.py — Amare ürün review makalesi yazar ve WordPress'e yayınlar
Kullanım: python3 article_writer.py [product_key]
"""

import os
import sys
import base64
import requests
from dotenv import load_dotenv
load_dotenv("/root/antigravity-ai/.env")
from anthropic import Anthropic

# ─── Config ────────────────────────────────────────────────────────────────────
WP_URL      = "https://amarereview.nl/wp-json/wp/v2/posts"
WP_USER     = "arkmedia25@gmail.com"
WP_APP_PASS = "rAoAvw0PKmplYN9PCN1lTRFI"   # spaties verwijderd
AFFILIATE_BASE = "https://www.amare.com/2075008/nl-NL"
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ─── Ürün Kataloğu ─────────────────────────────────────────────────────────────
PRODUCTS = {
    "happy_juice": {
        "name": "Amare Happy Juice Edge Plus",
        "slug": "happy-juice-edge-plus-watermelon",
        "wp_slug": "amare-happy-juice-review-2026",
        "keywords": ["happy juice", "amare happy juice", "happy juice review", "happy juice ervaringen"],
        "topic": "energie en focus",
    },
    "sunrise": {
        "name": "Amare Sunrise",
        "slug": "sunrise",
        "wp_slug": "amare-sunrise-review-2026",
        "keywords": ["amare sunrise", "sunrise supplement", "ochtend energie supplement"],
        "topic": "ochtendenergie en opstartritueel",
    },
    "sunset": {
        "name": "Amare Sunset",
        "slug": "sunset",
        "wp_slug": "amare-sunset-review-2026",
        "keywords": ["amare sunset", "sunset supplement", "slaap supplement"],
        "topic": "slaapkwaliteit en avondontspanning",
    },
    "edge": {
        "name": "Amare Edge",
        "slug": "edge",
        "wp_slug": "amare-edge-review-2026",
        "keywords": ["amare edge", "focus supplement", "mentale energie"],
        "topic": "mentale focus en cognitieve prestaties",
    },
    "restore": {
        "name": "Amare Restore",
        "slug": "restore",
        "wp_slug": "amare-restore-review-2026",
        "keywords": ["amare restore", "darm supplement", "darmgezondheid"],
        "topic": "darmgezondheid en detox",
    },
    "triangle": {
        "name": "Amare Triangle of Wellness Xtreme",
        "slug": "triangle-of-wellness-xtreme",
        "wp_slug": "amare-triangle-wellness-review-2026",
        "keywords": ["amare triangle", "triangle of wellness", "amare compleet pakket"],
        "topic": "complete mentale en fysieke wellness",
    },
    "ignite_her": {
        "name": "Amare Ignite for Her",
        "slug": "ignite-for-her",
        "wp_slug": "amare-ignite-for-her-review-2026",
        "keywords": ["amare ignite for her", "hormoonbalans vrouw", "vrouwen supplement"],
        "topic": "hormoonbalans en vrouwelijke vitaliteit",
    },
    "ignite_him": {
        "name": "Amare Ignite for Him",
        "slug": "ignite-for-him",
        "wp_slug": "amare-ignite-for-him-review-2026",
        "keywords": ["amare ignite for him", "testosteron supplement", "energie man"],
        "topic": "mannelijke hormoonbalans en vitaliteit",
    },
    "hl5": {
        "name": "Amare HL5 Collageen",
        "slug": "hl5",
        "wp_slug": "amare-hl5-collageen-review-2026",
        "keywords": ["amare hl5", "collageen supplement", "huid supplement"],
        "topic": "huid, haar en gewrichten via collageen",
        "vorm": "vloeibaar (drinkbare shot, aangenaam van smaak — geen poeder of capsule)",
    },
    "fit20": {
        "name": "Amare Fit20 Eiwitshake Vanille",
        "slug": "fit20-vanilla",
        "wp_slug": "amare-fit20-review-2026",
        "keywords": ["amare fit20", "eiwitshake", "proteïne supplement"],
        "topic": "spieropbouw en gezond gewicht",
    },
    "mentabiotics": {
        "name": "Amare MentaBiotics",
        "slug": "mentabiotics",
        "wp_slug": "amare-mentabiotics-review-2026",
        "keywords": ["amare mentabiotics", "probiotica supplement", "darm-hersenas"],
        "topic": "darm-hersenverbinding en mentale balans via probiotica",
    },
    "on_shots": {
        "name": "Amare ON Shots",
        "slug": "on-shots",
        "wp_slug": "amare-on-shots-review-2026",
        "keywords": ["amare on shots", "energie shot", "adaptogenen supplement"],
        "topic": "snelle energie en focus via adaptogene shots",
    },
    "nitro_xtreme": {
        "name": "Amare Nitro Xtreme",
        "slug": "nitro-xtreme-56ml",
        "wp_slug": "amare-nitro-xtreme-review-2026",
        "keywords": ["amare nitro xtreme", "doorbloeding supplement", "no supplement"],
        "topic": "doorbloeding, energie en fysieke prestaties",
    },
    "origin": {
        "name": "Amare Origin Chocolate Eiwitshake",
        "slug": "origin-chocolate",
        "wp_slug": "amare-origin-chocolate-review-2026",
        "keywords": ["amare origin", "vegan eiwitshake", "chocolade proteïne"],
        "topic": "plantaardige eiwitten en gezond gewicht",
    },
    "skin_to_mind": {
        "name": "Amare Skin to Mind Collection",
        "slug": "skin-to-mind-collection",
        "wp_slug": "amare-skin-to-mind-review-2026",
        "keywords": ["amare huidverzorging", "skin to mind", "amare serum"],
        "topic": "huidverzorging van binnenuit en van buitenaf",
    },
    "rootist": {
        "name": "Amare Rootist Haarverzorging",
        "slug": "rootist-dynamic-pack",
        "wp_slug": "amare-rootist-haarwelzijn-review-2026",
        "keywords": ["amare rootist", "haaruitval supplement", "haar welzijn"],
        "topic": "haargroei, haaruitval en gezonde hoofdhuid",
    },
    "edge_mango": {
        "name": "Amare Edge Plus Mango",
        "slug": "edge-plus-mango",
        "wp_slug": "amare-edge-plus-mango-review-2026",
        "keywords": ["amare edge mango", "happy juice mango", "focus drank"],
        "topic": "focus, darmgezondheid en mentale helderheid",
    },
}

SEO_TITLES = {
    "happy_juice":  "Amare Happy Juice Review 2026 – Eerlijke Ervaringen & Resultaten",
    "sunrise":      "Amare Sunrise Review 2026 – Ochtendenergie Supplement, Werkt Het?",
    "sunset":       "Amare Sunset Review 2026 – Beter Slapen met Dit Supplement?",
    "edge":         "Amare Edge Review 2026 – Meer Focus en Mentale Energie?",
    "restore":      "Amare Restore Review 2026 – Darmgezondheid in een Capsule?",
    "triangle":     "Amare Triangle of Wellness Review 2026 – Compleet Pakket?",
    "ignite_her":   "Amare Ignite for Her Review 2026 – Hormoonbalans Supplement",
    "ignite_him":   "Amare Ignite for Him Review 2026 – Testosteron & Energie",
    "hl5":          "Amare HL5 Collageen Review 2026 – Voor Huid, Haar & Gewrichten",
    "fit20":        "Amare Fit20 Review 2026 – Gezonde Eiwitshake of Niet?",
    "mentabiotics": "Amare MentaBiotics Review 2026 – Probiotica voor Darm & Brein?",
    "on_shots":     "Amare ON Shots Review 2026 – Adaptogene Energie Shot, Werkt Het?",
    "nitro_xtreme": "Amare Nitro Xtreme Review 2026 – Doorbloeding & Energie Boost",
    "origin":       "Amare Origin Chocolate Review 2026 – Vegan Eiwitshake Eerlijk Getest",
    "skin_to_mind": "Amare Skin to Mind Review 2026 – Huidverzorging van Binnen & Buiten",
    "rootist":      "Amare Rootist Review 2026 – Oplossing tegen Haaruitval?",
    "edge_mango":   "Amare Edge Plus Mango Review 2026 – Focus & Darmgezondheid",
}

# ─── Makale Üretimi ─────────────────────────────────────────────────────────────
def generate_article(product_key: str) -> str:
    p = PRODUCTS[product_key]
    affiliate_link = f"{AFFILIATE_BASE}/{p['slug']}"
    btn = (
        f'<div style="text-align:center;margin:32px 0;">'
        f'<a href="{affiliate_link}" rel="sponsored" '
        f'style="background:#2A5C45;color:#fff;padding:16px 36px;border-radius:10px;'
        f'text-decoration:none;font-weight:700;font-size:17px;">'
        f'✅ Bekijk {p["name"]} bij Amare →</a></div>'
    )

    garantie_blok = """<div style="background:#f0faf4;border-left:5px solid #2A5C45;padding:20px 24px;margin:32px 0;border-radius:8px;">
<h3 style="color:#2A5C45;margin-top:0;">🛡️ 30 dagen niet-goed-geld-terug garantie</h3>
<p>Amare staat volledig achter hun producten. Heb je het 30 dagen gebruikt maar ervaar je <strong>geen enkel verschil</strong>? Stuur dan de lege of volle verpakking retour en je krijgt <strong>je volledige aankoopbedrag terug</strong> — geen vragen gesteld. Je kunt het dus <strong>volledig risicoverloos proberen</strong>.</p>
</div>"""

    vorm_info = f"\nProductvorm: {p['vorm']}" if p.get('vorm') else ""
    prompt = f"""Schrijf een uitgebreide, betrouwbare Nederlandse productreview van "{p['name']}".
Het gaat over het thema: {p['topic']}.{vorm_info}

Gebruik precies deze HTML-structuur (geen markdown, alleen HTML):

<h2>Wat is {p['name']}?</h2>
[150 woorden: productbeschrijving, ingrediënten, hoe het werkt]

<h2>Mijn ervaringen met {p['name']}</h2>
[200 woorden: persoonlijke ervaring, eerlijk en geloofwaardig, eerste week / tweede week / na een maand]

<h2>Ingrediënten en wetenschappelijke onderbouwing</h2>
[150 woorden: actieve ingrediënten, studies, darm-hersenverbinding indien relevant]

<h2>Voordelen en nadelen</h2>
<ul>
<li>✅ [voordeel 1]</li>
<li>✅ [voordeel 2]</li>
<li>✅ [voordeel 3]</li>
<li>❌ [eerlijk nadeel]</li>
</ul>

<h2>Voor wie is {p['name']} geschikt?</h2>
[100 woorden: doelgroep]

<h2>Prijs en waar te bestellen?</h2>
[80 woorden over prijs/waarde, dan deze exacte garantie blok en knop:]
{garantie_blok}
{btn}

<h2>Conclusie – Is {p['name']} het waard?</h2>
[100 woorden eindoordeel — benadruk nogmaals de risicovrije proefperiode van 30 dagen, dan:]
{garantie_blok}
{btn}

REGELS:
- Schrijf ALLEEN in het Nederlands
- Geen overdreven reclame — eerlijk en informatief
- Verwerk deze zoekwoorden natuurlijk: {', '.join(p['keywords'])}
- Totaal 800–1000 woorden
- Geef ALLEEN de HTML terug, geen inleiding of uitleg"""

    client = Anthropic(api_key=CLAUDE_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


# ─── WordPress Yayınlama ────────────────────────────────────────────────────────
def post_to_wordpress(title: str, content: str, product_key: str) -> str:
    p = PRODUCTS[product_key]
    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }
    meta_desc = (
        f"Lees onze eerlijke review van {p['name']}. "
        f"Ervaringen, ingrediënten, voor- en nadelen. Is het het geld waard?"
    )
    payload = {
        "title":   title,
        "content": content,
        "status":  "publish",
        "slug":    p["wp_slug"],
        "meta": {
            "yoast_wpseo_metadesc": meta_desc,
            "yoast_wpseo_focuskw":  p["keywords"][0],
        },
    }

    # Önce mevcut makaleyi ara, varsa güncelle
    search = requests.get(f"{WP_URL}?slug={p['wp_slug']}", headers=headers, timeout=15)
    existing = search.json()
    if existing:
        post_id = existing[0]["id"]
        print(f"⚠️  Mevcut makale bulundu (ID:{post_id}), güncelleniyor…")
        r = requests.post(f"{WP_URL}/{post_id}", headers=headers, json=payload, timeout=30)
        return r.json().get("link", "")

    # Yoksa yeni oluştur
    r = requests.post(WP_URL, headers=headers, json=payload, timeout=30)
    if r.status_code in (200, 201):
        return r.json().get("link", "")

    raise RuntimeError(f"WordPress API hatası {r.status_code}: {r.text[:300]}")


# ─── Ana Fonksiyon ──────────────────────────────────────────────────────────────
def write_and_publish(product_key: str) -> str:
    if product_key not in PRODUCTS:
        raise ValueError(f"Bilinmeyen ürün: '{product_key}'. Mevcut: {list(PRODUCTS.keys())}")

    p = PRODUCTS[product_key]
    print(f"📝 Makale yazılıyor: {p['name']}")
    content = generate_article(product_key)

    title = SEO_TITLES.get(product_key, f"{p['name']} Review 2026")
    print(f"📤 WordPress'e yükleniyor: {title}")
    url = post_to_wordpress(title, content, product_key)

    print(f"✅ Yayınlandı → {url}")
    return url


# ─── CLI ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "happy_juice"
    try:
        url = write_and_publish(key)
        print(url)
    except Exception as e:
        print(f"❌ Hata: {e}", file=sys.stderr)
        sys.exit(1)
