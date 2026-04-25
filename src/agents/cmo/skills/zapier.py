# -*- coding: utf-8 -*-
"""
CMO Agent — platform publisher (Instagram direct, TikTok/YouTube via Zapier).
.env gereken:
  ZAPIER_WEBHOOK_TIKTOK=https://hooks.zapier.com/hooks/catch/xxx/zzz/
  ZAPIER_WEBHOOK_YOUTUBE=https://hooks.zapier.com/hooks/catch/xxx/www/
"""
import os
import requests
from src.core.logging import get_logger

logger = get_logger("cmo.zapier")

PLATFORM_ENV = {
    "ig":  "ZAPIER_WEBHOOK_INSTAGRAM",
    "tt":  "ZAPIER_WEBHOOK_TIKTOK",
    "yt":  "ZAPIER_WEBHOOK_YOUTUBE",
}


def post_via_zapier(platform: str, video_url: str, caption: str,
                    brand: str = "", topic: str = "") -> tuple[bool, str]:
    if platform == "ig":
        from src.agents.cmo.skills.instagram import post_reel
        return post_reel(video_url, caption, brand=brand)

    env_key = PLATFORM_ENV.get(platform)
    if not env_key:
        return False, f"Onbekend platform: {platform}"

    webhook_url = os.getenv(env_key)
    if not webhook_url:
        return False, f"{env_key} niet ingesteld in .env"

    payload = {
        "video_url": video_url,
        "caption":   caption,
        "brand":     brand,
        "topic":     topic,
        "platform":  platform,
    }

    try:
        r = requests.post(webhook_url, json=payload, timeout=15)
        if r.ok:
            logger.info(f"Zapier {platform} OK: {r.status_code}")
            return True, f"Verstuurd naar Zapier ({platform.upper()})"
        else:
            logger.error(f"Zapier {platform} fout: {r.status_code} {r.text[:200]}")
            return False, f"Zapier fout {r.status_code}: {r.text[:100]}"
    except Exception as e:
        logger.error(f"Zapier {platform} exception: {e}")
        return False, str(e)


def post_to_all(video_url: str, caption: str, brand: str = "", topic: str = "") -> dict:
    results = {}
    for platform in PLATFORM_ENV:
        ok, msg = post_via_zapier(platform, video_url, caption, brand, topic)
        results[platform] = (ok, msg)
    return results
