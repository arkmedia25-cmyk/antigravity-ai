import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

def test_instagram_token():
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    biz_id = os.getenv("INSTAGRAM_BUSINESS_ID")
    
    if not token:
        print("❌ INSTAGRAM_ACCESS_TOKEN not found in .env")
        return
    
    print(f"Testing token: {token[:10]}...{token[-10:]}")
    
    # Test 1: Get User Info (Me)
    url = f"https://graph.facebook.com/v19.0/me?access_token={token}"
    try:
        res = requests.get(url).json()
        if "error" in res:
            print(f"❌ Token Validation Failed: {res['error']['message']}")
        else:
            print(f"✅ Token is VALID for User: {res.get('name')} (ID: {res.get('id')})")
            
            # Test 2: Check Business Account access if biz_id is provided
            if biz_id:
                biz_url = f"https://graph.facebook.com/v19.0/{biz_id}?fields=name,username&access_token={token}"
                biz_res = requests.get(biz_url).json()
                if "error" in biz_res:
                    print(f"❌ Business Account Access Failed: {biz_res['error']['message']}")
                else:
                    print(f"✅ Business Account Linked: {biz_res.get('name')} (@{biz_res.get('username')})")
            else:
                print("⚠️ INSTAGRAM_BUSINESS_ID not found in .env, skipping biz account check.")
                
    except Exception as e:
        print(f"⚠️ Exception during test: {e}")

if __name__ == "__main__":
    test_instagram_token()
