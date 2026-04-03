import os
import requests
import json
from dotenv import load_dotenv

# Load env variables
load_dotenv()

APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("META_APP_SECRET")
# Using Meta's own explorer as a trusted redirect to bypass whitelist issues
REDIRECT_URI = "https://developers.facebook.com/tools/explorer/"

def start_auth_flow():
    if not APP_ID or not APP_SECRET:
        print("❌ HATA: .env dosyanızda META_APP_ID veya META_APP_SECRET eksik!")
        return

    # 1. Login Link Generation (Asking for TOKEN directly on a trusted Meta domain)
    scopes = "instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement,public_profile"
    auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?client_id={APP_ID}&redirect_uri={REDIRECT_URI}&scope={scopes}&response_type=token"

    print("\n" + "="*50)
    print("🚀 INSTAGRAM AUTHENTICATION BRIDGE (V4 - ULTRA) 🚀")
    print("="*50)
    print("\nLütfen şu adımları izleyin:")
    print(f"\n1. Şu linke tıklayın ve Facebook ile giriş yapın:\n\n{auth_url}")
    print("\n2. Giriş yaptıktan sonra Meta Graph API Explorer sayfası açılacak.")
    print("3. Tarayıcı adres çubuğundaki (URL) EN UZUN ADRESİ komple kopyalayıp buraya yapıştırın.")
    print("\n" + "="*50)
    
    redirected_url = input("\n👇 Kopyaladığınız adresi (URL) buraya yapıştırın: ").strip()
    
    short_token = None
    
    # Extract Access Token from Fragment or Query
    if "access_token=" in redirected_url:
        short_token = redirected_url.split("access_token=")[1].split("&")[0]
        print(f"\n✅ Doğrudan anahtar bulundu. 'Ömürlük' (60 Günlük) hale getiriliyor...")
    elif "code=" in redirected_url:
        auth_code = redirected_url.split("code=")[1].split("&")[0].split("#")[0]
        print(f"\n✅ Onay kodu bulundu. Kısa süreli anahtara çevriliyor...")
        
        token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params_short = {
            "client_id": APP_ID,
            "client_secret": APP_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": auth_code
        }
        res_short = requests.get(token_url, params=params_short)
        data_short = res_short.json()
        
        if "access_token" in data_short:
            short_token = data_short["access_token"]
        else:
            print(f"❌ Kod Değişim Hatası: {data_short.get('error', {}).get('message', 'Bilinmeyen hata')}")
            return
    else:
        print("❌ Hata: Adreste 'access_token' bulunabildi. Lütfen tarayıcıyı bekleyin ve TAM kopyalayın.")
        return

    # 2. Exchange Short Token for Long Token
    if short_token:
        token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params_long = {
            "grant_type": "fb_exchange_token",
            "client_id": APP_ID,
            "client_secret": APP_SECRET,
            "fb_exchange_token": short_token
        }
        
        try:
            res_long = requests.get(token_url, params=params_long)
            data_long = res_long.json()
            
            if "access_token" in data_long:
                long_token = data_long["access_token"]
                print(f"\n✨ ZAFER! 60 Günlük (Long-Lived) Anahtarınız Başarıyla Kaydedildi.")
                
                # 3. Update .env file
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
                
                print("\n📁 .env dosyası güncellendi. Instagram motorunuz ateşlemeye hazır!")
            else:
                print(f"❌ Uzun Süreli Token Hatası: {data_long.get('error', {}).get('message', 'Bilinmeyen hata')}")
        except Exception as e:
            print(f"❌ Sistemsel hata: {str(e)}")

if __name__ == "__main__":
    start_auth_flow()
