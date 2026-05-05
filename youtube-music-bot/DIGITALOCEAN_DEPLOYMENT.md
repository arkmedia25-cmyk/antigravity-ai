# Neon Pulse v2.3 — DigitalOcean Deployment

**Server:** 168.231.107.135 (2GB RAM, Ubuntu 22.04)  
**Date:** 2026-05-06  
**Status:** Ready for deployment

---

## 📋 Pre-Deployment

**Verified:**
- ✅ DigitalOcean server accessible (SSH port 22 open)
- ✅ Ubuntu 22.04 LTS confirmed
- ✅ Python 3.11+ available
- ✅ FFmpeg installable
- ✅ Root SSH access available

**Required Credentials (prepare before starting):**
```
KIE_API_KEY=your_suno_key
YOUTUBE_API_KEY=your_youtube_key
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...
YOUTUBE_REFRESH_TOKEN=... (from first OAuth)
YOUTUBE_CHANNEL_ID=... (Neon Pulse music channel)
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
PEXELS_API_KEY=... (optional)
NVIDIA_API_KEY=... (optional)
```

---

## 🚀 Deployment Steps (SSH)

### Step 1: Connect to DigitalOcean Server

```bash
ssh root@168.231.107.135
```

### Step 2: Navigate to Project Directory

```bash
cd /root/antigravity-ai
```

**Current structure:**
```
/root/antigravity-ai/
├── src/agents/cmo/           ← Existing CMO system
├── src/interfaces/telegram/   ← Existing Telegram bot
├── logs/                      ← Existing logs
├── youtube-music-bot/         ← Existing YouTube bot
└── (will add) neonpulse/      ← NEW Neon Pulse v2.3
```

### Step 3: Clone Latest Version

```bash
cd /root
git clone https://github.com/arkmedia25-cmyk/antigravity-ai.git neon-pulse-v2.3
cd neon-pulse-v2.3/youtube-music-bot
```

Veya güncel kodu pull et:
```bash
cd /root/antigravity-ai
git fetch origin
git checkout main
cd youtube-music-bot
```

### Step 4: Install System Dependencies (if needed)

```bash
sudo apt update
sudo apt install -y python3.11 python3-pip ffmpeg git curl jq unzip
```

### Step 5: Create Neon Pulse Directories

```bash
# Create project directories
mkdir -p /home/deploy/neonpulse/youtube-music-bot
cd /home/deploy/neonpulse/youtube-music-bot

# Copy code from git
cp -r /root/antigravity-ai/youtube-music-bot/* .

# Create required directories
mkdir -p state/backups state/research
mkdir -p logs output
mkdir -p channels/neonpulse/thumbnails
mkdir -p backgrounds/{synthwave-night-drive,cyberpunk-ambient,lofi-cyberpunk,darksynth-workout,outrun-retrowave,vaporwave-chill}

# Set permissions
chmod 750 state logs output backgrounds
```

### Step 6: Install Python Dependencies

```bash
cd /home/deploy/neonpulse/youtube-music-bot
python3 -m pip install -r requirements.txt
```

### Step 7: Create .env File

```bash
# Create .env file
nano .env
```

**Paste all credentials:**
```env
KIE_API_KEY=your_suno_api_key
YOUTUBE_API_KEY=your_youtube_api_key
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_client_secret
YOUTUBE_REFRESH_TOKEN=your_refresh_token
YOUTUBE_CHANNEL_ID=your_channel_id
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
PEXELS_API_KEY=your_pexels_key
NVIDIA_API_KEY=your_nvidia_key
SYSTEM_TIMEZONE=Europe/Amsterdam
LOG_LEVEL=INFO
```

**Save:** `Ctrl+X` → `Y` → `Enter`

### Step 8: Create Log Files

```bash
cd /home/deploy/neonpulse/youtube-music-bot
for logfile in system.log bot.log error.log monitor.log backup.log alerts.log; do
  touch logs/$logfile
  chmod 640 logs/$logfile
done
```

### Step 9: Create Systemd Service

```bash
# Copy service file
sudo cp neonpulse-telegram.service /etc/systemd/system/neonpulse-bot.service

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable neonpulse-bot.service
```

### Step 10: Install Logrotate

```bash
sudo tee /etc/logrotate.d/neonpulse > /dev/null <<'EOF'
/home/deploy/neonpulse/youtube-music-bot/logs/*.log {
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
```

### Step 11: Install Cron Jobs

```bash
# Install crontab for root or deploy user
sudo crontab -e

# Paste these lines:
# Daily pipeline run (06:00 UTC)
0 6 * * * cd /home/deploy/neonpulse/youtube-music-bot && /usr/bin/python3 main_runner.py >> logs/system.log 2>&1

# Log rotation (01:00 UTC)
0 1 * * * /usr/sbin/logrotate /etc/logrotate.d/neonpulse

# Weekly backup (02:00 UTC on Sunday)
0 2 * * 0 cd /home/deploy/neonpulse/youtube-music-bot && bash scripts/deploy_backup.sh >> logs/backup.log 2>&1

# Hourly monitoring (every hour)
0 * * * * cd /home/deploy/neonpulse/youtube-music-bot && bash scripts/deploy_monitoring.sh >> logs/monitor.log 2>&1
```

### Step 12: Set Script Permissions

