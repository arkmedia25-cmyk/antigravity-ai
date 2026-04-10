#!/usr/bin/env python3
"""
seo_updater.py — amarereview.nl tüm postlarını tara ve güncelle:
  - Yoast focus keyword + meta description
  - Doğru kategori ataması
  - Slug 2025 → 2026
  - Yayın tarihi bugüne çek
"""
import base64
import requests
from datetime import datetime

WP_URL      = "https://amarereview.nl/wp-json/wp/v2"
WP_USER     = "arkmedia25@gmail.com"
WP_APP_PASS = "rAoAvw0PKmplYN9PCN1lTRFI"

token = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}
today = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

# ─── Kategorileri çek ─────────────────────────────────────────────────────────
print("📂 Kategoriler çekiliyor...")
cats_r = requests.get(f"{WP_URL}/categories?per_page=100", headers=headers, timeout=15)
cats = {c["name"].lower(): c["id"] for c in cats_r.json()}
print(f"   Bulunan kategoriler: {list(cats.keys())}")

def cat_id(name):
    return cats.get(name.lower())

# ─── Ürün → SEO + Kategori Haritası ──────────────────────────────────────────
PRODUCT_MAP = {
    "happy-juice": {
        "focus_kw": "amare happy juice",
        "meta_desc": "Eerlijke review van Amare Happy Juice Edge Plus. Ervaringen, ingrediënten, voor- en nadelen. Werkt het echt voor energie en focus?",
        "categories": ["supplement reviews", "energie & focus"],
    },
    "sunrise": {
        "focus_kw": "amare sunrise",
        "meta_desc": "Amare Sunrise review 2026: eerlijke ervaringen met dit ochtendenergie supplement. Ingrediënten, resultaten en onze conclusie.",
        "categories": ["supplement reviews", "energie & focus"],
    },
    "sunset": {
        "focus_kw": "amare sunset",
        "meta_desc": "Amare Sunset review 2026: helpt dit supplement echt voor betere slaap? Onze eerlijke ervaringen na 30 dagen.",
        "categories": ["supplement reviews", "slaap & ontspanning"],
    },
    "edge": {
        "focus_kw": "amare edge",
        "meta_desc": "Amare Edge review 2026: meer focus en mentale energie? Eerlijke test met ingrediënten, ervaringen en eindoordeel.",
        "categories": ["supplement reviews", "mentale gezondheid"],
    },
    "restore": {
        "focus_kw": "amare restore",
        "meta_desc": "Amare Restore review 2026: verbetert dit supplement je darmgezondheid? Ingrediënten, ervaringen en conclusie.",
        "categories": ["supplement reviews", "darmgezondheid"],
    },
    "triangle": {
        "focus_kw": "amare triangle of wellness",
        "meta_desc": "Amare Triangle of Wellness Xtreme review 2026: compleet wellness pakket getest. Eerlijke ervaringen en resultaten.",
        "categories": ["supplement reviews", "supplementen"],
    },
    "ignite-for-her": {
        "focus_kw": "amare ignite for her",
        "meta_desc": "Amare Ignite for Her review 2026: hormoonbalans supplement voor vrouwen getest. Eerlijke ervaringen en ingrediënten.",
        "categories": ["supplement reviews", "immuunsysteem"],
    },
    "ignite-for-him": {
        "focus_kw": "amare ignite for him",
        "meta_desc": "Amare Ignite for Him review 2026: testosteron en energie supplement getest. Eerlijke ervaringen na 30 dagen.",
        "categories": ["supplement reviews", "energie & focus"],
    },
    "hl5": {
        "focus_kw": "amare hl5 collageen",
        "meta_desc": "Amare HL5 Collageen review 2026: voor huid, haar en gewrichten. Eerlijke ervaringen met dit vloeibare collageen supplement.",
        "categories": ["supplement reviews", "supplementen"],
    },
    "fit20": {
        "focus_kw": "amare fit20",
        "meta_desc": "Amare Fit20 eiwitshake review 2026: gezond en effectief? Eerlijke test met voedingswaarden, smaak en resultaten.",
        "categories": ["supplement reviews", "gewichtsbeheersing"],
    },
    "mentabiotics": {
        "focus_kw": "amare mentabiotics",
        "meta_desc": "Amare MentaBiotics review 2026: probiotica voor darm én brein. Eerlijke ervaringen en wetenschappelijke onderbouwing.",
        "categories": ["supplement reviews", "darmgezondheid", "mentale gezondheid"],
    },
    "on-shots": {
        "focus_kw": "amare on shots",
        "meta_desc": "Amare ON Shots review 2026: adaptogene energie shot getest. Werkt het echt voor snelle focus en energie?",
        "categories": ["supplement reviews", "energie & focus"],
    },
    "nitro-xtreme": {
        "focus_kw": "amare nitro xtreme",
        "meta_desc": "Amare Nitro Xtreme review 2026: doorbloeding en energie supplement getest. Eerlijke ervaringen en conclusie.",
        "categories": ["supplement reviews", "energie & focus"],
    },
    "origin-chocolate": {
        "focus_kw": "amare origin chocolate",
        "meta_desc": "Amare Origin Chocolate review 2026: vegan eiwitshake eerlijk getest. Smaak, voedingswaarden en resultaten.",
        "categories": ["supplement reviews", "gewichtsbeheersing"],
    },
    "skin-to-mind": {
        "focus_kw": "amare skin to mind",
        "meta_desc": "Amare Skin to Mind review 2026: huidverzorging van binnen en buiten getest. Eerlijke ervaringen en resultaten.",
        "categories": ["supplement reviews", "supplementen"],
    },
    "rootist": {
        "focus_kw": "amare rootist",
        "meta_desc": "Amare Rootist review 2026: oplossing tegen haaruitval? Eerlijke ervaringen met dit haarwelzijn supplement.",
        "categories": ["supplement reviews", "supplementen"],
    },
    "edge-plus-mango": {
        "focus_kw": "amare edge plus mango",
        "meta_desc": "Amare Edge Plus Mango review 2026: focus en darmgezondheid in één drank? Eerlijke ervaringen en ingrediënten.",
        "categories": ["supplement reviews", "energie & focus", "darmgezondheid"],
    },
}

