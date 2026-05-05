# Pre-Deployment Checklist — Neon Pulse v2.3

Deployment başlamadan önce aşağıdaki items'ı kontrol et:

## 📋 VPS Hazırlığı

- [ ] VPS sunucusu sağlanmış (Ubuntu 22.04 LTS)
- [ ] SSH key'i set up edilmiş
- [ ] SSH ile sunucuya bağlanabiliyor
- [ ] VPS IP adresi ve SSH credentials hazır
- [ ] Root veya sudo access var

## 🔑 API Credentials

Tüm credentials'lar hazır ve test edilmiş mi?

### Suno API
- [ ] KIE_API_KEY alındı (kie.ai dashboard)
- [ ] Token kredisi var (at least 30 credit for first run)
- [ ] Çalıştığı test edildi

### YouTube API
- [ ] YOUTUBE_API_KEY elde edildi (Google Cloud Console)
- [ ] YOUTUBE_CLIENT_ID elde edildi
- [ ] YOUTUBE_CLIENT_SECRET elde edildi
- [ ] YOUTUBE_CHANNEL_ID elde edildi (Neon Pulse music channel)
- [ ] YOUTUBE_REFRESH_TOKEN hazırlanacak (first OAuth flow)

### Telegram Bot
- [ ] Bot oluşturuldu (@BotFather)
- [ ] TELEGRAM_BOT_TOKEN alındı
- [ ] TELEGRAM_CHAT_ID (Musa's personal chat) alındı

### Optional
- [ ] PEXELS_API_KEY (background videos)
- [ ] NVIDIA_API_KEY (if using NVIDIA services)

## 📦 Repository

- [ ] YouTube Music Bot repository erişilebilir (GitHub)
- [ ] Latest version (main branch) kontrol edildi
- [ ] CLAUDE.md v2.3 okundu ve anlaşıldı
- [ ] PHASE reports incelendi (Phase 0-8)
- [ ] Deploy scripts'e bakıldı (scripts/ directory)

## 🗂️ Dosyalar Hazır mı?

**VPS'de oluşturulacak:**
- [ ] `/home/deploy/neonpulse/` — Project directory
- [ ] `.env` — Credentials file (locally prepared)
- [ ] `state/` — State management directory
- [ ] `logs/` — Log directory
- [ ] `output/` — Working directory
- [ ] `backgrounds/` — Video backgrounds

## ⚙️ Sistem Gereksinimleri

**VPS Specs:**
- [ ] 2GB RAM minimum
- [ ] 20GB SSD minimum
- [ ] Ubuntu 22.04 LTS (or compatible)
- [ ] Python 3.11+ available
- [ ] FFmpeg 5.0+ installable
- [ ] Internet connection stable

## 🔐 Security Review

**Credentials Security:**
- [ ] .env file `.gitignore`'da (no accidental pushes)
- [ ] .env local'de prepare edilecek, sunucuya yapıştırılacak
- [ ] API keys dev environment'da test edildi
- [ ] Credentials'lar secure storage'da (not in code/git)

**Server Security:**
- [ ] Firewall configured (SSH 22, optional HTTPS 443)
- [ ] SSH key authentication active
- [ ] Password authentication disabled (optional but recommended)
- [ ] Non-root deploy user created
- [ ] File permissions set correctly (600 for .env, 755 for scripts)

## 📚 Documentation Review

- [ ] VPS_QUICK_START.md okundu
- [ ] PHASE8_DEPLOYMENT_CHECKLIST.md incelendi
- [ ] DEPLOYMENT_SUMMARY.md kontrol edildi
- [ ] scripts/deploy_setup.sh anlaşıldı
- [ ] CLAUDE.md v2.3 — Production Deployment section okundu

## 🧪 Pre-Flight Tests (Optional)

Deployment öncesi local test:

- [ ] `python3 main_runner.py --mock` çalıştırıldı (2 saniye)
- [ ] Tüm required packages installed (`pip list`)
- [ ] FFmpeg working (`ffmpeg -version`)
- [ ] .env variables test edildi (API connectivity)
- [ ] Telegram bot token valid (`curl ... getMe`)

## 📱 Notification Setup

Deployment ve first run notifications:

- [ ] Telegram chat ID doğrulandı
- [ ] Telegram bot token test edildi
- [ ] Notification messages ayarlandı (/on /off /status)
- [ ] Test message gönderilebildi

## ✅ Final Sign-Off

**Deployment'a başlamadan önce confirm:**

- [ ] Tüm credentials hazır ve test edilmiş
- [ ] VPS erişilebilir ve SSH working
- [ ] Documentation okundu
- [ ] Security review completed
- [ ] Backup strategy anlaşıldı

---

## 🚀 Deployment Flow

Hazırlandıktan sonra:

1. SSH ile VPS'ye bağlan
2. `scripts/deploy_setup.sh` çalıştır (5 dakika)
3. `.env` dosyasını edit et (credentials ekle)
4. Bot'u start et: `systemctl start neonpulse-bot.service`
5. Test'i çalıştır: `python3 main_runner.py --mock`
6. Telegram'dan `/status` gönder
7. 06:00 UTC'de first run'ı izle

---

## ⏰ Timeline

| Adım | Süre | Notlar |
|------|------|--------|
| VPS Provision | 5 min | Cloud provider'dan |
| SSH Setup | 2 min | Key generation + config |
| Deploy Script | 5 min | Otomatik installation |
| .env Setup | 3 min | Manual credentials entry |
| Bot Start | 1 min | systemctl start |
| Dry-run Test | 2 min | --mock mode |
| **TOPLAM** | **~20 min** | Production ready |

---

## 📞 Support

**Deployment sırasında sorun çıkarsa:**

1. Adımı tekrarlayıp hata mesajını not et
2. Error log'ları kontrol et
3. CLAUDE.md v2.3 — Hata Yönetimi section'ı oku
4. PHASE8_DEPLOYMENT_CHECKLIST.md — Troubleshooting section'ı kontrol et

---

**Tamamlanmış mı?** ✅ Deployment başlatabilirsin!

---

*Prepared: 2026-05-06 by Claude Code*
*Neon Pulse v2.3 — Production Ready*
