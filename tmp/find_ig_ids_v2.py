import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

def find_instagram_ids():
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    if not token:
        print("❌ INSTAGRAM_ACCESS_TOKEN not found in .env")
        return

    print(f"--- 🔍 Finding Instagram Business ID ---")
    
    url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={token}"
    try:
        res = requests.get(url).json()
        if "error" in res:
            print(f"❌ Error: {res['error']['message']}")
            return
        
        pages = res.get("data", [])
        for page in pages:
            page_id = page.get("id")
            page_name = page.get("name")
            
            ig_url = f"https://graph.facebook.com/v19.0/{page_id}?fields=instagram_business_account&access_token={token}"
            ig_res = requests.get(ig_url).json()
            
            ig_auth = ig_res.get("instagram_business_account")
            if ig_auth:
                ig_id = ig_auth.get("id")
                det_url = f"https://graph.facebook.com/v19.0/{ig_id}?fields=username,name&access_token={token}"
                det_res = requests.get(det_url).json()
                print(f"✅ FOUND: {det_res.get('name')} (@{det_res.get('username')}) -> ID: {ig_id}")
    except Exception as e:
        print(f"⚠️ Exception: {e}")

if __name__ == "__main__":
    find_instagram_ids()