```bash
cd /home/deploy/neonpulse/youtube-music-bot
chmod +x scripts/deploy_backup.sh
chmod +x scripts/deploy_monitoring.sh
chmod 600 .env
```

### Step 13: Start Bot Service

```bash
sudo systemctl start neonpulse-bot.service
sleep 2
sudo systemctl status neonpulse-bot.service
```

**Expected output:** `active (running)`

### Step 14: Dry-Run Test

```bash
cd /home/deploy/neonpulse/youtube-music-bot
python3 main_runner.py --mock --niche synthwave-night-drive
```

**Expected output:** Completes in ~2 seconds, no errors

### Step 15: Verify Telegram Bot

Send test message to bot:
```
/status
```

**Expected response:** System information (uptime, disk, last run)

---

## 📊 Deployment Verification

### Check Bot Status

```bash
sudo systemctl status neonpulse-bot.service
```

### Follow Logs

```bash
tail -f /home/deploy/neonpulse/youtube-music-bot/logs/system.log
```

### Check Cron Schedule

```bash
sudo crontab -l | grep neonpulse
```

### Verify .env Loaded

```bash
cd /home/deploy/neonpulse/youtube-music-bot
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('TELEGRAM_BOT_TOKEN:', '✓' if os.getenv('TELEGRAM_BOT_TOKEN') else '✗')"
```

---

## 🔧 Troubleshooting

### Bot not starting?

```bash
# Check service errors
sudo journalctl -u neonpulse-bot.service -n 50

# Check manual startup
cd /home/deploy/neonpulse/youtube-music-bot
python3 telegram_bot.py
```

### .env not found?

```bash
# Verify file exists
ls -la /home/deploy/neonpulse/youtube-music-bot/.env

# Check permissions
chmod 600 /home/deploy/neonpulse/youtube-music-bot/.env

# Verify content
cat /home/deploy/neonpulse/youtube-music-bot/.env | head -5
```

### Cron not running?

```bash
# Verify crontab
sudo crontab -l

# Check cron logs
sudo tail -50 /var/log/syslog | grep CRON

# Manual test
cd /home/deploy/neonpulse/youtube-music-bot && python3 main_runner.py --mock
```

### YouTube upload fails?

```bash
# Check logs
tail -100 /home/deploy/neonpulse/youtube-music-bot/logs/system.log | grep -i youtube

# Verify YouTube credentials
echo $YOUTUBE_API_KEY
echo $YOUTUBE_CLIENT_ID
```

---

## 📅 Schedule Verification

**Daily Schedule (UTC times):**
- `06:00` — Daily pipeline run (auto)
- `01:00` — Log rotation (auto)
- `02:00 (Sunday)` — Weekly backup (auto)
- `Hourly` — Health monitoring (auto)

**Manual Commands:**
```bash
# Start bot
sudo systemctl start neonpulse-bot.service

# Stop bot
sudo systemctl stop neonpulse-bot.service

# Restart bot
sudo systemctl restart neonpulse-bot.service

# Manual pipeline run
cd /home/deploy/neonpulse/youtube-music-bot && python3 main_runner.py

# Manual monitoring
bash scripts/deploy_monitoring.sh

# Manual backup
bash scripts/deploy_backup.sh
```

---

## 📈 Post-Deployment

### First Run (tomorrow at 06:00 UTC)

Watch the logs:
```bash
tail -f /home/deploy/neonpulse/youtube-music-bot/logs/system.log
```

### Weekly Tasks

```bash
# Check backup completion
ls -lh /home/deploy/neonpulse/youtube-music-bot/state/backups/

# Review performance
jq '.monthly_summary' /home/deploy/neonpulse/youtube-music-bot/state/token_log.json

# Check niche stats
jq '.' /home/deploy/neonpulse/youtube-music-bot/state/genres-history.json
```

### Monthly Tasks

```bash
# API spending analysis
cat /home/deploy/neonpulse/youtube-music-bot/state/token_log.json | jq '.monthly_tokens'

# Test disaster recovery
tar -tzf /home/deploy/neonpulse/youtube-music-bot/state/backups/neonpulse-backup-*.tar.gz | head -20
```

---

## 🎯 Success Criteria

✅ Deployment successful when:

1. **Bot Service Active**
   ```bash
   sudo systemctl status neonpulse-bot.service
   # Shows: active (running)
   ```

2. **Telegram Responsive**
   - `/status` returns system info
   - `/trends` shows trending niches

3. **First Run Succeeds** (06:00 UTC next day)
   - Check: `logs/system.log`
   - Receive: Telegram notification
   - Result: New videos in `state.json`

4. **Monitoring Active**
   - `logs/monitor.log` has hourly entries
   - `logs/backup.log` shows weekly backups
   - No alerts = healthy system

---

## 📞 Support & Escalation

**If issues occur:**

1. Check `logs/system.log` and `logs/error.log`
2. Review PHASE8_DEPLOYMENT_CHECKLIST.md
3. Consult CLAUDE.md v2.3 for system architecture
4. Check SERVER_REHBERI.md for DigitalOcean troubleshooting

---

**Status:** 🚀 Ready for production deployment

**Next Step:** Execute SSH commands in order (Steps 1-15 above)

---

*Prepared: 2026-05-06 by Claude Code*
*Neon Pulse v2.3 — DigitalOcean Production Ready*
