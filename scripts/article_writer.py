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
        "keywords": ["amare edge mango", "amare edge plus mango ervaringen", "happy juice mango", "focus drank kopen"],
        "topic": "focus, darmgezondheid en mentale helderheid",
    },
    # ── Nieuwe artikelen op basis van keyword research 2026 ──────────────────
    "happy_juice_kopen": {
        "name": "Amare Happy Juice Edge Plus",
        "slug": "happy-juice-edge-plus-watermelon",
        "wp_slug": "amare-happy-juice-kopen-nederland-2026",
        "keywords": ["amare happy juice kopen", "happy juice kopen nederland", "amare happy juice prijs", "happy juice bestellen"],
        "topic": "waar en hoe je Amare Happy Juice koopt in Nederland — prijs, kortingscode en levering",
    },
    "happy_juice_bijwerkingen": {
        "name": "Amare Happy Juice Edge Plus",
        "slug": "happy-juice-edge-plus-watermelon",
        "wp_slug": "amare-happy-juice-bijwerkingen-2026",
        "keywords": ["amare happy juice bijwerkingen", "happy juice bijwerkingen", "happy juice veiligheid", "happy juice ingrediënten gevaar"],
        "topic": "bijwerkingen, veiligheid en contra-indicaties van Amare Happy Juice",
    },
    "amare_vs_concurrenten": {
        "name": "Amare vs Concurrenten",
        "slug": "amare-vergelijking",
        "wp_slug": "amare-supplement-vergelijking-concurrenten-2026",
        "keywords": ["amare supplement vergelijking", "amare vs other supplements", "beste gut-brain supplement nederland", "amare alternatief"],
        "topic": "vergelijking van Amare supplementen versus de beste concurrenten in Nederland",
    },
    "gut_brain": {
        "name": "Gut-Brain Axis Supplementen",
        "slug": "gut-brain-axis",
        "wp_slug": "gut-brain-axis-supplement-nederland-2026",
        "keywords": ["gut brain axis supplement", "darm hersenas supplement", "mentale gezondheid darm", "probiotica focus nederland"],
        "topic": "de darm-hersenverbinding (gut-brain axis) en welke supplementen het beste werken voor mentale gezondheid",
    },
}

# ─── Ürün Gerçekleri (PDF Factsheets) ────────────────────────────────────────
PRODUCT_FACTS = {
    "happy_juice": """
- Ingrediënten: Magnesium, prebiotica (inuline), probiotica (Lactobacillus), adaptogenen, GABA, 5-HTP
- Werking: ondersteunt darm-hersenverbinding (gut-brain axis), kalmeert het zenuwstelsel, verbetert focus
- Kenmerken: vloeibaar zakje (watermeloen smaak), suikervrij, plantaardig
- Voordelen: meer energie, betere stemming, minder stress, verbeterde concentratie
""",
    "edge": """
- Ingrediënten: mango-extract, Lycium barbarum (gojibessen), bètacaroteen, vitamine B5 (calciumpantothenaat)
- Werking: pantotheenzuur ondersteunt energiemetabolisme, synthese van steroïde hormonen en neurotransmitters, helpt vermoeidheid verminderen
- Kenmerken: plantaardig, geen cafeïne, zakje
- Voordelen: meer energie zonder crash, dagelijkse vitaliteit, mentale helderheid
""",
    "edge_mango": """
- Ingrediënten: mango-extract, Lycium barbarum (gojibessen), natuurlijke cafeïne (Coffea arabica)
- Werking: cafeïne verbetert concentratie en verhoogt alertheid; goji ondersteunt algehele vitaliteit
- Kenmerken: plantaardig, mango smaak, met cafeïne, 30 zakjes
- Voordelen: snelle focus, verhoogde alertheid, actieve levensstijl ondersteuning
""",
    "mentabiotics": """
- Ingrediënten: magnesium, groene thee-extract, artisjokextract, ApplePhenon, gemberwortelextract, druivenpitextract, zeeden-extract, Bifidobacterium longum, Lactobacillus helveticus, Lactobacillus rhamnosus
- Werking: magnesium draagt bij aan normale psychische functie; probiotica ondersteunen darm-hersenverbinding; vermindert vermoeidheid
- Kenmerken: 3 bacteriestammen, plantaardige extracten, wetenschappelijk onderbouwd
- Voordelen: betere mentale balans, minder angst, gezondere darmflora, meer energie
""",
    "nitro_xtreme": """
- Ingrediënten: noni-vruchtensapconcentraat (hoog geconcentreerd), aanvullende vitamines en mineralen
- Werking: ondersteuning van nutriëntenopname uit Sunrise en Sunset; essentieel onderdeel Triangle of Wellness
- Kenmerken: vloeibaar, hoge concentratie noni, speciaal voor actieve mensen
- Voordelen: betere opname van andere supplementen, verbeterde doorbloeding, meer energie
""",
    "sunset": """
- Ingrediënten: vitamine E (D-alfa-tocoferol, natuurlijke vorm), vitamine A (retinylpalmitaat), vitamine D3 (zonneschijn-vitamine), omega-3 (uit vis)
- Werking: vitamine E beschermt cellen tegen oxidatieve stress; vitamine D3 voor botten, immuunfunctie en mentaal welbevinden; vitamine A voor zicht en huid
- Kenmerken: lactosevrij, glutenvrij, NIET geschikt voor veganisten (bevat vis), 3 capsules per dag
- Voordelen: betere nachtrust, cel bescherming, sterk immuunsysteem, gezonde huid
""",
    "triangle": """
- Inhoud: Sunrise + Sunset + Nitro Xtreme (de drie populairste Amare supplementen)
- Werking: compleet dagsysteem — ochtend (Sunrise), avond (Sunset), opname-ondersteuning (Nitro)
- Kenmerken: naadloze dagelijkse routine, synergetische werking van drie producten samen
- Voordelen: complete mentale en fysieke wellness, dag en nacht ondersteuning, maximale nutriëntenopname
""",
    "gut_brain": """
- Wetenschappelijke basis: darm-hersenverbinding (vaguszenuw); 95% serotonine geproduceerd in darmen
- Relevante supplementen: probiotica (Lactobacillus, Bifidobacterium), magnesium, prebiotica, adaptogenen
- Amare producten: MentaBiotics (darm-hersenas), Happy Juice (GABA + probiotica), Restore (darmgezondheid)
- Trend 2026: gut-brain axis supplementen groeien 23% per jaar in Nederland
""",
}

