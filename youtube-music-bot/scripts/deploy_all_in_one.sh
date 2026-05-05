#!/bin/bash
# Neon Pulse v2.3 — One-Shot DigitalOcean Deployment
# Usage: bash deploy_all_in_one.sh
# Runs on: DigitalOcean 168.231.107.135

set -e

echo "🚀 Neon Pulse v2.3 — Full DigitalOcean Deployment"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_step() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

# Step 1: Update system
echo ""
log_step "Step 1: System Update"
apt update
apt upgrade -y

# Step 2: Install dependencies
echo ""
log_step "Step 2: Installing Dependencies"
apt install -y python3.11 python3-pip ffmpeg git curl jq unzip

# Step 3: Clone/Update repo
echo ""
log_step "Step 3: Getting Latest Code"
cd /root
if [ -d "antigravity-ai" ]; then
    cd antigravity-ai
    git fetch origin
    git checkout main
    cd ..
else
    git clone https://github.com/arkmedia25-cmyk/antigravity-ai.git
fi

# Step 4: Create Neon Pulse directories
echo ""
log_step "Step 4: Creating Neon Pulse Directories"
mkdir -p /home/deploy/neonpulse/youtube-music-bot
cd /home/deploy/neonpulse/youtube-music-bot

# Copy code
cp -r /root/antigravity-ai/youtube-music-bot/* .

# Create required directories
mkdir -p state/backups state/research
mkdir -p logs output
mkdir -p channels/neonpulse/thumbnails
mkdir -p backgrounds/{synthwave-night-drive,cyberpunk-ambient,lofi-cyberpunk,darksynth-workout,outrun-retrowave,vaporwave-chill}

chmod 750 state logs output backgrounds

# Step 5: Install Python packages
echo ""
log_step "Step 5: Installing Python Packages"
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -r requirements.txt

# Step 6: Create log files
echo ""
log_step "Step 6: Creating Log Files"
for logfile in system.log bot.log error.log monitor.log backup.log alerts.log; do
    touch logs/$logfile
    chmod 640 logs/$logfile
done

# Step 7: Create .env file (with placeholder)
echo ""
log_step "Step 7: Creating .env File"
if [ ! -f .env ]; then
    cat > .env <<'EOF'
# Suno API
KIE_API_KEY=REPLACE_WITH_YOUR_SUNO_KEY

# YouTube API
YOUTUBE_API_KEY=REPLACE_WITH_YOUR_YOUTUBE_API_KEY
YOUTUBE_CLIENT_ID=REPLACE_WITH_YOUR_CLIENT_ID
YOUTUBE_CLIENT_SECRET=REPLACE_WITH_YOUR_CLIENT_SECRET
YOUTUBE_REFRESH_TOKEN=REPLACE_WITH_YOUR_REFRESH_TOKEN
YOUTUBE_CHANNEL_ID=REPLACE_WITH_YOUR_CHANNEL_ID

# Telegram Bot
TELEGRAM_BOT_TOKEN=REPLACE_WITH_YOUR_BOT_TOKEN
TELEGRAM_CHAT_ID=REPLACE_WITH_YOUR_CHAT_ID

# Optional
PEXELS_API_KEY=REPLACE_WITH_YOUR_PEXELS_KEY
NVIDIA_API_KEY=REPLACE_WITH_YOUR_NVIDIA_KEY

# System
SYSTEM_TIMEZONE=Europe/Amsterdam
LOG_LEVEL=INFO
EOF
    chmod 600 .env
    log_warn ".env created with placeholders — EDIT THIS FILE with your credentials!"
else
    chmod 600 .env
    log_step ".env already exists"
fi

# Step 8: Install Systemd service
echo ""
log_step "Step 8: Installing Systemd Service"
cp neonpulse-telegram.service /etc/systemd/system/neonpulse-bot.service
systemctl daemon-reload
systemctl enable neonpulse-bot.service

# Step 9: Install Logrotate
echo ""
log_step "Step 9: Installing Logrotate"
tee /etc/logrotate.d/neonpulse > /dev/null <<'EOF'
/home/deploy/neonpulse/youtube-music-bot/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
}
EOF
logrotate -f /etc/logrotate.d/neonpulse || true

# Step 10: Install Cron jobs
echo ""
log_step "Step 10: Installing Cron Jobs"
cat > /tmp/neonpulse_cron.txt <<'EOF'
# Neon Pulse v2.3 Cron Schedule
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Daily pipeline run (06:00 UTC)
0 6 * * * cd /home/deploy/neonpulse/youtube-music-bot && /usr/bin/python3 main_runner.py >> logs/system.log 2>&1

# Log rotation (01:00 UTC)
0 1 * * * /usr/sbin/logrotate /etc/logrotate.d/neonpulse

# Weekly backup (02:00 UTC on Sunday)
0 2 * * 0 cd /home/deploy/neonpulse/youtube-music-bot && bash scripts/deploy_backup.sh >> logs/backup.log 2>&1

# Hourly monitoring (every hour)
0 * * * * cd /home/deploy/neonpulse/youtube-music-bot && bash scripts/deploy_monitoring.sh >> logs/monitor.log 2>&1
EOF

crontab /tmp/neonpulse_cron.txt
rm /tmp/neonpulse_cron.txt

# Step 11: Set script permissions
echo ""
log_step "Step 11: Setting Script Permissions"
chmod +x scripts/deploy_backup.sh
chmod +x scripts/deploy_monitoring.sh
chmod 600 .env

# Step 12: Start Bot Service
echo ""
log_step "Step 12: Starting Telegram Bot"
systemctl start neonpulse-bot.service
sleep 2

if systemctl is-active --quiet neonpulse-bot.service; then
    log_step "Bot service started successfully"
else
    log_warn "Bot service may have issues. Check: systemctl status neonpulse-bot.service"
fi

# Step 13: Dry-run test
echo ""
log_step "Step 13: Running Dry-Run Test"
python3 main_runner.py --mock --niche synthwave-night-drive > /tmp/dryrun.log 2>&1
if grep -q "MOCK:" /tmp/dryrun.log; then
    log_step "Dry-run test passed!"
    head -10 /tmp/dryrun.log
else
    log_warn "Dry-run output:"
    head -10 /tmp/dryrun.log
fi

# Step 14: Verify cron
echo ""
log_step "Step 14: Verifying Cron Schedule"
crontab -l | grep -c neonpulse >/dev/null && log_step "$(crontab -l | grep neonpulse | wc -l) cron jobs installed" || log_error "Cron jobs not installed"

# Step 15: Final verification
echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE"
echo "=========================================="
echo ""
echo "📋 NEXT STEPS (CRITICAL):"
echo ""
echo "1️⃣  EDIT .env WITH YOUR CREDENTIALS:"
echo "   nano /home/deploy/neonpulse/youtube-music-bot/.env"
echo ""
echo "   Replace these placeholders:"
echo "   - KIE_API_KEY (Suno)"
echo "   - YOUTUBE_API_KEY"
echo "   - YOUTUBE_CLIENT_ID"
echo "   - YOUTUBE_CLIENT_SECRET"
echo "   - YOUTUBE_REFRESH_TOKEN"
echo "   - YOUTUBE_CHANNEL_ID"
echo "   - TELEGRAM_BOT_TOKEN"
echo "   - TELEGRAM_CHAT_ID"
echo ""
echo "2️⃣  RESTART BOT AFTER .env EDIT:"
echo "   systemctl restart neonpulse-bot.service"
echo ""
echo "3️⃣  TEST TELEGRAM BOT:"
echo "   Send /status command to your Telegram bot"
echo ""
echo "4️⃣  CHECK STATUS:"
echo "   systemctl status neonpulse-bot.service"
echo ""
echo "5️⃣  MONITOR LOGS:"
echo "   tail -f /home/deploy/neonpulse/youtube-music-bot/logs/system.log"
echo ""
echo "📅 SCHEDULED RUNS:"
echo "   Daily: 06:00 UTC (automatic)"
echo "   First run: Tomorrow at 06:00 UTC"
echo ""
echo "📊 VERIFICATION:"
echo "   - Bot logs: /home/deploy/neonpulse/youtube-music-bot/logs/bot.log"
echo "   - System logs: /home/deploy/neonpulse/youtube-music-bot/logs/system.log"
echo "   - State: /home/deploy/neonpulse/youtube-music-bot/state/state.json"
echo ""
echo "🚀 System ready. Edit .env and restart bot to activate!"
echo ""
