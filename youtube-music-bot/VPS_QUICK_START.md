# Neon Pulse v2.3 — VPS Quick Start Guide

**Tarih:** 2026-05-06  
**Versiyon:** v2.3 (Production Ready)  
**Hedef:** Ubuntu 22.04 LTS VPS

---

## 📋 Ön Koşullar

- ✅ VPS sunucusu (Ubuntu 22.04 LTS recommended)
- ✅ Minimum 2GB RAM, 20GB SSD
- ✅ SSH access (root veya sudo)
- ✅ Internet bağlantısı

---

## 🚀 Hızlı Kurulum (5 dakika)

### 1. SSH ile sunucuya bağlan

```bash
ssh root@YOUR_VPS_IP
```

### 2. Deploy script'i indir ve çalıştır

```bash
cd /tmp
git clone https://github.com/arkmedia25-cmyk/antigravity-ai.git
cd antigravity-ai/youtube-music-bot
bash scripts/deploy_setup.sh
```

**Script otomatik olarak:**
- ✅ Sistem güncellemesi (apt update/upgrade)
- ✅ Python 3.11, FFmpeg, Git kurulumu
- ✅ `deploy` user'ı oluştur
- ✅ `/home/deploy/neonpulse` dizini oluştur
- ✅ Repository clone'la
- ✅ Python dependencies yükle
- ✅ Directory structure oluştur
- ✅ Systemd service yükle
- ✅ Cron jobs configure et
- ✅ Logrotate setup et
- ✅ Dry-run test çalıştır

---

## 🔐 Adım 2: Credentials Ekle

Script tamamlandıktan sonra `.env` dosyasını düzenle:

```bash
sudo nano /home/deploy/neonpulse/youtube-music-bot/.env
```

**Gerekli değişkenler:**

```env
# Suno API
KIE_API_KEY=your_suno_api_key

# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_client_secret
YOUTUBE_REFRESH_TOKEN=your_refresh_token (first OAuth flow)
YOUTUBE_CHANNEL_ID=your_channel_id

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Optional
PEXELS_API_KEY=your_pexels_key
NVIDIA_API_KEY=your_nvidia_key
```

**Kaydet ve çık:** `Ctrl+X` → `Y` → `Enter`

---

## ✅ Adım 3: Bot Başlatma ve Doğrulama

### Bot'u başlat

```bash
sudo systemctl start neonpulse-bot.service
```

### Bot status kontrol et

```bash
sudo systemctl status neonpulse-bot.service
```

Beklenen çıktı: `active (running)`

### Bot loglarını izle

```bash
tail -f /home/deploy/neonpulse/youtube-music-bot/logs/bot.log
```

### Telegram Bot test

Bot'a Telegram'dan test mesajı gönder:

```
/status
```

Beklenen cevap: System information (uptime, kalan disk, vb.)

---

## 📅 Otomasyonu Doğrula

Cron jobs kurulu:

```bash
sudo -u deploy crontab -l
```

**Beklenen schedule:**
- `0 6 * * *` — Günlük pipeline (06:00 UTC)
- `0 1 * * *` — Log rotation (01:00 UTC)
- `0 2 * * 0` — Haftalık backup (Pazar 02:00 UTC)
- `0 * * * *` — Saatlik monitoring

---

## 📊 İlk Run'ı İzle

**Sonraki sabah 06:00 UTC'de:**

```bash
# System logları izle
tail -f /home/deploy/neonpulse/youtube-music-bot/logs/system.log

# State'i kontrol et
jq . /home/deploy/neonpulse/youtube-music-bot/state/state.json

# Bot'a Telegram'dan /status gönder
```

---

## 🔧 Troubleshooting

### Bot çalışmıyor?

```bash
# Status kontrol
sudo systemctl status neonpulse-bot.service

# Detailed logs
sudo journalctl -u neonpulse-bot.service -n 50

# Manual başlat
cd /home/deploy/neonpulse/youtube-music-bot
python3 telegram_bot.py
```

### .env okuma hatası?

```bash
# Permissions kontrol
ls -la /home/deploy/neonpulse/youtube-music-bot/.env

# Deploy user tarafından okunabilir mi test
sudo -u deploy cat /home/deploy/neonpulse/youtube-music-bot/.env
```

### Dry-run test

```bash
cd /home/deploy/neonpulse/youtube-music-bot
python3 main_runner.py --mock --niche synthwave-night-drive
```

Beklenen: İşlem ~2 saniyede tamamlanır, hata log'a yazılmaz.

---

## 📈 Production Monitoring

**Günlük:** Logları kontrol et
```bash
tail -100 /home/deploy/neonpulse/youtube-music-bot/logs/system.log
```

**Haftalık:** Performansı analiz et
```bash
jq '.monthly_summary' /home/deploy/neonpulse/youtube-music-bot/state/token_log.json
jq '.' /home/deploy/neonpulse/youtube-music-bot/state/genres-history.json
```

**Aylık:** Backup test et
```bash
ls -lh /home/deploy/neonpulse/youtube-music-bot/state/backups/
```

---

## 🚨 Önemli Kurallar

- ❌ `.env` dosyasını paylaşma (credentials içeriyor)
- ❌ Git push'u `.env` ile yapma (already in .gitignore)
- ✅ Her hafta backups kontrol et
- ✅ Error logs'u günlük oku
- ✅ Disk space'i (>90%) alert'e göz at

---

## 📞 Destek

**Sorun çıkarsa:**

1. Log dosyasını oku: `/home/deploy/neonpulse/youtube-music-bot/logs/`
2. PHASE8_DEPLOYMENT_CHECKLIST.md'i incele
3. CLAUDE.md v2.3'te sistem mimarisini oku

---

## İleri Adımlar (Optional)

### Automatic Backups to Cloud

S3 sync'i ekle (deploy_backup.sh'de):
```bash
aws s3 sync /home/deploy/neonpulse/youtube-music-bot/state/backups/ s3://your-bucket/neonpulse/
```

### Custom Domain SSL

HTTPS kurulumu (opsiyonel):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --standalone -d your-domain.com
```

### Process Monitoring (PM2)

```bash
npm install -g pm2
pm2 start telegram_bot.py --name neonpulse-bot
pm2 save
```

---

**Tamamlandı!** 🎉

Sistem production'da çalışmaya hazır. İlk video yarın 06:00 UTC'de otomatik üretilecek.
