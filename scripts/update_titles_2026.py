#!/usr/bin/env python3
"""
update_titles_2026.py — amarereview.nl'deki tüm 2025 başlıklı postları 2026 yapar
"""
import base64
import requests

WP_URL      = "https://amarereview.nl/wp-json/wp/v2/posts"
WP_USER     = "arkmedia25@gmail.com"
WP_APP_PASS = "rAoAvw0PKmplYN9PCN1lTRFI"

token = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

# Tüm postları çek (sayfalı)
all_posts = []
page = 1
while True:
    r = requests.get(WP_URL, headers=headers, params={"per_page": 100, "page": page}, timeout=15)
    if r.status_code != 200 or not r.json():
        break
    all_posts.extend(r.json())
    if len(r.json()) < 100:
        break
    page += 1

print(f"Toplam {len(all_posts)} post bulundu.")

updated = 0
for post in all_posts:
    raw_title = post["title"]["rendered"]
    if "2025" in raw_title:
        new_title = raw_title.replace("2025", "2026")
        r = requests.post(
            f"{WP_URL}/{post['id']}",
            headers=headers,
            json={"title": new_title},
            timeout=15
        )
        if r.status_code in (200, 201):
            print(f"✅ {raw_title[:60]} → 2026")
            updated += 1
        else:
            print(f"❌ HATA ({r.status_code}): {raw_title[:60]}")

print(f"\nToplam {updated} post güncellendi.")
