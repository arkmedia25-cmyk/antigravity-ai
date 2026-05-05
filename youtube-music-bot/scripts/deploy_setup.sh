#!/bin/bash
# Neon Pulse v2.3 Complete VPS Setup Script
# Usage: bash deploy_setup.sh
# Runs on: Ubuntu 22.04 LTS

set -e

echo "🚀 Neon Pulse v2.3 — VPS Production Setup"
echo "==========================================="

# Variables
PROJECT_DIR="/home/deploy/neonpulse"
REPO_URL="https://github.com/arkmedia25-cmyk/antigravity-ai.git"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Step 1: System Updates
echo ""
log_step "Step 1: System Update"
sudo apt update
sudo apt upgrade -y

# Step 2: Install Dependencies
echo ""
log_step "Step 2: Installing Dependencies"
sudo apt install -y \
    python3.11 \
    python3-pip \
    ffmpeg \
    git \
    curl \
    jq \
    unzip

# Step 3: Create deploy user
echo ""
log_step "Step 3: Creating deploy user"
if id -u deploy &>/dev/null; then
    log_warn "User 'deploy' already exists"
else
    sudo useradd -m -s /bin/bash deploy
    log_step "User 'deploy' created"
fi

# Step 4: Create project directory
echo ""
log_step "Step 4: Creating project directory"
sudo mkdir -p "$PROJECT_DIR"
sudo chown deploy:deploy "$PROJECT_DIR"
chmod 755 "$PROJECT_DIR"

# Step 5: Clone Repository (as deploy user)
echo ""
log_step "Step 5: Cloning Repository"
cd "$PROJECT_DIR"
sudo -u deploy git clone "$REPO_URL" . 2>/dev/null || {
    sudo -u deploy git pull origin main
}
sudo -u deploy git checkout main
log_step "Repository cloned"

# Step 6: Navigate to youtube-music-bot
echo ""
log_step "Step 6: Setting up youtube-music-bot"
cd "$PROJECT_DIR/youtube-music-bot"

# Step 7: Install Python Dependencies
echo ""
log_step "Step 7: Installing Python packages"
sudo -u deploy python3 -m pip install --user -r requirements.txt
log_step "Dependencies installed"

# Step 8: Create .env from template
echo ""
log_step "Step 8: Setting up .env file"
if [ ! -f .env ]; then
    log_warn ".env not found. Create it manually with:"
    echo "  nano $PROJECT_DIR/youtube-music-bot/.env"
    echo ""
    echo "Required variables:"
    echo "  KIE_API_KEY=..."
    echo "  YOUTUBE_API_KEY=..."
    echo "  YOUTUBE_CLIENT_ID=..."
    echo "  YOUTUBE_CLIENT_SECRET=..."
    echo "  YOUTUBE_REFRESH_TOKEN=..."
    echo "  YOUTUBE_CHANNEL_ID=..."
    echo "  TELEGRAM_BOT_TOKEN=..."
    echo "  TELEGRAM_CHAT_ID=..."
    echo "  PEXELS_API_KEY=..."
else
    chmod 600 .env
    log_step ".env configured (600 permissions)"
fi

# Step 9: Create Directory Structure
echo ""
log_step "Step 9: Creating directory structure"
sudo -u deploy mkdir -p state/backups state/research
sudo -u deploy mkdir -p logs output
sudo -u deploy mkdir -p channels/neonpulse/thumbnails
sudo -u deploy mkdir -p backgrounds/{synthwave-night-drive,cyberpunk-ambient,lofi-cyberpunk,darksynth-workout,outrun-retrowave,vaporwave-chill}
chmod 750 state logs output
log_step "Directories created"

# Step 10: Create Log Files
echo ""
log_step "Step 10: Setting up log files"
for logfile in system.log bot.log error.log monitor.log backup.log alerts.log; do
    sudo -u deploy touch "logs/$logfile"
    chmod 640 "logs/$logfile"
done
log_step "Log files created"

# Step 11: Install Systemd Service
echo ""
log_step "Step 11: Installing Systemd Service"
sudo cp scripts/neonpulse-bot.service /etc/systemd/system/ 2>/dev/null || {
    sudo cp neonpulse-telegram.service /etc/systemd/system/neonpulse-bot.service
}
sudo systemctl daemon-reload
sudo systemctl enable neonpulse-bot.service
log_step "Systemd service installed and enabled"

# Step 12: Install Logrotate
echo ""
log_step "Step 12: Installing logrotate configuration"
sudo tee /etc/logrotate.d/neonpulse > /dev/null <<EOF
$PROJECT_DIR/youtube-music-bot/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 deploy deploy
    sharedscripts
}
EOF
sudo logrotate -f /etc/logrotate.d/neonpulse || true
log_step "Logrotate configured"

# Step 13: Install Crontab (as deploy user)
echo ""
log_step "Step 13: Installing cron jobs"
sudo -u deploy crontab - <<'CRONTAB'
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
CRONTAB
log_step "Cron jobs installed"

# Step 14: Make scripts executable
echo ""
log_step "Step 14: Setting script permissions"
chmod +x scripts/deploy_backup.sh
chmod +x scripts/deploy_monitoring.sh
log_step "Scripts executable"

# Step 15: Start Bot Service
echo ""
log_step "Step 15: Starting Telegram Bot"
sudo systemctl start neonpulse-bot.service
sleep 2
if sudo systemctl is-active --quiet neonpulse-bot.service; then
    log_step "Bot service started successfully"
else
    log_warn "Bot service may have issues. Check: sudo systemctl status neonpulse-bot.service"
fi

# Step 16: Dry-run test
echo ""
log_step "Step 16: Running dry-run test"
cd "$PROJECT_DIR/youtube-music-bot"
sudo -u deploy python3 main_runner.py --mock --niche synthwave-night-drive > /tmp/dryrun.log 2>&1
if grep -q "MOCK:" /tmp/dryrun.log; then
    log_step "Dry-run completed successfully"
    cat /tmp/dryrun.log | head -20
else
    log_warn "Dry-run test output:"
    cat /tmp/dryrun.log | head -20
fi

# Step 17: Verification
echo ""
echo "=========================================="
echo "✅ SETUP COMPLETE"
echo "=========================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Edit .env with your credentials:"
echo "   sudo nano $PROJECT_DIR/youtube-music-bot/.env"
echo ""
echo "2. Start the bot:"
echo "   sudo systemctl start neonpulse-bot.service"
echo ""
echo "3. Check bot status:"
echo "   sudo systemctl status neonpulse-bot.service"
echo ""
echo "4. Follow logs:"
echo "   tail -f $PROJECT_DIR/youtube-music-bot/logs/system.log"
echo ""
echo "5. Test Telegram:"
echo "   /status command to check system"
echo ""
echo "6. First run scheduled for 06:00 UTC daily"
echo ""
echo "📌 Important Files:"
echo "   - .env: $PROJECT_DIR/youtube-music-bot/.env (edit with credentials)"
echo "   - Logs: $PROJECT_DIR/youtube-music-bot/logs/"
echo "   - State: $PROJECT_DIR/youtube-music-bot/state/"
echo ""
echo "🔗 Documentation:"
echo "   - DEPLOYMENT_SUMMARY.md"
echo "   - PHASE8_DEPLOYMENT_CHECKLIST.md"
echo "   - CLAUDE.md (v2.3)"
echo ""