SEO_TITLES = {
    "happy_juice":              "Amare Happy Juice Ervaringen 2026 – Werkt Het Echt? Eerlijke Review",
    "sunrise":                  "Amare Sunrise Ervaringen 2026 – Ochtendenergie Supplement Getest",
    "sunset":                   "Amare Sunset Ervaringen 2026 – Beter Slapen? Eerlijke Review",
    "edge":                     "Amare Edge Ervaringen 2026 – Meer Focus en Energie? Eerlijk Getest",
    "restore":                  "Amare Restore Ervaringen 2026 – Darmgezondheid Supplement Getest",
    "triangle":                 "Amare Triangle of Wellness Ervaringen 2026 – Compleet Pakket?",
    "ignite_her":               "Amare Ignite for Her Ervaringen 2026 – Hormoonbalans Supplement",
    "ignite_him":               "Amare Ignite for Him Ervaringen 2026 – Testosteron & Energie",
    "hl5":                      "Amare HL5 Collageen Ervaringen 2026 – Huid, Haar & Gewrichten",
    "fit20":                    "Amare Fit20 Ervaringen 2026 – Eiwitshake Eerlijk Getest",
    "mentabiotics":             "Amare MentaBiotics Ervaringen 2026 – Probiotica voor Darm & Brein",
    "on_shots":                 "Amare ON Shots Ervaringen 2026 – Energie Shot Eerlijk Getest",
    "nitro_xtreme":             "Amare Nitro Xtreme Ervaringen 2026 – Doorbloeding & Energie",
    "origin":                   "Amare Origin Chocolate Ervaringen 2026 – Vegan Eiwitshake Getest",
    "skin_to_mind":             "Amare Skin to Mind Ervaringen 2026 – Huidverzorging Supplement",
    "rootist":                  "Amare Rootist Ervaringen 2026 – Haaruitval Supplement Getest",
    "edge_mango":               "Amare Edge Plus Mango Ervaringen 2026 – Focus & Darmgezondheid",
    "happy_juice_kopen":        "Amare Happy Juice Kopen in Nederland 2026 – Prijs & Kortingscode",
    "happy_juice_bijwerkingen": "Amare Happy Juice Bijwerkingen 2026 – Veilig? Eerlijk Getest",
    "amare_vs_concurrenten":    "Amare vs Concurrenten 2026 – Beste Gut-Brain Supplement Nederland",
    "gut_brain":                "Gut-Brain Axis Supplement 2026 – Top 5 voor Mentale Gezondheid NL",
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
    facts_info = f"\n\nOFFICIËLE PRODUCTFEITEN (gebruik deze exacte informatie):\n{PRODUCT_FACTS[product_key]}" if product_key in PRODUCT_FACTS else ""
    prompt = f"""Schrijf een uitgebreide, betrouwbare Nederlandse productreview van "{p['name']}".
Het gaat over het thema: {p['topic']}.{vorm_info}{facts_info}

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
- Geef ALLEEN de HTML terug, geen inleiding of uitleg
- VERBODEN: geen ```html of ``` blokken, geen markdown, alleen pure HTML"""

    client = Anthropic(api_key=CLAUDE_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text.strip()
    # Markdown code fences temizle
    import re
    text = re.sub(r'^```[a-z]*\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n?```$', '', text, flags=re.MULTILINE)
    return text.strip()


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
