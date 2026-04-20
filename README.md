# Antigravity AI - Proje Durum ve Takip Dosyası

> **ÖNEMLİ ÇALIŞMA KURALI:** Geliştirme sürecinde, yapay zeka ajanları (Antigravity/Claude vs.) her yeni oturuma veya göreve başladıklarında ilk olarak bu **README.md** dosyasını okuyacaklar. Her görevin veya günün sonunda, yapılan işlemler, çözülen hatalar ve tam olarak "nerede kalındığı" bu dosyaya kaydedilecektir. Böylece herkes her an güncel durumun farkında olacaktır.

---

## 🔧 Video Pipeline Kritik Düzeltmeleri — [20 Nisan 2026]

### Tespit Edilen ve Çözülen Bug'lar

**Bug 1 — Brand hiç iletilmiyordu (`src/orchestrator.py`)**
- `_extract_brand()` ile marka çıkarılıyordu ama agent'lara `brand` parametresi **hiç gönderilmiyordu**
- `/zen` komutu bile olsa tüm ajanlar default `"glowup"` ile çalışıyordu
- **Düzeltme:** `selected_agent.process(input, chat_id=chat_id, brand=brand_name)` — brand chain boyunca iletiliyor ✅

**Bug 2 — Video üretimi hiç tetiklenmiyordu (`src/agents/content_agent.py`)**
- ContentAgent delegasyonu için `has_video_kw AND has_reels_marker` gerekiyordu
- `/zen magnesium` → prompt `"@holistiglow magnesium"` — içinde video keyword yok → video hiç üretilmiyordu
- **Düzeltme:** Prompt'a `"maak een reel over:"` eklendi (handler + scheduler) ✅

**Bug 3 — MCP bridge her AI çağrısında 60s timeout yapıyordu (`src/skills/mcp_client.py`)**
- Her `ask_ai()` çağrısı 3 ayrı MCP subprocess spawn ediyordu (route_model + check_safety + get_tools)
- Bir video = 5-6 `ask_ai` çağrısı × 3 MCP çağrısı = 18 subprocess → **pipeline kilitleniyor**
- **Düzeltme:** MCP timeout 60s → 8s, ContentAgent ve VideoProducer'da `use_mcp=False` ✅

**Bug 4 — Telegram Markdown parse hatası (tüm mesajlar)**
- `task_id` formatı `1776689681_5f61` — içindeki `_` Markdown italik başlatıcı olarak yorumlanıyordu
- Tüm dinamik mesajlarda `parse_mode="Markdown"` kaldırıldı ✅

**Bug 5 — `complete_task` methodu yoktu (`src/core/task_queue.py`)**
- Handler `task_queue.complete_task()` çağırıyordu, doğrusu `update_status("completed")`
- **Düzeltme:** `task_queue.update_status(task_id, "completed")` ✅

**Bug 6 — `mcp` modülü sunucuda kurulu değildi**
- `from mcp import ...` import hatası tüm AI çağrılarını çökertiyordu
- **Düzeltme:** `try/except ImportError` ile opsiyonel import, `mcp_bridge = None` fallback ✅

**Bug 7 — Brand VideoProducer data dict'ine eklenmemişti**
- `_send_video_message` de `data.get("brand", "glowup")` yazıyordu ama VideoProducer brand döndürmüyordu
- **Düzeltme:** `data={"brand": brand, ...}` eklendi ✅

**Bug 8 — Icons path Windows'a hardcoded (`src/skills/video_skill.py`)**
- `C:\Users\mus-1\.gemini\...` — Linux sunucuda çalışmıyordu
- **Düzeltme:** `os.path.join(_get_project_root(), "assets", "icons", ...)` ✅

### Yeni Özellikler

- **Video altında Title / Description / Tags** — VideoProducer'ın ürettiği metadata Telegram caption'ına eklendi ✅
- **Uzun içerik metni kaldırıldı** — Instagram post + email listesi artık video ile birlikte gönderilmiyor ✅
- **Video kalitesi artırıldı** — Pexels overlay alpha 65→35, `preset fast`, `crf 20` ✅
- **`ecosystem.config.js` düzeltildi** — `interpreter: "python3"` → `interpreter: "none"`, venv Python tam yolu ✅

### Sunucu Altyapısı

- **2GB Swap eklendi** — 961MB RAM'li VPS'te FFmpeg OOM kill sorununu çözdü ✅
- **Swap kalıcı** — `/etc/fstab`'a eklendi, reboot'ta kaybolmayacak ✅

