import time
import requests
import sys
import os
import threading
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../agents/linkedin-agent"))

from cmo_agent import run_cmo
from linkedin_agent import run_linkedin

TOKEN = os.getenv("TELEGRAM_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

def safe_request(url, method="get", **kwargs):
    for i in range(5):
        try:
            if method == "get":
                response = requests.get(url, timeout=30, **kwargs)
            else:
                response = requests.post(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Bağlantı hatası (deneme {i+1}): {e}")
            time.sleep(2)
    return None

def get_updates(offset=None):
    params = {"timeout": 20}
    if offset is not None:
        params["offset"] = offset
    response = safe_request(f"{URL}/getUpdates", method="get", params=params)
    if response:
        return response.json()
    return {"result": []}

def send_message(chat_id, text):
    data = {"chat_id": chat_id, "text": text}
    safe_request(f"{URL}/sendMessage", method="post", data=data)

def process_command(chat_id, text):
    try:
        if text.startswith("/start"):
            send_message(chat_id,
                "🚀 CMO AI Bot hazır!\n\n"
                "/idea - video fikri\n"
                "/seo - başlık ve etiket\n"
                "/script - kısa video\n"
                "/cmo - pazarlama sistemi kur\n"
                "/linkedin - LinkedIn mesajı yaz"
            )

        elif text.startswith("/idea"):
            send_message(chat_id, "🔥 Düşünüyor...")
            response = run_cmo("Bana viral bir video fikri üret")
            send_message(chat_id, f"💡 Video Fikri:\n{response}")

        elif text.startswith("/seo"):
            send_message(chat_id, "🔍 SEO analiz yapıyor...")
            response = run_cmo("YouTube için SEO başlık ve etiket üret")
            send_message(chat_id, f"📋 SEO:\n{response}")

        elif text.startswith("/script"):
            send_message(chat_id, "📝 Script yazıyor...")
            response = run_cmo("Kısa bir video scripti yaz")
            send_message(chat_id, f"🎬 Script:\n{response}")

        elif text.startswith("/cmo"):
            task = text.replace("/cmo", "").strip()
            if not task:
                send_message(chat_id, "❗ Örnek: /cmo Hollanda'da lead sistemi kur")
            else:
                send_message(chat_id, "🟣 CMO düşünüyor... (30 saniye sürebilir)")
                response = run_cmo(task)
                send_message(chat_id, f"🏢 CMO:\n{response}")

        elif text.startswith("/linkedin"):
            task = text.replace("/linkedin", "").strip()
            if not task:
                send_message(chat_id,
                    "❗ Örnek kullanım:\n\n"
                    "/linkedin connectie bericht voor drukke moeders\n"
                    "/linkedin follow-up bericht na connectie\n"
                    "/linkedin waardebericht over Happy Juice\n"
                    "/linkedin zacht aanbod bericht"
                )
            else:
                send_message(chat_id, "🔗 LinkedIn mesajı hazırlanıyor... (30 saniye sürebilir)")
                response = run_linkedin(task)
                send_message(chat_id, f"💼 LinkedIn:\n{response}")

        else:
            send_message(chat_id, f"Sen yazdın: {text}")

    except Exception as e:
        print(f"Handle hatası: {e}")
        send_message(chat_id, f"❌ Hata: {e}")

def handle_command(chat_id, text):
    thread = threading.Thread(target=process_command, args=(chat_id, text))
    thread.daemon = True
    thread.start()

def main():
    print("🤖 Bot çalışıyor... Telegram'dan mesaj bekleniyor.")
    last_update_id = None

    while True:
        try:
            updates = get_updates(last_update_id)

            for update in updates.get("result", []):
                last_update_id = update["update_id"] + 1

                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"]["text"]
                    print("Gelen mesaj:", text)
                    handle_command(chat_id, text)

            time.sleep(1)

        except ConnectionError as e:
            print(f"🔴 Bağlantı koptu: {e}")
            time.sleep(15)
        except Exception as e:
            print(f"🔴 Beklenmedik hata: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()