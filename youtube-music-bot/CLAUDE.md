# YouTube Müzik Otomasyonu — Agent Bağlamı

> **Claude için:** Bu dosyayı her oturumda oku. Projenin tam bağlamını buradan al,
> kullanıcıya tekrar sormadan devam et.

---

## Sen Kimsin?

Sen **Claude** (claude-sonnet-4-6) — bu projenin baş mühendisi ve operatörüsün.
Kullanıcı: **Musa Bey** (Antigravity projesi sahibi, Hollanda bazlı).

Görevin:
- Suno ile AI müzik üret
- FFmpeg ile 60-90 dakikalık YouTube videoları oluştur
- YouTube'a otomatik yükle
- Sistemi canlı tut, hataları logla, Telegram'a bildir

Musa Bey teknik değil — kurulumları sen yaparsın, ona sadece sonucu gösterirsin.

---

## Proje Amacı

Kie.ai Suno API → AI müzik → 60-90 dk video → YouTube otomatik upload → AdSense geliri

Hedef niş: **Healing Frequencies + Sleep Music** (düşük rekabet, yüksek izlenme süresi)

---

## API & Kimlik Bilgileri

| Değişken | Açıklama | Durum |
|----------|----------|-------|
| `KIE_API_KEY` | kie.ai API erişimi (Suno dahil) | HAZIR — .env'e eklenecek |
| `YOUTUBE_CLIENT_ID` | Google OAuth2 | Henüz alınmadı |
| `YOUTUBE_CLIENT_SECRET` | Google OAuth2 | Henüz alınmadı |
| `TELEGRAM_BOT_TOKEN` | Bildirimler için | Mevcut sistemden alınacak |
| `TELEGRAM_CHAT_ID` | Bildirimler için | Mevcut sistemden alınacak |

**.env dosyası bu klasörde tutulacak — asla commit etme.**

---

## Sistem Mimarisi

```
CRON (06:00 her gün)
    │
    ▼
[1] suno_generate.py     ← kie.ai API → 15-22 parça MP3 indir
    │
    ▼
[2] audio_process.py     ← FFmpeg: normalize + crossfade + concat → tek MP3
    │
    ▼
[3] video_build.py       ← FFmpeg: background.mp4 loop + audio + waveform
    │
    ▼
[4] thumbnail_make.py    ← Pillow: 1280x720 JPG, otomatik başlık + marka
    │
    ▼
[5] youtube_upload.py    ← Google API v3: upload + metadata + chapters
    │
    ▼
[6] notify.py            ← Telegram: "Video yüklendi: {başlık} → {url}"
```

---

## Dosya Yapısı

```
youtube-music-bot/
├── CLAUDE.md               ← bu dosya
├── .env                    ← API keyleri (git ignore)
├── .gitignore
├── requirements.txt
├── main_runner.py          ← tüm adımları sıraya koyar
├── suno_generate.py        ← kie.ai → MP3 dosyaları
├── audio_process.py        ← FFmpeg ses işleme
├── video_build.py          ← FFmpeg video oluşturma
├── thumbnail_make.py       ← Pillow thumbnail
├── youtube_upload.py       ← YouTube API upload
├── notify.py               ← Telegram bildirim
├── genres.json             ← niş listesi + prompt şablonları
├── backgrounds/            ← looping MP4'ler (Creative Commons)
├── output/                 ← geçici ses/video (her çalışmadan sonra temizlenir)
├── thumbnails/             ← üretilen thumbnail'lar
└── logs/
    └── youtube.log
```

---

## Kanal Stratejisi & İçerik Rotasyonu

`genres.json` dosyasında tanımlı, sistem her gün sıradakini seçer:

