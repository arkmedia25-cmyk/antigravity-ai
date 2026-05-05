# YouTube Müzik Otomasyonu — Agent Bağlamı (v2.1)

> **Claude için:** Bu dosyayı her oturum başında oku. Kullanıcı: **Musa** (Hollanda).
> **Felsefe:** Token Koruma > Onay > Otomasyon > Hız.
> **Altın Kural:** Hata olursa SİSTEM DURUR. Suno tokeni asla riske atılmaz.
> **Dil:** Türkçe yorum, İngilizce kod (snake_case), İngilizce video metadata.

---

## Kanal Bilgisi & Marka Kimliği

**Kanal Adı:** Neon Pulse music
**Durum:** Mevcut kanal — yeni kanal AÇILMAYACAK, bu kanal üzerinden devam edilecek.
**Marka Tonu:** Elektronik, retro-fütüristik, synthwave/cyberpunk estetiği.
**Görsel Dil:** Neon ışıklar, mor-pembe-cyan paleti, 80'ler retro-futurism, gece şehir manzaraları, geometrik desenler.
**Hedef Kitle:** 18-35 yaş, oyun severler, çalışma müziği dinleyenler, synthwave/retrowave hayranları, geç saat çalışanlar.

**Marka ile uyumlu niş aileleri:**
- Synthwave / Retrowave / Outrun
- Cyberpunk ambient / Darksynth
- Lofi cyberpunk / Chill synthwave
- Future funk / Vaporwave
- Neon noir / Dark electronic
- 80s nostalgia / Retro arcade

**Marka ile UYUMSUZ olanlar (bu kanalda YAPMA):**
- Klasik müzik, akustik gitar
- Sleep music with rain, piano lullaby
- Spa / meditation / tibet bowls
- Acoustic lofi / coffee shop ambience
- Healing frequencies / 432Hz / chakra (marka tonuna uymaz)

---

## Proje Özeti

AI müzik üretip **Neon Pulse music** kanalına otomatik yükleyen pipeline. Mevcut kanalda viral olabilecek synthwave/cyberpunk müzikleri üretir.

**Akış:** Trend araştırma → Suno müzik → uzun video (60-90 dk) → Telegram onay → YouTube yayın → 50sn Short çıkar → Telegram onay → YouTube Short yayın.

**Strateji:** Her run öncesi YouTube'da synthwave/cyberpunk nişinde trend olanı araştır, viral potansiyali yüksek format/başlık/süre seç. 30 günlük metrik takibi ile niş alt-türlerini optimize et.

---

## Sistem Mimarisi (Onay Akışlı v2)

```
[CRON 06:00 / Telegram /run_now]
    │
    ▼
[0] preflight_check.py    ← TÜM ÖN KOŞULLAR. Hata varsa Suno'ya hiç DOKUNMA.
    │   ✓ Sistem ON mu? (state.json)
    │   ✓ Disk > 5 GB?
    │   ✓ FFmpeg çalışıyor mu?
    │   ✓ YouTube token geçerli mi?
    │   ✓ Telegram erişilebilir mi?
    │   ✓ Background video dosyası var mı?
    │   ✓ Önceki run temiz mi (lockfile yok)?
    ▼
[1] trend_research.py     ← YouTube'da Neon Pulse nişinde trend araştır
    │   • YouTube Data API ile son 7-30 gün viral videoları getir
    │   • Başlık kalıpları, süre, tag, thumbnail stilini analiz et
    │   • Viral skoru en yüksek alt-niş ve format öner
    │   • Sonuç: research/trend_report_YYYYMMDD.json
    ▼
[2] niche_select.py       ← Trend raporu + history → niş ve prompt seç
    │
    ▼
[3] suno_generate.py      ← 3 API çağrısı = 6 parça (~18-24 dk)
    │   ⚠ Her çağrı öncesi state.json güncelle.
    │   ⚠ Hata olursa: kaydet, dur, Telegram'a haber ver.
    ▼
[4] audio_process.py      ← FFmpeg: 6 parça normalize + crossfade
    │                       → loop 3x veya 4x → 60 veya 90 dk MP3
    ▼
[5] video_build.py        ← Niş havuzundan animated background seç
    │                       → loop + audio + (opsiyonel) waveform
    ▼
[6] thumbnail_make.py     ← Niş template + dinamik başlık (Pillow)
    │
    ▼
[7] telegram_review.py    ← Long video + thumbnail → Musa'ya gönder
    │   ⏸ Onay bekle (max 24 saat)
    │   ✅ Onayla → devam      ❌ Reddet → DUR + log
    │   🔄 Yeniden üret → onay iste (TOKEN harcar)
    ▼
[8] youtube_upload.py     ← Long upload + AI disclosure + UNLISTED
    │                       (sonra public yapılır)
    ▼
[9] short_extract.py      ← Audio peak analizi → en yoğun 45-50sn kesit
    │                        → 1080x1920 dikey format + overlay
    ▼
[10] telegram_review.py   ← Short → Musa'ya gönder, onay bekle
    │
    ▼
[11] youtube_upload.py    ← Short upload (#Shorts tag, 60sn altı)
    │
    ▼
[12] memory_save.py       ← genres-history.json + trend feedback güncelle
    │
    ▼
[13] cleanup.py           ← output/ temizle (BAŞARILI ise)
    │
    ▼
[14] notify.py            ← "✅ Tamamlandı: long URL + short URL"
```

