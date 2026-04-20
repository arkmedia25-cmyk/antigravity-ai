#!/usr/bin/env python3
"""
daily_article_writer_amarenl.py — Publiceert dagelijks 1 SEO-artikel op amarenl.com
Draait via cron: 0 10 * * * cd /root/antigravity-ai && venv/bin/python3 scripts/daily_article_writer_amarenl.py >> logs/article_amarenl.log 2>&1
"""
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_FILE_DIR)
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

STATE_FILE = os.path.join(_PROJECT_ROOT, "article_amarenl_state.json")

ARTICLE_QUEUE = [
    "magnesium_slaap",
    "vitamine_d_tekort",
    "omega3_hersenen",
    "collageen_huid",
    "probiotica_darm",
    "vitamine_b_energie",
    "adaptogenen_stress",
    "gut_brain_stemming",
    "vitamine_e_huid",
    "vitamine_c_immuun",
    "zink_testosteron",
    "calcium_botten",
    "mct_energie",
    "ijzer_vermoeidheid",
    "prebiotica_vezels",
]


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"completed": [], "last_run": None}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def main():
    state = load_state()
    completed = set(state.get("completed", []))

    next_article = None
    for key in ARTICLE_QUEUE:
        if key not in completed:
            next_article = key
            break

    if not next_article:
        print(f"[{datetime.now()}] ✅ Alle artikelen geschreven! Cyclus wordt opnieuw gestart.")
        state["completed"] = []
        save_state(state)
        next_article = ARTICLE_QUEUE[0]

    print(f"[{datetime.now()}] 📝 Vandaag: {next_article}")

    if _FILE_DIR not in sys.path:
        sys.path.insert(0, _FILE_DIR)

    try:
        from article_writer_amarenl import write_and_publish
        url = write_and_publish(next_article)
        print(f"[{datetime.now()}] ✅ Gepubliceerd: {url}")

        state["completed"].append(next_article)
        state["last_run"] = datetime.now().isoformat()
        state[f"last_{next_article}"] = {"url": url, "date": datetime.now().isoformat()}
        save_state(state)

    except Exception as e:
        print(f"[{datetime.now()}] ❌ Fout bij {next_article}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