---

En son **16 Nisan 2026** itibariyle aşağıdaki kritik "Gelecek Nesil" özellikler eklendi ve sistem tam otonom **"Agency Swarm OS"** mimarisine taşındı:

### 🎬 Video Üretim Hattı Robustluğu - [16 Nisan]
- **Permissive Delegation** → `ContentAgent` artık çok daha geniş anahtar kelime (video, üret, maak vb.) ve marker setini tanıyor. AI formatı şaşırsa bile video tetikleniyor. ✅
- **Extraction İyileştirmesi** → `VideoProducerAgent` seslendirme metni çıkarma mantığı esnetildi ve detaylı loglamaya geçildi. ✅
- **Zamanlanmış Bot Düzeltmesi** → Gece/Sabah botunun video üretmeyi atlamasına neden olan katı kurallar esnetildi. ✅

### 📝 Blog Otomasyon Onarımı (amarereview.nl) - [16 Nisan]
- **OpenAI Fallback** → Anthropic kredisi bittiğinde bot artık durmuyor, otomatik olarak OpenAI (GPT-4o) üzerinden makale yazmaya devam ediyor. ✅
- **Cron Kayması Giderildi** → Sunucudaki hatalı `/opt/n8n/` yolları ve yanlış dosya eşleşmeleri `/root/antigravity-ai/` altına çekilerek düzeltildi. ✅
- **Manuel Doğrulama** → Amare Restore makalesi başarıyla yayınlandı ve doğrulandı. ✅

---

En son **14 Nisan 2026** itibariye:

### 🧠 Autonomous Brain (Cognitive Layer) - [YENİ]
- **Think-Act-Observe Loop** → `SwarmOrchestrator` artık hedefleri küçük görevlere böler, sonuçları gözlemler ve kendi stratejisini dinamik olarak değiştirir. ✅
- **Instinct Service** → Ajanların "atomik içgüdüleri" (learned behaviors) kalıcı hale getirildi. Hatalardan ders çıkaran bir geri bildirim döngüsü kuruldu. ✅
- **Self-Healing** → API kredisi bitmesi veya kilitlenme gibi durumlarda otonom fallback (yedekleme) mekanizmaları devreye alındı. ✅

### 🛠️ ECC Skill Integration (20+ Skills)
- **Everything Claude Code (ECC)** → 20 farklı uzmanlık paketi (Cost-Aware Pipeline, Blueprint, Agent-Harness, AI-Regression-Testing vb.) sisteme tam entegre edildi. ✅
- **Standardized Harness** → Tüm ajanlar artık profesyonel `AgentResponse` kontratıyla (Status/Summary/Next Actions) konuşuyor. ✅

### 🎬 Pro Video Engine (VideoDB & HeyGen)
- **VideoDB Integration** → Bulut tabanlı profesyonel video düzenleme. Dikey format (9:16) reframe, otomatik altyazı yakma ve akıllı kurgu. ✅
- **HeyGen Resiliency** → HeyGen kredi hatalarına karşı otonom "Static/Dynamic Hybrid" kurgu fallback'i geliştirildi. ✅
- **Parallel Render** → FFmpeg deadlock'ları giderildi, kurgu süreci %60 hızlandırıldı. ✅

### 🎙️ Voice AI & Müşteri Destek Pipeline
- **Pipeline Kurulumu** → Whisper (Yazıya dökme) + Claude (Akıllı Analiz) + ElevenLabs (Premium Ses) hattı kuruldu. ✅
- **Hata Toleransı** → Anthropic kredisi bittiğinde otomatik olarak OpenAI'a (GPT-4o) geçiş yapan "Resilient Fallback" eklendi. ✅
- **Dil Tespiti** → Kullanıcının konuştuğu dili otomatik tespit edip aynı dilde, vurgulu ve doğal cevap verme özelliği eklendi.

### 🎬 Video Yükleme ve Altyazı Fix
- **Catbox Kaldırıldı** → Catbox.moe'nun kapanması nedeniyle yükleme hattı yerel sunucuya (`arkmediaflow.com/outputs/`) ve yedek olarak `bashupload.com`'a taşındı. ✅
- **URL Path Senkronizasyonu** → `/media/` yerine `/outputs/` yolu tüm sistemde (Telegram & Make.com) standartlaştırıldı. ✅