---

## Telegram Bot Komutları & Keyboard Butonları

### 🎛️ Main Keyboard (Persistent Menu)

Bot'a `/start` veya herhangi bir komut gönderince şu butonlar görünür:

```
┌─────────────────────────┐
│  🟢 /on  │  🔴 /off    │
├─────────────────────────┤
│ ▶️ /run_now │ ⏹️ /cancel │
├─────────────────────────┤
│ 📊 /status │ 📱 /trends │
├─────────────────────────┤
│ 💰 /tokens │ 📺 /history│
├─────────────────────────┤
│ 🧪 /test  │ 🔍 /research│
└─────────────────────────┘
```

### 📱 Komutlar (Keyboard veya Text)

| Komut | Açıklama | Button |
|-------|----------|--------|
| `/start` | Bot'u başlat, keyboard'u göster | — |
| `/help` | Tüm komutları listele + keyboard | — |
| `/on` | Sistemi aç (cron tetikleyebilir) | 🟢 /on |
| `/off` | Sistemi kapat (devam eden run biter, yeni başlamaz) | 🔴 /off |
| `/status` | Sistem durumu, son run, sıradaki niş, kalan token | 📊 /status |
| `/run_now` | Manuel başlat (cron beklemeden) | ▶️ /run_now |
| `/cancel` | Devam eden işlemi iptal et, state temizle | ⏹️ /cancel |
| `/resume` | Hata sonrası kaldığı yerden devam et | — |
| `/history` | Son 10 yüklenen video listesi | 📺 /history |
| `/tokens` | Suno API kalan kredi (kie.ai sorgusu) | 💰 /tokens |
| `/skip` | Sıradaki nişi atla, bir sonrakine geç | — |
| `/test` | Mock mod ile dry-run (Suno çağrısı YAPMAZ) | 🧪 /test |
| `/trends` | Son trend araştırma raporunu göster | 📱 /trends |
| `/research` | Manuel trend araştırması başlat (Suno çağrısı yok, sadece YouTube API) | 🔍 /research |

### 🎯 Video Onay Butonları (Inline)

**Long Video Onayı:**
- ✅ Onayla → youtube_upload step'ine geç, upload başlar
- ❌ Reddet → run ERROR'a düşer, state sıfırlanır
- 🔄 Yeniden Üret → suno_generate step'ine geri dön (TOKEN harcar)

**Short Video Onayı:**
- ✅ Yayınla → YouTube'a Short upload, public et
- ❌ Sil → run iptal edilir, short dosyası silinir

---

## Hata Yönetimi & Token Koruma (EN KRİTİK BÖLÜM)

### Pre-flight Kontroller (Suno çağrısından ÖNCE zorunlu)

```
1. Sistem state ON mu?            → değilse SESSIZCE çık
2. Disk boş > 5 GB?                → değilse Telegram alarm + DUR
3. FFmpeg subprocess çalışıyor mu? → değilse alarm + DUR
4. YouTube token expire?           → refresh dene, başarısızsa alarm + DUR
5. Telegram bot ping?              → başarısızsa lokalde log + DUR
6. Background dosyası var mı?      → yoksa alarm + DUR
7. Önceki state ERROR mu?          → manuel müdahale gerekir, /resume bekle
8. Lockfile var mı?                → varsa zaten çalışıyor, çık
```

### Hata Davranış Matrisi

| Aşama | Hata | Davranış |
|-------|------|----------|
| Pre-flight | Herhangi | Suno'ya HİÇ dokunma. Alarm + DUR. |
| Suno çağrı 1 | Network/timeout | 3 retry (10s, 30s, 90s). Sonra DUR. |
| Suno çağrı 2 (1 başarılı) | Hata | Mevcut parça korunur. State'e yaz. DUR. /resume ile sonraki çağrı yapılır. |
| Suno generation fail | API hatası | Retry YAPMA. Token koruma. Musa'ya sor. |
| Audio process | FFmpeg hatası | Retry 1 kez. Sonra DUR. Müzik dosyaları korunur. |
| Video build | FFmpeg/disk | DUR. Müzik korunur. /resume ile devam. |
| YouTube upload | Kota | 30 dk sonra retry × 5. Olmazsa ertesi gün. |
| YouTube upload | Auth | Token refresh. Olmazsa Musa'ya OAuth bağlantısı gönder. |
| Telegram timeout | 24 saat onay yok | DUR. Cleanup YAPMA. /resume bekle. |

**Altın Kural:** Suno'dan başarıyla indirilen her parça `state.json`'a kaydedilir. /resume çağrısında o parçalar tekrar üretilmez. Para yanmaz.

### Retry Politikası

