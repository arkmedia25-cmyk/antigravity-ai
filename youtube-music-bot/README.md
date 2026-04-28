# 🤖 YouTube Music Bot (Autonomous Pipeline)

Bu repo, 4 farklı niş YouTube kanalı (SleepWave, NeonPulse, HealingFlow, BinauralMind) için tamamen otonom çalışan bir video üretim ve yükleme botunu barındırır.

## 📌 Son Güncellemeler & Yapılanlar (29 Nisan 2026)

Bugün sistem tamamen "bulletproof" ve üretime hazır hale getirildi. Yapılan işlemler:

### 1. ⚙️ Otomatik Çalışma Sistemi (Task Scheduler)
- `INSTALL_TASK_RUN_AS_ADMIN.ps1` scripti oluşturuldu.
- Bu script sayesinde Windows Task Scheduler'a bot eklendi ve her gece tam **01:00'da** herhangi bir manuel müdahaleye gerek kalmadan sırayla 4 kanal için video üretmeye ayarlandı.

### 2. 🌍 SEO, GEO ve İçerik Optimizasyonu
- Botun YouTube yükleme kodları (`youtube_upload.py`) yeniden yazıldı. Sabit etiketler (hardcoded tags) kaldırıldı.
- Artık her videonun başlığı (A/B Test uyumlu), açıklaması (description), etiketleri (tags) ve anahtar kelimeleri tamamen global (İngilizce), niş odaklı ve hatasız bir şekilde kendi `genres.json` dosyasından çekiliyor.
- Türkçe karakterler veya spesifik isimler sistemden temizlendi. İş e-postası (`info@kbmedia.nl`) tüm video açıklamalarına standart şablonla bağlandı.

### 3. 🕒 US Prime Time (Amerikan Hedef Kitlesi) Saat Ayarları
Tüm videolar "hemen yayınla (public)" yerine, Amerika Doğu Yakası (EST - New York) saatlerine göre "Zamanlanmış (Scheduled)" olarak YouTube'a atılır:
- **Uyku Müzikleri (SleepWave & BinauralMind):** İnsanların uyuma saatine göre EST 21:00 - 23:00 (Avrupa saati: 03:00 - 05:00)
- **Enerji / Spor Müzikleri (NeonPulse):** Sabah sporu EST 07:00 ve İş çıkışı EST 17:00
- **Odak / Rahatlama (HealingFlow):** Çalışma saatleri EST 09:00 ve Öğleden sonra EST 14:00

### 4. 🖼️ Thumbnail & Mobil Doğrulama
- 3 kanalın YouTube telefon (mobil) onayı sağlandığı için bot bu kanallara yapay zeka ile kendi ürettiği küçük resimleri (thumbnails) sorunsuz yükleyecek.
- Onaysız kanallar için YouTube sisteminden otomatik rastgele thumbnail seçilecek.

---
*Bot 100% otonom çalışmaktadır.*
