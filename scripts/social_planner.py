#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
social_planner.py — Dagelijkse reel generator + Telegram goedkeuring.

Genereert een reel voor het gegeven merk en stuurt naar Telegram voor goedkeuring.
De gebruiker kan dan downloaden, aanpassen of publiceren via Instagram/TikTok/YouTube.

Gebruik:
  python3 scripts/social_planner.py holistiglow
  python3 scripts/social_planner.py glowup

Optimale cron voor Nederland (CET):
  30 9  * * 1-5 cd /root/antigravity-ai && venv/bin/python3 scripts/social_planner.py holistiglow >> logs/social.log 2>&1
  0  11 * * *   cd /root/antigravity-ai && venv/bin/python3 scripts/social_planner.py glowup      >> logs/social.log 2>&1
  0  17 * * 1-5 cd /root/antigravity-ai && venv/bin/python3 scripts/social_planner.py holistiglow >> logs/social.log 2>&1
  30 19 * * *   cd /root/antigravity-ai && venv/bin/python3 scripts/social_planner.py glowup      >> logs/social.log 2>&1
"""
import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime

_DIR  = Path(__file__).parent
_ROOT = _DIR.parent
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "812914122")

# Approval state: video id → metadata, opgeslagen in .social_approvals.json
APPROVALS_FILE = _ROOT / ".social_approvals.json"

PLATFORM_LABELS = {
    "ig":  "📸 Instagram",
    "tt":  "🎵 TikTok",
    "yt":  "▶️ YouTube",
    "all": "🌐 Alle platforms",
}


def _load_approvals() -> dict:
    try:
        return json.loads(APPROVALS_FILE.read_text()) if APPROVALS_FILE.exists() else {}
    except Exception:
        return {}


def _save_approvals(data: dict):
    APPROVALS_FILE.write_text(json.dumps(data, indent=2))


def _new_id() -> str:
    return str(int(time.time()))[-6:]


def _send_telegram(chat_id: str, text: str, video_path: str | None = None,
                   reply_markup: dict | None = None):
    base = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    if video_path and Path(video_path).exists():
        with open(video_path, "rb") as f:
            data: dict = {"chat_id": chat_id, "caption": text, "parse_mode": "Markdown"}
            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)
            requests.post(f"{base}/sendVideo", data=data,
                          files={"video": f}, timeout=120)
    else:
        payload: dict = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
        requests.post(f"{base}/sendMessage", json=payload, timeout=30)


def notify_approval(brand: str, video_path: str, topic: str, style: str):
    """Stuur video naar Telegram met goedkeuringsbuttons."""
    vid_id = _new_id()
    approvals = _load_approvals()
    approvals[vid_id] = {
        "path":   video_path,
        "brand":  brand,
        "topic":  topic,
        "style":  style,
        "ts":     datetime.now().isoformat(),
    }
    _save_approvals(approvals)

    handle_map = {"holistiglow": "@HolistiGlow", "glowup": "@GlowUpNL"}
    handle = handle_map.get(brand, brand)

    caption = (
        f"🎬 *Nieuwe reel klaar!*\n\n"
        f"🏷 Merk : {handle}\n"
        f"📌 Topic: `{topic}`\n"
        f"🎨 Stijl: `{style}`\n\n"
        f"Kies wat je wilt doen:"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "⬇️ Download", "callback_data": f"dl_{vid_id}"},
                {"text": "✏️ Aanpassen", "callback_data": f"rev_{vid_id}"},
            ],
            [
                {"text": "📸 Instagram",     "callback_data": f"pub_ig_{vid_id}"},
                {"text": "🎵 TikTok",        "callback_data": f"pub_tt_{vid_id}"},
            ],
            [
                {"text": "▶️ YouTube",       "callback_data": f"pub_yt_{vid_id}"},
                {"text": "🌐 Alle platforms","callback_data": f"pub_all_{vid_id}"},
            ],
        ]
    }

    _send_telegram(TELEGRAM_CHAT_ID, caption, video_path=video_path, reply_markup=keyboard)
    print(f"[{datetime.now()}] Telegram: goedkeuring verstuurd (id={vid_id})")


def run(brand: str = "holistiglow"):
    print(f"\n[{datetime.now()}] Social Planner — {brand}")

    sys.path.insert(0, str(_DIR))
    from amarenl_reel_maker import run as make_reel, get_next_topic

    topic = get_next_topic(brand)
    print(f"  Topic: {topic}")

    video_path = make_reel(topic_key=topic, brand=brand)
    if not video_path:
        print(f"[{datetime.now()}] FOUT: video generatie mislukt")
        sys.exit(1)

    # Lees gebruikte stijl uit de state
    from amarenl_reel_maker import STYLE_STATE, load_brand_config
    try:
        state = json.loads(Path(STYLE_STATE).read_text())
        cfg = load_brand_config(brand)
        style_idx = state.get(f"last_{brand}", 0)
        style_name = cfg.STYLES[style_idx]["name"]
    except Exception:
        style_name = "onbekend"

    notify_approval(brand, video_path, topic, style_name)
    print(f"[{datetime.now()}] Klaar: {video_path}")


if __name__ == "__main__":
    _brand = sys.argv[1] if len(sys.argv) > 1 else "holistiglow"
    if _brand not in ("holistiglow", "glowup"):
        print(f"Onbekend merk: {_brand}. Gebruik: holistiglow of glowup")
        sys.exit(1)
    run(_brand)
