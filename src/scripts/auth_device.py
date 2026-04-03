import os
import requests
import time
from dotenv import load_dotenv

# Load env variables
load_dotenv()

APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("META_APP_SECRET")
CLIENT_TOKEN = os.getenv("META_CLIENT_TOKEN")

def start_device_auth():
    if not APP_ID or not APP_SECRET or not CLIENT_TOKEN:
        print("❌ HATA: .env dosyanızda META_APP_ID, META_APP_SECRET veya META_CLIENT_TOKEN eksik!")
        return

    print("\n" + "="*50)
    print("🚀 INSTAGRAM AUTHENTICATION (V5.1 - CLIENT_TOKEN MODE) 🚀")
    print("="*50)
    print("\n1. Yetkilendirme kodu üretiliyor (Client Token ile)...")

    # Step 1: Generate Device Code
    # NEW: Using CLIENT_TOKEN to bypass #190 error
    scopes = "instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement,public_profile"
    
    url = "https://graph.facebook.com/v18.0/device/login"
    payload = {
        "access_token": f"{APP_ID}|{CLIENT_TOKEN}", # THIS IS THE KEY!
        "scope": scopes
    }
    
    try:
        res = requests.post(url, data=payload)
        data = res.json()
        
        if "code" not in data:
            print(f"❌ Kod Alınamadı: {data.get('error', {}).get('message', 'Bilinmeyen hata')}")
            return

        user_code = data["user_code"]
        verification_uri = data["verification_uri"]
        code_on_device = data["code"]

        expires_in = data.get("expires_in", 300)
        print(f"\n✅ Kodunuz Hazır: {user_code}")
        print(f"⏳ Bu kodun tam {expires_in} saniye (yaklaşık {expires_in//60} dakika) ömrü var.")
        print(f"\n2. Şimdi şu adrese gidin: {verification_uri}")
        print(f"3. Ekrana şu kodu yazın: {user_code}")
        print("\n⏳ Onay verdiğinizde ben otomatik olarak algılayıp 'Ömürlük Anahtar'ı alacağım...")

        # Step 2: Poll for Access Token
        poll_url = "https://graph.facebook.com/v18.0/device/login_status"
        poll_payload = {
            "access_token": f"{APP_ID}|{CLIENT_TOKEN}",
            "code": code_on_device
        }

        short_token = None
        start_time = time.time()
        while time.time() - start_time < expires_in:
            time.sleep(2) # Faster polling
            poll_res = requests.post(poll_url, data=poll_payload)
            poll_data = poll_res.json()
            
            if "access_token" in poll_data:
                short_token = poll_data["access_token"]
                break
            
            error_data = poll_data.get("error", {})
            error_subcode = error_data.get("error_subcode")
            
            # Subcode 1349152 means waiting for user approval
            if error_subcode == 1349152:
                # Still waiting... maybe print a dot to show life?
                print(".", end="", flush=True)
                continue
            elif error_subcode == 1349174: # Code expired
                print("\n❌ Kodun süresi Meta tarafından doldu.")
                return
            elif "error" in poll_data:
                print(f"\n❌ Hata: {error_data.get('message')}")
                return
        
        if not short_token:
            print("\n❌ Zaman aşımı: Kodun süresi bitti.")
            return


        # Step 3: Exchange for Long-Lived Token
        if short_token:
            print("\n✅ Onay algılandı! Şimdi bu anahtarı 'Ömürlük' (60 Günlük) hale getiriyorum...")
            exchange_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            exchange_params = {
                "grant_type": "fb_exchange_token",
                "client_id": APP_ID,
                "client_secret": APP_SECRET,
                "fb_exchange_token": short_token
            }
            
            res_long = requests.get(exchange_url, params=exchange_params)
            data_long = res_long.json()
            
            if "access_token" in data_long:
                long_token = data_long["access_token"]
                print(f"\n✨ ZAFER! 60 Günlük (Long-Lived) Anahtarınız Alındı ve Kaydedildi.")
                
                # Update .env
                with open(".env", "r") as f:
                    lines = f.readlines()
                
                new_lines = []
                found = False
                for line in lines:
                    if line.startswith("INSTAGRAM_ACCESS_TOKEN="):
                        new_lines.append(f"INSTAGRAM_ACCESS_TOKEN={long_token}\n")
                        found = True
                    else:
                        new_lines.append(line)
                
                if not found:
                    new_lines.append(f"INSTAGRAM_ACCESS_TOKEN={long_token}\n")
                
                with open(".env", "w") as f:
                    f.writelines(new_lines)
                
                print("\n📁 .env dosyası güncellendi. Instagram motorunuz artık 100% CANLI!")
                print("\n🚀 Artık botunuza gidip /stats yazabilir veya video üretebilirsiniz!")
            else:
                print(f"❌ Uzun Süreli Token Hatası: {data_long.get('error', {}).get('message', 'Bilinmeyen hata')}")

    except Exception as e:
        print(f"❌ Sistemsel hata: {str(e)}")

if __name__ == "__main__":
    start_device_auth()
