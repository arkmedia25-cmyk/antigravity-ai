# YouTube Music Bot — 4-Channel Automation

Auto-generates daily AI music videos and uploads them to 4 YouTube channels.

## Channels

| Channel | Type | Niche |
|---------|------|-------|
| binauralmind | binaural | Delta / Theta / Alpha / Beta / Gamma binaural beats |
| healingflow | standard | 528Hz, Tibetan bowls, Reiki, Chakra, Spa |
| neonpulse | standard | Cinematic, EDM, Electronic, Ambient |
| sleepwave | standard | Sleep music, Rain, Piano, Nature, Delta waves |

## Pipeline

```
queue_runner.py  (runs all channels sequentially)
  ↓
main_runner.py --channel {slug}
  ↓
suno_generate.py   → kie.ai API (V4_5) → MP3 download
  ↓
audio_process.py   → FFmpeg normalize + crossfade → final.mp3
  ↓                  (track_paths x2 loop = 50% cost saving)
binaural_generate.py  → numpy WAV + FFmpeg mix  [binauralmind only]
  ↓
video_build.py     → FFmpeg 1920x1080 background loop + waveform overlay
  ↓
thumbnail_make.py  → Pillow 1280x720 JPEG → channels/{slug}/thumbnails/
  ↓
youtube_upload.py  → YouTube Data API v3 → scheduled publish
  ↓
notifier.py        → Telegram notification
```

## Folder Structure

```
channels/
  {slug}/
    channel.json       — channel config (active, token_file, telegram_chat_id)
    genres.json        — genre rotation list
    token.pickle       — YouTube OAuth token
    backgrounds/       — bg_{genre-slug}.mp4 per genre
    thumbnails/        — generated thumbnails (per run)
    output/            — saved video copies (permanent)
    .rotation_state.json  — tracks last used genre index
output/                — working temp dir (cleared after each run)
pipeline/              — suno_generate, audio_process, video_build, thumbnail_make, youtube_upload
core/                  — notifier
```

## Running

```bash
# Run all 4 channels
python queue_runner.py

# Run with publish-hour override (test: publish today at 13:00 Amsterdam)
python queue_runner.py --publish-hour 13

# Run single channel
python main_runner.py --channel neonpulse --publish-hour 13

# Test without YouTube upload
python main_runner.py --channel neonpulse --no-upload
```

## Scheduler (Windows Task Scheduler)

Runs nightly at 01:00 via Windows Task Scheduler:
```
Program: C:\Users\mus-1\AppData\Local\Programs\Python\Python311\python.exe
Arguments: -u queue_runner.py
Start in: D:\OneDrive\Bureaublad\Antigravity\youtube-music-bot
```

## Credentials

| Service | Location |
|---------|----------|
| kie.ai API key | `.env` → `KIE_API_KEY` |
| Telegram Bot token | `.env` → `TELEGRAM_TOKEN` |
| YouTube OAuth | `channels/{slug}/token.pickle` (one per channel) |
| Google OAuth client | `.env` → `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |

## Genres per Channel (5 per channel, rotates daily)

**binauralmind:** delta-sleep, theta-meditation, alpha-focus, beta-energy, gamma-creativity

**healingflow:** 528hz-healing, tibetan-bowls, reiki-healing, chakra-healing, spa-relaxation

**neonpulse:** epic-cinematic, electronic-focus, dark-cinematic, energy-edm, futuristic-ambient

**sleepwave:** deep-sleep-432hz, rain-sleep, delta-waves-sleep, piano-sleep, nature-sleep

## YouTube ToS Rules

- **NEVER** put "No Ads", "Ad-Free" in titles, tags, thumbnails or descriptions
- Use `{duration} Min` not `{duration} Hour` in title templates
- Each channel slug must be unique across all channels

## Re-authenticating YouTube OAuth

```bash
python get_token.py --channel binauralmind
```

## Reset Genre Rotation (re-run a specific genre)

```bash
# Reset binauralmind to start from delta-sleep (index 0)
python -c "import json; open('channels/binauralmind/.rotation_state.json','w').write(json.dumps({'last_index':-1,'last_date':'2026-01-01'}))"
```

## Logs

Each channel writes to `logs/{slug}.log`. Queue summary in `logs/queue.log`.
