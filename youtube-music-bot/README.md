# Neon Pulse Music — YouTube Automation Pipeline

> AI-powered synthwave/cyberpunk music generation and YouTube automation for **Neon Pulse music** channel.

## 📊 Project Status (2026-05-09)

**Version:** v2.4 — Backend Complete, Deployment Pending SSH Configuration

| Component | Status | Notes |
|-----------|--------|-------|
| **Background Preparation** | ✅ Complete | 6 niches × 20 MP4 videos (Pexels) |
| **Thumbnail Generation** | ✅ Complete | Pillow-based 1280×720 PNG (neon themes) |
| **Video Build Pipeline** | ✅ Complete | FFmpeg background + audio merge (30 FPS) |
| **Audio Processing** | ✅ Complete | Normalize, crossfade, dynamic loop |
| **Mock Full Pipeline** | ✅ Complete | 14-step dry-run verified |
| **State Recovery** | ✅ Complete | `/resume` functionality working |
| **Telegram Bot** | ✅ Ready | Keyboard UI, inline approval buttons |
| **VPS Deployment** | ❌ Blocked | SSH key auth missing (ED25519) |
| **Real Suno API** | ⏳ Pending | Ready locally, blocked on VPS |
| **YouTube Upload** | ⏳ Pending | OAuth ready, production test pending |

---

## 🎯 What Works Now (May 9, 2026)

### ✅ Completed Session (May 8)

1. **Background Video Library** — 6 niches × 20 HD videos from Pexels
   ```bash
   python3 scripts/backgrounds_downloader.py
   # ✅ outputs: backgrounds/{niche}/*.mp4
   ```

2. **FFmpeg Seamless Loop Testing** — Validated loop frame continuity
   ```bash
   python3 scripts/test_ffmpeg_loops.py
   # ✅ test_loops/niche_loop3x.mp4
   ```

3. **Neon-Themed Thumbnails** — Dynamic 1280×720 PNG with per-niche colors
   ```bash
   python3 scripts/thumbnail_maker.py
   # ✅ thumbnails/output/{niche}_*.png
   ```

4. **Video Build Module** — Background + audio merge with FPS lock
   ```python
   from modules.video_build import build_video
   build_video(audio_path, niche="synthwave-night-drive")
   # ✅ output/video/synthwave-night-drive_*.mp4
   ```

5. **Full Pipeline Dry-Run** — All 14 steps simulated (no token spend)
   ```bash
   python3 main_runner.py --mock --niche synthwave-night-drive
   # ✅ Preflight → Trend → Niche → Suno-mock → Audio → Video → Thumbnail
   ```

6. **State Recovery** — Tested `/resume` from mid-pipeline failure
   ```bash
   # Simulated failure at step 5, then:
   python3 main_runner.py --resume
   # ✅ Restarted from step 6, artifacts preserved
   ```

---

## 📋 14-Step Pipeline

```
1.  preflight_check     → Disk, FFmpeg, API keys validation
2.  trend_research      → YouTube viral analysis (YouTube Data API)
3.  niche_select        → Select niche by trend score
4.  suno_generate       → 3 API calls = 6 music tracks (~18 min)
5.  audio_process       → Normalize, crossfade, dynamic loop
6.  video_build         → Background video + audio → MP4
7.  thumbnail_make      → Dynamic 1280×720 PNG (Pillow)
8.  telegram_review     → Send long video for 24h approval
9.  youtube_upload      → Upload as UNLISTED (after approval)
10. short_extract       → 45-second peak section (vertical)
11. telegram_review     → Send short video for approval
12. youtube_upload      → YouTube Short (public)
13. memory_save         → Update genres-history.json
14. cleanup             → Remove output/ (success only)
```

Failure stops pipeline. Use `/resume` to continue from last checkpoint.

---

## 🚀 Quick Start (Local Machine)

### Installation
```bash
pip install -r requirements.txt
# Requires: Python 3.11+, FFmpeg 5.0+
```

### Configuration
```bash
cp .env.example .env
# Fill in API keys:
# - PEXELS_API_KEY (free: pexels.com/api)
# - YOUTUBE_API_KEY (YouTube Data API)
# - YOUTUBE_CLIENT_ID/SECRET/REFRESH_TOKEN
# - YOUTUBE_CHANNEL_ID (Neon Pulse music)
# - KIE_API_KEY (Suno proxy: kie.ai)
# - TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
```

### Test (Zero Cost)
```bash
# Mock full pipeline
python3 main_runner.py --mock --niche synthwave-night-drive

# Download backgrounds
python3 scripts/backgrounds_downloader.py

# Generate thumbnails
python3 scripts/thumbnail_maker.py

# Test individual modules
python3 -m modules.preflight_check
python3 -m modules.trend_research --show-latest
```

### Real Run (Costs ~€10)
```bash
# Full pipeline with real Suno API
python3 main_runner.py --niche synthwave-night-drive
# Telegram will ask for approval at steps 8 and 11
```

---

## 📁 Directory Structure

