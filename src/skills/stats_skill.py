import os
import requests
import json

def get_instagram_stats(business_id, access_token):
    """
    Fetches followers count and media stats for a given Instagram Business ID.
    """
    if not business_id or not access_token:
        return {"error": "Eksik API bilgileri (Business ID veya Token yok)."}

    # Base URL for Instagram Graph API
    url = f"https://graph.facebook.com/v18.0/{business_id}"
    
    # Fields to fetch: followers_count, follows_count, media_count, etc.
    params = {
        "fields": "followers_count,follows_count,media_count,name,username",
        "access_token": access_token
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error" in data:
            return {"error": data["error"].get("message", "Bilinmeyen API hatası")}
            
        return data
    except Exception as e:
        return {"error": str(e)}

def format_stats_dashboard(glow_stats, holisti_stats):
    """
    Formats the stats into a beautiful Telegram message.
    """
    dashboard = "📊 ** AGENCY ANALYTICS DASHBOARD ** 📈\n\n"
    
    # GlowUp Stats
    dashboard += "🟢 **@GlowUpNL**\n"
    if "error" in glow_stats:
        dashboard += f"⚠️ Veri alınamadı: {glow_stats['error']}\n"
    else:
        dashboard += f"👥 Takipçi: {glow_stats.get('followers_count', 0):,}\n"
        dashboard += f"🎬 Gönderi: {glow_stats.get('media_count', 0)}\n"
        dashboard += "✨ Durum: Aktif & Büyüyor\n"
    
    dashboard += "\n" + "─" * 15 + "\n\n"
    
    # HolistiGlow Stats
    dashboard += "🟣 **@HolistiGlow**\n"
    if "error" in holisti_stats:
        dashboard += f"⚠️ Veri alınamadı: {holisti_stats['error']}\n"
    else:
        dashboard += f"👥 Takipçi: {holisti_stats.get('followers_count', 0):,}\n"
        dashboard += f"🎬 Gönderi: {holisti_stats.get('media_count', 0)}\n"
        dashboard += "🌿 Durum: Yayında\n"
        
    dashboard += "\n🚀 _Agency sisteminiz otonom çalışmaya devam ediyor._"
    return dashboard