- **Network/IO**: 3 deneme, exponential backoff (10s → 30s → 90s)
- **Suno generation fail**: Retry YOK. Manuel onay iste.
- **YouTube quota**: 5 deneme, 30 dk arayla
- **YouTube auth**: 1 refresh denemesi, başarısızsa kullanıcıya
- **FFmpeg**: 1 retry, sonra DUR

---

## State Management

### `state/state.json`

```json
{
  "system_status": "ON",
  "current_run": {
    "id": "run_20260505_06",
    "step": "suno_generate",
    "step_progress": 2,
    "step_total": 3,
    "niche": "synthwave-night-drive",
    "started_at": "2026-05-05T06:00:00Z",
    "audio_files": [
      "output/audio/track1.mp3",
      "output/audio/track2.mp3"
    ],
    "video_path": null,
    "thumbnail_path": null,
    "long_uploaded": false,
    "long_video_id": null,
    "short_uploaded": false,
    "short_video_id": null,
    "errors": []
  },
  "last_successful_run": {
    "id": "run_20260504_06",
    "completed_at": "2026-05-04T08:42:11Z",
    "long_url": "https://youtube.com/watch?v=...",
    "short_url": "https://youtube.com/shorts/..."
  },
  "telegram_pending": {
    "type": "long_video_review",
    "sent_at": "2026-05-05T07:15:00Z",
    "message_id": 12345,
    "expires_at": "2026-05-06T07:15:00Z"
  }
}
```

**Kural:** Her adım başında ve sonunda state güncellenir. Adım atomik olmalı — yazma kesilirse `state.json.tmp` üzerinden recovery yapılır.

### `state/genres-history.json`

```json
{
  "synthwave-night-drive": {
    "last_used": "2026-05-04",
    "use_count": 14,
    "previous_titles": [
      "Synthwave Night Drive | 1 Hour Retro 80s Mix",
      "Neon Highway Synthwave | 1 Hour Drive Music"
    ],
    "previous_prompts_hash": [
      "a3f5e7b2c1d4...",
      "f8e2d1a9c3b5..."
    ],
    "trend_score": 7.2,
    "avg_views": 142
  }
}
```

**Niş seçim algoritması:**
1. Son 7 günde kullanılan nişler ELENDİ
2. Kalan nişlerden trend_score × ortalama_view skorlaması
3. En yüksek skorlu seçilir
4. Aynı prompt hash'i daha önce kullanıldıysa prompt minik varyasyon eklenir
5. Title'da `{year}` ve `{date_variant}` ile her gün unique başlık

### `state/token_log.json`

Her Suno çağrısı ve tahmini maliyet kaydedilir. Aylık özet `/tokens` komutunda gösterilir.

---

## Niş Stratejisi — Neon Pulse music Kanalı

Trend araştırma modülü her run öncesi YouTube'da synthwave/cyberpunk nişinde **son 7-30 gün viral** içeriği analiz eder. Aşağıdaki niş havuzu sabit değildir — trend skoruna göre rotasyon yapılır.

### Aktif Niş Havuzu

```json
[
  {
    "slug": "synthwave-night-drive",
    "title_template": "Synthwave Night Drive | {hours} Hour Retro 80s Mix | Neon Pulse",
    "suno_prompt_base": "synthwave, retrowave, 80s synth, night drive, neon, analog synth, instrumental, no vocals, mid-tempo, atmospheric",
    "duration_target_min": 60,
    "loop_multiplier": 3,
    "tags": ["synthwave", "retrowave", "80s music", "night drive", "outrun", "synthwave mix", "retro", "neon"]
  },
  {
    "slug": "cyberpunk-ambient",
    "title_template": "Cyberpunk Ambient | {hours} Hour Dark Future Soundscape | Neon Pulse",
    "suno_prompt_base": "cyberpunk ambient, dark synth, futuristic, dystopian, atmospheric, no vocals, slow tempo, cinematic, blade runner style",
    "duration_target_min": 75,
    "loop_multiplier": 4,
    "tags": ["cyberpunk music", "dark ambient", "cyberpunk 2077", "futuristic music", "sci-fi music", "ambient electronic"]
  },
  {
    "slug": "lofi-cyberpunk",
    "title_template": "Lofi Cyberpunk | {hours} Hour Chill Beats to Code/Study | Neon Pulse",
    "suno_prompt_base": "lofi cyberpunk, chill electronic beats, neon city, study music, mellow synth, no vocals, downtempo, atmospheric",
    "duration_target_min": 90,
    "loop_multiplier": 4,
    "tags": ["lofi cyberpunk", "lofi beats", "cyberpunk lofi", "chill cyberpunk", "study music", "coding music", "programming music"]
  },
  {
    "slug": "darksynth-workout",
    "title_template": "Darksynth Workout Mix | {hours} Hour Aggressive Synthwave | Neon Pulse",
    "suno_prompt_base": "darksynth, aggressive synthwave, dark electronic, heavy bass, workout music, instrumental, driving rhythm, energetic",
    "duration_target_min": 60,
    "loop_multiplier": 3,
    "tags": ["darksynth", "dark synthwave", "workout music", "gym music", "aggressive synthwave", "dark electronic"]
  },
  {
    "slug": "outrun-retrowave",
    "title_template": "Outrun Retrowave | {hours} Hour 80s Driving Music | Neon Pulse",
    "suno_prompt_base": "outrun, retrowave, 80s driving music, sunset, neon highway, energetic synth, instrumental, mid-tempo",
    "duration_target_min": 60,
    "loop_multiplier": 3,
    "tags": ["outrun", "retrowave", "80s synth", "driving music", "sunset music", "vaporwave"]
  },
  {
    "slug": "vaporwave-chill",
    "title_template": "Vaporwave Aesthetic | {hours} Hour A E S T H E T I C Mix | Neon Pulse",
    "suno_prompt_base": "vaporwave, slowed synth, dreamy, nostalgic, chillwave, atmospheric, instrumental, slow tempo",
    "duration_target_min": 60,
    "loop_multiplier": 3,
    "tags": ["vaporwave", "aesthetic music", "chillwave", "slowed", "nostalgic music", "dreamy"]
  }
]
```

