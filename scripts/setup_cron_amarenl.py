#!/usr/bin/env python3
"""One-time cron setup for amarenl.com daily article writer. Run: python3 scripts/setup_cron_amarenl.py"""
import subprocess

cron_line = "0 10 * * * cd /root/antigravity-ai && venv/bin/python3 scripts/daily_article_writer_amarenl.py >> logs/article_amarenl.log 2>&1"

result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
existing = result.stdout if result.returncode == 0 else ""

lines = [l for l in existing.splitlines() if "daily_article_writer_amarenl" not in l]
lines.append(cron_line)
new_crontab = "\n".join(lines) + "\n"

proc = subprocess.run(["crontab", "-"], input=new_crontab, text=True, capture_output=True)
if proc.returncode == 0:
    print("✅ Cron kuruldu!")
    subprocess.run(["crontab", "-l"])
else:
    print("❌ Hata:", proc.stderr)
