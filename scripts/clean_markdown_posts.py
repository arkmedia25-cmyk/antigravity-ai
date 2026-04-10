#!/usr/bin/env python3
"""
clean_markdown_posts.py — Mevcut WordPress postlarındaki ```html bloklarını temizler
"""
import base64
import re
import requests

WP_URL      = "https://amarereview.nl/wp-json/wp/v2/posts"
WP_USER     = "arkmedia25@gmail.com"
WP_APP_PASS = "rAoAvw0PKmplYN9PCN1lTRFI"

token = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

# Tüm postları çek
all_posts = []
page = 1
while True:
    r = requests.get(WP_URL, headers=headers, params={"per_page": 100, "page": page}, timeout=60)
    batch = r.json()
    if not batch or r.status_code != 200:
        break
    all_posts.extend(batch)
    if len(batch) < 100:
        break
    page += 1

print(f"{len(all_posts)} post taranıyor...\n")

cleaned = 0
for post in all_posts:
    content = post["content"]["rendered"]
    if "```" in content:
        new_content = re.sub(r'```[a-z]*\n?', '', content)
        new_content = re.sub(r'\n?```', '', new_content)
        r = requests.post(f"{WP_URL}/{post['id']}", headers=headers,
                          json={"content": new_content}, timeout=20)
        if r.status_code in (200, 201):
            print(f"✅ Temizlendi: {post['title']['rendered'][:60]}")
            cleaned += 1
        else:
            print(f"❌ HATA [{post['id']}]: {r.status_code}")

print(f"\n{cleaned} post temizlendi.")
