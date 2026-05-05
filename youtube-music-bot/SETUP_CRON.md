# Neon Pulse v2.1 — Cron & Systemd Setup

## Cron Job (Daily Pipeline Execution)

### 1. Edit crontab
```bash
crontab -e
```

### 2. Add daily entry (6 AM Amsterdam time)
```cron
# Neon Pulse v2.1 — Daily music generation
0 6 * * * cd /home/musa/neonpulse && /usr/bin/python3 main_runner.py >> logs/system.log 2>&1
```

**Timing Notes:**
- `0 6` = 06:00 local time
- Runs every day at that time
- Logs to `logs/system.log`
- `.lock` file prevents concurrent runs

### 3. Verify installation
```bash
crontab -l    # List your crons
tail -f logs/system.log  # Watch execution
```

---

## Systemd Service (Telegram Bot — Long-Running)

Telegram bot must run 24/7 to handle `/on`, `/off`, `/run_now` commands and approval buttons.

### 1. Create service file
**File:** `/etc/systemd/system/neonpulse-telegram.service`

```ini
[Unit]
Description=Neon Pulse Telegram Bot (v2.1)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=musa
WorkingDirectory=/home/musa/neonpulse
ExecStart=/usr/bin/python3 telegram_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 2. Enable and start
```bash
sudo systemctl enable neonpulse-telegram.service
sudo systemctl start neonpulse-telegram.service
sudo systemctl status neonpulse-telegram.service
```

### 3. Monitor logs
```bash
journalctl -u neonpulse-telegram.service -f  # Follow logs
journalctl -u neonpulse-telegram.service --since today  # Today's logs
```

### 4. Restart service
```bash
sudo systemctl restart neonpulse-telegram.service
```

---

## Production Checklist

- [ ] `crontab -e` — Add daily 06:00 cron job
- [ ] Systemd service file created at `/etc/systemd/system/neonpulse-telegram.service`
- [ ] `systemctl enable neonpulse-telegram.service` — Auto-restart on reboot
- [ ] Test cron with `--mock` mode first
- [ ] Test Telegram bot connectivity (`/status` command)
- [ ] Verify logs are writing to `logs/system.log` and `logs/error.log`
- [ ] Set up log rotation (optional: `logrotate`)

---

## Manual Testing (Before Production)

```bash
# Test run in mock mode
python main_runner.py --mock --niche synthwave-night-drive

# Test Telegram bot locally
python telegram_bot.py &

# In another terminal, test commands
# (Make sure your chat_id matches TELEGRAM_CHAT_ID in .env)

# Then in Telegram: /status, /on, /off, etc.
```

---

## Troubleshooting

### Cron not running
```bash
# Check system cron logs
grep CRON /var/log/syslog | tail -20

# Verify script permissions
chmod +x main_runner.py
```

### Telegram bot disconnects
```bash
# Restart service
sudo systemctl restart neonpulse-telegram.service

# Check for token validity
grep "TELEGRAM_BOT_TOKEN" .env
```

### State locked (zombie process)
```bash
# Remove lock file if run crashes
rm state/.lock

# Then resume
python main_runner.py  # Reads state, continues from last step
```

---

## Environment Variables (.env)

Required for cron/systemd:
```bash
KIE_API_KEY=...
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...
YOUTUBE_API_KEY=...
YOUTUBE_CHANNEL_ID=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
SYSTEM_TIMEZONE=Europe/Amsterdam
LOG_LEVEL=INFO
```

Ensure `.env` is NOT in `.gitignore` root (add to `/home/musa/neonpulse/.env` directly, outside git).

---

## Metrics & Monitoring

Monitor these files during production:

| File | Purpose |
|------|---------|
| `logs/system.log` | Main pipeline execution log |
| `logs/error.log` | Error details |
| `state/state.json` | Current run state |
| `state/genres-history.json` | Niche performance metrics |
| `state/token_log.json` | Suno API cost tracking |
| `state/research/trend_report_*.json` | Daily trend reports (cache) |

---

## Cost Tracking

Monthly Suno API usage:
```bash
cat state/token_log.json | jq '.monthly_summary'
```

Expected: ~€30-50/month for 30 videos (3 API calls each = 90 calls total)

---

**Next:** Run `/ultrareview` on this branch or `git push` to production 🚀
