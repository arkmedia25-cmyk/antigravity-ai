# -*- coding: utf-8 -*-
"""
HolistiGlow reel configuratie.
Aanpassen zonder de andere merken of de engine te raken.
"""

HANDLE      = "@HolistiGlow"
VOICE       = "nova"          # OpenAI TTS stem
SPEED       = 1.0             # TTS snelheid
CTA_HASHTAGS = "#wellness #gezondheid #supplements #nl"

# 6 aardse, kalme stijlen (sage/groen palette)
STYLES = [
    {"name": "sage",       "accent": (130, 150, 120), "card_hook": (130, 150, 120), "card_content": (20,  28,  18)},
    {"name": "stone",      "accent": (122, 111, 94),  "card_hook": (122, 111, 94),  "card_content": (28,  22,  14)},
    {"name": "lavender",   "accent": (125, 122, 154), "card_hook": (125, 122, 154), "card_content": (22,  20,  38)},
    {"name": "terracotta", "accent": (154, 107, 94),  "card_hook": (154, 107, 94),  "card_content": (38,  20,  16)},
    {"name": "moss",       "accent": (94,  122, 94),  "card_hook": (94,  122, 94),  "card_content": (14,  28,  14)},
    {"name": "dusk",       "accent": (94,  107, 122), "card_hook": (94,  107, 122), "card_content": (14,  20,  30)},
]

# Dagelijkse topic rotatie — volgorde is de posting volgorde
TOPIC_QUEUE = [
    "magnesium", "vitamine_d", "omega3", "collageen_supplement",
    "probiotica", "vitamine_b", "adaptogenen", "vitamine_c_immuun",
    "zink", "gut_brain",
]

# Reel scripts per topic
DEMO_SCRIPTS = {
    "magnesium": {
        "pexels_query": "woman sleeping bedroom calm night",
        "sections": [
            ("hook",    "Slecht slapen?",
                        "Magnesium tekort speelt mee!",
                        "Slecht slapen? Magnesium tekort speelt mee!"),
            ("content", "Reguleert melatonine",
                        "voor een diepere nachtrust",
                        "Magnesium reguleert melatonine voor een diepere nachtrust."),
            ("content", "70% van Nederlanders",
                        "heeft een magnesiumtekort",
                        "Zeventig procent van Nederlanders heeft een magnesiumtekort."),
            ("content", "Ontspant spieren",
                        "en zenuwstelsel s nachts",
                        "Magnesium ontspant je spieren en zenuwstelsel voor het slapengaan."),
            ("cta",     "Volg {handle} voor meer tips",
                        "Link in bio",
                        "Volg ons voor meer wellness tips. Link staat in de bio!"),
        ],
    },
    "vitamine_d": {
        "pexels_query": "sunlight woman nature outdoor healthy",
        "sections": [
            ("hook",    "Moe? Somber?",
                        "Check je vitamine D!",
                        "Moe en somber? Check dan je vitamine D level!"),
            ("content", "80% heeft tekort",
                        "in de Nederlandse winter",
                        "Tachtig procent van Nederlanders heeft in de winter een vitamine D tekort."),
            ("content", "Versterkt immuunsysteem",
                        "en je energieniveau",
                        "Vitamine D versterkt je immuunsysteem en verhoogt je energieniveau."),
            ("content", "15-30 min zon per dag",
                        "of een goed supplement",
                        "Dagelijks vijftien tot dertig minuten zon of een goed supplement helpt."),
            ("cta",     "Volg {handle} voor meer tips",
                        "Link in bio",
                        "Volg ons voor meer wellness tips. Link staat in de bio!"),
        ],
    },
    "omega3": {
        "pexels_query": "salmon fish healthy food brain focus",
        "sections": [
            ("hook",    "Wazig hoofd?",
                        "Omega-3 helpt je hersenen",
                        "Wazig hoofd? Omega-3 helpt je hersenen scherp te blijven!"),
            ("content", "DHA voedt hersencellen",
                        "voor betere concentratie",
                        "DHA voedt hersencellen voor betere concentratie."),
            ("content", "Vermindert ontsteking",
                        "in je hele lichaam",
                        "Omega-3 vermindert ontstekingen in je hele lichaam."),
            ("content", "Vette vis 2x per week",
                        "of een omega-3 supplement",
                        "Eet vette vis tweemaal per week of neem een omega-3 supplement."),
            ("cta",     "Volg {handle} voor meer tips",
                        "Link in bio",
                        "Volg ons voor meer wellness tips. Link staat in de bio!"),
        ],
    },
    "probiotica": {
        "pexels_query": "healthy gut yogurt fermented food woman",
        "sections": [
            ("hook",    "Opgeblazen gevoel?",
                        "Je darmflora is de sleutel",
                        "Opgeblazen gevoel? Je darmflora is de sleutel!"),
            ("content", "100 triljoen bacteriën",
                        "leven in jouw darmen",
                        "Honderd triljoen bacteriën leven in jouw darmen."),
            ("content", "Herstelt balans na stress",
                        "of antibiotica",
                        "Probiotica herstelt de balans na stress of antibioticagebruik."),
            ("content", "Yoghurt, kefir, kimchi",
                        "gefermenteerd eten helpt",
                        "Gefermenteerd eten zoals yoghurt, kefir en kimchi helpen."),
            ("cta",     "Volg {handle} voor meer tips",
                        "Link in bio",
                        "Volg ons voor meer wellness tips. Link staat in de bio!"),
        ],
    },
    "adaptogenen": {
        "pexels_query": "woman meditation calm stress relief nature",
        "sections": [
            ("hook",    "Chronische stress?",
                        "Adaptogenen helpen herstellen",
                        "Chronische stress? Adaptogenen helpen je lichaam herstellen!"),
            ("content", "Ashwagandha verlaagt cortisol",
                        "het stresshormoon",
                        "Ashwagandha verlaagt cortisol, het stresshormoon in je lichaam."),
            ("content", "Rhodiola verhoogt energie",
                        "zonder overprikkeling",
                        "Rhodiola verhoogt energie zonder je te overprikkelen."),
            ("content", "Maca balanceert hormonen",
                        "en verbetert je humeur",
                        "Maca ondersteunt de balans van hormonen en je humeur."),
            ("cta",     "Volg {handle} voor meer tips",
                        "Link in bio",
                        "Volg ons voor meer wellness tips. Link staat in de bio!"),
        ],
    },
}
