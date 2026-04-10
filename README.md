# Antigravity AI - Proje Durum ve Takip Dosyası

> **ÖNEMLİ ÇALIŞMA KURALI:** Geliştirme sürecinde, yapay zeka ajanları (Antigravity/Claude vs.) her yeni oturuma veya göreve başladıklarında ilk olarak bu **README.md** dosyasını okuyacaklar. Her görevin veya günün sonunda, yapılan işlemler, çözülen hatalar ve tam olarak "nerede kalındığı" bu dosyaya kaydedilecektir. Böylece herkes her an güncel durumun farkında olacaktır.

---

## 📌 Nerede Kaldık? (Mevcut Durum)

En son **10 Nisan 2026** itibariyle aşağıdaki işlemler tamamlandı:

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

## 🚀 Bekleyen Görevler ve Sonraki Adım

- **Server cron kurulumu:** `python3 /opt/n8n/daily_article_writer.py` günlük 09:00 UTC
  ```bash
  cat > /etc/cron.d/amare-articles << 'EOF'
  0 9 * * * root /usr/bin/python3 /opt/n8n/daily_article_writer.py >> /root/antigravity-ai/logs/article_writer.log 2>&1
  EOF
  ```
- **Server dosya kopyalama:**
  ```bash
  git pull && cp scripts/article_writer.py /opt/n8n/ && cp scripts/daily_article_writer.py /opt/n8n/
  ```
- **GlowUp video kalitesi** — word-wrap sonrası canlı test yapılmalı
- **wellness_producer.py** — HeyGen pipeline test edilmeli

---

## 🧪 Son Test Raporu (10 Nisan)
- **Video pipeline:** zoompan → scale+crop ✅ (VPS'te çalışıyor)
- **Altyazı taşması:** 26 karakter wrap ile giderildi ✅
- **SEO güncelleme:** 37 post ✅
- **Schema markup:** 35 post ✅
- **Markdown temizleme:** 0 sorunlu post ✅
