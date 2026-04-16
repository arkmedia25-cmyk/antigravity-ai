#!/usr/bin/env python3
"""
daily_article_writer.py — Elke dag schrijft dit script automatisch 1 nieuw artikel.
Houdt bij welke producten al geschreven zijn in een state file.
Draait via cron: 0 9 * * * python3 /opt/n8n/daily_article_writer.py
"""
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
# Dynamically find the .env in project root
_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_FILE_DIR)
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

# State file bijhoudt voortgang
STATE_FILE = os.path.join(_PROJECT_ROOT, "article_writer_state.json")

# Volgorde van te schrijven artikelen (nieuwe producten eerst, dan updates)
ARTICLE_QUEUE = [
    # Nieuwe artikelen (nog niet gepubliceerd)
    "restore",
    "on_shots",
    "origin",
    "ignite_him",
    "ignite_her",
    "hl5",
    "happy_juice_kopen",
    "happy_juice_bijwerkingen",
    "amare_vs_concurrenten",
    "gut_brain",
    # Bestaande artikelen opnieuw genereren (SEO refresh)
    "happy_juice",
    "sunrise",
    "sunset",
    "edge",
    "triangle",
    "mentabiotics",
    "nitro_xtreme",
    "fit20",
    "skin_to_mind",
    "rootist",
    "edge_mango",
]

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"completed": [], "last_run": None}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def main():
    state = load_state()
    completed = set(state.get("completed", []))

    # Vind het volgende product dat nog niet geschreven is
    next_product = None
    for product_key in ARTICLE_QUEUE:
        if product_key not in completed:
            next_product = product_key
            break

    if not next_product:
        # Alle artikelen geschreven — reset de cyclus voor een nieuwe ronde
        print(f"[{datetime.now()}] ✅ Alle artikelen geschreven! Reset voor nieuwe cyclus.")
        state["completed"] = []
        save_state(state)
        # Begin opnieuw met het eerste product
        next_product = ARTICLE_QUEUE[0]

    print(f"[{datetime.now()}] 📝 Vandaag schrijven: {next_product}")

    # Importeer en voer article_writer uit
    # Import from the scripts directory (same as this file)
    if _FILE_DIR not in sys.path:
        sys.path.insert(0, _FILE_DIR)
        
    try:
        from article_writer import write_and_publish
        url = write_and_publish(next_product)
        print(f"[{datetime.now()}] ✅ Gepubliceerd: {url}")

        # State bijwerken
        state["completed"].append(next_product)
        state["last_run"] = datetime.now().isoformat()
        state[f"last_{next_product}"] = {"url": url, "date": datetime.now().isoformat()}
        save_state(state)

    except Exception as e:
        print(f"[{datetime.now()}] ❌ Fout bij {next_product}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
