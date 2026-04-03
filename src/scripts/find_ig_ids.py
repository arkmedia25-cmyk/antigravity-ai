import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")

def find_instagram_ids():
    if not ACCESS_TOKEN:
        print("❌ HATA: INSTAGRAM_ACCESS_TOKEN bulunamadı!")
        return

    print("\n" + "="*50)
    print("🔍 BAĞLI HESAPLAR VE ID'LER ARANIYOR...")
    print("="*50)

    # Step 1: Get Facebook Pages linked to this user
    url = "https://graph.facebook.com/v18.0/me/accounts"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": "name,instagram_business_account"
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()
        
        # DEBUG: Print Raw JSON
        print("\n--- [DEBUG: RAW META RESPONSE] ---")
        print(json.dumps(data, indent=2))
        print("--- [END DEBUG] ---\n")

        if "data" not in data:
            print(f"❌ HATA: Veri alınamadı! {data}")
            return
        
        print(f"\n✅ {len(data['data'])} tane bağlı sayfa bulundu.\n")
        
        found_accounts = []
        for page in data["data"]:
            page_name = page.get("name")
            page_id = page.get("id")
            ig_account = page.get("instagram_business_account")
            
            print(f"📄 SAYFA ADI: {page_name}")
            print(f"🆔 SAYFA ID : {page_id}")
            
            if ig_account:
                ig_id = ig_account.get("id")
                print(f"📸 IG BUSINESS ID: {ig_id} ✅ BAĞLI")
                found_accounts.append({
                    "page_name": page_name,
                    "ig_id": ig_id
                })
            else:
                print("⚠️ IG BUSINESS ID: Bulunamadı (Instagram henüz bağlı değil!)")
            
            print("-" * 30)
        
        if not found_accounts:
            print("\n❌ HATA: Görünürde hiçbir Instagram Business hesabı bulunamadı!")
            print("💡 İPUCU: Lütfen Instagram hesabınızın 'Ayarlar -> Hesap -> Profesyonel' olduğundan emin olun.")
        else:
            print(f"\n✨ TOPLAM {len(found_accounts)} BAŞARILI BAĞLANTI TESPİT EDİLDİ! ✨")


    except Exception as e:
        print(f"❌ HATA: {str(e)}")

if __name__ == "__main__":
    find_instagram_ids()
