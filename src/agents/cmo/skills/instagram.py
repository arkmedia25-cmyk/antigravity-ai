# -*- coding: utf-8 -*-
"""
CMO Agent — Instagram Graph API Reel publisher.
.env gerekli:
  INSTAGRAM_ACCESS_TOKEN=...
  INSTAGRAM_BUSINESS_ID_HOLISTIGLOW=17841474979967259
  INSTAGRAM_BUSINESS_ID_GLOWUP=17841407710796044
"""
import os
import time
import requests
from src.core.logging import get_logger

logger = get_logger("cmo.instagram")

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
GRAPH_URL    = "https://graph.facebook.com/v19.0"

_BRAND_IDS = {
    "holistiglow": os.getenv("INSTAGRAM_BUSINESS_ID_HOLISTIGLOW", "17841474979967259"),
    "glowup":      os.getenv("INSTAGRAM_BUSINESS_ID_GLOWUP",      "17841407710796044"),
}
_DEFAULT_ID = os.getenv("INSTAGRAM_BUSINESS_ID", "17841474979967259")


def _get_business_id(brand: str = "") -> str:
    return _BRAND_IDS.get(brand.lower(), _DEFAULT_ID)


def post_reel(video_url: str, caption: str, brand: str = "") -> tuple[bool, str]:
    """
    Post een Reel naar Instagram via Graph API.
    brand: 'holistiglow' | 'glowup'
    Returns: (success, message)
    """
    if not ACCESS_TOKEN:
        return False, "INSTAGRAM_ACCESS_TOKEN ontbreekt in .env"

    business_id = _get_business_id(brand)
    logger.info(f"Instagram [{brand}]: container aanmaken voor {business_id}...")

    r = requests.post(
        f"{GRAPH_URL}/{business_id}/media",
        params={
            "media_type":   "REELS",
            "video_url":    video_url,
            "caption":      caption,
            "access_token": ACCESS_TOKEN,
        },
        timeout=30,
    )

    if not r.ok:
        msg = r.json().get("error", {}).get("message", r.text[:200])
        logger.error(f"Container fout: {msg}")
        return False, f"Container fout: {msg}"

    container_id = r.json().get("id")
    if not container_id:
        return False, "Geen container ID ontvangen"

    logger.info(f"Container {container_id} — wachten op verwerking...")

    for attempt in range(12):
        time.sleep(10)
        status_r = requests.get(
            f"{GRAPH_URL}/{container_id}",
            params={"fields": "status_code", "access_token": ACCESS_TOKEN},
            timeout=15,
        )
        status = status_r.json().get("status_code", "")
        logger.info(f"Status ({attempt+1}/12): {status}")

        if status == "FINISHED":
            break
        elif status == "ERROR":
            return False, "Video verwerking mislukt (ERROR)"
    else:
        return False, "Timeout: verwerking duurde te lang"

    pub_r = requests.post(
        f"{GRAPH_URL}/{business_id}/media_publish",
        params={"creation_id": container_id, "access_token": ACCESS_TOKEN},
        timeout=30,
    )

    if not pub_r.ok:
        msg = pub_r.json().get("error", {}).get("message", pub_r.text[:200])
        logger.error(f"Publish fout: {msg}")
        return False, f"Publish fout: {msg}"

    post_id = pub_r.json().get("id", "")
    logger.info(f"Reel gepubliceerd [{brand}]: {post_id}")
    return True, f"Gepubliceerd! Post ID: {post_id}"
