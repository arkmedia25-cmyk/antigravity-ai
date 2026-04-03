import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

def find_instagram_ids_debug():
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    if not token:
        print("❌ INSTAGRAM_ACCESS_TOKEN not found in .env")
        return

    print(f"--- 🔍 Finding Instagram Business ID ---")
    
    # 1. Get User Info
    me_url = f"https://graph.facebook.com/v19.0/me?fields=name,id&access_token={token}"
    me_res = requests.get(me_url).json()
    print(f"User: {me_res.get('name')} ({me_res.get('id')})")

    # 2. Get Facebook Pages
    url = f"https://graph.facebook.com/v19.0/me/accounts?fields=name,id,access_token&access_token={token}"
    try:
        res = requests.get(url).json()
        if "error" in res:
            print(f"❌ Error fetching pages: {res['error']['message']}")
            return
        
        pages = res.get("data", [])
        print(f"Found {len(pages)} Facebook Page(s).")
        
        for page in pages:
            page_name = page.get("name")
            page_id = page.get("id")
            
            # 3. Get Instagram Business Account for this Page
            ig_url = f"https://graph.facebook.com/v19.0/{page_id}?fields=instagram_business_account&access_token={token}"
            ig_res = requests.get(ig_url).json()
            
            ig_auth = ig_res.get("instagram_business_account")
            if ig_auth:
                ig_id = ig_auth.get("id")
                # 4. Get IG Details (Username)
                det_url = f"https://graph.facebook.com/v19.0/{ig_id}?fields=username,name&access_token={token}"
                det_res = requests.get(det_url).json()
                print(f"✅ FOUND IG: {det_res.get('username')} (Name: {det_res.get('name')}) -> ID: {ig_id}")
            else:
                print(f"   (No IG linked to {page_name})")
                
    except Exception as e:
        print(f"⚠️ Exception: {e}")

if __name__ == "__main__":
    find_instagram_ids_debug()
