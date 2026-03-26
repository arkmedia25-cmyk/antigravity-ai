import os
import json
from ai_client import ask_ai
 
def load_json(filepath):
    """JSON dosyasını yükler ve debug bilgisi verir"""
    print(f"📂 Dosya aranıyor: {filepath}")
    
    if os.path.exists(filepath):
        print(f"✅ Dosya bulundu!")
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print(f"❌ DOSYA BULUNAMADI: {filepath}")
        print(f"   Klasör var mı: {os.path.exists(os.path.dirname(filepath))}")
    return {}
 
def load_memory():
    """Memory klasöründeki tüm JSON dosyalarını yükler"""
    
    # Mevcut dosyanın yolunu bul
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📍 Çalışma dizini: {current_dir}")
    
    # Memory klasörünün yolunu hesapla
    memory_dir = os.path.abspath(os.path.join(current_dir, "../../memory"))
    print(f"📂 Memory klasörü: {memory_dir}")
    print(f"   Memory var mı: {os.path.exists(memory_dir)}")
    
    # Eğer memory klasörü yoksa, alternatif yol dene
    if not os.path.exists(memory_dir):
        print("⚠️  Memory klasörü bulunamadı, alternatif yol deneniyor...")
        # OneDrive klasörü için direkt yol
        memory_dir = r"C:\Users\mus-1\OneDrive\Bureaublad\Antigravity\memory"
        print(f"📂 Alternatif yol: {memory_dir}")
    
    # Her dosyayı sırayla yükle
    brand = load_json(os.path.join(memory_dir, "brand.json"))
    audience = load_json(os.path.join(memory_dir, "audience.json"))
    products = load_json(os.path.join(memory_dir, "products.json"))
    learned = load_json(os.path.join(memory_dir, "learned.json"))
    
    print(f"\n📊 Yüklenen veriler:")
    print(f"   Brand: {len(brand)} anahtar")
    print(f"   Audience: {len(audience)} anahtar")
    print(f"   Products: {len(products.get('products', []))} ürün")
    print(f"   Learned: {len(learned)} anahtar")
    print(f"   Affiliate link: {products.get('affiliate_link', 'YOK')}\n")
    
    return brand, audience, products, learned
 
def run_email(task):
    """Email oluşturma görevi çalıştırır"""
    try:
        print("="*60)
        print("🚀 EMAIL AGENT BAŞLIYOR...")
        print("="*60 + "\n")
        
        brand, audience, products, learned = load_memory()
 
        system_prompt = f"""
Je bent een e-mail marketing specialist voor Amare Global Brand Partner in Nederland.
 
MERK INFO:
{json.dumps(brand, ensure_ascii=False, indent=2)}
 
DOELGROEPEN:
{json.dumps(audience, ensure_ascii=False, indent=2)}
 
PRODUCTEN:
{json.dumps(products, ensure_ascii=False, indent=2)}
 
EMAIL REGELS:
- Schrijf altijd in het Nederlands tenzij anders gevraagd
- Nooit medische claims maken
- Persoonlijk en warm van toon
- Maximaal 300 woorden per email
- Altijd een duidelijke onderwerpregel
- Nooit spam-achtige taal
- Focus op waarde geven eerst, verkopen later
- Gebruik storytelling en empathie
 
EMAIL TYPES:
1. Welkomst email (na aanmelding)
2. Nurture reeks (5-7 emails)
3. Productintroductie email
4. Testimonial email
5. Aanbieding email
6. Follow-up email
7. Re-engagement email
 
Voor elke email geef:
- Onderwerpregel (pakkend, niet spam)
- Preview tekst (eerste zin die inbox toont)
- Volledige email tekst
- CTA knop tekst
- Beste verzendtijd
 
Voor een reeks geef alle emails op volgorde met:
- Dag nummer
- Doel van deze email
- Volledige tekst
"""
 
        full_prompt = (
            f"{system_prompt}\n\n"
            f"TAAK: {task}\n\n"
            f"Schrijf professionele, persoonlijke emails die converteren."
        )
 
        print("💬 AI'ya gönderiliyor...")
        response = ask_ai(full_prompt)
        print("✅ Email oluşturuldu!\n")
        print("="*60)
        
        return response
 
    except Exception as e:
        error_msg = f"❌ Email agent hatası: {e}"
        print(error_msg)
        import traceback
        print(traceback.format_exc())
        return error_msg
 
 
# Test fonksiyonu
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TEST MODU")
    print("="*60 + "\n")
    
    # Önce sadece dosya yükleme testi
    print("1️⃣ Dosya yükleme testi...\n")
    try:
        brand, audience, products, learned = load_memory()
        print("\n✅ TÜM DOSYALAR BAŞARIYLA YÜKLENDİ!")
        
        # Affiliate link'i test et
        print("\n2️⃣ Affiliate link testi...")
        if 'affiliate_link' in products:
            print(f"✅ Affiliate link bulundu: {products['affiliate_link']}")
        else:
            print("❌ Affiliate link bulunamadı!")
            
    except Exception as e:
        print(f"\n❌ TEST BAŞARISIZ: {e}")
        import traceback
        print(traceback.format_exc())