**Ortak description hook (Neon Pulse imzası):**
```
Welcome to Neon Pulse — your home for synthwave, cyberpunk, and retro electronic music.
Perfect for night drives, gaming, coding, working out, or just vibing in the neon glow.

🌃 Subscribe for daily neon-fueled mixes.
```

### Trend Bazlı Niş Seçim Algoritması

`niche_select.py` aşağıdaki sıraya göre çalışır:

1. `research/trend_report_YYYYMMDD.json` oku
2. Niş havuzundaki her niş için skoru hesapla:
   - **Trend skoru** (0-10): Son 7 günde o alt-türde yüksek izlenmeli video sayısı
   - **Tekrar cezası**: Son 7 günde o niş kullanıldıysa -5
   - **Kanal performans skoru**: Bu kanalda o nişin ortalama izlenmesi
3. En yüksek toplam skorlu nişi seç
4. Trend raporundaki **viral başlık kalıplarına** göre title_template'i dinamik düzenle
5. Suno prompt'una trend rapordan çıkan **ek anahtar kelime** ekle (max 2)

### 30 Günlük Optimizasyon

- Her hafta `/history` ile son 7 video performansı kontrol
- Ortalama izlenme < 50 → en zayıf niş havuzdan çıkarılır
- > 200 → o nişin alt-varyantları üretilir (örn. synthwave-night-drive → synthwave-rainy-night)
- En iyi 3 niş %70 rotasyon, deneysel %30 rotasyon

---

## Trend Araştırma Modülü (`trend_research.py`)

**Amaç:** Suno tokeni harcanmadan ÖNCE, YouTube'da bu kanalın nişinde neyin viral olduğunu öğrenmek. Üretilecek video formatı, başlık, süre, anahtar kelime kararlarını veri ile vermek.

### Çalışma Mantığı

1. **YouTube Data API** ile sorgular:
   - `search.list` — anahtar kelimeler: "synthwave mix", "cyberpunk music", "retrowave", "darksynth", "lofi cyberpunk", "outrun"
   - Filtreler: son 30 gün, video, EN dili, music kategorisi (10)
   - `videos.list` — bulunan video ID'lerinin: viewCount, likeCount, duration, tags, title

2. **Skorlama:**
   - **Hız skoru**: viewCount / (yaş_gün) — günlük ortalama izlenme
   - **Engagement**: (likeCount / viewCount) × 1000
   - **Yeni kanal bonusu**: kanal abone < 100K ise +1.5 (büyük kanalları kopyalamak yerine ulaşılabilir hedef)
   - **Toplam viral skor**: 0-10 arası normalize

3. **Kalıp çıkarma:**
   - En iyi 20 videonun başlıklarındaki ortak anahtar kelimeler
   - Süre dağılımı (1H, 2H, 3H hangisi daha viral?)
   - Thumbnail renk paleti analizi (hex dominant renk — Pillow ile)
   - Tag frekans analizi

4. **Çıktı:** `state/research/trend_report_YYYYMMDD.json`
   ```json
   {
     "generated_at": "2026-05-05T05:30:00Z",
     "queries_used": ["synthwave mix", "cyberpunk music", ...],
     "top_videos_analyzed": 87,
     "viral_keywords": ["1 hour", "night drive", "neon", "80s", "retro"],
     "best_duration_min": 60,
     "trending_subgenres": [
       {"slug": "synthwave-night-drive", "viral_score": 8.4},
       {"slug": "cyberpunk-ambient", "viral_score": 7.1}
     ],
     "title_pattern_suggestions": [
       "{genre} | {hours} Hour | {mood_word} Mix | {year}",
       "{genre} {activity_word} | {hours} Hour | Best {year} Mix"
     ],
     "thumbnail_color_palette": ["#ff006e", "#8338ec", "#3a86ff"],
     "youtube_quota_used": 350
   }
   ```

### YouTube API Kota Yönetimi (Kritik)

- Günlük kota: 10.000 unit
- `search.list` = 100 unit/sorgu — günde max 6 anahtar kelime sorgusu
- `videos.list` = 1 unit/video — 100 video detayı = 100 unit
- **Trend araştırma günlük max: 1.500 unit** (10-15% kota)
- Upload (long + short): ~3.200 unit
- **Toplam tahmin: ~4.700 unit/gün** — kota dışı kalmaz

