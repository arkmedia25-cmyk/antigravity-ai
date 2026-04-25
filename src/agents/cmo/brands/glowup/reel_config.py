# -*- coding: utf-8 -*-
"""
GlowUpNL reel configuratie.
Aanpassen zonder de andere merken of de engine te raken.
"""

HANDLE      = "@GlowUpNL"
VOICE       = "shimmer"       # OpenAI TTS stem
SPEED       = 1.0             # TTS snelheid
CTA_HASHTAGS = "#beauty #skincare #glow #glowup #nl"

# 6 warme, energieke stijlen (coral/oranje palette — brand primary #FF7056)
STYLES = [
    {"name": "coral",      "accent": (255, 112, 86),  "card_hook": (200,  68,  48), "card_content": (52,  16,  10)},
    {"name": "flamingo",   "accent": (255, 105, 145), "card_hook": (210,  62, 100), "card_content": (50,  10,  22)},
    {"name": "sunset",     "accent": (240, 130,  60), "card_hook": (195,  88,  28), "card_content": (50,  22,   6)},
    {"name": "rose",       "accent": (225,  85, 100), "card_hook": (178,  50,  64), "card_content": (46,  10,  16)},
    {"name": "peach",      "accent": (255, 175, 135), "card_hook": (210, 118,  85), "card_content": (50,  24,  16)},
    {"name": "terracotta", "accent": (198,  96,  70), "card_hook": (156,  62,  40), "card_content": (40,  14,   8)},
]

# Dagelijkse topic rotatie
TOPIC_QUEUE = [
    "skincare_ochtend", "vitamine_c_serum", "retinol_nacht",
    "hyaluronzuur", "spf_dagelijks", "beauty_sleep",
    "dubbel_reinigen", "glow_from_within", "ogen_verzorging", "lippenverzorging",
]

# Reel scripts per topic
DEMO_SCRIPTS = {
    "skincare_ochtend": {
        "pexels_query": "woman morning skincare routine mirror bathroom",
        "sections": [
            ("hook",    "Geglazuurde huid?",
                        "Start met de juiste routine",
                        "Geglazuurde huid? Start elke ochtend met de juiste routine!"),
            ("content", "Stap 1: micellair water",
                        "verwijdert olie en resten",
                        "Stap één: micellair water verwijdert olie en nachtcrème resten."),
            ("content", "Stap 2: vitamine C serum",
                        "beschermt en verlicht",
                        "Stap twee: vitamine C serum beschermt je huid en verlicht vlekken."),
            ("content", "Stap 3: SPF 50+",
                        "de nummer 1 anti-aging stap",
                        "Stap drie: SPF vijftig plus is de nummer één anti-aging stap."),
            ("cta",     "Volg {handle} voor meer tips",
                        "Link in bio",
                        "Volg ons voor meer beauty tips. Link staat in de bio!"),
        ],
    },
    "vitamine_c_serum": {
        "pexels_query": "glowing skin woman face close up radiant beauty",
        "sections": [
            ("hook",    "Dof en ongelijk?",
                        "Vitamine C serum is je fix",
                        "Dof en ongelijk? Vitamine C serum is jouw fix!"),
            ("content", "Stopt pigmentvlekken",
                        "voor een egale teint",
                        "Vitamine C serum stopt pigmentvlekken voor een egale teint."),
            ("content", "Stimuleert collageen",
                        "voor strakkere huid",
                        "Het stimuleert collageenproductie voor een strakkere huid."),
            ("content", "Gebruik elke ochtend",
                        "vóór je moisturizer",
                        "Gebruik het elke ochtend vóór je moisturizer voor maximaal effect."),
            ("cta",     "Volg {handle} voor meer tips",
                        "Link in bio",
                        "Volg ons voor meer beauty tips. Link staat in de bio!"),
        ],
    },
    "retinol_nacht": {
        "pexels_query": "woman night skincare sleep bedroom beauty",
        "sections": [
            ("hook",    "Rimpels? Poriën?",
                        "Retinol werkt terwijl jij slaapt",
                        "Rimpels en grote poriën? Retinol werkt terwijl jij slaapt!"),
            ("content", "Vernieuwt huidcellen",
                        "sneller dan normaal",
                        "Retinol vernieuwt huidcellen sneller dan normaal."),
            ("content", "Start met 0,1%",
                        "bouw rustig op",
                        "Begin met nul komma één procent retinol en bouw rustig op."),
            ("content", "Altijd s avonds",
                        "en altijd SPF overdag",
                        "Gebruik retinol altijd s avonds en altijd SPF overdag."),
            ("cta",     "Volg {handle} voor meer tips",
                        "Link in bio",
                        "Volg ons voor meer beauty tips. Link staat in de bio!"),
        ],
    },
    "hyaluronzuur": {
        "pexels_query": "woman hydrated glowing skin water moisture",
        "sections": [
            ("hook",    "Droge strakke huid?",
                        "Hyaluronzuur hydrateert diep",
                        "Droge strakke huid? Hyaluronzuur hydrateert diep van binnen!"),
            ("content", "Trekt 1000x zijn gewicht",
                        "aan water in je huid",
                        "Hyaluronzuur trekt duizend keer zijn gewicht aan water in je huid."),
            ("content", "Aanbrengen op vochtige huid",
                        "voor het beste resultaat",
                        "Breng het aan op vochtige huid voor het beste resultaat."),
            ("content", "Werkt voor alle huidtypen",
                        "ook voor vette huid",
                        "Hyaluronzuur werkt voor alle huidtypen, ook voor vette huid."),
            ("cta",     "Volg {handle} voor meer tips",
                        "Link in bio",
                        "Volg ons voor meer beauty tips. Link staat in de bio!"),
        ],
    },
    "spf_dagelijks": {
        "pexels_query": "woman sunscreen outdoor summer sun protection",
        "sections": [
            ("hook",    "SPF elke dag",
                        "ook binnenshuis!",
                        "SPF elke dag, ook binnenshuis! Dit is waarom."),
            ("content", "UV-stralen dringen door glas",
                        "ook op bewolkte dagen",
                        "UV-stralen dringen door glas, zelfs op bewolkte dagen."),
            ("content", "SPF vertraagt huidveroudering",
                        "met tot 80%",
                        "SPF vertraagt huidveroudering met tot tachtig procent."),
            ("content", "Goede SPF voelt licht aan",
                        "geen wit waas meer",
                        "Een goede SPF voelt licht aan en laat geen wit waas achter."),
            ("cta",     "Volg {handle} voor meer tips",
                        "Link in bio",
                        "Volg ons voor meer beauty tips. Link staat in de bio!"),
        ],
    },
    "beauty_sleep": {
        "pexels_query": "woman sleeping silk pillow beauty rest night",
        "sections": [
            ("hook",    "Acht uur slaap",
                        "is ook skincare!",
                        "Acht uur slaap is ook skincare! Zo werkt het."),
            ("content", "Huid herstelt het meest",
                        "tussen 22:00 en 02:00",
                        "Je huid herstelt het meest tussen tweeëntwintig en twee uur s nachts."),
            ("content", "Slaaptekort verhoogt cortisol",
                        "oorzaak van puistjes",
                        "Slaaptekort verhoogt cortisol, een oorzaak van puistjes."),
            ("content", "Silk pillowcase vermindert",
                        "rimpels en haarbreuk",
                        "Een zijden kussensloop vermindert rimpels en haarbreuk."),
            ("cta",     "Volg {handle} voor meer tips",
                        "Link in bio",
                        "Volg ons voor meer beauty tips. Link staat in de bio!"),
        ],
    },
}
