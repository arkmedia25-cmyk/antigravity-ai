# Antigravity Proje Dokümantasyonu

**Proje:** Antigravity — AI destekli pazarlama otomasyon botu
**Hedef Pazar:** Hollanda (Nederland) — Amare Global affiliate sistemi
**Platform:** Railway (deployment) + Telegram (kullanıcı arayüzü)
**Dil:** Python 3.11
**Son güncelleme:** 2026-03-24

> **ÖNEMLİ:** Bu dosya, projeye her yeni dosya veya değişiklik eklendiğinde güncellenmeli.
> Claude ile her oturumda yeni bir şey eklendiğinde burayı güncellemesini iste.

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

---

## 1. Proje Mimarisi

```
Telegram Kullanıcısı
        ↓
skills/automation/telegram_handler.py   ← Ana giriş noktası (bot döngüsü)
        ↓
src/interfaces/telegram/handler.py      ← Yeni komut yönlendirici (Phase 3+)
        ↓
src/orchestrator.py                     ← Agent seçici
        ↓
src/agents/[cmo|content|sales|research]_agent.py  ← AI agent'lar
        ↓
src/skills/ai_client.py                 ← Claude / GPT API bağlantısı
        ↓
memory/*.json                           ← Marka, ürün, kitle hafızası
```

**Fallback zinciri:**
Yeni sistem (`src/`) hata verirse → eski sistem (`agents/` + `skills/automation/`) devreye girer.

---

## 2. Klasör Yapısı

```
Antigravity/
│
├── src/                        ← YENİ sistem (Phase 0-5)
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── logging.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── agent_utils.py
│   │   ├── cmo_agent.py
│   │   ├── content_agent.py
│   │   ├── sales_agent.py
│   │   └── research_agent.py
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── memory_manager.py
│   │   └── storage/
│   │       └── __init__.py
│   ├── skills/
│   │   ├── __init__.py
│   │   └── ai_client.py
│   └── interfaces/
│       ├── __init__.py
│       ├── telegram/
│       │   ├── __init__.py
│       │   └── handler.py
│       ├── web/
│       │   └── __init__.py
│       └── api/
│           └── __init__.py
│
├── agents/                     ← ESKİ agent dosyaları (hâlâ aktif)
│   ├── cmo-agent/
│   │   └── cmo.txt             ← CMO system prompt
│   ├── content-agent/
│   │   └── content_agent.py
│   ├── email-agent/
│   │   └── email_agent.py
│   └── linkedin-agent/
│       └── linkedin_agent.py
│
├── skills/
│   └── automation/
│       ├── telegram_handler.py ← Bot ana döngüsü (giriş noktası)
│       ├── cmo_agent.py        ← Eski CMO agent (fallback)
│       ├── ai_client.py        ← Eski AI istemci (fallback)
│       ├── test_ai.py
│       └── test_cmo.py
│
├── memory/                     ← Kalıcı marka/ürün/kitle verileri
│   ├── brand.json
│   ├── products.json
│   ├── audience.json
│   └── learned.json
│
├── tests/                      ← Otomatik testler
│   ├── conftest.py
│   ├── test_phase0_imports.py
│   ├── test_phase1_basic.py
│   ├── test_phase2_telegram_bridge.py
│   ├── test_phase5_agents.py
│   ├── test_ai.py
│   ├── test_cmo.py
│   └── unit/ integration/ fixtures/
│
├── PROJE_DOKUMAN.md            ← Bu dosya
├── requirements.txt
├── runtime.txt
├── Procfile
└── .env                        ← API anahtarları (git'e eklenmez)
```

---

## 3. Eski Sistem — agents/ ve skills/

### `skills/automation/telegram_handler.py`
**Görev:** Telegram bot ana döngüsü. Tüm sistemi başlatan dosya.
**Ne yapar:**
- Telegram API'ye bağlanır, mesajları alır
- Komutları ayrıştırır ve ilgili agent'a yönlendirir
- Yeni sistem (`src/`) yüklüyse onu kullanır, yoksa eski fonksiyonlara düşer
- `send_message()` fonksiyonu: mesajı 4096 karakter chunk'lara böler, debug log basar

