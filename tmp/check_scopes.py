import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

def check_token_scopes():
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    if not token:
        print("❌ INSTAGRAM_ACCESS_TOKEN not found in .env")
        return

    print(f"--- 🔍 Checking Token Scopes ---")
    
    debug_url = f"https://graph.facebook.com/debug_token?input_token={token}&access_token={token}"
    try:
        res = requests.get(debug_url).json()
        if "error" in res:
            print(f"❌ Error: {res['error']['message']}")
            # Fallback if app-level access token is needed for debug_token
            print("Trying alternate debug method...")
            url = f"https://graph.facebook.com/v19.0/me?fields=permissions&access_token={token}"
            res = requests.get(url).json()
            perms = res.get("permissions", {}).get("data", [])
            active_perms = [p['permission'] for p in perms if p['status'] == 'granted']
            print(f"✅ Granted Permissions: {', '.join(active_perms)}")
        else:
            data = res.get("data", {})
            scopes = data.get("scopes", [])
            print(f"✅ Token Scopes: {', '.join(scopes)}")
            print(f"✅ Expires: {data.get('expires_at')}")
            print(f"✅ Valid: {data.get('is_valid')}")
    except Exception as e:
        print(f"⚠️ Exception: {e}")

if __name__ == "__main__":
    check_token_scopes()
