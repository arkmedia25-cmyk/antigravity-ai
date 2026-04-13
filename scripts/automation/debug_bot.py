import requests
import os
from dotenv import load_dotenv

def check_bot_status():
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("TELEGRAM_TOKEN not found in .env")
        return

    print(f"Checking status for token: {token[:10]}...")
    
    # 1. getMe
    r_me = requests.get(f"https://api.telegram.org/bot{token}/getMe")
    print(f"getMe: {r_me.json()}")
    
    # 2. getWebhookInfo
    r_webhook = requests.get(f"https://api.telegram.org/bot{token}/getWebhookInfo")
    print(f"getWebhookInfo: {r_webhook.json()}")
    
    # 3. deleteWebhook (to clear any conflicts)
    print("Attempting to delete webhook...")
    r_delete = requests.get(f"https://api.telegram.org/bot{token}/deleteWebhook")
    print(f"deleteWebhook result: {r_delete.json()}")

if __name__ == "__main__":
    check_bot_status()
