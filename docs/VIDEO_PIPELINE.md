# Video Pipeline — Technische Documentatie

> Systeem: Antigravity Agency OS
> Laatste update: 2026-04-20

---

## Overzicht

Het videosysteem produceert automatisch korte Reels (30–60s) voor twee merken:
- **@GlowUpNL** — energiek, beauty & wellness voor vrouwen 25–45
- **@HolistiGlow** — rustgevend, holistische gezondheid & kruidenkunde

### Automatisch schema (Amsterdam tijd)
| Tijd | Merk | Thema |
|---|---|---|
| 08:00 | @HolistiGlow | Ochtend wellness |
| 12:30 | @GlowUpNL | Middagenergie |
| 20:15 | @GlowUpNL | Avondroutine |
| 22:00 | @HolistiGlow | Nacht / slaap |

### Handmatige commando's (Telegram)
```
/luna <onderwerp>   → @GlowUpNL video
/zen <onderwerp>    → @HolistiGlow video
/priya <onderwerp>  → Dr. Priya HeyGen avatar video
```

---

## Pipeline Architectuur

```
Telegram Command / Scheduler
        ↓
  Orchestrator (src/orchestrator.py)
        ↓
  ContentAgent (src/agents/content_agent.py)
    → Schrijft script + metadata
    → Delegeert via next_agent="video_producer"
        ↓
  VideoProducerAgent (src/agents/video_producer_agent.py)
    → Genereert title, caption, tags, Pexels zoekterm
    → Roept VideoSkill aan
        ↓
  VideoSkill (src/skills/video_skill.py)
    → Haalt achtergrondvideo op via Pexels API
    → TTS via ElevenLabs
    → FFmpeg: video + audio + ASS ondertitels
    → Output: outputs/video_TIMESTAMP.mp4
        ↓
  Uploader (src/skills/uploader_skill.py)
    → Upload naar arkmediaflow.com/media/
    → Geeft publieke URL terug
        ↓
  Telegram bericht met knoppen:
    📥 Download | ✍️ Revise | 📸 Instagram | 📱 TikTok
```

---

## Bestanden

| Bestand | Functie |
|---|---|
| `src/agents/content_agent.py` | Script schrijven, delegeren naar video |
| `src/agents/video_producer_agent.py` | Metadata genereren, VideoSkill aanroepen |
| `src/skills/video_skill.py` | FFmpeg pipeline, Pexels, ElevenLabs |
| `src/skills/uploader_skill.py` | Upload naar publieke URL |
| `src/scheduler/content_scheduler.py` | Automatisch schema 4x per dag |
| `src/interfaces/telegram/handler.py` | Telegram commando's & callbacks |

---

## Veelvoorkomende Problemen & Oplossingen

### Video wordt niet geproduceerd
1. Check PM2: `pm2 status` — bot moet `online` zijn
2. Check logs: `pm2 logs my_ai_ark_agent_bot --lines 50`
3. Controleer of `reel` in de prompt staat (triggert VideoProducer)
4. Check ElevenLabs/Pexels API keys in `.env`

### Video duurt te lang (timeout)
- Ken Burns zoompan is UITGESCHAKELD (veroorzaakte 300s timeout)
- FFmpeg preset: `fast`, crf: `20`
- Max video duur: 60s
- Als het >120s duurt → check Pexels API responstijd

### Bot antwoordt niet op commando's
- Check: `pm2 logs` voor errors
- Check: TELEGRAM_TOKEN in `.env`
- Herstart: `pm2 restart my_ai_ark_agent_bot`

### "Can't parse entities" Telegram error
- Nooit `parse_mode="Markdown"` gebruiken bij dynamische content met task_id of onderwerpnamen
- Alleen vaste tekst mag Markdown gebruiken

### MCP bridge hangt
- `use_mcp=False` is standaard in kritieke paden
- MCP timeout: 8 seconden (was 60s)

---

## API Keys (in .env)

| Key | Gebruik |
|---|---|
| `OPENAI_API_KEY` | Script genereren, metadata |
| `ELEVENLABS_API_KEY` | TTS voice-over |
| `ELEVENLABS_VOICE_ID` | Stem ID voor ElevenLabs |
| `PEXELS_API_KEY` | Achtergrondvideo's |
| `HEYGEN_API_KEY` | Dr. Priya avatar (/priya commando) |
| `TELEGRAM_TOKEN` | Bot authenticatie |
| `TELEGRAM_CHAT_ID` | Scheduler output chat |

---

## Video Kwaliteit Instellingen

```python
# src/skills/video_skill.py
overlay_alpha = 35          # Pexels achtergrond transparantie (0=volledig zichtbaar, 100=zwart)
ffmpeg_preset = "fast"      # Encodeersnelheid
crf = 20                    # Kwaliteit (lager = beter, 18-28 normaal)
max_duration = 60           # Seconden
subtitle_fontsize = 42      # ASS ondertitels lettergrootte
subtitle_wrap = 26          # Tekens per regel
```

---

## Todo / Verbeterpunten

- [ ] Instagram auto-publish via Meta API testen
- [ ] TikTok auto-publish integreren
- [ ] Video thumbnail genereren (voor YouTube)
- [ ] A/B testing: twee versies per slot genereren
- [ ] HeyGen avatar voor alle slots (nu alleen /priya)
