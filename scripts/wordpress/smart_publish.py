import os
import requests
from dotenv import load_dotenv

load_dotenv()

def auto_publish():
    # 1. En son alınan token'ı kullan
    access_token = "EAAktZAsle4pMBRLurTHntT6W0ZBvFpgCq7ptgQOPL8EWsFXghXc3xNqal0hmY7yeZBFZApjcnG1azpZCmEl41xiRTGoE6euzDMBH59bpFASX3oYeZCnVCYrHh57aVrMpB0KJ7dbQ589BU7YuMGmkiRADJfkwbamucsmaJvUWqbtypNEXOyHZBjiYWvcdWWrQiDyTH8CjDj3tt92bMwEVlhRTVuBKhe07VR88KD0VSetNUXwgsbcFxTjjHITlblwPhEHBWdJ2JAgn3xLtN5IFj4Mk03RAL7ATppx3AZDZD"
    
    print("--- 🚀 AUTO-IDENTIFY & PUBLISH STARTING ---")
    
    # 2. Token ile yetkili sayfaları ve bunlara bağlı IG hesaplarını tara
    url = "https://graph.facebook.com/v22.0/me/accounts"
    params = {"access_token": access_token, "fields": "name,instagram_business_account{id,username}"}
    
    target_ig_id = None
    
    try:
        res = requests.get(url, params=params).json()
        if "data" in res:
            for page in res["data"]:
                ig_info = page.get("instagram_business_account")
                if ig_info:
                    print(f"📍 Checking Instagram Account: @{ig_info.get('username')} (ID: {ig_info.get('id')})")
                    # Eğer @glowupnl1 hesabını bulursak bunu hedef alalım
                    if "glowupnl" in ig_info.get("username", "").lower():
                        target_ig_id = ig_info.get("id")
                        print(f"🎯 TARGET IDENTIFIED: @{ig_info.get('username')}")
                        break
        
        if not target_ig_id:
            print("❌ Error: Could not automatically find @glowupnl1 account. Please check linked accounts in Business Suite.")
            return

        # 3. .env dosyasını otomatik güncelle (ilerisi için)
        print(f"💾 Updating .env with correct ID: {target_ig_id}")
        # Bu kısımda manuel güncelleme yerine script içinde ID'yi kullanacağız
        
        # 4. Paylaşım İşlemi
        video_url = "https://files.catbox.moe/rhqjlc.mp4"
        caption = "Wil je meer energie in de ochtend zonder cafeïne? Probeer dit! #GlowUpNL"
        
        print(f"🎬 Publishing to IG ID: {target_ig_id}...")
        
        # Step A: Container Creation
        post_url = f"https://graph.facebook.com/v22.0/{target_ig_id}/media"
        post_params = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": access_token
        }
        
        create_res = requests.post(post_url, data=post_params).json()
        container_id = create_res.get("id")
        
        if container_id:
            print(f"✅ Container created: {container_id}. Waiting for processing (20s)...")
            import time
            time.sleep(20)
            
            # Step B: Publish
            publish_url = f"https://graph.facebook.com/v22.0/{target_ig_id}/media_publish"
            publish_params = {
                "creation_id": container_id,
                "access_token": access_token
            }
            final_res = requests.post(publish_url, data=publish_params).json()
            
            if "id" in final_res:
                print(f"🎉 SUCCESS! Reels published. Media ID: {final_res.get('id')}")
            else:
                print(f"❌ Final Publish Error: {final_res.get('error', {}).get('message')}")
        else:
            print(f"❌ Container Error: {create_res.get('error', {}).get('message')}")
            
    except Exception as e:
        print(f"⚠️ Exception: {e}")

if __name__ == "__main__":
    auto_publish()
