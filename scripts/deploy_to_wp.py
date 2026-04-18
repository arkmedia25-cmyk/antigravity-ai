import requests
import os
import json
import re
from dotenv import load_dotenv

# Path to the .env file in the workspace root
load_dotenv(r"c:\Users\mus-1\OneDrive\Bureaublad\Antigravity\.env")

SITE_URL = os.getenv("WP_SITE_URL")
USERNAME = os.getenv("WP_USERNAME")
PASSWORD = os.getenv("WP_APP_PASSWORD")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    session.auth = (USERNAME, PASSWORD)
    return session

def fetch_media_map():
    session = get_session()
    url = f"{SITE_URL}/wp-json/wp/v2/media"
    params = {"per_page": 100}
    print(f"Connecting to {url}...")
    try:
        response = session.get(url, params=params, timeout=15)
        response.raise_for_status()
        media = response.json()
        media_map = {item['title']['rendered'].lower(): item['source_url'] for item in media}
        print(f"Found {len(media_map)} items in Media Library.")
        return media_map
    except Exception as e:
        print(f"Error fetching media: {e}")
        return {}

def deploy_page(title, content, slug="home-page"):
    session = get_session()
    url = f"{SITE_URL}/wp-json/wp/v2/pages"
    try:
        check_resp = session.get(url, params={"slug": slug})
        check_resp.raise_for_status()
        existing_pages = check_resp.json()
        data = {
            "title": title, 
            "content": content, 
            "status": "publish", 
            "slug": slug,
            "meta": {
                "ast-main-header-display": "disabled",
                "ast-hfb-above-header-display": "disabled",
                "ast-hfb-below-header-display": "disabled",
                "ast-hfb-mobile-header-display": "disabled",
                "footer-sml-layout": "disabled",
                "site-post-title": "disabled",
                "site-content-layout": "page-builder",
                "ast-site-content-layout": "page-builder"
            }
        }
        if existing_pages:
            page_id = existing_pages[0]["id"]
            target_url = f"{url}/{page_id}"
            print(f"Updating page ID: {page_id}...")
        else:
            target_url = url
            print("Creating new page...")
        response = session.post(target_url, json=data)
        response.raise_for_status()
        result = response.json()
        print(f"Successfully deployed! URL: {result['link']}")
        return result['link']
    except Exception as e:
        print(f"Deployment error: {e}")
        return None

if __name__ == "__main__":
    html_path = r"c:\Users\mus-1\OneDrive\Bureaublad\Antigravity\amare_bridge_site\index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    media = fetch_media_map()
    # Simple replace logic for visual check
    for key, url in media.items():
        if "restore" in key: content = content.replace("https://amarenl.com/cdn/shop/files/Restore.jpg", url)
        if "happy" in key and "juice" in key: content = content.replace("https://amarenl.com/cdn/shop/files/HappyJuicePack_EDGE_Plus_MangoSunrise_EU.png", url)
    
    deploy_page("Amare Wellness", f"<!-- wp:html -->\n{content}\n<!-- /wp:html -->", slug="amarenl")