### Cache & Sıklık

- Trend raporu **24 saat cache** edilir
- Aynı gün 2. çağrı yapılırsa cache'den döner (kota koruma)
- Manuel `/research` komutu cache'i bypass eder (Telegram'dan onay alır önce)

---

## Background Video Stratejisi (Neon Pulse Estetiği)

Her niş için `backgrounds/{slug}/` klasöründe **3-5 farklı** seamless loop MP4. Tüm görseller marka kimliğine uygun: neon, mor-pembe-cyan paleti, retro-fütüristik, gece şehir, geometrik.

| Niş | Background Türü |
|-----|----------------|
| synthwave-night-drive | Neon highway POV, 80s araba dashboard, mor-pembe sunset, retro grid |
| cyberpunk-ambient | Yağmurlu neon şehir, holographic billboard, dystopian skyline, blade runner vibes |
| lofi-cyberpunk | Lo-fi anime cyberpunk room, neon pencere, hacker setup, chill kız hologram |
| darksynth-workout | Dark cyber tunnel, glitch effect, aggressive neon flicker, kırmızı-siyah palet |
| outrun-retrowave | 80s palmiye sunset, retro araba, neon grid yol, mor gökyüzü |
| vaporwave-chill | Eski Roma heykeli + neon, retro Windows 95, glitch aesthetic, pembe-cyan |