```
neonpulse/
├── CLAUDE.md                      # v2.4 Complete docs (889 lines)
├── README_v24.md                  # This file
├── requirements.txt
├── main_runner.py                 # 14-step orchestrator
├── telegram_bot.py                # Bot daemon
├── .env                           # API keys (gitignored)
│
├── scripts/
│   ├── backgrounds_downloader.py  ✅ Pexels → backgrounds/
│   ├── test_ffmpeg_loops.py       ✅ FFmpeg validator
│   ├── thumbnail_maker.py         ✅ Pillow generator
│   ├── deploy_backup.sh           📦 Backup scripts
│   └── deploy_monitoring.sh       📦 Health checks
│
├── modules/
│   ├── preflight_check.py         ✅ System validation
│   ├── trend_research.py          ✅ YouTube API analysis
│   ├── niche_select.py            ✅ Trend-based selection
│   ├── suno_generate.py           ✅ Suno API + mock mode
│   ├── audio_process.py           ✅ FFmpeg pipeline
│   ├── video_build.py             ✅ Background + audio merge
│   ├── thumbnail_make.py          ✅ Pillow generation
│   ├── telegram_review.py         ✅ Approval flow
│   ├── youtube_upload.py          ✅ OAuth upload
│   ├── short_extract.py           ✅ 45s extraction
│   ├── memory_save.py             ✅ State persistence
│   ├── cleanup.py                 ✅ Output cleanup
│   └── notify.py                  ✅ Completion alerts
│
├── state/
│   ├── state.json                 # Current run
│   ├── genres-history.json        # Niche performance
│   ├── token_log.json             # Suno spending
│   └── research/                  # Trend cache
│
├── backgrounds/
│   ├── synthwave-night-drive/     # 20× MP4
│   ├── cyberpunk-ambient/         # 20× MP4
│   ├── lofi-cyberpunk/            # 20× MP4
│   ├── darksynth-workout/         # 20× MP4
│   ├── outrun-retrowave/          # 20× MP4
│   └── vaporwave-chill/           # 20× MP4
│
├── thumbnails/output/             # Generated PNG (1280×720)
├── output/
│   ├── audio/                     # 60-90min MP3
│   ├── video/                     # Full length MP4
│   └── short/                     # 45s vertical MP4
│
├── logs/
│   ├── system.log
│   ├── error.log
│   ├── token_usage.log
│   └── claude-md-history/         # v2.3, v2.2, etc.
│
└── deployment/
    ├── .crontab                   # 06:00 UTC daily
    ├── neonpulse-bot.service      # Systemd service
    └── PHASE8_DEPLOYMENT_CHECKLIST.md
```

---

## 🎨 6 Niche Themes

| Niche | Accent Color | Secondary | Target Audience |
|-------|-------------|-----------|-----------------|
| synthwave-night-drive | #ff006e (pink) | #00f5ff (cyan) | 80s synth lovers |
| cyberpunk-ambient | #00ff88 (neon-green) | #ff0099 (magenta) | Sci-fi chill |
| lofi-cyberpunk | #eeba1f (gold) | #ff00ff (magenta) | Study/code music |
| darksynth-workout | #ff3366 (red) | #ffff00 (yellow) | Gym/aggressive |
| outrun-retrowave | #ff006e (pink) | #00ffff (cyan) | Retro fans |
| vaporwave-chill | #ff1493 (deep-pink) | #00ced1 (turquoise) | Aesthetic/dreamy |

---

## 📱 Telegram Commands

| Command | Button | Action |
|---------|--------|--------|
| `/on` | 🟢 | Enable system (allow cron) |
| `/off` | 🔴 | Disable system |
| `/run_now` | ▶️ | Start pipeline now |
| `/cancel` | ⏹️ | Stop running pipeline |
| `/status` | 📊 | Current status + last run |
| `/trends` | 📱 | Latest trend report |
| `/tokens` | 💰 | Suno API balance |
| `/history` | 📺 | Last 10 videos |
| `/test` | 🧪 | Mock dry-run (free) |
| `/research` | 🔍 | Manual trend analysis |

**During approval:** Inline buttons (✅ Approve, ❌ Reject, 🔄 Regenerate)

---

## 🚨 Current Blocker

### ❌ VPS SSH Access

**Issue:** ED25519 key not authorized on `deploy@168.231.107.135`
- Local key exists: `~/.ssh/id_ed25519.pub`
- VPS `authorized_keys` not configured
- GitHub clone/pull from VPS fails

**Fix Requires:** Terminal access to VPS (password, IPMI, host panel, etc.)

```bash
# Once in VPS:
ssh-keygen -t ed25519 -f ~/.ssh/github_deploy
cat ~/.ssh/github_deploy.pub > ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

---

## 💰 Operating Costs

| Item | Est./Month |
|------|-----------|
| Suno API (kie.ai) | €30–50 |
| YouTube Data API | Free |
| Telegram | Free |
| VPS (2GB/20GB) | €5–10 |
| **Total** | **€35–60** |

Pilot phase: break-even within 3–4 months via AdSense.

---

## ✅ Verified Features

- ✅ Background video downloads (Pexels API, 6 niches × 20 each)
- ✅ FFmpeg seamless loops (validated, no frame jumps)
- ✅ Dynamic thumbnails (1280×720, theme colors)
- ✅ Video encoding (H.264, 30 FPS, audio sync)
- ✅ Audio processing (crossfade, normalize, loop)
- ✅ Mock pipeline (full dry-run, zero cost)
- ✅ State recovery (`/resume` from any step)
- ✅ Telegram UI (keyboard, inline buttons)
- ✅ YouTube OAuth (ready, untested)
- ✅ Logging + error tracking

---

## 📋 Next Steps

1. **[BLOCKER]** Fix VPS SSH access
2. **Test real Suno run** (local machine)
3. **Deploy to VPS** (copy .env, start service)
4. **First production video** (approve via Telegram)
5. **Monitor 30 days** (track metrics, optimize niches)

---

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** — Complete technical reference (v2.4, 889 lines)
- **[Deployment Checklist](deployment/PHASE8_DEPLOYMENT_CHECKLIST.md)** — VPS setup guide

---

**Last Updated:** 2026-05-09 | **Status:** Backend ✅ Deployment ⏳ | **Version:** v2.4