### 🖥️ Agency OS Dashboard (Arayüz)
- **Dashboard Prototipi** → Görseldeki premium tasarıma uygun, koyu tema ve turuncu vurgulu HTML/CSS/JS dashboard hazırlandı. ✅
- **Dashboard API** → Arayüzü orkestratöre bağlayan **FastAPI (src/server.py)** sunucusu kuruldu. ✅
- **Docker Ready** → Tüm sistemi DigitalOcean'a tek komutla taşımak için Dockerfile hazırlandı. ✅

### 🧹 Büyük Reorganizasyon ve Bot Onarımı
- **Klasör Düzenlemesi** → Tüm scriptler `/scripts/automation/` ve `/scripts/wordpress/` altına taşındı.
- **Telegram Bot Fix** → `@my_ai_ark_agent_bot` üzerindeki `memory` ve `encoding` hataları giderildi. ✅
- **Dr. Priya VO Fix** → Seslendirme öncesi "Sanitizer" eklendi (Başlıklar ve emojiler artık okunmuyor). ✅
- **Bağımlılıklar** → `Pillow` (PIL) ve `python-telegram-bot` güncellendi.

### 🎬 Video Pipeline Düzeltmeleri
- **zoompan kaldırıldı** → `scale+crop` ile değiştirildi (`src/skills/video_skill.py`) — VPS'te sessiz hang yapıyordu
- **Altyazı word-wrap** eklendi — max 26 karakter/satır, fontsize 42, max 3 satır (taşma giderildi)
- **Hook arka planı** koyu gri yapıldı `(50, 50, 50, 180)` — eskiden siyahtı
- **Pexels sorgusu düzeltildi** — "aesthetic human wellness" prefix kaldırıldı, konu ile eşleşiyor artık
- **FFmpeg timeout** 300s eklendi, çıktı dosyası varlık kontrolü eklendi

### 📲 Telegram & Make.com
- **Download butonu** artık URL butonu → `arkmediaflow.com/media/<dosya>` (Telegram 50MB limiti aşıldı)
- **Make.com webhook** video render sonrası otomatik tetikleniyor (manuel buton yerine)
- `static/` klasörüne kopyalama + URL oluşturma otomatik

### 🧹 Hetzner Temizliği
- Hetzner server (134.209.80.233) iptal edildi — tüm referanslar silindi
- `AI Otomasyonu/Claude_Ajanlar/.claude/settings.local.json` temizlendi
- `fix_canva.py` silindi
- `PROJE_DOKUMAN.md` güncellendi

