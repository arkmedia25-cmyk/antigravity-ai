#!/usr/bin/env python3
"""
setup_cron_social.py — Sociale media cron instellen op de server.
Run: python3 scripts/setup_cron_social.py

Optimale posttijden Nederland (CET):
  09:30  HolistiGlow  — TikTok/Instagram ochtend
  11:00  GlowUpNL     — Instagram/TikTok lunch
  17:00  HolistiGlow  — YouTube na school/werk
  19:30  GlowUpNL     — Prime time alle platforms

Nieuw merk toevoegen: voeg regel toe aan SOCIAL_CRONS en maak brands/<merk>/reel_config.py aan.
"""
import subprocess

BASE = "cd /root/antigravity-ai && venv/bin/python3 scripts/social_planner.py"
LOG  = ">> logs/social.log 2>&1"

SOCIAL_CRONS = [
    # (minuut, uur, dag_van_week, merk, omschrijving)
    ("30", "9",  "1-5", "holistiglow", "HolistiGlow ochtend (weekdagen)"),
    ("0",  "11", "*",   "glowup",      "GlowUpNL lunch (elke dag)"),
    ("0",  "17", "1-5", "holistiglow", "HolistiGlow avond (weekdagen)"),
    ("30", "19", "*",   "glowup",      "GlowUpNL prime time (elke dag)"),
]

ARTICLE_CRONS = [
    "0 10 * * * cd /root/antigravity-ai && venv/bin/python3 scripts/daily_article_writer_amarenl.py >> logs/article_amarenl.log 2>&1",
]


def build_cron_line(minute, hour, dow, brand):
    return f"{minute} {hour} * * {dow} {BASE} {brand} {LOG}"


def setup():
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""

    # Verwijder alleen sociale media crons (bewaar de rest)
    lines = [
        l for l in existing.splitlines()
        if "social_planner.py" not in l
    ]

    print("Sociale media crons die worden toegevoegd:")
    for minute, hour, dow, brand, desc in SOCIAL_CRONS:
        line = build_cron_line(minute, hour, dow, brand)
        lines.append(line)
        print(f"  {minute:>3} {hour:>3} * * {dow:<5}  [{brand}] {desc}")

    # Artikel cron behouden (of toevoegen als niet aanwezig)
    for art_line in ARTICLE_CRONS:
        if not any("daily_article_writer_amarenl" in l for l in lines):
            lines.append(art_line)

    new_crontab = "\n".join(lines) + "\n"

    proc = subprocess.run(["crontab", "-"], input=new_crontab,
                          text=True, capture_output=True)
    if proc.returncode == 0:
        print("\nCron ingesteld:")
        subprocess.run(["crontab", "-l"])
    else:
        print("Fout:", proc.stderr)


if __name__ == "__main__":
    setup()
