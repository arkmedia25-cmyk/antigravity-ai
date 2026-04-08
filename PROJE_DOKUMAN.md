# Antigravity — Master Log & Proje Dokümantasyonu

**Proje:** Antigravity — AI destekli pazarlama otomasyon botu
**Hedef Pazar:** Hollanda (Nederland) — Amare Global affiliate sistemi
**Platform:** DigitalOcean (deployment) + Telegram (kullanıcı arayüzü)
**Dil:** Python 3.11
**Son güncelleme:** 2026-04-04 (Claude ile senkronize edildi)

> **ÖNEMLİ:** Bu "Master Log" dosyasıdır. Projeye her yeni dosya veya değişiklik
> eklendiğinde Claude'dan bu dosyayı güncellemesini iste. Yeni bir oturumda sadece
> bu dosyayı okutarak sistemi 1 saniyede kavramasını sağlayabilirsin.

---

## HIZLI DURUM PANELİ (en son durum — 2026-04-04)

> **NOT:** Hetzner VPS (116.203.74.27 / arkmediaflow.com) artık kullanılmıyor. Tüm sistem DigitalOcean üzerinde.

| Sistem | Durum | Detay |
|---|---|---|
| Telegram Bot | ✅ Çalışıyor | polling modu, DigitalOcean'da canlı |
| Canva OAuth | ✅ **Gekoppeld!** | 2026-03-29 00:22 CET bağlandı |
| Make.com Webhook | ✅ Bağlı | .env'de MAKE_WEBHOOK_URL mevcut |
| Instagram Publish (Meta API) | ⚠️ Yarım | publisher_skill.py hazır, .env credentials eksik |
| TikTok Publish | ❌ Placeholder | "under development" döndürüyor |
| Video Kalitesi (PIL+FFmpeg) | ⚠️ Çalışıyor | Düşük kalite, Remotion ile değiştirilecek |
| Remotion video-engine | ⚠️ Kurulu | HelloWorld template, brand composition yok |
| Luna (GLW-01) agent | ✅ Aktif | @GlowUpNL, energetik, mercan/şeftali |
| Zen (HLG-01) agent | ✅ Aktif | @HolistiGlow, sakin, bej/yeşil |
| Pexels B-Roll | ✅ Aktif | telegram_handler.py'de entegre |
| Hetzner VPS | 🚫 Kullanılmıyor | Unut/sil |
| SSL (arkmediaflow.com) | ✅ Aktif | https callback çalışıyor |
| Memory (SQLite) | ✅ Kalıcı | 11 kayıt, restart sonrası korunuyor |
| OpenAI (gpt-4.1-mini) | ✅ Bağlı | Ana AI motoru |
| Funnel Tracking | ✅ Aktif | chat_id 812914122 → stage: intent (19 etkileşim) |
| Test Sayısı | ✅ 105 test | Phase 9 itibarıyla tamamı geçiyor |
| PROJE_DOKUMAN.md | ✅ Güncel | 2026-03-29 tarihiyle senkronize |

---

## İçindekiler