# ─── Tüm postları çek ─────────────────────────────────────────────────────────
print("\n📄 Tüm postlar çekiliyor...")
all_posts = []
page = 1
while True:
    r = requests.get(f"{WP_URL}/posts", headers=headers,
                     params={"per_page": 100, "page": page}, timeout=15)
    batch = r.json()
    if not batch or r.status_code != 200:
        break
    all_posts.extend(batch)
    if len(batch) < 100:
        break
    page += 1

print(f"   {len(all_posts)} post bulundu.\n")

updated = 0
skipped = 0

for post in all_posts:
    post_id   = post["id"]
    raw_title = post["title"]["rendered"]
    slug      = post.get("slug", "")

    # Bu post ürün haritasında var mı?
    matched_key = None
    for key in PRODUCT_MAP:
        if key in slug:
            matched_key = key
            break

    payload = {}

    # Slug 2025 → 2026
    if "2025" in slug:
        payload["slug"] = slug.replace("2025", "2026")

    # Başlık 2025 → 2026
    if "2025" in raw_title:
        payload["title"] = raw_title.replace("2025", "2026")

    # Tarih bugüne çek
    payload["date"] = today

    # SEO + kategori
    if matched_key:
        info = PRODUCT_MAP[matched_key]

        # Kategori ID'lerini topla
        cat_ids = []
        for cat_name in info["categories"]:
            cid = cat_id(cat_name)
            if cid:
                cat_ids.append(cid)
        if cat_ids:
            payload["categories"] = cat_ids

        # Yoast SEO meta
        payload["meta"] = {
            "yoast_wpseo_focuskw":  info["focus_kw"],
            "yoast_wpseo_metadesc": info["meta_desc"],
        }

    if not payload or list(payload.keys()) == ["date"]:
        skipped += 1
        continue

    r = requests.post(f"{WP_URL}/posts/{post_id}", headers=headers, json=payload, timeout=20)
    if r.status_code in (200, 201):
        print(f"✅ [{post_id}] {raw_title[:55]}")
        updated += 1
    else:
        print(f"❌ [{post_id}] HATA {r.status_code}: {r.text[:100]}")

print(f"\n✅ {updated} post güncellendi, {skipped} atlandı.")
