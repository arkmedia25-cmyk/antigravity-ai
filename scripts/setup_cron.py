#!/usr/bin/env python3
"""One-time cron setup script. Run once on server: python3 scripts/setup_cron.py"""
import subprocess

cron_line = "0 9 * * * cd /root/antigravity-ai && venv/bin/python3 scripts/daily_article_writer.py >> logs/article_cron.log 2>&1"

# Get existing crontab (if any)
result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
existing = result.stdout if result.returncode == 0 else ""

# Remove old amare cron lines to avoid duplicates
lines = [l for l in existing.splitlines() if "daily_article_writer" not in l]
lines.append(cron_line)
new_crontab = "\n".join(lines) + "\n"

# Install
proc = subprocess.run(["crontab", "-"], input=new_crontab, text=True, capture_output=True)
if proc.returncode == 0:
    print("✅ Cron kuruldu!")
    subprocess.run(["crontab", "-l"])
else:
    print("❌ Hata:", proc.stderr)
