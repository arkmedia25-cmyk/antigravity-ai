#!/bin/bash
# Crontab'ı sıfırdan yazar — her zaman idempotent.
# Kullanım: bash scripts/setup_cron.sh

set -e
ROOT="/root/antigravity-ai"
PYTHON="$ROOT/venv/bin/python3"

crontab - <<EOF
# === MAKALE YAZICI ===
0 9  * * * cd $ROOT && $PYTHON scripts/daily_article_writer.py >> logs/article.log 2>&1
0 10 * * * cd $ROOT && $PYTHON scripts/daily_article_writer_amarenl.py >> logs/article_amarenl.log 2>&1

# === SOSYAL MEDYA (CMO Agent) ===
30 9  * * 1-5 cd $ROOT && $PYTHON src/agents/cmo/social_planner.py holistiglow >> logs/social.log 2>&1
0  11 * * *   cd $ROOT && $PYTHON src/agents/cmo/social_planner.py glowup      >> logs/social.log 2>&1
0  17 * * 1-5 cd $ROOT && $PYTHON src/agents/cmo/social_planner.py holistiglow >> logs/social.log 2>&1
30 19 * * *   cd $ROOT && $PYTHON src/agents/cmo/social_planner.py glowup      >> logs/social.log 2>&1
EOF

echo "✅ Crontab güncellendi:"
crontab -l