**Kurallar:**
- Sadece **Creative Commons** kaynak (Pexels, Pixabay video, Mixkit) veya **kendi ürettiğin** AI görsel/video
- Loop noktası seamless (FFmpeg ile pre-test edilmeli)
- Süre min 30 sn, max 2 dk (kısa loop'lar telif riskli)
- Format: MP4, H.264, 1080p, 30fps, ~15-30 MB
- Her video build'de havuzdan **farklı** background seçilir
- Marka tonu dışına ÇIKMA (akustik, doğa, klasik vb. background YOK)

---

## Short Versiyon (40-50 sn)

`short_extract.py` adımları:

1. Long videonun audio'sunu oku, RMS energy ölç (numpy)
2. Sliding window (45 sn) ile en yüksek toplam enerji bölgesini bul
3. Genelde 2.-3. parçanın ortası — algoritma onu bulur
4. O bölgeden 45 saniye kes
5. **Format dönüşümü:**
   - Çözünürlük: 1080x1920 (9:16 dikey)
   - Background: orijinal background `crop=ih*9/16:ih,scale=1080:1920`
   - Audio: aynı kesit
6. **Overlay:**
   - Üstte: `🎵 Full version on channel ⬆`
   - Niş thumbnail'ından küçük watermark (köşeye)
7. Hashtag set: `#Shorts #Synthwave #NeonPulse`
8. Title: `{long_title} — Short Version`

---

## Telegram Onay Mesajı Formatı

```
🎵 Yeni video hazır: Synthwave Night Drive | 1 Hour Retro 80s Mix
📊 Süre: 60 dk | Boyut: 280 MB | Niş: synthwave-night-drive
🎼 Suno parçaları: 6 × 3 loop
🖼️ Thumbnail aşağıda

[Video önizleme — ilk 60 sn olarak gönderilir]
[Thumbnail JPG]

✅ Onayla   ❌ Reddet   🔄 Yeniden üret
```

Onay süresi: 24 saat. Süre dolarsa state ERROR'a düşer, /resume veya /cancel beklenir.

---

## Dosya Yapısı

```
neonpulse/
├── CLAUDE.md
├── .env
├── .gitignore
├── requirements.txt
├── main_runner.py             ← Tüm akışı sıralar
├── telegram_bot.py            ← Bot listener (sürekli açık servis)
├── modules/
│   ├── __init__.py
│   ├── preflight_check.py
│   ├── state_manager.py
│   ├── trend_research.py      ← YENİ — YouTube viral analiz
│   ├── niche_select.py
│   ├── suno_generate.py
│   ├── audio_process.py
│   ├── video_build.py
│   ├── thumbnail_make.py
│   ├── telegram_review.py
│   ├── youtube_upload.py
│   ├── short_extract.py
│   ├── memory_save.py
│   ├── cleanup.py
│   └── notify.py
├── state/
│   ├── state.json
│   ├── genres-history.json
│   ├── token_log.json
│   ├── research/              ← YENİ — trend raporları cache
│   │   └── trend_report_YYYYMMDD.json
│   └── .lock                  ← Çalışırken oluşur, biterken silinir
├── genres.json
├── backgrounds/
│   ├── synthwave-night-drive/
│   ├── cyberpunk-ambient/
│   └── ...
├── thumbnails/
│   ├── templates/             ← Niş başına PNG template
│   └── output/                ← Üretilenler
├── output/                    ← Geçici (her başarılı run sonrası temizlenir)
│   ├── audio/
│   ├── video/
│   └── short/
├── tests/
│   ├── test_state.py
│   ├── test_audio.py
│   └── ...
└── logs/
    ├── system.log
    ├── error.log
    └── token_usage.log
```

---

## API & Kimlik Bilgileri (.env)

```
KIE_API_KEY=...
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...
YOUTUBE_REFRESH_TOKEN=...        # OAuth ilk akış sonrası kaydedilir
YOUTUBE_CHANNEL_ID=...            # Neon Pulse music kanal ID'si
YOUTUBE_API_KEY=...               # Trend araştırma için (search.list, videos.list)
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...              # Sadece Musa'nın chat ID'si
SYSTEM_TIMEZONE=Europe/Amsterdam
LOG_LEVEL=INFO
```

> **Not:** `YOUTUBE_API_KEY` ile `YOUTUBE_CLIENT_ID/SECRET` farklıdır. API key sadece okuma sorguları (trend araştırma) için, OAuth credentials upload için kullanılır.

`.env` asla commit edilmez. Tüm sensitive ve transient dosyalar `.gitignore`'da olmalı:

**Gerekli .gitignore entries:**
```
.env
client_secret.json
token.json
token.pickle
state/state.json
state/genres-history.json
state/token_log.json
state/.lock
state/research/
output/
logs/
__pycache__/
*.pyc
*.mp3
*.mp4
*.jpg
thumbnails/
```

Güvenlik: Asla `git status` → `git add .` kombo yapma. Her commit öncesi `git diff` kontrol et.

---

## Sık Kullanılan Komutlar

```bash
# Mock mod test (Suno çağrısı YAPMAZ, token harcamaz)
python3 main_runner.py --mock --niche synthwave-night-drive

# Manuel trend araştırma (sadece YouTube API, Suno çağrısı YOK)
python3 -m modules.trend_research --force

# Son trend raporunu göster
python3 -m modules.trend_research --show-latest

# Sadece bir adımı çalıştır
python3 -m modules.video_build --input output/audio/full.mp3
python3 -m modules.thumbnail_make --niche synthwave-night-drive --duration 60

# State sıfırla (sadece manuel müdahale sonrası)
python3 main_runner.py --reset-state

# Telegram bot başlat (production'da systemd service olarak)
python3 telegram_bot.py

# Logları izle
tail -f logs/system.log
tail -f logs/error.log

# Suno token harcaması özet
cat state/token_log.json | jq

# Cron entry (production)
0 6 * * * cd /home/musa/neonpulse && /usr/bin/python3 main_runner.py >> logs/system.log 2>&1

# Lockfile manuel temizle (sadece zombie process sonrası!)
rm state/.lock
```

---

## YAPMA (Negatif Talimatlar)

- ❌ Pre-flight kontrolleri atlayıp Suno API'sini çağırma
- ❌ Hata oluştuğunda otomatik Suno retry yapma — kullanıcıya sor
- ❌ Onay beklemeden YouTube'a public upload etme (UNLISTED → onay → public)
- ❌ AI içerik disclosure flag'ini false bırakma
- ❌ Hata durumunda `output/` klasörünü temizleme (debug için tut)
- ❌ Aynı Suno prompt hash'ini iki kez kullanma (memory kontrol)
- ❌ Telegram chat_id'yi koda gömme (.env)
- ❌ `state.json`'u manuel düzenleme (state_manager API kullan)
- ❌ Telifli görsel/ses/video kullanma (sadece CC veya kendi üretim)
- ❌ Lockfile olmadan cron'u çalıştırma (filelock zorunlu)
- ❌ OAuth token / API key'i log'a yazma (`[REDACTED]` kullan)
- ❌ Yeni kanal AÇMA — sadece "Neon Pulse music" kanalı kullanılır
- ❌ Marka kimliği dışında niş/background/thumbnail kullanma (sleep music, klasik, healing, doğa sesleri vb.)
- ❌ Trend araştırma yapmadan niş seçme — `trend_research.py` her run'da çalışmalı
- ❌ YouTube API kotasını trend araştırma ile tüketme (max 1.500 unit/gün)
- ❌ "Healing" / "432Hz" tıbbi vaat içeren açıklama yazma
- ❌ Aynı thumbnail görselini iki video için kullanma
- ❌ Long ve Short'u aynı başlıkla yükleme (Short title'a "— Short" ek)
- ❌ Trend raporunu cache olmadan tekrar tekrar çağırma (24 saat cache zorunlu)

---

## Kodlama Kuralları