**Kritik fonksiyonlar:**
```
safe_request()      → HTTP istek gönderici, 5 deneme, hata body'sini loglar
send_message()      → Telegram'a mesaj gönderir, otomatik chunk split
process_command()   → Komut yönlendirici (if/elif zinciri)
handle_command()    → Her komutu ayrı thread'de çalıştırır
main()              → Ana polling döngüsü
```

**Yönlendirme tablosu:**

| Komut | Nereye gider |
|---|---|
| `/start` | Hoşgeldin mesajı |
| `/cmo` | `_new_handler` → CmoAgent (fallback: `run_cmo`) |
| `/content` | `_new_handler` → ContentAgent (fallback: `run_content`) |
| `/sales` | `_new_handler` → SalesAgent |
| `/research` | `_new_handler` → ResearchAgent |
| `/email` | `run_email()` (eski sistem) |
| `/linkedin` | `run_linkedin()` (eski sistem) |
| `/idea` | `run_cmo()` (eski sistem) |
| `/seo` | `run_cmo()` (eski sistem) |
| `/script` | `run_cmo()` (eski sistem) |

---

### `skills/automation/cmo_agent.py`
**Görev:** Eski CMO agent — fallback olarak kullanılır.
**Ne yapar:**
- `memory/*.json` dosyalarını yükler
- `agents/cmo-agent/cmo.txt` system prompt'unu yükler
- `ask_ai()` ile Claude'a sorar
- Düz string döner (JSON parse etmez — düzeltildi)

---

### `skills/automation/ai_client.py`
**Görev:** Eski AI istemcisi — eski agent'lar bunu kullanır.
**Ne yapar:** Claude (Anthropic) veya GPT (OpenAI) API'ye bağlanır.

---

### `agents/cmo-agent/cmo.txt`
**Görev:** CMO agent'ın system prompt dosyası.
**Ne yapar:** AI'ya CMO rolünü, görevini ve davranış kurallarını tanımlar.

---

### `agents/content-agent/content_agent.py`
**Görev:** Eski içerik üretici — `/content` fallback'i.
**Ne yapar:** Instagram, Reels, email içeriği üretir. Düz string döner.

---

### `agents/email-agent/email_agent.py`
**Görev:** Email dizisi üretici.
**Ne yapar:** Hollandalı hedef kitleye yönelik email reeksleri oluşturur.

---

### `agents/linkedin-agent/linkedin_agent.py`
**Görev:** LinkedIn mesaj üretici.
**Ne yapar:** Connectie, follow-up, waardebericht gibi LinkedIn mesajları oluşturur.

---

## 4. Yeni Sistem — src/

