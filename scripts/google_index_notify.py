#!/usr/bin/env python3
"""
google_index_notify.py — Yeni/güncellenen postları Google & Bing'e bildirir.

Yöntem 1: Sitemap ping (credentials gerekmez)
Yöntem 2: Google Indexing API (service account JSON gerekir)

Kullanım:
  python3 google_index_notify.py                  # Sitemap ping
  python3 google_index_notify.py --api            # Indexing API (service account gerekli)
  python3 google_index_notify.py --url <url>      # Tek URL indexing API
"""
import sys
import base64
import requests
from datetime import datetime, timezone

WP_URL      = "https://amarereview.nl/wp-json/wp/v2/posts"
WP_USER     = "arkmedia25@gmail.com"
WP_APP_PASS = "rAoAvw0PKmplYN9PCN1lTRFI"
SITE_URL    = "https://amarereview.nl"
SITEMAP_URL = "https://amarereview.nl/sitemap_index.xml"

# ─── Yöntem 1: Sitemap Ping ────────────────────────────────────────────────────
def ping_sitemap():
    engines = {
        "Google": f"https://www.google.com/ping?sitemap={SITEMAP_URL}",
        "Bing":   f"https://www.bing.com/ping?sitemap={SITEMAP_URL}",
    }
    print("📡 Sitemap ping gönderiliyor...\n")
    for name, url in engines.items():
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                print(f"✅ {name}: Sitemap bildirildi")
            else:
                print(f"⚠️  {name}: HTTP {r.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")


# ─── Yöntem 2: Google Indexing API ────────────────────────────────────────────
def index_urls_via_api(urls: list, service_account_json: str):
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        print("❌ google-auth kütüphanesi eksik:")
        print("   pip3 install google-auth google-api-python-client")
        return

    SCOPES = ["https://www.googleapis.com/auth/indexing"]
    creds = service_account.Credentials.from_service_account_file(
        service_account_json, scopes=SCOPES
    )
    service = build("indexing", "v3", credentials=creds)

    print(f"\n🔍 Google Indexing API — {len(urls)} URL gönderiliyor...\n")
    for url in urls:
        try:
            body = {"url": url, "type": "URL_UPDATED"}
            resp = service.urlNotifications().publish(body=body).execute()
            print(f"✅ {url}")
        except Exception as e:
            print(f"❌ {url}: {e}")


# ─── Son güncellenen postları çek ─────────────────────────────────────────────
def get_recent_urls(days: int = 1) -> list:
    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
    headers = {"Authorization": f"Basic {token}"}
    after = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00")
    r = requests.get(WP_URL, headers=headers,
                     params={"per_page": 100, "after": after, "status": "publish"},
                     timeout=30)
    posts = r.json() if r.status_code == 200 else []
    urls = [p["link"] for p in posts if "link" in p]
    print(f"📋 Bugün güncellenen/eklenen {len(urls)} post bulundu.")
    return urls


# ─── Ana ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    use_api   = "--api" in sys.argv
    single_url = None
    if "--url" in sys.argv:
        idx = sys.argv.index("--url")
        single_url = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None

    # Her zaman sitemap ping yap
    ping_sitemap()

    if use_api or single_url:
        import os
        sa_file = os.getenv("GOOGLE_SA_JSON", "/root/antigravity-ai/google_service_account.json")
        if not os.path.exists(sa_file):
            print(f"\n⚠️  Google service account bulunamadı: {sa_file}")
            print("   Kurmak için: https://console.cloud.google.com/iam-admin/serviceaccounts")
            print("   JSON dosyasını /root/antigravity-ai/google_service_account.json olarak kaydet")
            print("   Search Console'da bu service account'a Owner yetkisi ver")
            sys.exit(1)

        urls = [single_url] if single_url else get_recent_urls()
        if urls:
            index_urls_via_api(urls, sa_file)
        else:
            print("ℹ️  Bugün güncellenmiş post yok.")
    else:
        # Sitemap ping yeterliyse bugünkü URL'leri listele
        urls = get_recent_urls()
        if urls:
            print("\n📎 Bugün güncellenen URL'ler:")
            for u in urls:
                print(f"   {u}")