1. [Proje Mimarisi](#1-proje-mimarisi)
2. [Klasör Yapısı](#2-klasör-yapısı)
3. [Eski Sistem — agents/ ve skills/](#3-eski-sistem--agents-ve-skills)
4. [Yeni Sistem — src/](#4-yeni-sistem--src)
5. [Testler — tests/](#5-testler--tests)
6. [Hafıza Dosyaları — memory/](#6-hafıza-dosyaları--memory)
7. [Yapılandırma Dosyaları](#7-yapılandırma-dosyaları)
8. [Telegram Komut Tablosu](#8-telegram-komut-tablosu)
9. [Phase Geçmişi](#9-phase-geçmişi)
10. [Bilinen Sorunlar ve Açık Görevler](#10-bilinen-sorunlar-ve-açık-görevler)
11. [Canva Entegrasyonu — Detaylı Teknik Notlar](#11-canva-entegrasyonu--detaylı-teknik-notlar)

---

## 1. Proje Mimarisi

```
Telegram Kullanıcısı
        ↓
skills/automation/telegram_handler.py   ← Ana giriş noktası (bot döngüsü + Flask OAuth server)
        ↓
src/interfaces/telegram/handler.py      ← Komut yönlendirici (Phase 3+)
        ↓
src/orchestrator.py                     ← 7 agent'ı yöneten router
        ↓
src/agents/[cmo|content|sales|research|email|linkedin|canva]_agent.py
        ↓
src/skills/ai_client.py                 ← OpenAI / Anthropic API bağlantısı
        ↓
src/memory/memory_manager.py            ← SQLite kalıcı bellek (Phase 6+)
```

**Flask OAuth callback:**

```
https://arkmediaflow.com/canva/callback  ← SSL üzerinden Canva OAuth tamamlanıyor
        ↓
_start_canva_callback_server()           ← arka plan thread, aynı bot process içinde
        ↓
canva_client.exchange_code()             ← PKCE doğrulama
        ↓
SQLite: u{chat_id}:canva_tokens:access_token kaydedildi
        ↓
Telegram'a "✅ Canva-account succesvol gekoppeld!" mesajı
```

**Fallback zinciri:**
Yeni sistem (`src/`) hata verirse → eski sistem (`agents/` + `skills/automation/`) devreye girer.

---

## 2. Klasör Yapısı

```
Antigravity/
│
├── src/                              ← YENİ sistem (Phase 0-9)
│   ├── __init__.py
│   ├── main.py                       ← Flask app (DigitalOcean web endpoint)
│   ├── orchestrator.py               ← 7 agent router
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py               ← .env yükleyici (CANVA değişkenleri dahil)
│   ├── core/
│   │   ├── __init__.py
│   │   └── logging.py                ← merkezi logger
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py             ← abstract BaseAgent
│   │   ├── agent_utils.py            ← paylaşılan yardımcılar (memory, prompt, funnel)
│   │   ├── cmo_agent.py
│   │   ├── content_agent.py
│   │   ├── sales_agent.py
│   │   ├── research_agent.py
│   │   ├── email_agent.py
│   │   ├── linkedin_agent.py
│   │   └── canva_agent.py            ← Phase 9 — Canva OAuth + tasarım oluşturucu
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── memory_manager.py         ← SQLite, namespace, per-user, funnel tracking
│   │   └── storage/
│   │       ├── __init__.py
│   │       └── memory.db             ← kalıcı veritabanı (git'te yok)
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── ai_client.py              ← OpenAI gpt-4.1-mini + Anthropic claude
│   │   ├── canva_client.py           ← Canva REST API (OAuth PKCE, design, export)
│   │   ├── tts_skill.py              ← Text-to-Speech (ses üretimi)
│   │   └── video_skill.py            ← Video oluşturma
│   └── interfaces/
│       ├── __init__.py
│       ├── telegram/
│       │   ├── __init__.py
│       │   └── handler.py            ← TelegramHandler (7 komut + rate limit)
│       ├── web/
│       │   └── __init__.py
│       └── api/
│           └── __init__.py
│
├── agents/                           ← ESKİ agent dosyaları (fallback olarak aktif)
│   ├── cmo-agent/
│   │   └── cmo.txt                   ← CMO system prompt
│   ├── content-agent/
│   │   ├── content_agent.py
│   │   └── content_prompt.txt
│   ├── email-agent/
│   │   ├── email_agent.py
│   │   └── email_prompt.txt
│   ├── linkedin-agent/
│   │   ├── linkedin_agent.py
│   │   └── linkedin_prompt.txt
│   ├── research-agent/
│   │   └── research_prompt.txt
│   └── sales-agent/
│       └── sales_prompt.txt
│
├── skills/
│   └── automation/
│       ├── telegram_handler.py       ← Bot ana döngüsü + Flask OAuth callback server
│       ├── .env                      ← API anahtarları (git'te yok)
│       ├── cmo_agent.py              ← Eski CMO agent (fallback)
│       ├── ai_client.py              ← Eski AI istemci (fallback)
│       ├── test_ai.py
│       └── test_cmo.py
│
├── memory/                           ← Kalıcı marka/ürün/kitle verileri (JSON)
│   ├── brand.json
│   ├── products.json
│   ├── audience.json
│   ├── learned.json
│   └── brain.md                      ← Elle yazılmış marka beyin dosyası
│
├── prompts/                          ← Funnel prompt dosyaları
│   └── funnel/
│       ├── awareness.txt             ← Farkındalık aşaması (0-1 etkileşim)
│       ├── interest.txt              ← İlgi aşaması (2-4 etkileşim)
│       ├── consideration.txt         ← Değerlendirme aşaması (5-9 etkileşim)
│       └── intent.txt                ← Satın alma niyeti (10+ etkileşim)
│
├── outputs/                          ← Video/ses çıktıları
│   ├── final_video.mp4
│   ├── audio_final.mp3
│   ├── test_video_v*.mp4 (v1-v6)
│   ├── test_audio_v*.mp3 (v1-v3)
│   ├── debug_frame*.png (frame1-3)
│   └── timestamps.json
│
├── tests/                            ← Otomatik testler (105 test, tamamı geçiyor)
│   ├── conftest.py
│   ├── test_phase0_imports.py        ← 6 test
│   ├── test_phase1_basic.py          ← 9 test
│   ├── test_phase2_telegram_bridge.py← 9 test
│   ├── test_phase5_agents.py         ← 21 test
│   ├── test_phase6_email_linkedin.py ← 18 test
│   ├── test_phase7b_memory.py        ← 14 test
│   ├── test_phase7c_chat_id.py       ← 10 test
│   ├── test_phase8_funnel_logic.py   ← 15 test
│   ├── test_phase9_live_simulation.py← 3 senaryo (live sim)
│   ├── test_ai.py
│   ├── test_cmo.py
│   └── unit/ integration/ fixtures/
│
├── PROJE_DOKUMAN.md                  ← Bu dosya (Master Log)
├── requirements.txt
├── runtime.txt                       ← python-3.11
├── requirements.txt
├── bot_test_log.txt                  ← Canlı bot test logları
├── create_final_video.py             ← Video üretim scripti
├── tts_with_timestamps.py            ← TTS + timestamp üretici
├── app.log                           ← Uygulama log dosyası
└── .env                              ← API anahtarları (git'te yok)
```

---

## 3. Eski Sistem — agents/ ve skills/

### `skills/automation/telegram_handler.py`

**Görev:** Telegram bot ana döngüsü + Flask OAuth callback sunucusu.
**Ne yapar:**

- Telegram API'ye bağlanır, mesajları polling ile alır
- Komutları ayrıştırır ve ilgili agent'a yönlendirir
- Yeni sistem (`src/`) yüklüyse onu kullanır, yoksa eski fonksiyonlara düşer
- `send_message()` fonksiyonu: mesajı 4096 karakter chunk'lara böler
- `_start_canva_callback_server()`: Flask'ı arka plan thread'de başlatır
- Canva video export çıktısını Telegram'a `video` olarak, PNG'yi `photo` olarak gönderir

**Kritik fonksiyonlar:**

```
safe_request()                → HTTP istek gönderici, 5 deneme, hata body'sini loglar
send_message()                → Telegram'a mesaj gönderir, otomatik chunk split
process_command()             → Komut yönlendirici (if/elif zinciri)
handle_command()              → Her komutu ayrı thread'de çalıştırır
_start_canva_callback_server()→ Flask OAuth callback, background thread
main()                        → Ana polling döngüsü
```

**Yönlendirme tablosu:**

| Komut | Nereye gider |
|---|---|
| `/start` | Hoşgeldin mesajı (9 komut listesi) |
| `/cmo` | `_new_handler` → CmoAgent (fallback: `run_cmo`) |
| `/content` | `_new_handler` → ContentAgent (fallback: `run_content`) |
| `/sales` | `_new_handler` → SalesAgent |
| `/research` | `_new_handler` → ResearchAgent |
| `/email` | `_new_handler` → EmailAgent (fallback: `run_email`) |
| `/linkedin` | `_new_handler` → LinkedInAgent (fallback: `run_linkedin`) |
| `/canva` | `_new_handler` → CanvaAgent |
| `/idea` | `run_cmo()` (eski sistem) |
| `/seo` | `run_cmo()` (eski sistem) |
| `/script` | `run_cmo()` (eski sistem) |

---

## 4. Yeni Sistem — src/

### `src/config/settings.py`

**Görev:** Tüm konfigürasyonu tek yerden yönetir.
**Ne yapar:**

- `.env` dosyasını yükler
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `TELEGRAM_TOKEN` okur
- `CANVA_CLIENT_ID`, `CANVA_CLIENT_SECRET`, `CANVA_REDIRECT_URI` okur
- `MEMORY_DB_PATH` okur
- `Settings.validate()` → `TELEGRAM_TOKEN` + `OPENAI_API_KEY` zorunlu

---

### `src/agents/canva_agent.py`

**Görev:** Canva tasarım oluşturma ve export agent'ı. (Phase 9 — YENİ)
**Ne yapar:**

- `process()` alt-komutları ayrıştırır: `auth`, `export`, veya tasarım tipi
- `_auth(chat_id)` → PKCE code_verifier üretir, SQLite'a kaydeder, OAuth URL döner
- `_create_design(type, title, chat_id)` → Canva API ile yeni tasarım oluşturur, edit_url döner
- `_export(design_id, chat_id)` → async export başlatır, URL döner
- `_get_token(chat_id)` → SQLite'dan access_token yükler

**Desteklenen tasarım tipleri:**
`instagram`, `story`, `reels`, `tiktok`, `youtube`, `facebook`, `linkedin`, `presentatie`, `flyer`, `poster`

---

### `src/skills/canva_client.py`

**Görev:** Canva REST API istemcisi. (Phase 9 — YENİ)
**Ne yapar:**

- `get_auth_url(state)` → OAuth URL + PKCE code_verifier üretir
- `exchange_code(code, verifier)` → auth code'u access+refresh token'a çevirir
- `refresh_access_token(refresh_token)` → token yenileme
- `create_design(token, type, title)` → POST /designs
- `start_export(token, design_id, fmt)` → POST /exports (async)
- `wait_for_export(token, export_id)` → polling ile download URL bekler (90s timeout)

**Sabitler:**

```python
DESIGN_TYPES = {instagram: (1080,1080), story/reels/tiktok: (1080,1920),
                youtube: (1920,1080), facebook: (1200,630), linkedin: (1200,627),
                presentatie: (1920,1080), flyer/poster: (794,1123)}
EXPORT_FORMAT = {video/tiktok/reels/youtube: "MP4", default: "PNG"}
```

---

### `src/orchestrator.py`

**Görev:** Tüm 7 agent'ı yöneten merkezi router.
**Kayıtlı agent'lar:** `cmo`, `content`, `sales`, `research`, `email`, `linkedin`, `canva`

---

### `src/interfaces/telegram/handler.py`

**Görev:** Telegram mesajlarını orchestrator'a köprüleyen katman.
**Ne yapar:**

- Rate limiting: 30 saniyede max 5 istek (chat_id başına)
- `_COMMAND_AGENT_MAP`: `/canva→canva` dahil 7 komut
- Her komut için `_USAGE_HINTS` (argüman girilmezse gösterilir)
- Funnel tracking: her başarılı komut sonrası `track_interaction()` çağrılır

---

### `src/memory/memory_manager.py`

**Görev:** Agent'ların kalıcı SQLite belleği.
**Ne yapar:**

- `save(key, value, chat_id=None)` / `load(key, chat_id=None)` / `delete(key)`
- Namespace: `MemoryManager(namespace="canva_tokens")` → key format: `namespace:key`
- User-scoped: `save(key, value, chat_id=123)` → `u123:namespace:key`
- `track_interaction(chat_id, agent, task)` → funnel aşaması + zaman + sayaç
- `get_user_profile(chat_id)` → kullanıcı özet profili
- Funnel aşamaları: awareness(0-1) → interest(2-4) → consideration(5-9) → intent(10+)
- SQLite tablosu: `memory(key TEXT PRIMARY KEY, value TEXT)`

**Şu anki veritabanı içeriği (2026-03-29 itibarıyla):**

```
u812914122:funnel:funnel:first_seen       → "2026-03-28T20:24:16"
u812914122:funnel:funnel:last_active      → "2026-03-28T23:22:53" (= 00:22 CET)
u812914122:funnel:funnel:last_agent       → "canva"
u812914122:funnel:funnel:interaction_count→ 19
u812914122:funnel:funnel:stage            → "intent"
u812914122:cmo:last_task                  → "Dank je wel 😊"
u812914122:cmo:last_response              → "Graag gedaan! ..."
u812914122:canva_tokens:access_token      → JWT (aktif)
u812914122:canva_tokens:refresh_token     → JWT (aktif)
canva_tokens:pkce_812914122_*             → PKCE verifier (kullanıldı, temizlenmeli)
```

---

### `src/skills/ai_client.py`

**Görev:** Yeni sistemin AI bağlantısı.
**Ne yapar:**

- `ask_ai(prompt, provider="openai")` → varsayılan OpenAI `gpt-4.1-mini`
- `provider="claude"` → Anthropic `claude-sonnet-4-20250514`
- GPT-4o-mini conversation memory: son 10 mesaj context olarak ekleniyor

---

### `src/main.py`

**Görev:** DigitalOcean web endpoint (Flask).
**Ne yapar:**

- `GET /` → "OK"
- `GET /canva/callback` → Canva OAuth code alır (basit echo — gerçek işlem telegram_handler'da)
- `GET /cmo?q=...` → OpenAI gpt-4o-mini ile direkt CMO yanıtı

---

## 5. Testler — tests/

| Dosya | Test Sayısı | Kapsam |
|---|---|---|
| test_phase0_imports.py | 6 | src/ modül importları |
| test_phase1_basic.py | 9 | BaseAgent, CmoAgent, MemoryManager, Orchestrator |
| test_phase2_telegram_bridge.py | 9 | TelegramHandler → Orchestrator köprüsü |
| test_phase5_agents.py | 21 | Content/Sales/Research agent + routing |
| test_phase6_email_linkedin.py | 18 | Email/LinkedIn + SQLite MemoryManager |
| test_phase7b_memory.py | 14 | Namespace, per-user, funnel tracking |
| test_phase7c_chat_id.py | 10 | chat_id zinciri (agent→orchestrator→handler) |
| test_phase8_funnel_logic.py | 15 | Funnel stage + prompt injection |
| test_phase9_live_simulation.py | 3 | Canlı uçtan uca senaryo simülasyonu |
| **TOPLAM** | **105** | **tamamı geçiyor** |

---

## 6. Hafıza Dosyaları — memory/

### `memory/brand.json`

Marka bilgisi — isim, değerler, slogan, tonlama kuralları.

### `memory/products.json`

Tüm Amare ürünleri — isim, faydalar, hedef kitle, key message.
Ürünler: Happy Juice Pack, MentaBiotics, EDGE+, Sunrise, HL5 Collageen, vb.
Affiliate link: `https://www.amare.com/2075008/nl-NL`

### `memory/audience.json`

Hedef kitle segmentleri — yaş, profil, sorunlar, motivasyon.

### `memory/learned.json`

Zaman içinde öğrenilen tercihler: `approved_hooks`, `rejected_styles`, `approved_ctas`

### `memory/brain.md`

Elle yazılmış marka beyin dosyası — yüksek seviye strateji notları.

---

## 7. Yapılandırma Dosyaları

### `.env` (git'te yok — hem proje kökünde hem skills/automation/ içinde)

```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...        (opsiyonel)
TELEGRAM_TOKEN=...
CANVA_CLIENT_ID=OC-AZ0ma8LaN_5C
CANVA_CLIENT_SECRET=...
CANVA_REDIRECT_URI=https://arkmediaflow.com/canva/callback
```

### `requirements.txt`

Bağımlılıklar: `anthropic`, `openai`, `requests`, `python-dotenv`, `pytest`, `flask`

### `runtime.txt`

DigitalOcean/Dokku için Python versiyonu: `python-3.11`

### `Procfile` / `railway.toml` (Kaldırıldı)

Artık sadece DigitalOcean Droplet üzerinde manuel kontrol sağlanıyor.

---

## 8. Telegram Komut Tablosu

| Komut | Agent | Sistem | Çıktı |
|---|---|---|---|
| `/cmo <görev>` | CmoAgent | src/ (fallback: eski) | Strateji raporu |
| `/content <konu>` | ContentAgent | src/ (fallback: eski) | Instagram + Reels + Email |
| `/sales <senaryo>` | SalesAgent | src/ | DM + Kapanış + İtiraz |
| `/research <konu>` | ResearchAgent | src/ | Trend + Rakip + Kitle |
| `/email <görev>` | EmailAgent | src/ (fallback: eski) | Email reeksi |
| `/linkedin <görev>` | LinkedInAgent | src/ (fallback: eski) | LinkedIn mesajı |
| `/canva auth` | CanvaAgent | src/ | OAuth URL → Canva koppeling |
| `/canva instagram <başlık>` | CanvaAgent | src/ | Edit URL + export hint |
| `/canva reels <başlık>` | CanvaAgent | src/ | Edit URL + export hint |
| `/canva export <design_id>` | CanvaAgent | src/ | MP4/PNG download URL |
| `/start` | — | — | 7 komut listesi |
| `/idea` | run_cmo | eski | Video fikri |
| `/seo` | run_cmo | eski | SEO başlık + tags |
| `/script` | run_cmo | eski | Video script |

---

## 9. Phase Geçmişi

### Phase 9 — Canva Entegrasyonu + Sistem Sabitleme (DONE — 2026-03-28/29)

**Bu proje için en büyük entegrasyon.**

- `src/agents/canva_agent.py` — CanvaAgent: auth, create_design, export
- `src/skills/canva_client.py` — Canva REST API (OAuth 2.0 PKCE, design, export)
- `src/orchestrator.py` → canva agent kayıtlı (7. agent)
- `src/interfaces/telegram/handler.py` → /canva routing + detaylı USAGE_HINTS
- `skills/automation/telegram_handler.py`:
  - `_start_canva_callback_server()` → Flask OAuth callback, background thread
  - Canva video export → Telegram'a `sendVideo` ile iletiliyor
  - PNG export → `sendPhoto` ile iletiliyor
- `src/config/settings.py` → CANVA_CLIENT_ID, CANVA_CLIENT_SECRET, CANVA_REDIRECT_URI eklendi
- Import path fix: `src.orchestrator`, `src.memory`, `src.core` prefix'leri düzeltildi
- CanvaAgent `.memory` attribute eksikliği düzeltildi
- `.gitignore` → `*.db`, `*.db-shm`, `*.db-wal` eklendi
- `.claude/skills/` → python-testing, python-patterns, security-review, deployment-patterns
- **Phase 9 live simulation: 3/3 senaryo geçti (54 saniye, OpenAI gpt-4.1-mini)**
- **105 unit test: tamamı geçiyor**
- **SSL:** `arkmediaflow.com` üzerinde HTTPS aktif, Canva OAuth callback çalışıyor
- **CANVA GEKKOPPELd:** 2026-03-29 00:22 CET — chat_id 812914122 başarıyla bağlandı
  - access_token: SQLite'a kaydedildi ✅
  - refresh_token: SQLite'a kaydedildi ✅

### Phase 8 — Intelligent Funnel Logic (DONE — 2026-03-24)

- `prompts/funnel/awareness.txt` — educeer, bouw vertrouwen, geen verkoop
- `prompts/funnel/interest.txt` — geef waarde, deel inzichten
- `prompts/funnel/consideration.txt` — help beslissing, zachte social proof
- `prompts/funnel/intent.txt` — duidelijke gepersonaliseerde aanbeveling + CTA
- `src/agents/agent_utils.py` — `_load_funnel_instruction(stage)` + `build_funnel_context(chat_id)`
- Tüm 6 agent — `_call_ai(task, chat_id=None)` + funnel context enjeksiyonu
- **102/102 test passing**

### Phase 7C — chat_id wiring (DONE — 2026-03-24)

- `process(input_data, chat_id=None)` imzası tüm agent'lara yayıldı
- Orchestrator → agent'a chat_id iletiliyor
- TelegramHandler → funnel.track_interaction() her komut sonrası
- **87/87 test passing**

### Phase 7B — Memory iyileştirme (DONE — 2026-03-24)

- Namespace desteği (`MemoryManager(namespace="agent_name")`)
- `save_user(chat_id, key, value)` + `load_user` + `delete_user`
- `track_interaction(chat_id, agent, task)` → funnel aşaması + zaman damgası
- Funnel aşamaları: awareness → interest → consideration → intent
- **77/77 test passing**

### Phase 7A — Prompt dosyalarına taşıma (DONE — 2026-03-24)

- Tüm agent system prompt'ları hardcoded'dan `.txt` dosyalarına taşındı
- `agents/email-agent/email_prompt.txt`, `linkedin_prompt.txt`, `content_prompt.txt`,
  `sales_prompt.txt`, `research_prompt.txt`
- `src/agents/agent_utils.py` — `load_agent_prompt()` helper
- **63/63 test passing**

### Phase 6 — Email + LinkedIn + SQLite Memory (DONE — 2026-03-24)

- `src/memory/memory_manager.py` → SQLite tabanlı, thread-safe, restart sonrası kalıcı
- `src/agents/email_agent.py` — EmailAgent
- `src/agents/linkedin_agent.py` — LinkedInAgent
- `/start` → 9 komut gösteriliyor
- **63 test passing**

### Phase 5 — Multi-agent sistemi (DONE)

- ContentAgent, SalesAgent, ResearchAgent eklendi
- Orchestrator 4 → 6 agent
- **21 yeni test**

### Phase 0-4 — Temel altyapı (DONE)

- Phase 0: `src/` paket yapısı, settings, logging
- Phase 1: BaseAgent, MemoryManager, CmoAgent, Orchestrator
- Phase 2: TelegramHandler bridge
- Phase 3: Eski sistemle entegrasyon (try/except fallback)
- Phase 4: Gerçek AI bağlantısı (Anthropic + OpenAI)

---

## 10. Bilinen Sorunlar ve Açık Görevler

### 🔴 Phase 10A — Make.com Publish Fix (ÖNCELİKLİ)

**Sorun:** `publish_ig_` ve `publish_tt_` butonları Make.com yerine Meta Graph API'yi çağırıyor.
**Çözüm:** `skills/automation/telegram_handler.py` → `_do_publish()` fonksiyonu güncellenecek.

Adımlar:

- [ ] Video → catbox.moe'a yükle (UploaderSkill — zaten var)
- [ ] Public URL + brand + platform → Make.com webhook'a gönder
- [ ] Make.com senaryosu: webhook → Instagram Reels post
- [ ] TikTok için ayrı Make.com senaryosu

**Mevcut durum:**

```python
# telegram_handler.py _do_publish() — BOZUK
res = publisher_skill.publish_to_instagram(public_url, ...)   # Meta API direkt → çalışmıyor
res = publisher_skill.publish_to_tiktok(public_url, ...)      # Placeholder → hata döndürüyor
```

**Hedef:**

```python
# Make.com webhook üzerinden
requests.post(MAKE_WEBHOOK_URL, json={"video_url": public_url, "brand": brand, "platform": "instagram"})
```

### 🟡 Phase 10B — Remotion Video Kalitesi (SIRADAKI)

**Sorun:** PIL + FFmpeg video animasyonsuz, amatör görünüm.
**Çözüm:** `video-engine/` Remotion ile brand-aware composition.

Adımlar:

- [ ] `video-engine/src/GlowUp.tsx` — Luna / @GlowUpNL composition (mercan/şeftali)
- [ ] `video-engine/src/Holisti.tsx` — Zen / @HolistiGlow composition (bej/yeşil)
- [ ] Props: hook, probleem, oplossing, bewijs, cta, voiceover, bgVideoUrl (Pexels)
- [ ] Python bridge: `subprocess` → `npx remotion render` → MP4
- [ ] `skills/automation/telegram_handler.py` → `create_reel()` yerine Remotion render

### Eski Açık Görevler (düşük öncelik)

- [ ] Canva token yenileme (refresh_token akışı)
- [ ] PKCE verifier temizliği
- [ ] Hardcoded Windows path temizliği (agents/ klasörü)
- [ ] src/skills/ai_client.py — uncommitted değişiklikler

### Bilinen kısıtlamalar

- Make.com webhook URL mevcut ama sadece `src/interfaces/telegram/handler.py`'de kullanılıyor
- `skills/automation/telegram_handler.py` hâlâ ana bot dosyası (polling modu)
- Remotion render Windows'ta lokal çalışıyor, DigitalOcean'a taşımak gerekebilir

---

## 11. Canva Entegrasyonu — Detaylı Teknik Notlar

### OAuth 2.0 PKCE Akışı

```
1. /canva auth → CanvaAgent._auth(chat_id)
2. code_verifier = secrets.token_urlsafe(64)
3. code_challenge = base64(sha256(verifier))
4. SQLite'a kaydet: canva_tokens:pkce_{chat_id}_{nonce} = verifier
5. Kullanıcıya auth_url gönder
6. Kullanıcı tarayıcıda onaylar
7. Canva → https://arkmediaflow.com/canva/callback?code=...&state=chat_id_nonce
8. Flask callback: verifier'ı SQLite'tan yükle
9. canva_client.exchange_code(code, verifier) → access + refresh token
10. SQLite'a kaydet: u{chat_id}:canva_tokens:access_token = JWT
11. Telegram'a: "✅ Canva-account succesvol gekoppeld!"
```

### .env Canva değişkenleri

```
CANVA_CLIENT_ID=OC-AZ0ma8LaN_5C
CANVA_REDIRECT_URI=https://arkmediaflow.com/canva/callback
```

(CLIENT_SECRET git'e girmez)

### Canva API Endpoint'leri

```
Auth URL:  https://www.canva.com/api/oauth/authorize
Token URL: https://api.canva.com/rest/v1/oauth/token
API Base:  https://api.canva.com/rest/v1
Scopes:    design:content:read design:content:write design:meta:read
```

### SSL Durumu

- Domain: `arkmediaflow.com`
- SSL sertifikası DigitalOcean/Cloudflare üzerinden aktif
- Kanıt: CANVA_REDIRECT_URI `https://` protokolü ile çalışıyor
- Bağlantı tarihi: 2026-03-29 00:22 CET

---

*Bu dosya Antigravity projesinin Master Log'udur.*
*Her yeni phase, bağlantı veya kritik değişiklikte Claude'dan güncellenmesini iste.*
*Son senkronizasyon: 2026-03-29 — Claude Sonnet 4.6*
