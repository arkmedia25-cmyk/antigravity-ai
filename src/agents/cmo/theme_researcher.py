#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Günlük tema araştırması — Burak araştırmasını JSON'a dönüştür.

Her gün 07:00'de çalışır, NL wellness trendlerini araştırıp
daily_themes_YYYY-MM-DD.json oluşturur.

Çıktı:
  src/social_themes/daily_themes_2026-05-09.json

Içerik:
  {
    "date": "2026-05-09",
    "holistiglow": [
      {"topic_key": "magnesium_sleep", "hook": "...", "content": [...], ...},
      ...
    ],
    "glowup": [...]
  }
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Dosya yolları
_DIR = Path(__file__).parent  # src/agents/cmo/
_ROOT = _DIR.parent.parent.parent  # antitravity-ai root
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

# Çıktı dizini
THEMES_DIR = _DIR / "social_themes"
THEMES_DIR.mkdir(exist_ok=True)

PUBLISHED_FILE = THEMES_DIR / "published_titles.json"

# Burak araştırmasını yükle
try:
    import sys as _sys
    _sys.path.insert(0, "/c/tmp/ark_agents")
    from agents.research_agent import research_trends
except ImportError:
    research_trends = None


def load_published_titles() -> dict:
    """Yayınlanan başlıkları yükle."""
    try:
        return json.loads(PUBLISHED_FILE.read_text(encoding="utf-8")) if PUBLISHED_FILE.exists() else {"holistiglow": [], "glowup": []}
    except Exception:
        return {"holistiglow": [], "glowup": []}


def is_title_published(brand: str, hook: str, full_title: str) -> bool:
    """Başlık daha önce yayınlandı mı kontrol et."""
    published = load_published_titles()
    brand_history = published.get(brand, [])

    # Hook veya full_title eşleşirse -> published
    for item in brand_history:
        if (item.get("hook") == hook or
            item.get("full_title") == full_title or
            item.get("hook") in full_title):  # partial match
            return True
    return False


def mark_title_published(brand: str, topic_key: str, hook: str, full_title: str):
    """Başlığı yayınlanan listesine ekle."""
    published = load_published_titles()
    if brand not in published:
        published[brand] = []

    published[brand].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "topic_key": topic_key,
        "hook": hook,
        "full_title": full_title
    })

    # Son 90 gün tutma (eski girdileri sil)
    cutoff_date = (datetime.now() - __import__('datetime').timedelta(days=90)).strftime("%Y-%m-%d")
    published[brand] = [t for t in published[brand] if t.get("date", "0") >= cutoff_date]

    PUBLISHED_FILE.write_text(json.dumps(published, indent=2, ensure_ascii=False), encoding="utf-8")