- Türkçe yorum, İngilizce kod (snake_case)
- Her API çağrısı try/except ile sarılı, exception detayı `error.log`'a
- Sensitive data (token, key) asla log'a yazılmaz → `[REDACTED]`
- `print()` YOK, sadece `logging` modülü (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- Her modül stand-alone test edilebilir (`if __name__ == "__main__":`)
- Type hints zorunlu (Python 3.11+)
- Dosyaların sonunda boş satır
- Major değişiklik öncesi `python -m pytest tests/`
- State değişimi atomik: `state.json.tmp` → rename → `state.json`

---

## Bağımlılıklar

```
# requirements.txt
google-api-python-client>=2.100.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
Pillow>=10.0.0
requests>=2.31.0
python-dotenv>=1.0.0
python-telegram-bot>=20.6
ffmpeg-python>=0.2.0
numpy>=1.26.0          # audio peak detection + trend skorlama
filelock>=3.13.0       # cron lock
pydantic>=2.5.0        # state schema validation
isodate>=0.6.1         # YouTube duration parse (PT1H30M)
```

Sistem: `ffmpeg` (apt), Python 3.11+

---

## Maliyet Tahmini (Aylık)

| Kalem | Tutar |
|-------|-------|
| Suno API (kie.ai) — 30 video × 3 çağrı | ~€30-50 |
| YouTube Data API | Ücretsiz (kota içinde) |
| Telegram Bot | Ücretsiz |
| VPS (sunucu) | ~€5-10 |
| **TOPLAM** | **~€35-60/ay** |

Pilot ay maliyeti €60'ı aşmazsa devam. AdSense gelmeden önce 3-4 ay maliyet cebimizden.

---

## Kontrol Listesi (Mevcut Kanal Üzerinden)

```
[x] 1. .env dosyası oluştur ve doldur (KIE_API_KEY, YOUTUBE_*, TELEGRAM_*)
[x] 2. YOUTUBE_API_KEY ekle (trend araştırma için, OAuth'tan ayrı)
[x] 3. requirements.txt kur (venv içinde)
[x] 4. FFmpeg sunucu kurulumu (apt install ffmpeg)
[x] 5. Neon Pulse music kanalı için YouTube OAuth ilk akışı (refresh_token al)
[x] 6. Telegram bot oluştur (@BotFather), chat_id öğren
[ ] 7. 6 niş için 3-5'er background MP4 hazırla (synthwave/cyberpunk estetiği, CC)
[ ] 8. 6 niş için thumbnail PNG template (neon palet, dinamik metin alanı)
[ ] 9. genres.json güncelle (6 niş, Neon Pulse markası) — v2.1
[ ] 10. state_manager.py yaz, unit test
[ ] 11. preflight_check.py — tüm kontroller
[ ] 12. trend_research.py yaz — YouTube API entegrasyonu, kota güvenli
[ ] 13. trend_research.py test (manuel /research komutu ile)
[ ] 14. niche_select.py — trend raporu okuma + skorlama mantığı
[ ] 15. telegram_bot.py güncelleştir — komutları test et (/on /off /status /trends)
[ ] 16. suno_generate.py güncelleştir — MOCK mod ile test (token YOK)
[ ] 17. audio_process.py güncelleştir — gerçek müziklerle test (loop 3x ve 4x)
[ ] 18. video_build.py güncelleştir — 1 video üret, manuel izle
[ ] 19. thumbnail_make.py test (her niş için)
[ ] 20. telegram_review.py — onay akışı test
[ ] 21. youtube_upload.py — Neon Pulse kanalına UNLISTED test upload
[ ] 22. short_extract.py — peak detection test
[ ] 23. memory_save.py test (genres-history + trend feedback)
[ ] 24. End-to-end DRY-RUN (Suno mock, trend gerçek, YouTube unlisted)
[ ] 25. İlk gerçek run (Suno açık, YouTube unlisted, onay sonrası public)
[ ] 26. Cron + lockfile testi (zombie process simülasyonu)
[ ] 27. 7 gün gözlem, error.log + trend_report'lar kontrol
[ ] 28. Niş havuzunu performansa göre revize et
[ ] 29. Public production'a geç (günlük cron aktif)
```

---

## YouTube Politika Uyumu (Kritik!)

- ✅ Her upload'da `selfDeclaredMadeForKids: false`
- ✅ AI içerik disclosure flag aktif (`alteredOrSyntheticContent: true`)
- ✅ Description'da: "AI-generated music. Created with Suno. — Neon Pulse music"
- ✅ Repetitive content riskine karşı: her video farklı thumbnail + başlık varyasyonu + farklı süre + farklı alt-niş
- ✅ Thumbnail'da clickbait/abartı YASAK ("Click here!", "MUST WATCH" vb. yok)
- ✅ Trend araştırma: tag/title kopyalama YOK, sadece pattern ve format ilhamı
- ✅ Long videolar UNLISTED yüklenir, onay sonrası public yapılır
- ✅ Short tamamen `60sn altı`, `9:16`, `#Shorts` etiketli olmalı
- ✅ Mevcut kanal aboneliği/izlenme metriklerine zarar verecek deneysel format kullanmadan önce Telegram'dan onay al

---

---

---

## Production Deployment (v2.3)

**Status:** Ready for Linux VPS deployment (Ubuntu 22.04+)

**Pre-requisites:**
- Linux VPS with Python 3.11+, FFmpeg 5.0+
- 2GB RAM minimum, 20GB SSD
- `deploy` user account created
- SSH + Git access

**Deployment Checklist:** `PHASE8_DEPLOYMENT_CHECKLIST.md`

**Cron Schedule** (see `.crontab`):
- 06:00 UTC — Daily pipeline run
- 01:00 UTC — Log rotation
- 02:00 UTC (Sundays) — State backup
- Hourly — Health monitoring

**Systemd Service:**
```bash
sudo cp neonpulse-bot.service /etc/systemd/system/
sudo systemctl enable neonpulse-bot.service
sudo systemctl start neonpulse-bot.service
```

**Log Management:**
- Daily rotation with 30-90 day retention
- Automatic compression
- Alerts on errors, disk space, process down

**Monitoring:**
- Hourly health checks (preflight)
- Disk space alerts (>90%)
- Bot process monitoring with auto-restart
- Error log tracking

**Backup:**
- Weekly state file backups
- 90-day retention
- Optional cloud sync (S3/Google Drive)

---

## Protokoller

### Yedek Formatı

Dosya değişikliği öncesinde yedek:
```
{dosya}.backup-YYYYMMDD-HHMM
Örnek: state.json.backup-20260506-1430
```

**CLAUDE.md yedekleri:** `logs/claude-md-history/CLAUDE.backup-YYYYMMDD-HHMM.md`

---

### Güvenlik Protokolü

**API Key / Token görülerse:**
- ❌ Terminal'e echo/print/log — YAPMA
- ✅ Test çıktısında `[REDACTED]` göster
- ✅ `git diff` kontrol — commit ÖNCESI
- ❌ Credentials repo'ya hiç commit — .gitignore kontrol

**Hassas dosyalar (asla stage etme):**
- `.env` (API keys, tokens)
- `client_secret.json` (OAuth credentials)
- `token.json`, `token.pickle` (OAuth token)
- `state/state.json` (current run state)
- `state/genres-history.json` (history data)
- `state/token_log.json` (API usage tracking)
- `state/.lock` (lockfile)
- `state/research/` (cache)

---

### İletişim Protokolü

Musa **teknik geliştirici DEĞİLDİR**. Senden:

- ✅ Kısa, anlaşılır özet
- ✅ Teknik jargon = tek cümlede açıklama
- ✅ Karar gerekiyorsa 2-3 seçenek sun, sen seç
- ✅ Hata olunca panik yapma — sakin durum açıkla
- ✅ "Yapamam" dersen sebep + alternatif öner
- ✅ Token tasarrufu: Bu açılış mesajını özetleyerek tekrarlama. Sadece "Anladım, raporu hazırlıyorum" de.

---

### CLAUDE.md Güncelleme Protokolü

**Şu durumlarda güncelle:**
1. Yeni modül eklendiğinde
2. Akış değiştiğinde (pipeline steps)
3. Yeni kural/yasak çıktığında
4. Hata sonrası ders aldığında → YAPMA listesine ekle

**Güncelleme adımları:**
1. Eski sürümü `logs/claude-md-history/` klasörüne yedekle: `CLAUDE.backup-YYYYMMDD-HHMM.md`
2. Ana dosyayı güncelle
3. Versiyon Geçmişi section'da semver entry ekle: `**v2.X** (YYYY-MM-DD) — Değişiklik açıklaması`

---

## Sürüm Durumu (2026-05-06)

**v2.3 — PRODUCTION READY** ✅

- Phase 0-4: Code audit + fixes (105 issues) ✅
- Phase 5: Integration testing (all 14 steps) ✅
- Phase 6: Live testing (4/4 tests passed) ✅
- Phase 7: Production deployment checklist ✅

**Deployment Files:**
- `.crontab` — Daily schedule (06:00 UTC)
- `neonpulse-bot.service` — Systemd daemon
- `scripts/deploy_monitoring.sh` — Health checks
- `scripts/deploy_backup.sh` — Weekly backups
- `PHASE8_DEPLOYMENT_CHECKLIST.md` — Complete guide

**Status:** Sunucu kurulumu ve deployment hazırdır.

---

## Versiyon Geçmişi

- **v2.3** (2026-05-06) — Phase 6-8 Complete: Integration testing (all 14 steps) + Live testing (Trend Research, State Recovery, Telegram, Full Dry-Run) + Production Deployment (Cron, Systemd, Monitoring, Backup, Checklist). YOUTUBE_API_KEY recovered from skills/automation. All 15+ modules integrated. UTF-8 encoding fixed. Mock modes for FFmpeg-heavy steps (audio, video, shorts). Ready for production VPS deployment.
- **v2.2** (2026-05-06) — Phase 0-4 audit tamamlandı, 105 tests passing. Yeni protokoller: Güvenlik (backup format, [REDACTED], git diff), İletişim (özet-tabanlı, 2-3 seçenek), CLAUDE.md güncelleme prosedürü. .gitignore updated: state/ directory files. Phase 5 final report: memory_save, cleanup, notify, main_runner (28 fixes, v2.1 complete).
- **v2.1** (2026-05-05) — Neon Pulse music kanalı bağlamı, marka kimliği bölümü, synthwave/cyberpunk niş havuzu (sleep music nişleri kaldırıldı), `trend_research.py` modülü eklendi (YouTube viral analiz), `/trends` ve `/research` Telegram komutları, YOUTUBE_API_KEY env değişkeni, niş seçimi trend skoru bazlı algoritma
- **v2.0** (2026-05-05) — Onay akışı, state management, token koruma, Telegram bot kontrolü, Short versiyonu, niş memory
- v1.0 — İlk taslak (deprecated)