### `src/config/settings.py`
**Görev:** Tüm konfigürasyonu tek yerden yönetir.
**Ne yapar:**
- `.env` dosyasını yükler
- `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `TELEGRAM_TOKEN` değişkenlerini okur
- `Settings` sınıfı + `validate()` metodu
- `settings` instance'ı dışa aktarılır (singleton)

---

### `src/core/logging.py`
**Görev:** Tüm sistem için merkezi log sistemi.
**Ne yapar:**
- `get_logger(name)` fonksiyonu döner
- `DEBUG` seviyesinde formatlı log basar
- Her agent kendi adıyla logger alır: `agent.cmo`, `agent.content`, vb.

---

### `src/agents/base_agent.py`
**Görev:** Tüm agent'ların base sınıfı.
**Ne yapar:**
- `ABC` (Abstract Base Class) — direkt instantiate edilemez
- `process(input_data: str) -> str` abstract metodu zorunlu kılar
- Her agent `name` ve `logger` alır

---

### `src/agents/agent_utils.py`
**Görev:** Agent'lar arasında paylaşılan yardımcı fonksiyonlar.
**Ne yapar:**
- `load_memory_context()` → `memory/*.json` dosyalarını yükler, formatlı string döner
- `_load_json()` → güvenli JSON yükleyici (hata olursa `{}` döner)
- Tüm agent'lar buradan import eder — kod tekrarı yok

---

### `src/agents/cmo_agent.py`
**Görev:** Ana strateji agent'ı — CMO rolü.
**Ne yapar:**
- `cmo.txt` system prompt'unu yükler
- `load_memory_context()` ile hafıza bağlamını ekler
- Yapılandırılmış strateji çıktısı üretir (Summary, Strategy, Recommendation, Next Steps)
- `MemoryManager`'a son görev ve yanıtı kaydeder

---

### `src/agents/content_agent.py`
**Görev:** İçerik üretimi agent'ı.
**Ne yapar:**
- Instagram post, Reels fikri, Email dizisi üretir
- Çıktı formatı: `📸 INSTAGRAM POST`, `🎬 REELS FİKRİ`, `📧 EMAIL DİZİSİ`
- Hollanda/Türk kültürüne uygun ton

---

### `src/agents/sales_agent.py`
**Görev:** Satış senaryoları agent'ı.
**Ne yapar:**
- DM scriptleri, kapanış mesajları, itiraz yönetimi üretir
- Çıktı formatı: `💬 DM SCRİPTİ`, `🤝 KAPANIS MESAJI`, `🛡️ İTİRAZ YÖNETİMİ`
- Baskısız, empatik satış tonu

---

### `src/agents/research_agent.py`
**Görev:** Pazar araştırması agent'ı.
**Ne yapar:**
- Pazar trendleri, rakip analizi, hedef kitle sorunları üretir
- Çıktı formatı: `📈 PAZAR TRENDLERİ`, `🔍 RAKİP İÇGÖRÜLERİ`, `💡 HEDEF KİTLE SORUNLARI`
- Hollanda pazarına odaklı

---

### `src/memory/memory_manager.py`
**Görev:** Agent'ların geçici belleği.
**Ne yapar:**
- `save(key, value)` / `load(key)` / `delete(key)` — dict tabanlı
- Her agent session boyunca son görev ve yanıtı saklar
- **Şu an in-memory** — bot kapanırsa veri kaybolur (Phase 6'da kalıcı olacak)

---

### `src/skills/ai_client.py`
**Görev:** Yeni sistemin AI bağlantısı.
**Ne yapar:**
- `ask_ai(prompt, provider="claude")` fonksiyonu
- `provider="claude"` → Anthropic `claude-sonnet-4-20250514`
- `provider="openai"` → OpenAI `gpt-4.1-mini`
- Hata olursa `"HATA: ..."` string döner

---

### `src/orchestrator.py`
**Görev:** Tüm agent'ları yöneten merkezi router.
**Ne yapar:**
- Başlangıçta 4 agent oluşturur: `cmo`, `content`, `sales`, `research`
- `handle_request(input_text, agent="cmo")` → doğru agent'a yönlendirir
- Bilinmeyen agent adı → hata mesajı döner
- `orchestrator.cmo` → backward-compatible property

---

### `src/interfaces/telegram/handler.py`
**Görev:** Telegram mesajlarını orchestrator'a köprüleyen katman.
**Ne yapar:**
- Gerçek Telegram API bağlantısı yok — sadece metin yönlendirme
- `_COMMAND_AGENT_MAP`: `/cmo→cmo`, `/content→content`, `/sales→sales`, `/research→research`
- `/` ile başlayan bilinmeyen komut → "Onbekend commando"
- Düz metin → CMO agent'a yönlendirilir

---

## 5. Testler — tests/

### `tests/conftest.py`
**Görev:** pytest fixtures ve ortak test yapılandırması.

### `tests/test_phase0_imports.py` — 6 test
**Görev:** Tüm `src/` modüllerinin import edildiğini doğrular.
Testler: settings, logging, get_logger, döngüsel import yok, paket yapısı.

### `tests/test_phase1_basic.py` — 9 test
**Görev:** BaseAgent, CmoAgent, MemoryManager, Orchestrator temel davranışları.
Testler: abstract class, init, process, save/load/delete, routing.

### `tests/test_phase2_telegram_bridge.py` — 9 test
**Görev:** TelegramHandler → Orchestrator köprüsü.
Testler: init, /cmo routing, boş komut, düz metin, boş input, bilinmeyen komut, chat_id bağımsızlığı, eski handler import edilmemesi.

### `tests/test_phase5_agents.py` — 21 test
**Görev:** ContentAgent, SalesAgent, ResearchAgent ve tam routing.
Testler: 3 agent init/process/memory + orchestrator 4 agent + 6 Telegram komut routing.

### `tests/test_ai.py` / `tests/test_cmo.py`
**Görev:** `skills/automation/` klasöründen kopyalanmış eski testler.

---

## 6. Hafıza Dosyaları — memory/

### `memory/brand.json`
**İçerik:** Marka bilgisi — isim, değerler, slogan, tonlama kuralları.

### `memory/products.json`
**İçerik:** Tüm Amare ürünleri — isim, faydalar, hedef kitle, key message.
**Örnek ürünler:** Happy Juice Pack, MentaBiotics, EDGE+, Sunrise, HL5 Collageen, vb.
**Affiliate link:** `https://www.amare.com/2075008/nl-NL`

### `memory/audience.json`
**İçerik:** Hedef kitle segmentleri — yaş, profil, sorunlar, motivasyon.

### `memory/learned.json`
**İçerik:** Zaman içinde öğrenilen tercihler.
Alanlar: `approved_hooks`, `rejected_styles`, `approved_ctas`

---

## 7. Yapılandırma Dosyaları

### `.env` (git'te yok)
```
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
TELEGRAM_TOKEN=...
```

### `requirements.txt`
Bağımlılıklar: `anthropic`, `openai`, `python-telegram-bot` veya `requests`, `python-dotenv`, `pytest`

### `runtime.txt`
Railway için Python versiyonu: `python-3.11`

### `Procfile`
Railway start komutu: `web: python skills/automation/telegram_handler.py`

---

## 8. Telegram Komut Tablosu

| Komut | Agent | Sistem | Çıktı |
|---|---|---|---|
| `/cmo <görev>` | CmoAgent | src/ (fallback: eski) | Strateji raporu |
| `/content <konu>` | ContentAgent | src/ (fallback: eski) | Instagram + Reels + Email |
| `/sales <senaryo>` | SalesAgent | src/ | DM + Kapanış + İtiraz |
| `/research <konu>` | ResearchAgent | src/ | Trend + Rakip + Kitle |
| `/email <görev>` | run_email | eski | Email reeksi |
| `/linkedin <görev>` | run_linkedin | eski | LinkedIn mesajı |
| `/idea` | run_cmo | eski | Video fikri |
| `/seo` | run_cmo | eski | SEO başlık + tags |
| `/script` | run_cmo | eski | Video script |
| `/start` | — | — | Komut listesi |

---

## 9. Phase Geçmişi

### Phase 0 — Temel yapı (DONE)
- `src/` paket yapısı oluşturuldu
- `src/config/settings.py` — .env yükleyici
- `src/core/logging.py` — merkezi logger
- `tests/conftest.py` + `tests/test_phase0_imports.py`

### Phase 1 — Agent altyapısı (DONE)
- `src/agents/base_agent.py` — abstract BaseAgent
- `src/memory/memory_manager.py` — dict tabanlı bellek
- `src/agents/cmo_agent.py` — ilk agent
- `src/orchestrator.py` — ilk yönlendirici
- `tests/test_phase1_basic.py` — 9 test

### Phase 2 — Telegram köprüsü (DONE)
- `src/interfaces/telegram/handler.py` — TelegramHandler
- `tests/test_phase2_telegram_bridge.py` — 9 test

### Phase 3 — Eski sistemle entegrasyon (DONE)
- `skills/automation/telegram_handler.py` güncellendi
- Yeni sistem try/except ile yüklenir, hata olursa eski sistem çalışır
- `/cmo` komutu yeni sisteme yönlendirildi

### Phase 4 — Gerçek AI bağlantısı (DONE)
- `src/skills/ai_client.py` — Anthropic + OpenAI istemci
- `src/agents/cmo_agent.py` — gerçek AI çağrısı + cmo.txt prompt

### Phase 8 — Intelligent Funnel Logic (DONE — 2026-03-24)
- `prompts/funnel/awareness.txt` — educeer, bouw vertrouwen, geen verkoop
- `prompts/funnel/interest.txt` — geef waarde, deel inzichten
- `prompts/funnel/consideration.txt` — help beslissing, zachte social proof
- `prompts/funnel/intent.txt` — duidelijke gepersonaliseerde aanbeveling + CTA
- `src/agents/agent_utils.py` — `_load_funnel_instruction(stage)` dosyadan yüklüyor; `build_funnel_context(chat_id)` stage-aware blok döndürüyor
- Tüm 6 agent — `_call_ai(task, chat_id=None)` + funnel context enjeksiyonu
- Prompt yapısı: system prompt → memory context → **funnel context** → task
- chat_id=None → funnel bloğu eklenmez (geriye dönük uyumluluk korundu)
- `tests/test_phase8_funnel_logic.py` — 15 test
- **102/102 test passing**

### Phase 7C — chat_id wiring (DONE — 2026-03-24)
- `src/agents/base_agent.py` → `process(input_data, chat_id=None)` imzası
- Tüm 6 agent → `process(input_data, chat_id=None)`, `save(key, value, chat_id=chat_id)`
- `src/orchestrator.py` → `handle_request(input_text, agent, chat_id=None)`, chat_id'yi agent'a iletiyor
- `src/interfaces/telegram/handler.py` → chat_id tüm zincirden geçiyor; `_funnel.track_interaction()` her komut sonrası çağrılıyor; chat_id=0 → None (anonim) olarak işleniyor
- Tüm önceki testler güncellendi (assert_called_with yeni imzayla uyumlu)
- `tests/test_phase7c_chat_id.py` → 10 test (agent scoping, orchestrator pass-through, funnel tracking)
- **87/87 test passing**

### Phase 7B — Memory iyileştirme (DONE — 2026-03-24)
- `src/memory/memory_manager.py` → namespace desteği (`MemoryManager(namespace="agent_name")`)
- Key format: `{namespace}:{key}` (namespace'siz) veya `u{chat_id}:{namespace}:{key}` (user-scoped)
- `save_user(chat_id, key, value)` + `load_user(chat_id, key)` + `delete_user()` eklendi
- `track_interaction(chat_id, agent, task)` → funnel aşaması + zaman damgası + etkileşim sayısı kaydeder
- `get_user_profile(chat_id)` → kullanıcı özet profili döner
- `user_keys(chat_id)` → bir kullanıcıya ait tüm raw key'leri döner
- Funnel aşamaları: awareness (0-1) → interest (2-4) → consideration (5-9) → intent (10+)
- Tüm agent'lar: `MemoryManager(namespace=self.name)` → agent'lar arası key çakışması giderildi
- `tests/test_phase7b_memory.py` → 14 test (namespace, per-user, funnel)
- **77/77 test passing** (hiçbir mevcut test kırılmadı)

### Phase 7A — Prompt dosyalarına taşıma (DONE — 2026-03-24)
- `agents/email-agent/email_prompt.txt` — email system prompt + Telegram-friendly output format
- `agents/linkedin-agent/linkedin_prompt.txt` — linkedin system prompt + output format
- `agents/content-agent/content_prompt.txt` — content system prompt + output format
- `agents/sales-agent/sales_prompt.txt` — sales system prompt + output format (yeni klasör)
- `agents/research-agent/research_prompt.txt` — research system prompt + output format (yeni klasör)
- `src/agents/agent_utils.py` — `load_agent_prompt(agent_dir, filename)` helper eklendi
- `src/agents/email_agent.py` — hardcoded prompt kaldırıldı, dosyadan yüklüyor
- `src/agents/linkedin_agent.py` — hardcoded prompt kaldırıldı, dosyadan yüklüyor
- `src/agents/content_agent.py` — hardcoded prompt kaldırıldı, dosyadan yüklüyor
- `src/agents/sales_agent.py` — hardcoded prompt kaldırıldı, dosyadan yüklüyor
- `src/agents/research_agent.py` — hardcoded prompt kaldırıldı, dosyadan yüklüyor
- **63/63 test passing** (mimari değişmedi)

### Phase 6 — Email + LinkedIn src/ migrasyonu + MemoryManager SQLite (DONE — 2026-03-24)
- `src/memory/memory_manager.py` → SQLite tabanlı, thread-safe, restart sonrası kalıcı
- `src/agents/email_agent.py` → EmailAgent (Hollandaca email reeksleri)
- `src/agents/linkedin_agent.py` → LinkedInAgent (connectie, follow-up, waardebericht)
- `src/orchestrator.py` → email + linkedin agent kayıtlı
- `src/interfaces/telegram/handler.py` → /email + /linkedin yönlendirme
- `skills/automation/telegram_handler.py` → /email + /linkedin yeni sisteme bağlandı (fallback korundu)
- `/start` mesajı güncellendi — tüm 9 komut gösteriliyor
- `tests/test_phase6_email_linkedin.py` → 18 test (MemoryManager SQLite + 2 agent + routing)
- **Toplam: 63 test, tamamı geçiyor**

### Phase 5 — Multi-agent sistemi (DONE)
- `src/agents/agent_utils.py` — paylaşılan hafıza yükleyici
- `src/agents/content_agent.py` — ContentAgent
- `src/agents/sales_agent.py` — SalesAgent
- `src/agents/research_agent.py` — ResearchAgent
- `src/orchestrator.py` güncellendi — 4 agent kayıtlı
- `src/interfaces/telegram/handler.py` güncellendi — /content, /sales, /research
- `skills/automation/telegram_handler.py` güncellendi — yeni routing
- `tests/test_phase5_agents.py` — 21 test

### Buglar ve Düzeltmeler (DONE)
- `skills/automation/telegram_handler.py` → `send_message()`: 4096 chunk split eklendi, 400 Bad Request düzeltildi
- `skills/automation/telegram_handler.py` → `safe_request()`: hata body'si loglanıyor
- `skills/automation/cmo_agent.py` → `extract_json_from_response()` silindi, düz string döndürülüyor
- `requirements.txt` → UTF-16'dan UTF-8'e dönüştürüldü
- `Procfile` → doğru start komutu yazıldı

---

## 10. Bilinen Sorunlar ve Açık Görevler

### Açık görevler (Phase 7+)
- [ ] Her agent için ayrı `.txt` system prompt dosyası eklenecek
- [ ] Canlı Telegram testi yapılacak (tüm komutlar)
- [ ] Hardcoded Windows path temizlenecek — `agents/email-agent/email_agent.py` ve `agents/content-agent/content_agent.py` (sadece eski fallback dosyaları)

### Bilinen kısıtlamalar
- `MemoryManager` şu an in-memory → bot kapanırsa öğrenilenler kaybolur
- `agents/content-agent/`, `agents/email-agent/`, `agents/linkedin-agent/` içindeki eski dosyalar hâlâ aktif (fallback)
- Hardcoded Windows path: `C:\Users\mus-1\...` — `email_agent.py` ve `content_agent.py` içinde fallback olarak mevcut

---

*Bu dosya Antigravity projesinin canlı dokümantasyonudur.*
*Her yeni dosya, değişiklik veya phase eklendiğinde bu dosya güncellenmeli.*
