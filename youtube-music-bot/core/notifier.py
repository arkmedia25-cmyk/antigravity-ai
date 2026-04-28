"""Telegram notifications — pipeline results and errors."""
import os
import sys
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEFAULT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send(message: str, chat_id: str = "") -> None:
    if not BOT_TOKEN:
        print("[notifier] Telegram token missing, skipped")
        return

    target = chat_id or DEFAULT_CHAT_ID
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": target, "text": message, "parse_mode": "HTML"},
            timeout=15,
        ).raise_for_status()
        print("[notifier] Telegram: sent")
    except Exception as e:
        print(f"[notifier] Telegram error: {e}")


def channel_report(channel_name: str, report: str, chat_id: str = "") -> None:
    send(f"📊 <b>{channel_name} Weekly Report</b>\n\n{report}", chat_id)


def orchestrator_summary(summary: str, chat_id: str = "") -> None:
    send(f"🎯 <b>Orchestrator Summary</b>\n\n{summary}", chat_id)


def error(source: str, detail: str, chat_id: str = "") -> None:
    send(f"❌ <b>Error [{source}]</b>\n<code>{detail[:300]}</code>", chat_id)
