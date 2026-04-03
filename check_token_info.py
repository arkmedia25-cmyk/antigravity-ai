import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_accounts():
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    
    print("--- 🔍 Checking Token Permissions and Accounts ---")
    
    # 1. Get Facebook Pages
    pages_url = "https://graph.facebook.com/v22.0/me/accounts"
    params = {"access_token": access_token}
    
    try:
        response = requests.get(pages_url, params=params)
        pages_data = response.json()
        
        if "data" in pages_data:
            print(f"Found {len(pages_data['data'])} Facebook Pages linked to this token.\n")
            for page in pages_data["data"]:
                page_name = page.get("name")
                page_id = page.get("id")
                print(f"📍 Page: {page_name} (ID: {page_id})")
                
                # Check for linked Instagram Business Accounts
                ig_url = f"https://graph.facebook.com/v22.0/{page_id}"
                ig_params = {
                    "fields": "instagram_business_account",
                    "access_token": access_token
                }
                ig_res = requests.get(ig_url, params=ig_params).json()
                
                ig_account = ig_res.get("instagram_business_account")
                if ig_account:
                    print(f"   ✅ Linked Instagram Business ID: {ig_account.get('id')}")
                else:
                    print("   ❌ No linked Instagram Business Account found for this page.")
        else:
            print(f"❌ Error fetching pages: {pages_data.get('error', {}).get('message', 'Unknown Error')}")
            
    except Exception as e:
        print(f"⚠️ Exception: {e}")

if __name__ == "__main__":
    check_accounts()
