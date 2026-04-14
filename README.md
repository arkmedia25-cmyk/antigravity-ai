# Antigravity AI - Proje Durum ve Takip Dosyası

> **ÖNEMLİ ÇALIŞMA KURALI:** Geliştirme sürecinde, yapay zeka ajanları (Antigravity/Claude vs.) her yeni oturuma veya göreve başladıklarında ilk olarak bu **README.md** dosyasını okuyacaklar. Her görevin veya günün sonunda, yapılan işlemler, çözülen hatalar ve tam olarak "nerede kalındığı" bu dosyaya kaydedilecektir. Böylece herkes her an güncel durumun farkında olacaktır.

---

En son **13-14 Nisan 2026** itibariyle aşağıdaki kritik "Gelecek Nesil" özellikler eklendi ve sistem "Agency Swarm OS" mimarisine taşındı:

### 🤖 Agency Swarm OS (Ajan Sürüsü) - [YENİ]
- **Swarm Protokolü** → Ajanların birbirine veri ve görev devretmesini sağlayan `SwarmMessage` protokolü kuruldu. ✅
- **Akıllı Orkestratör** → Ardışık (sequential) ajan zincirleme özelliği eklendi. (Örn: Research -> Video Producer otonom akışı). ✅
- **Video Producer Agent** → Wellness videolarını otonom üreten, ElevenLabs ve video skill'lerini yöneten uzman ajan eklendi. ✅
- **Ajan Güncellemeleri** → CMO, Content, Sales, Email, LinkedIn ve Research ajanları Swarm yapısına (structured JSON) uyumlu hale getirildi.

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

## 🚀 Yarınki Görevler (14 Nisan)

1.  **DigitalOcean Canlı Yayını:**
    - Docker container test edilecek.
    - `arkmediaflow.com` DNS'i yeni sunucuya veya FastAPI portuna (8000) yönlendirilecek.
2.  **Dashboard Canlı Veri Bağlantısı:**
    - Prototip olan dashboard, FastAPI üzerinden gerçek ajan aktivitelerini gösterecek şekilde güncellenecek.
3.  **Ajanlar Arası Otonom Test:**
    - "Tek sesle video üretimi" (Sesli mesaj -> Araştırma -> Video) akışı canlıda test edilecek.
4.  **Canva Token Yenileme:**
    - Yarım kalan PKCE verifier temizliği ve Canva token akışı tamamlanacak.

---

## 🧪 Son Test Raporu (10 Nisan)
- **Video pipeline:** zoompan → scale+crop ✅ (VPS'te çalışıyor)
- **Altyazı taşması:** 26 karakter wrap ile giderildi ✅
- **SEO güncelleme:** 37 post ✅
- **Schema markup:** 35 post ✅
- **Markdown temizleme:** 0 sorunlu post ✅
