import os
import requests
from dotenv import load_dotenv

load_dotenv()

def find_id():
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    url = "https://graph.facebook.com/v22.0/me/accounts"
    params = {"access_token": access_token, "fields": "name,instagram_business_account"}
    
    print("--- 🔍 Hunting for the correct Instagram Business ID ---")
    
    try:
        res = requests.get(url, params=params).json()
        if "data" in res:
            for page in res["data"]:
                print(f"📍 Checking Facebook Page: {page.get('name')}")
                ig_account = page.get("instagram_business_account")
                if ig_account:
                    print(f"   🎯 FOUND Instagram Business ID: {ig_account.get('id')}")
                else:
                    print("   ❌ No Instagram Business Account linked to this page.")
        else:
            print(f"❌ Error: {res.get('error', {}).get('message')}")
    except Exception as e:
        print(f"⚠️ Exception: {e}")

if __name__ == "__main__":
    find_id()