def generate_themes_for_brand(brand: str, trend_keywords: list) -> list:
    """
    Brand için günlük tema listesi oluştur.
    Her konu: topic_key, hook, content, pexels_query, trend_note
    """
    themes = []

    # Sabit tema şablonları (Burak'ın araştırmasını supplement etmek için)
    brand_templates = {
        "holistiglow": {
            "hobbies": "wellness supplements health nutrition",
            "examples": [
                {
                    "topic_key": "magnesium_sleep",
                    "hook": "Slecht slapen? Magnesium is je geheim wapen",
                    "content": [
                        "Magnesium reguleert melatonine",
                        "70% Nederlandse huishoudens heeft magnesiumtekort",
                        "Zorgt voor diepe slaapfasen"
                    ],
                    "pexels_query": "woman sleeping dark bedroom peaceful calm",
                },
                {
                    "topic_key": "vitamine_d_seasonal",
                    "hook": "Voelt lente je niet aan? Vitamine D tekort!",
                    "content": [
                        "Vitamine D reguleert serotoninproductie",
                        "Ondersteunt bot- en immuunsterkte",
                        "15-30 minuten zon dagelijks of supplement"
                    ],
                    "pexels_query": "woman sunlight spring nature outdoor bright",
                },
                {
                    "topic_key": "collagen_skin",
                    "hook": "Hoe voelt je huid zich vanbinnen?",
                    "content": [
                        "Collageen peptide absorbeert 90% efficiënter",
                        "Steunt huid van binnenuit",
                        "Zichtbare verbetering in 8-12 weken"
                    ],
                    "pexels_query": "woman smooth glowing skin beauty health natural",
                },
            ]
        },
        "glowup": {
            "hobbies": "skincare beauty face care cosmetics",
            "examples": [
                {
                    "topic_key": "retinol_routine",
                    "hook": "Retinol zonder irritatie? Dat kan!",
                    "content": [
                        "Begin met lage concentratie 0.25%",
                        "3x per week op schone, droge huid",
                        "Zichtbare rimpelvermindering in 12 weken"
                    ],
                    "pexels_query": "woman skincare routine beauty face skin care",
                },
                {
                    "topic_key": "sunscreen_daily",
                    "hook": "SPF 50+ is niet optioneel, het is nodig",
                    "content": [
                        "UV straling veroorzaakt 80% van huidveroudering",
                        "Minerale SPF beter voor gevoelige huid",
                        "Herverdeling om de 2 uur onder zon"
                    ],
                    "pexels_query": "woman sunscreen protection uv sun beach outdoors",
                },
                {
                    "topic_key": "hyaluronic_hydration",
                    "hook": "Je huid dorst naar hyaluronzuur",
                    "content": [
                        "Hyaluronzuur bindt 1000x water",
                        "Feuchtigheid is basis voor alle skin goals",
                        "Gebruik na toner, voor oils/crèmes"
                    ],
                    "pexels_query": "woman hydrated glowing skin beauty moisture fresh",
                },
            ]
        }
    }

    # Brand template'i al
    template = brand_templates.get(brand, brand_templates["holistiglow"])
    examples = template["examples"]

    # Yayınlanan başlıkları filtrele — aynı başlık yok ise kullan
    filtered = []
    for theme in examples:
        hook = theme.get("hook", "")
        full_title = theme.get("hook", "")
        if not is_title_published(brand, hook, full_title):
            filtered.append(theme)

    # Eğer hepsi yayınlandıysa, rotasyon başlat (eski başlıkları sil)
    if not filtered:
        print(f"  ⚠ Tüm başlıklar {brand} için yayınlandı, template sıfırlanıyor")
        published = load_published_titles()
        published[brand] = []  # Temizle
        PUBLISHED_FILE.write_text(json.dumps(published, indent=2, ensure_ascii=False), encoding="utf-8")
        filtered = examples

    return filtered


def run():
    """Günlük tema JSON'ı oluştur."""
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = THEMES_DIR / f"daily_themes_{today}.json"

    print(f"\n[{datetime.now()}] Theme Researcher — {today}")

    # Burak araştırmasını elde etmeyi dene (fallback: template kullan)
    burak_trends = {}
    if research_trends:
        try:
            burak_trends = research_trends()
            print(f"  ✓ Burak araştırması yüklendi")
        except Exception as e:
            print(f"  ⚠ Burak araştırması başarısız: {e}")

    # JSON oluştur
    holistiglow_themes = generate_themes_for_brand("holistiglow", burak_trends.get("holistiglow", []))
    glowup_themes = generate_themes_for_brand("glowup", burak_trends.get("glowup", []))

    daily_themes = {
        "date": today,
        "holistiglow": holistiglow_themes,
        "glowup": glowup_themes,
    }

    # Dosyaya yaz
    output_file.write_text(json.dumps(daily_themes, indent=2, ensure_ascii=False), encoding="utf-8")

    # Seçilen başlıkları published_titles.json'a işle
    # (sonra reel_maker/social_planner publish ettiğinde tekrar yazılmayacak)
    for theme in holistiglow_themes:
        mark_title_published("holistiglow", theme.get("topic_key", ""),
                           theme.get("hook", ""), theme.get("hook", ""))
    for theme in glowup_themes:
        mark_title_published("glowup", theme.get("topic_key", ""),
                           theme.get("hook", ""), theme.get("hook", ""))

    print(f"  ✓ Tema JSON oluşturuldu: {output_file}")
    print(f"    - HolistiGlow: {len(daily_themes['holistiglow'])} tema (yeni)")
    print(f"    - GlowUp: {len(daily_themes['glowup'])} tema (yeni)")
    print(f"  ✓ Başlıklar published_titles.json'a kaydedildi")


if __name__ == "__main__":
    run()