### 📝 AmareReview.nl Blog Otomasyonu
| Script | Konum | Ne Yapar |
|---|---|---|
| `article_writer.py` | `scripts/` + `/opt/n8n/` | Claude ile makale yazar, WordPress'e yayınlar |
| `daily_article_writer.py` | `scripts/` + `/opt/n8n/` | Günlük 1 makale yazar (cron: 09:00 UTC) |
| `seo_updater.py` | `scripts/` | Yoast SEO, kategori, slug/tarih 2025→2026 günceller |
| `add_schema_markup.py` | `scripts/` | JSON-LD Review schema ekler (Google yıldız puanı) |
| `clean_markdown_posts.py` | `scripts/` | ` ```html ` fence'larını temizler |
| `google_index_notify.py` | `scripts/` | Sitemap ping + Google Indexing API |
| `update_titles_2026.py` | `scripts/` | Toplu başlık + tarih 2025→2026 güncellemesi |

**Çalıştırılan sonuçlar:**
- 37 post Yoast SEO + kategori + slug güncellendi
- 35 makaleye JSON-LD Review schema eklendi (Google'da yıldız görünümü)
- Tüm 2025 başlıkları/tarihleri 2026'ya çevrildi

### 🧪 PDF Factsheet Verileri (PRODUCT_FACTS)
`article_writer.py` içindeki `PRODUCT_FACTS` dict'e aşağıdaki 6 ürün eklendi:
- **Restore** — 5 bakteri, 5 enzim, 9 botanik extract (PDF'den)
- **ON Shots** — guarana 100mg kafein, Bacopa, Ashwagandha, B1-B12 vitamini (PDF'den)
- **Origin Chocolate** — 23g bitkisel protein, MCT, prebiotik, vegan (PDF'den)
- **Ignite Him** — Rhodiola, Cordyceps, kırmızı pancar, çinko (PDF'den)
- **Ignite Her** — magnesium, shatavari, çemen, limon melisa — ⚠️ GLUTEN İÇERİR (PDF'den)
- **HL5** — 5g kollajen Tip I+III peptid, içilebilir sachet (PDF'den)

---

## 🛍️ AmareNL.com Bridge Site — Affiliate Link Audit & Fix [18 Nisan 2026]

### Affiliate Link Düzeltmeleri
- **12 kırık link onarıldı** — 404 veren veya genel `/shop` sayfasına yönlendiren linkler doğru ürün sayfalarına çevrildi
- **Excel sync tamamlandı** — `amare_bridge_site/astra_integration/products/AmareNL product lijst.xlsx` kaynak dosyasındaki 39 affiliate URL, tüm WP sayfalarıyla karşılaştırıldı ve eşleştirildi
- **Kısa URL formatı** (`nl-nl/[slug]`) doğrulandı — uzun `/shop/[cat]/[slug]` formatları 404 veriyor, kısa format çalışıyor

### Düzeltilen Sayfalar (WP Page ID → Yeni URL)
| ID | Sayfa | Eski Link | Yeni Link |
|---|---|---|---|
| 758 | Happy Juice Pack | `nl-NL/happy-juice-edge-plus-mango` (404) | `nl-nl/amareedge-plus-mango` |
| 754 | EDGE+ Mango | `nl-NL/happy-juice-edge-plus-mango` (404) | `nl-nl/amareedge-plus-mango` |
| 751 | EDGE Grape | (404) | `nl-nl/amareedge-plus-watermelon` |
| 760 | HL5 Peach Collagen | `/shop` (genel) | `nl-nl/hl5-peach` |
| 327 | FIT20 | `/shop` (genel) | `nl-nl/fit20` |
| 22 | Restore | `/shop/restore/restore` (404) | `nl-nl/restore` |
| 12 | Mentabiotics | `/shop/mentabiotics/mentabiotics` (404) | `nl-nl/mentabiotics` |
| 9 | Ignite Him | `/shop/ignite/ignite-for-him` (404) | `nl-nl/ignite-for-him` |
| 10 | Ignite Her | `/shop/ignite/ignite-for-her` (404) | `nl-nl/ignite-for-her` |
| 14 | Triangle Xtreme | `/shop` (genel) | `nl-nl/triangle-of-wellness-xtreme` |
| 36 | Homepage hero | (404) | `nl-nl/amareedge-plus-mango` |
| 743 | Alle Producten | (404) | `nl-nl/amareedge-plus-mango` |

### Yeni Oluşturulan Sayfa
- **HL5 2-Pack** (WP ID: 982) — `https://amarenl.com/hl5-2pack/`
  - Affiliate: `https://www.amare.com/2075008/nl-nl/hl5-peach-2pack`
  - Fiyat: €130,42 (Subscribe & Save) / €144,90 (eenmalig)
  - Script: `scripts/create_hl5_2pack.py`

### Yeni / Güncellenen Scriptler
| Script | Açıklama |
|---|---|
| `scripts/audit_affiliate_urls.py` | Tüm WP sayfalarındaki amare.com linklerini denetler |
| `scripts/fix_affiliate_links.py` | 12 kırık linki düzeltir (hardcoded FIXES dict) |
| `scripts/fix_all_affiliate_from_excel.py` | Excel'deki URL'leri WP sayfalarıyla karşılaştırır ve otomatik düzeltir |
| `scripts/create_hl5_2pack.py` | HL5 2-Pack ürün sayfasını WordPress'te oluşturur |
| `scripts/fix_why_responsive.py` | "Waarom Amare" bölümünün 4-kolon responsive grid düzenlemesi |

---

## 🚀 Yarınki Görevler (14 Nisan)

1.  **Mission DAG Orchestration:**
    - `claude-devfleet` entegrasyonu ile birden fazla ajanlı (Research + Content + Sales) paralel görevlerin canlı testi.
2.  **DigitalOcean Canlı Yayını:**
    - Docker container test edilecek ve `arkmediaflow.com` DNS'i yönlendirilecek.
3.  **Autonomous Content Factory:**
    - Dr. Priya videosunun günlük, sıfır müdahale ile (Autonomous Loop) üretimi ve yayınlanması.
4.  **AI Regression Monitoring:**
    - `verify_system.py` ile "AI Blind Spot" taramalarının periyodik hale getirilmesi.

---

## 🧪 Son Test Raporu (10 Nisan)
- **Video pipeline:** zoompan → scale+crop ✅ (VPS'te çalışıyor)
- **Altyazı taşması:** 26 karakter wrap ile giderildi ✅
- **SEO güncelleme:** 37 post ✅
- **Schema markup:** 35 post ✅
- **Markdown temizleme:** 0 sorunlu post ✅
