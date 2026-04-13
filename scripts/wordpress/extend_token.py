import os
import requests
from dotenv import load_dotenv

load_dotenv()

def extend_meta_token():
    app_id = os.getenv("META_APP_ID")
    app_secret = os.getenv("META_APP_SECRET")
    short_lived_token = "EAAktZAsle4pMBRGJ9xpl2jUqXIXnFftRM1dvhpSn9BuYiKHV37S5kR4ejyGyXdWjrLu1ZChgZBTorgeT8ZCUpox7MUM1fx7eFyRmMZAkVJLtMZAaMcLLatFYsvvYekrO2xTVPNsuA24MYnbcDPAJeLXWQNNCaoXWi8uIieowNgVkU7vuo2GmvQ8CZAqKZAEJLWxfp49kFtB4lGLbFdhjmZAvp8bkYyG6gVarPsIaZBQKO6yrlXKvXj914sKIrmhmqblqZCAloxkLhgpT8gwj9PLa44Fd2ySTtJZCmSYdOQZDZD"
    
    print(f"--- 🔄 Meta Token Extension Started (App: {app_id}) ---")
    
    url = "https://graph.facebook.com/v22.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_token
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "access_token" in data:
            long_lived_token = data["access_token"]
            print(f"✅ Success! Long-Lived Token obtained.")
            print(f"TOKEN_RESULT:{long_lived_token}")
            return long_lived_token
        else:
            print(f"❌ Error: {data.get('error', {}).get('message', 'Unknown Error')}")
            return None
    except Exception as e:
        print(f"⚠️ Exception: {e}")
        return None

if __name__ == "__main__":
    extend_meta_token()