```json
[
  {
    "slug": "deep-sleep-432hz",
    "title": "432Hz Healing Frequency | {duration} Hour Deep Sleep Music | No Ads | {year}",
    "prompt": "432hz healing ambient, soft piano, deep sleep, no vocals, relaxing, slow tempo, binaural beats",
    "duration_min": 75
  },
  {
    "slug": "study-lofi",
    "title": "Study Music Lo-Fi | {duration} Hour Focus Beats | No Ads | {year}",
    "prompt": "lofi hip hop, study beats, calm, no lyrics, coffee shop ambience, mellow",
    "duration_min": 90
  },
  {
    "slug": "spa-meditation",
    "title": "Spa & Meditation Music | {duration} Hour Ambient | Relaxing | {year}",
    "prompt": "spa ambient, meditation, tibetan bowls, nature sounds, peaceful, instrumental",
    "duration_min": 60
  },
  {
    "slug": "sleep-rain",
    "title": "Sleep Music with Rain | {duration} Hour | Deep Relaxation | {year}",
    "prompt": "ambient piano, rain sounds, sleep music, very slow, dreamy, no beat",
    "duration_min": 75
  },
  {
    "slug": "binaural-focus",
    "title": "Binaural Beats Focus | {duration} Hour Concentration | Study & Work | {year}",
    "prompt": "binaural beats, alpha waves, focus, concentration, minimal, electronic ambient",
    "duration_min": 60
  }
]
```

---

## YouTube Metadata Şablonu

```python
title    = "{niş} | {X} Hour | No Ads | {yıl}"
category = 10  # Music
tags     = ["sleep music", "432hz", "healing frequencies", "no ads",
            "relaxing music", "study music", "ambient", "meditation music",
            "deep sleep", "focus music", "lofi", "binaural beats"]

description = """
{hook_cümle}

Perfect for sleep, study, meditation, and relaxation.
No ads. No interruptions. Just pure music.

━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRACKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{otomatik_timestamps}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎵 New videos every day — Subscribe for daily music
📧 Business: info@kbmedia.nl
━━━━━━━━━━━━━━━━━━━━━━━━━━━
#sleepmusic #relaxingmusic #studymusic #432hz #ambientmusic
"""
```

---

## Kurulum Kontrol Listesi

```
[ ] 1. Google Cloud Console → YouTube Data API v3 etkinleştir
[ ] 2. OAuth 2.0 credentials → client_secret.json indir → bu klasöre koy
[ ] 3. Sunucuya FFmpeg kur: apt install ffmpeg
[ ] 4. pip install -r requirements.txt
[ ] 5. .env oluştur → KIE_API_KEY, TELEGRAM keyleri ekle
[ ] 6. 5 adet background MP4 indir (Creative Commons, loop uyumlu)
[ ] 7. genres.json yaz
[ ] 8. 6 Python modülü yaz (sıraya göre)
[ ] 9. Test: 1 video oluştur → manuel izle → YouTube'a manuel yükle
[  ] 10. YouTube kanalı oluştur (yoksa)
[ ] 11. youtube_upload.py OAuth token ilk kez al (tarayıcı gerekir)
[ ] 12. main_runner.py test et (end-to-end)
[ ] 13. Sunucuda cron: 0 6 * * * python3 main_runner.py >> logs/youtube.log 2>&1
[ ] 14. Telegram bildirimi test et
```

---

## Bağımlılıklar

```
# requirements.txt
google-api-python-client>=2.100.0
google-auth-oauthlib>=1.1.0
Pillow>=10.0.0
pydub>=0.25.0
requests>=2.31.0
python-dotenv>=1.0.0
```

Sistem: `ffmpeg` (apt), Python 3.11

---

## Gelir Hedefi

| Zaman | Görüntülenme/gün | RPM | Aylık |
|-------|-----------------|-----|-------|
| 3 ay | 500 | €5 | €75 |
| 6 ay | 5.000 | €5 | €750 |
| 12 ay | 30.000 | €6 | €5.400 |

Monetizasyon eşiği: **1.000 abone + 4.000 saat izlenme**
Tahminen: 3-4 ay içinde erişilir (günlük video yüklenirse)

---

## Önemli Kurallar

1. Her video için output/ klasörünü temizle — disk dolmasın
2. YouTube API günlük kotası: 10.000 unit — 1 upload ~1.600 unit kullanır, günde max 6 video
3. Aynı başlığı iki kez kullanma — genres.json rotasyonu sırası karıştır
4. Thumbnail'da telif hakkı olan görsel kullanma — sadece Pillow ile üret
5. .env'i asla git'e commit etme
6. Token süresi dolunca (oauth): kullanıcıya tarayıcı adımını yaptır
