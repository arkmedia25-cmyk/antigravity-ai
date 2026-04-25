# -*- coding: utf-8 -*-
"""
NIEUW MERK TEMPLATE — kopieer brands/_template/ naar brands/<merkname>/
Vul hieronder de gegevens in. Raak de engine (amarenl_reel_maker.py) niet aan.

Stappen voor nieuw merk:
  1. cp -r brands/_template brands/mijnmerk
  2. Pas identity.json aan
  3. Pas reel_config.py aan (hieronder)
  4. Voeg cron toe in social_planner.py
"""

HANDLE      = "@MijnMerk"
VOICE       = "nova"          # nova | shimmer | alloy | echo | fable | onyx
SPEED       = 1.0
CTA_HASHTAGS = "#nl #health #tips"

# 6 stijlvarianten — pas kleuren aan naar merkidentiteit (RGB tuples)
STYLES = [
    {"name": "variant1", "accent": (100, 120, 100), "card_hook": (100, 120, 100), "card_content": (20, 28, 18)},
    {"name": "variant2", "accent": (120, 110, 90),  "card_hook": (120, 110, 90),  "card_content": (28, 22, 14)},
    {"name": "variant3", "accent": (120, 120, 150), "card_hook": (120, 120, 150), "card_content": (20, 20, 38)},
    {"name": "variant4", "accent": (150, 100, 90),  "card_hook": (150, 100, 90),  "card_content": (38, 20, 16)},
    {"name": "variant5", "accent": (90,  120, 90),  "card_hook": (90,  120, 90),  "card_content": (14, 28, 14)},
    {"name": "variant6", "accent": (90,  100, 120), "card_hook": (90,  100, 120), "card_content": (14, 20, 30)},
]

# Voeg topics toe — dit zijn de dagelijkse reel onderwerpen
TOPIC_QUEUE = [
    "topic_1",
    "topic_2",
    "topic_3",
]

# Schrijf voor elk topic in TOPIC_QUEUE een script
DEMO_SCRIPTS = {
    "topic_1": {
        "pexels_query": "healthy woman lifestyle nature",  # zoekterm voor achtergrondvideo
        "sections": [
            # (tag, regel1_overlay, regel2_overlay, tts_tekst)
            # tag: 'hook' | 'content' | 'cta'
            ("hook",    "Pakkende vraag?",
                        "Subkop hier",
                        "Spreek de hook uit als volledige zin voor TTS."),
            ("content", "Feit 1 titel",
                        "korte toelichting",
                        "Spreek feit één uit als volledige zin."),
            ("content", "Feit 2 titel",
                        "korte toelichting",
                        "Spreek feit twee uit als volledige zin."),
            ("content", "Feit 3 titel",
                        "korte toelichting",
                        "Spreek feit drie uit als volledige zin."),
            ("cta",     "Volg {handle} voor meer tips",
                        "Link in bio",
                        "Volg ons voor meer tips. Link staat in de bio!"),
        ],
    },
}
