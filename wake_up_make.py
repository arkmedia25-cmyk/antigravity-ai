import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

def send_test_ping():
    url = os.getenv("MAKE_WEBHOOK_URL")
    data = {
        "video_url": "https://files.catbox.moe/rhqjlc.mp4",
        "caption": "Test Hook - Antigravity AI",
        "brand": "GlowUpNL"
    }
    
    print(f"--- 📡 Sending Test Ping to Make.com ---")
    print(f"URL: {url}")
    
    try:
        # 3 deneme yapalım garanti olsun
        for i in range(3):
            print(f"Attempt {i+1}...")
            response = requests.post(url, json=data)
            print(f"Response {i+1}: {response.status_code} - {response.text}")
            time.sleep(2)
            
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    send_test_ping()
