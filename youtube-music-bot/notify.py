import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEFAULT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send(message: str, chat_id: str = "") -> None:
    if not BOT_TOKEN:
        print("[notify] Telegram yapılandırılmamış, bildirim atlandı")
        return

    target = chat_id or DEFAULT_CHAT_ID
    resp = requests.post(f"{BASE_URL}/sendMessage", json={
        "chat_id": target,
        "text": message,
        "parse_mode": "HTML",
    }, timeout=15)
    resp.raise_for_status()
    print(f"[notify] Telegram: gönderildi")


def success(title: str, url: str, duration_min: int, chat_id: str = "") -> None:
    send(
        f"✅ <b>Yeni video yüklendi</b>\n\n"
        f"🎵 {title}\n"
        f"⏱ {duration_min} dakika\n"
        f"🔗 {url}",
        chat_id
    )


def error(step: str, detail: str, chat_id: str = "") -> None:
    send(
        f"❌ <b>Hata: {step}</b>\n\n"
        f"<code>{detail[:300]}</code>",
        chat_id
    )
