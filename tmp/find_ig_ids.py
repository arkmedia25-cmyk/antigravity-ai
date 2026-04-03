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
    
    # 1. Get Facebook Pages
    url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={token}"
    try:
        res = requests.get(url).json()
        if "error" in res:
            print(f"❌ Error fetching pages: {res['error']['message']}")
            return
        
        pages = res.get("data", [])
        if not pages:
            print("❌ No Facebook Pages found for this user.")
            return
        
        print(f"Found {len(pages)} Facebook Page(s). Checking for linked Instagram accounts...")
        
        for page in pages:
            page_name = page.get("name")
            page_id = page.get("id")
            page_token = page.get("access_token")
            
            # 2. Get Instagram Business Account for this Page
            ig_url = f"https://graph.facebook.com/v19.0/{page_id}?fields=instagram_business_account&access_token={token}"
            ig_res = requests.get(ig_url).json()
            
            ig_auth = ig_res.get("instagram_business_account")
            if ig_auth:
                ig_id = ig_auth.get("id")
                # 3. Get IG Details (Username)
                det_url = f"https://graph.facebook.com/v19.0/{ig_id}?fields=username,name&access_token={token}"
                det_res = requests.get(det_url).json()
                print(f"✅ FOUND: {det_res.get('name')} (@{det_res.get('username')}) -> ID: {ig_id}")
                print(f"Suggested .env entry: INSTAGRAM_BUSINESS_ID={ig_id}")
            else:
                print(f"ℹ️ Page '{page_name}' has no linked Instagram Business Account.")
                
    except Exception as e:
        print(f"⚠️ Exception: {e}")

if __name__ == "__main__":
    find_instagram_ids()
