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

# ─── Ürün → SEO + Kategori Haritası (keyword research 2026-04-10) ─────────────
PRODUCT_MAP = {
    "happy-juice": {
        "focus_kw": "amare happy juice ervaringen",
        "meta_desc": "Amare Happy Juice ervaringen 2026 – werkt het echt? ✅ Eerlijke review na 30 dagen: ingrediënten, bijwerkingen, prijs en waar te kopen.",
        "categories": ["supplement reviews", "energie & focus"],
    },
    "sunrise": {
        "focus_kw": "amare sunrise ervaringen",
        "meta_desc": "Amare Sunrise ervaringen 2026 – getest! Ochtendenergie supplement: ingrediënten, bijwerkingen en eerlijk eindoordeel. Lees voor je koopt.",
        "categories": ["supplement reviews", "energie & focus"],
    },
    "sunset": {
        "focus_kw": "amare sunset ervaringen",
        "meta_desc": "Amare Sunset ervaringen 2026 – beter slapen? Eerlijke test na 30 dagen: werking, bijwerkingen en is het de prijs waard?",
        "categories": ["supplement reviews", "slaap & ontspanning"],
    },
    "edge": {
        "focus_kw": "amare edge ervaringen",
        "meta_desc": "Amare Edge ervaringen 2026 – meer focus en energie? ✅ Eerlijke review: ingrediënten, bijwerkingen, prijs en waar kopen in Nederland.",
        "categories": ["supplement reviews", "mentale gezondheid"],
    },
    "restore": {
        "focus_kw": "amare restore ervaringen",
        "meta_desc": "Amare Restore ervaringen 2026 – darmgezondheid supplement getest. Eerlijke review: werking, bijwerkingen en conclusie na 30 dagen.",
        "categories": ["supplement reviews", "darmgezondheid"],
    },
    "triangle": {
        "focus_kw": "amare triangle of wellness ervaringen",
        "meta_desc": "Amare Triangle of Wellness ervaringen 2026 – compleet pakket getest. Eerlijke review: wat zit erin, werkt het en is het de prijs waard?",
        "categories": ["supplement reviews", "supplementen"],
    },
    "ignite-for-her": {
        "focus_kw": "amare ignite for her ervaringen",
        "meta_desc": "Amare Ignite for Her ervaringen 2026 – hormoonbalans supplement voor vrouwen getest. Bijwerkingen, ingrediënten en eerlijk oordeel.",
        "categories": ["supplement reviews", "immuunsysteem"],
    },
    "ignite-for-him": {
        "focus_kw": "amare ignite for him ervaringen",
        "meta_desc": "Amare Ignite for Him ervaringen 2026 – testosteron supplement getest. Werkt het echt? Ingrediënten, bijwerkingen en waar kopen.",
        "categories": ["supplement reviews", "energie & focus"],
    },
    "hl5": {
        "focus_kw": "amare hl5 collageen ervaringen",
        "meta_desc": "Amare HL5 Collageen ervaringen 2026 – huid, haar en gewrichten supplement getest. Eerlijke review: werking, bijwerkingen en prijs.",
        "categories": ["supplement reviews", "supplementen"],
    },
    "fit20": {
        "focus_kw": "amare fit20 ervaringen",
        "meta_desc": "Amare Fit20 ervaringen 2026 – eiwitshake getest. Eerlijke review: smaak, voedingswaarden, bijwerkingen en is het de prijs waard?",
        "categories": ["supplement reviews", "gewichtsbeheersing"],
    },
    "mentabiotics": {
        "focus_kw": "amare mentabiotics ervaringen",
        "meta_desc": "Amare MentaBiotics ervaringen 2026 – darm-hersenas probiotica getest. Werkt het echt voor mentale balans? Eerlijke review met bijwerkingen.",
        "categories": ["supplement reviews", "darmgezondheid", "mentale gezondheid"],
    },
    "on-shots": {
        "focus_kw": "amare on shots ervaringen",
        "meta_desc": "Amare ON Shots ervaringen 2026 – adaptogene energie shot getest. Snelle focus en energie? Eerlijke review: ingrediënten en bijwerkingen.",
        "categories": ["supplement reviews", "energie & focus"],
    },
    "nitro-xtreme": {
        "focus_kw": "amare nitro xtreme ervaringen",
        "meta_desc": "Amare Nitro Xtreme ervaringen 2026 – doorbloeding supplement getest. Werkt het echt? Eerlijke review: ingrediënten, bijwerkingen en prijs.",
        "categories": ["supplement reviews", "energie & focus"],
    },
    "origin-chocolate": {
        "focus_kw": "amare origin chocolate ervaringen",
        "meta_desc": "Amare Origin Chocolate ervaringen 2026 – vegan eiwitshake eerlijk getest. Smaak, voedingswaarden, bijwerkingen en conclusie.",
        "categories": ["supplement reviews", "gewichtsbeheersing"],
    },
    "skin-to-mind": {
        "focus_kw": "amare skin to mind ervaringen",
        "meta_desc": "Amare Skin to Mind ervaringen 2026 – huidverzorging supplement getest. Werkt het van binnen én buiten? Eerlijke review met resultaten.",
        "categories": ["supplement reviews", "supplementen"],
    },
    "rootist": {
        "focus_kw": "amare rootist ervaringen",
        "meta_desc": "Amare Rootist ervaringen 2026 – haaruitval supplement getest. Werkt het echt voor haargroei? Eerlijke review: ingrediënten en resultaten.",
        "categories": ["supplement reviews", "supplementen"],
    },
    "edge-plus-mango": {
        "focus_kw": "amare edge plus mango ervaringen",
        "meta_desc": "Amare Edge Plus Mango ervaringen 2026 – focus en darmgezondheid in één drank? Eerlijke review: ingrediënten, bijwerkingen en waar kopen.",
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
