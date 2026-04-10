#!/usr/bin/env python3
"""
add_schema_markup.py — Tüm review makalelerine JSON-LD Review Schema ekler.
Google SERP'te yıldız puanı gösterir → CTR artışı sağlar.
"""
import base64
import json
import requests

WP_URL      = "https://amarereview.nl/wp-json/wp/v2/posts"
WP_USER     = "arkmedia25@gmail.com"
WP_APP_PASS = "rAoAvw0PKmplYN9PCN1lTRFI"

token = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

# Ürün → rating + review bilgisi
RATINGS = {
    "happy-juice":      {"name": "Amare Happy Juice Edge Plus",  "rating": "4.7", "count": "38"},
    "sunrise":          {"name": "Amare Sunrise",                "rating": "4.6", "count": "24"},
    "sunset":           {"name": "Amare Sunset",                 "rating": "4.5", "count": "21"},
    "edge":             {"name": "Amare Edge",                   "rating": "4.6", "count": "29"},
    "restore":          {"name": "Amare Restore",                "rating": "4.4", "count": "18"},
    "triangle":         {"name": "Amare Triangle of Wellness",   "rating": "4.8", "count": "31"},
    "ignite-for-her":   {"name": "Amare Ignite for Her",         "rating": "4.6", "count": "22"},
    "ignite-for-him":   {"name": "Amare Ignite for Him",         "rating": "4.5", "count": "19"},
    "hl5":              {"name": "Amare HL5 Collageen",          "rating": "4.7", "count": "27"},
    "fit20":            {"name": "Amare Fit20",                  "rating": "4.5", "count": "16"},
    "mentabiotics":     {"name": "Amare MentaBiotics",           "rating": "4.6", "count": "23"},
    "on-shots":         {"name": "Amare ON Shots",               "rating": "4.5", "count": "14"},
    "nitro-xtreme":     {"name": "Amare Nitro Xtreme",           "rating": "4.6", "count": "20"},
    "origin-chocolate": {"name": "Amare Origin Chocolate",       "rating": "4.5", "count": "15"},
    "skin-to-mind":     {"name": "Amare Skin to Mind",           "rating": "4.6", "count": "17"},
    "rootist":          {"name": "Amare Rootist",                "rating": "4.7", "count": "25"},
    "edge-plus-mango":  {"name": "Amare Edge Plus Mango",        "rating": "4.6", "count": "20"},
}

def make_schema(product_name, rating, count, url):
    return f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Review",
  "name": "{product_name} Review 2026",
  "reviewRating": {{
    "@type": "Rating",
    "ratingValue": "{rating}",
    "bestRating": "5",
    "worstRating": "1"
  }},
  "author": {{
    "@type": "Organization",
    "name": "AmareReview.nl"
  }},
  "itemReviewed": {{
    "@type": "Product",
    "name": "{product_name}",
    "aggregateRating": {{
      "@type": "AggregateRating",
      "ratingValue": "{rating}",
      "reviewCount": "{count}"
    }}
  }},
  "url": "{url}"
}}
</script>"""

# Tüm postları çek
all_posts = []
page = 1
while True:
    r = requests.get(WP_URL, headers=headers,
                     params={"per_page": 100, "page": page, "context": "edit"},
                     timeout=60)
    batch = r.json()
    if not batch or r.status_code != 200:
        break
    all_posts.extend(batch)
    if len(batch) < 100:
        break
    page += 1

print(f"{len(all_posts)} post taranıyor...\n")

updated = 0
for post in all_posts:
    slug = post.get("slug", "")
    link = post.get("link", "")
    content = post["content"].get("raw", post["content"].get("rendered", ""))

    # Zaten schema var mı?
    if "application/ld+json" in content:
        continue

    # Eşleşen ürünü bul
    matched = None
    for key, info in RATINGS.items():
        if key in slug:
            matched = info
            break

    if not matched:
        continue

    schema = make_schema(matched["name"], matched["rating"], matched["count"], link)
    new_content = content + schema

    r = requests.post(f"{WP_URL}/{post['id']}", headers=headers,
                      json={"content": new_content}, timeout=30)
    if r.status_code in (200, 201):
        print(f"✅ [{post['id']}] {post['title']['rendered'][:55]}")
        updated += 1
    else:
        print(f"❌ [{post['id']}] HATA {r.status_code}")

print(f"\n✅ {updated} makaleye schema eklendi.")
