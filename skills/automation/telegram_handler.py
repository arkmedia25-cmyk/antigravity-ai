import time
import requests
import sys
import os
import threading
from dotenv import load_dotenv

try:
    from flask import Flask, request as flask_request
    _flask_available = True
except ImportError:
    _flask_available = False

# Windows konsolunda UTF-8 emoji destegi
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
 
load_dotenv(override=True)
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../agents/linkedin-agent"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../agents/content-agent"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../agents/email-agent"))

# Phase 3: add project root so src/ is importable
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
 
_src_path = os.path.join(_project_root, "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

from cmo_agent import run_cmo
from linkedin_agent import run_linkedin
from content_agent import run_content
from email_agent import run_email

# Phase 3: try to load new src/ system — bot keeps working if this fails
try:
    from src.interfaces.telegram.handler import TelegramHandler as _NewHandler
    _new_handler = _NewHandler()
    _use_new_system = True
    print("[Phase3] New src/ system loaded successfully")
except Exception as _e:
    _new_handler = None
    _use_new_system = False
    print(f"[Phase3] New src/ system unavailable — fallback active: {_e}")

# Video pipeline — laad skills vanuit src/
try:
    import sys as _sys
    _src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
    if _src_path not in _sys.path:
        _sys.path.insert(0, _src_path)
    from skills.tts_skill import generate_dutch_audio
    from skills.video_skill import create_reel
    from scheduler.content_scheduler import start_content_factory
    from skills.ai_client import ask_ai
    _video_pipeline_ok = True
    print("[Video] Pipeline geladen")
except Exception as _ve:
    _video_pipeline_ok = False
    print(f"[Video] Pipeline niet beschikbaar: {_ve}")
 
TOKEN = os.getenv("TELEGRAM_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"
 
def safe_request(url, method="get", **kwargs):
    """Veilige API request met retry logic"""
    for i in range(5):
        try:
            if method == "get":
                response = requests.get(url, timeout=30, **kwargs)
            else:
                response = requests.post(url, timeout=30, **kwargs)
            if not response.ok:
                # Log the full Telegram error body before raising
                print(f"[safe_request] HTTP {response.status_code} — Telegram zegt: {response.text}")
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Verbindingsfout (poging {i+1}): {e}")
            if i < 4:
                time.sleep(2)
    return None
 
def get_updates(offset=None):
    """Haal Telegram updates op"""
    params = {"timeout": 20}
    if offset is not None:
        params["offset"] = offset
    response = safe_request(f"{URL}/getUpdates", method="get", params=params)
    if response:
        return response.json()
    return {"result": []}
 
_TELEGRAM_MAX_LEN = 4096


def _safe_text(text) -> str:
    """Convert any value to a plain, non-empty string."""
    if not isinstance(text, str):
        text = str(text)
    text = text.strip()
    return text if text else "(geen inhoud)"


def send_video(chat_id, video_path: str, caption: str = ""):
    """Stuur video bestand naar Telegram chat met download button."""
    print(f"[send_video] chat_id={chat_id} | path={video_path}")
    import json
    try:
        with open(video_path, "rb") as f:
            # Add a button to download as a document (File)
            reply_markup = {
                "inline_keyboard": [[
                    {"text": "💾 Dosya Olarak İndir (Yüksek Kalite)", "callback_data": f"dl_doc_{os.path.basename(video_path)}"}
                ]]
            }
            safe_request(
                f"{URL}/sendVideo",
                method="post",
                data={
                    "chat_id": chat_id, 
                    "caption": caption,
                    "supports_streaming": True,
                    "reply_markup": json.dumps(reply_markup)
                },
                files={"video": (os.path.basename(video_path), f, "video/mp4")},
            )
    except Exception as e:
        print(f"[send_video] HATA: {e}")
        send_message(chat_id, f"Video gonderilirken hata: {e}")

def send_document(chat_id, file_path: str, caption: str = ""):
    """Stuur bestand als Document (onverpakt) naar Telegram."""
    print(f"[send_document] chat_id={chat_id} | path={file_path}")
    import os
    try:
        # Resolve absolute path or search in common locations
        final_path = file_path
        if not os.path.exists(final_path):
            candidates = [
                os.path.join(os.getcwd(), file_path),
                os.path.join(os.getcwd(), "outputs", os.path.basename(file_path))
            ]
            for c in candidates:
                if os.path.exists(c):
                    final_path = c
                    break
        
        if not os.path.exists(final_path):
             print(f"[send_document] HATA: Dosya bulunamadi: {file_path}")
             send_message(chat_id, f"⚠️ Dosya bulunamadı: {os.path.basename(file_path)}")
             return

        with open(final_path, "rb") as f:
            safe_request(
                f"{URL}/sendDocument",
                method="post",
                data={"chat_id": chat_id, "caption": caption},
                files={"document": (os.path.basename(final_path), f)},
            )
    except Exception as e:
        print(f"[send_document] HATA: {e}")
        send_message(chat_id, f"Dosya gonderilirken hata: {e}")


def _generate_and_send_video(chat_id, topic, brand="holisti"):
    """Tam video üretim akışı (Brand farkındalıklı)"""
    import time, datetime
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    brand_label = "@GlowUpNL" if brand == "glow" else "@HolistiGlow"
    tone = "energetic and result-oriented" if brand == "glow" else "calm and holistic"

    try:
        # Load Brand-Specific Squad Manifesto
        personality_file = f"{brand}_personality.txt"
        personality_path = os.path.join(os.getcwd(), "agents", personality_file)
        manifesto = ""
        if os.path.exists(personality_path):
            with open(personality_path, "r", encoding="utf-8") as f:
                manifesto = f.read()

        # Step 1: AI generates script, caption and tags
        send_message(chat_id, f"🎬 {brand_label} SQUAD iş başında!\nKonu: {topic}\nStrateji: {brand.upper()} Manifestosu uygulanıyor...")
        
        prompt = (
            f"=== SQUAD MANIFESTO - ACT AS THIS TEAM ===\n{manifesto}\n\n"
            f"Role: Expert Wellness Content Creator. Brand: {brand_label}.\n"
            f"Topic (may be in Turkish, translate to Dutch first): {topic}\n"
            "CRITICAL: YOUR OUTPUT MUST BE 100% IN DUTCH. NO TURKISH WORDS ALLOWED.\n"
            "GOAL: Create a high-conversion, trust-building Instagram package for Dutch women.\n"
            "STRUCTURE:\n"
            "1. HOOK (5-8 sec): Curiosity or problem-solving entrance.\n"
            "2. CONTENT (15-20 sec): 2-3 genuinely helpful tips.\n"
            "3. CTA (5 sec): Polite follow invitation.\n\n"
            "PROVIDE THESE 3 PARTS IN DUTCH ONLY:\n"
            "---SCRIPT---\n[STRICTLY DUTCH - Voiceover text only - NO TURKISH]\n"
            "---CAPTION---\n[STRICTLY DUTCH - Engaging Instagram caption]\n"
            "---TAGS---\n[Strategic Hashtags]\n"
        )
        full_response = ask_ai(prompt)
        
        # Parse response
        script = full_response.split("---SCRIPT---")[-1].split("---CAPTION---")[0].strip()
        caption_body = full_response.split("---CAPTION---")[-1].split("---TAGS---")[0].strip()
        tags = full_response.split("---TAGS---")[-1].strip()

        # Stap 2: Fragmented TTS (Zero Delay Mode)
        send_message(chat_id, f"Stap 2/3: {brand_label} seslendirme motoru çalışıyor (Kusursuz Akış & Enerji)...")
        
        # Split script into clean sentences
        import json, re
        raw_sentences = re.split(r'(?<=[.!?])\s+', script.strip())
        clean_sentences = []
        for s in raw_sentences:
            s_clean = re.sub(r'^\s*[\d]+[\.\)]\s*', '', s).strip()
            s_clean = re.sub(r'^\s*[-•*]\s*', '', s_clean).strip()
            if len(s_clean) >= 8: # More inclusive
                clean_sentences.append(s_clean)
        
        if not clean_sentences:
            clean_sentences = ["Welkom bij Holisti Glow. Ontdek je beste zelf vandaag!"]

        # Generate each audio fragment and store metadata
        fragment_data = []
        for i, text in enumerate(clean_sentences):
            f_name = f"audio_frag_{ts}_{i}.mp3"
            f_path = generate_dutch_audio(text, filename=f_name, voice="nova", speed=1.15)
            # Tag metadata for video_skill (0=hook, middle=content, last=cta)
            tag = "hook" if i == 0 else ("cta" if i == len(clean_sentences) - 1 else "content")
            fragment_data.append({"sentence": text, "audio": f_path, "tag": tag})

        # Save fragments for video_skill
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/fragments.json", "w", encoding="utf-8") as f:
            json.dump(fragment_data, f, ensure_ascii=False, indent=2)

        # Stap 3: Video renderen (create_reel picks up fragments.json)
        send_message(chat_id, "Stap 3/3: Video renderen (Sıfır Gecikme, Tam Senkronizasyon)...")
        video_path = create_reel(brand=brand, output_filename=f"reel_{brand}_{ts}.mp4")

        # Verstuur video
        final_caption = f"✨ {brand_label} Video Ready!\n\nCheck below for your caption & tags 👇"
        send_video(chat_id, video_path, caption=final_caption)
        
        # Send Copy-Paste Package
        package = (
            f"📝 **INSTAGRAM PACKAGE**\n\n"
            f"**Caption:**\n{caption_body}\n\n"
            f"**Hashtags:**\n`{tags}`"
        )
        send_message(chat_id, package)

    except Exception as e:
        print(f"[Video] HATA: {e}")
        send_message(chat_id, f"Video olusturulirken hata: {e}")


def send_message(chat_id, text):
    """Stuur bericht naar Telegram chat — splits automatisch bij >4096 tekens."""
    text = _safe_text(text)
    print(f"[send_message] chat_id={chat_id} | len={len(text)}")
    chunks = [text[i:i + _TELEGRAM_MAX_LEN] for i in range(0, len(text), _TELEGRAM_MAX_LEN)]
    for chunk in chunks:
        data = {"chat_id": chat_id, "text": chunk}
        safe_request(f"{URL}/sendMessage", method="post", data=data)

def send_message_with_markup(chat_id, text, reply_markup):
    """Stuur bericht met inline buttons."""
    import json
    data = {
        "chat_id": chat_id, 
        "text": text,
        "reply_markup": json.dumps(reply_markup)
    }
    safe_request(f"{URL}/sendMessage", method="post", data=data)
 
_CANVA_FILE_MARKER = "CANVA_FILE:"


def _send_canva_response(chat_id, response: str):
    """Send Canva agent response. If it contains a file URL, send the file via Telegram."""
    if _CANVA_FILE_MARKER in response:
        lines = response.split("\n")
        file_line = next((l for l in lines if l.startswith(_CANVA_FILE_MARKER)), None)
        text_lines = [l for l in lines if not l.startswith(_CANVA_FILE_MARKER)]
        text_body = "\n".join(text_lines).strip()

        if text_body:
            send_message(chat_id, text_body)

        if file_line:
            payload = file_line[len(_CANVA_FILE_MARKER):]
            parts = payload.split("|")
            file_url = parts[0].strip()
            fmt = parts[1].strip().lower() if len(parts) > 1 else "png"

            if fmt == "mp4":
                safe_request(f"{URL}/sendVideo", method="post",
                             data={"chat_id": chat_id, "video": file_url,
                                   "caption": "🎬 Canva video export"})
            else:
                safe_request(f"{URL}/sendDocument", method="post",
                             data={"chat_id": chat_id, "document": file_url,
                                   "caption": "🖼 Canva export"})
    else:
        send_message(chat_id, response)


def route_nl_request(chat_id, text):
    """Met GPT-4o bepalen wat een 'normaal' bericht betekent."""
    prompt = (
        f"Kullanıcı mesajı: '{text}'\n\n"
        "Sen @GlowUpNL markasının dijital asistanısın. Kullanıcının niyetini anla.\n"
        "Şu eylemlerden birini seç (action):\n"
        "1. 'video': Kullanıcı video/reels yapılmasını istiyor.\n"
        "2. 'idea': Kullanıcı içerik fikri istiyor.\n"
        "3. 'research': Kullanıcı pazar/trend araştırması istiyor.\n"
        "4. 'chat': Sadece soru soruyor veya sohbet ediyor.\n\n"
        "JSON döndür: { \"action\": \"...\", \"topic\": \"...\", \"reply\": \"Kullanıcıya verilecek kısa ön onay mesajı\" }"
    )
    from skills.ai_client import ask_ai
    try:
        from skills.ai_client import ask_ai
        # Force JSON response via the newly patched ask_ai
        decision = ask_ai(prompt, is_json=True)
        print(f"[Router] Decision: {decision}")
        
        action = decision.get("action", "chat")
        topic = decision.get("topic", "")
        reply = decision.get("reply", "Anladım, hemen ilgileniyorum...")
        
        if action == "video":
            import json
            # Ask which brand
            reply_markup = {
                "inline_keyboard": [[
                    {"text": "🔥 @GlowUpNL (Energetic)", "callback_data": f"brand_glow_video_{topic}"},
                    {"text": "🌿 @HolistiGlow (Calm)", "callback_data": f"brand_holisti_video_{topic}"}
                ]]
            }
            send_message_with_markup(chat_id, "Hangi kanal için video hazırlayalım komutanım?", reply_markup)
        elif action == "post":
            import json
            # Ask which brand for post
            reply_markup = {
                "inline_keyboard": [[
                    {"text": "🔥 @GlowUpNL (Energetic)", "callback_data": f"brand_glow_post_{topic}"},
                    {"text": "🌿 @HolistiGlow (Calm)", "callback_data": f"brand_holisti_post_{topic}"}
                ]]
            }
            send_message_with_markup(chat_id, "Hangi kanal için statik POST hazırlayalım?", reply_markup)
        elif action == "idea":
            send_message(chat_id, reply)
            process_command(chat_id, "/idea")
        elif action == "research":
            send_message(chat_id, reply)
            process_command(chat_id, f"/research {topic}")
        else:
            # Standart Chat
            response = ask_ai(f"Brand: @GlowUpNL. User asked: {text}. Respond as a wise best friend CMO (1-3 sentences).")
            send_message(chat_id, response)
    except Exception as e:
        print(f"[Router] HATA: {e}")
        send_message(chat_id, "Üzgünüm, ne demek istediğini tam anlayamadım ama her zaman /start ile komutları görebilirsin!")


def _run_agency_video(chat_id, brand, topic):
    """Markaya ozel trend analizi yap ve video uret."""
    try:
        import hunt_trends
        send_message(chat_id, f"🔍 @{brand.capitalize()}NL için güncel pazar trendleri taranıyor...")
        hunt_trends.hunt_trends(brand=brand)
        
        from autonomous_producer import run_production_line
        from src.skills.video_skill import create_reel
        import time
        
        send_message(chat_id, f"🎬 Otonom '{brand.capitalize()}' senaryosu (Trend uyumlu) hazırlanıyor...")
        pack = run_production_line(topic=topic)
        if not pack:
             send_message(chat_id, "❌ Senaryo üretilirken bir hata oluştu.")
             return
        
        data = pack["gpt_data"]
        from src.skills.ai_client import generate_image
        bg_path = generate_image(data['image_prompt'])
        
        send_message(chat_id, "🎥 Video render ediliyor (Agency Mode)...")
        video_path = create_reel(
            fragments=pack["fragments"],
            image_path=bg_path,
            output_filename=f"agency_{brand}_{int(time.time())}.mp4",
            brand=brand
        )
        
        send_video(chat_id, video_path, caption=f"✨ @{brand.capitalize()}NL Otonom Video!\n\nSenaryo: {data['dutch_script']}\n\n📝 **Posting Kit:**\n{data.get('instagram_caption', '')}")
    except Exception as e:
        print(f"[_run_agency_video] HATA: {e}")
        send_message(chat_id, f"❌ Agency video hatası: {e}")

def _run_agency_post(chat_id, brand, topic):
    """Markaya ozel statik post uret."""
    try:
        import hunt_trends
        send_message(chat_id, f"🔍 @{brand.capitalize()}NL için trend-odaklı görsel post planlanıyor...")
        hunt_trends.hunt_trends(brand=brand)
        
        from autonomous_producer import generate_autonomous_content
        send_message(chat_id, f"🎨 @{brand.capitalize()}NL statik post tasarımı (DALL-E) başlatıldı...")
        
        data = generate_autonomous_content(topic)
        if not data: return
        
        from src.skills.ai_client import generate_image
        # Post format is 1:1, ask DALL-E for square
        post_path = generate_image(data['image_prompt'] + " (Square 1:1 format, high-end photography, cinematic wellness style)")
        
        if not post_path: return
        
        send_document(chat_id, post_path, caption=f"🖼 @{brand.capitalize()}NL Statik Post Hazır!\n\n**Açıklama:**\n{data.get('instagram_caption', '')}\n\n**Etiketler:**\n`{data.get('hashtags', '')}`")
    except Exception as e:
        print(f"[_run_agency_post] HATA: {e}")
        send_message(chat_id, f"❌ Agency post hatası: {e}")


def process_command(chat_id, text):
    """Verwerk Telegram commando"""
    # NL Router for non-slash messages
    if not text.startswith("/"):
        import threading
        threading.Thread(target=route_nl_request, args=(chat_id, text), daemon=True).start()
        return

    try:
        if text.startswith("/squad_status"):
            # Competition Dashboard (Simulation for now based on generated files)
            glow_count = len([f for f in os.listdir("outputs") if "reel_glow" in f])
            holisti_count = len([f for f in os.listdir("outputs") if "reel_holisti" in f])
            
            winner = "🔥 GLOWUP" if glow_count > holisti_count else "🌿 HOLISTIGLOW" if holisti_count > glow_count else "🤝 BERABERE"
            
            status = (
                f"🏆 **SQUAD REKABETİ: GÜNCEL DURUM**\n\n"
                f"🔥 **GLOWUP SQUAD (@GlowUpNL)**\n"
                f"└ Üretilen Reel: {glow_count}\n"
                f"└ Mood: Enerjik & Hırslı\n\n"
                f"🌿 **HOLISTIGLOW SQUAD (@HolistiGlow)**\n"
                f"└ Üretilen Reel: {holisti_count}\n"
                f"└ Mood: Bilge & Huzurlu\n\n"
                f"📊 **ŞU AN ÖNDE OLAN:** {winner}\n"
                f"🏁 **Hedef:** 30 günde 2.000 takipçi!"
            )
            send_message(chat_id, status)

        elif text.startswith("/start"):
            # Start the 24/7 Automated Content Factory
            start_content_factory(chat_id)
            send_message(chat_id,
                "🚀 Antigravity AI Bot Hazır!\n\n"
                "🎬 **VİDEO ÜRETİMİ (GlowUp & Holisti)**\n"
                "/video_glow <konu> - Mercan/Şeftali temalı @GlowUpNL videosu\n"
                "/video_holisti <konu> - Bej/Yeşil temalı @HolistiGlow videosu\n\n"
                "🧠 **STRATEJİ & ANALİZ**\n"
                "/cmo - Pazarlama stratejisi ve büyüme tavsiyesi\n"
                "/research - Pazar trendleri ve rakip analizi\n\n"
                "📱 **İÇERİK ÜRETİMİ**\n"
                "/content - Instagram/Reels metinleri\n"
                "/idea - Viral video fikirleri\n"
                "/script - Video senaryosu\n\n"
                "🎨 **TASARIM**\n"
                "/canva - Canva tasarımları oluştur\n\n"
                "💡 *Örnek: /video_glow sabah rutini ve enerji*"
            )

        elif text.startswith("/video_glow"):
            topic = text.replace("/video_glow", "").strip() or "Gezondheid"
            threading.Thread(target=_generate_and_send_video, args=(chat_id, topic, "glow")).start()
            
        elif text.startswith("/video_holisti"):
            topic = text.replace("/video_holisti", "").strip() or "Wellness"
            threading.Thread(target=_generate_and_send_video, args=(chat_id, topic, "holisti")).start()

        elif text.startswith("/gezellig"):
            # Otonom NL Wellness (Gezellig Vibe)
            topic = text.replace("/gezellig", "").strip()
            def run_otonom():
                try:
                    from autonomous_producer import run_production_line
                    from src.skills.video_skill import create_reel
                    import time
                    
                    send_message(chat_id, f"🎬 Otonom 'Gezellig' Senarist (GPT) iş başında... {f'Konu: {topic}' if topic else ''}")
                    pack = run_production_line(topic=topic)
                    if not pack:
                         send_message(chat_id, "❌ GPT senaryo yazarken bir hata oluştu.")
                         return
                    
                    data = pack["gpt_data"]
                    
                    send_message(chat_id, f"🎨 Işıkçı (DALL-E) seti hazırlıyor: {data['image_prompt'][:50]}...")
                    from src.skills.ai_client import generate_image
                    bg_path = generate_image(data['image_prompt'])
                    
                    if not bg_path:
                        send_message(chat_id, "⚠️ Görsel oluşturulamadı, varsayılan arka plan kullanılıyor.")
                        bg_path = os.path.join(os.getcwd(), "outputs", "gezellig_default.png")
                    
                    send_message(chat_id, "🎥 Stüdyo & Kameraman (FFmpeg) kayda giriyor...")
                    
                    video_path = create_reel(
                        fragments=pack["fragments"],
                        image_path=bg_path,
                        output_filename=f"gezellig_{int(time.time())}.mp4",
                        brand="glow"
                    )
                    
                    send_video(chat_id, video_path, caption=f"✨ Otonom Gezellig Wellness!\n\nSenaryo: {data['dutch_script']}")
                    
                    # Send Instagram Posting Kit (Copy-Paste friendly)
                    posting_kit = (
                        f"📝 **INSTAGRAM POSTING KIT**\n\n"
                        f"**Titel:** {data.get('title', 'Wellness Tip')}\n\n"
                        f"**Caption:**\n{data.get('instagram_caption', 'Ontdek wellness tips bij @GlowUpNL!')}\n\n"
                        f"**Tags:**\n`{data.get('hashtags', '#wellness #gezellig #glowup')}`"
                    )
                    send_message(chat_id, posting_kit)
                except Exception as e:
                    send_message(chat_id, f"❌ Otonom üretim hatası: {e}")
            
            threading.Thread(target=run_otonom, daemon=True).start()

        elif text.startswith("/gezellig_set"):
            # Otonom NL Wellness BULK SET Production
            parts = text.split()
            count = 3 # Default
            if len(parts) > 1 and parts[1].isdigit():
                count = int(parts[1])
            
            def run_bulk_otonom():
                try:
                    from autonomous_producer import run_production_line
                    from src.skills.video_skill import create_reel
                    import time
                    
                    send_message(chat_id, f"🔋 {count}'lü otonom 'Gezellig' set üretimi başlatıldı. GPT senaryoları sıraya koyuyor...")
                    
                    for i in range(count):
                        send_message(chat_id, f"🔄 Set Üretimi: {i+1}/{count} hazırlanıyor...")
                        pack = run_production_line() # Random wellness tip
                        if not pack: continue
                        
                        data = pack["gpt_data"]
                        
                        from src.skills.ai_client import generate_image
                        bg_path = generate_image(data['image_prompt'])
                        
                        video_path = create_reel(
                            fragments=pack["fragments"],
                            image_path=bg_path,
                            output_filename=f"gezellig_set_{i+1}_{int(time.time())}.mp4",
                            brand="glow"
                        )
                        send_video(chat_id, video_path, caption=f"✨ Set Parçası {i+1}/{count} hazır!\n\nSenaryo: {data['dutch_script']}")
                    
                    send_message(chat_id, f"✅ {count}'lü Gezellig Wellness seti başarıyla tamamlandı!")
                except Exception as e:
                    send_message(chat_id, f"❌ Bulk üretim hatası: {e}")
            
            threading.Thread(target=run_bulk_otonom, daemon=True).start()

        elif text.startswith("/video"):
            topic = text.replace("/video", "").strip() or "Wellness"
            threading.Thread(target=_generate_and_send_video, args=(chat_id, topic, "holisti")).start()
            if not topic:
                send_message(chat_id,
                    "🎬 Video olusturma:\n\n"
                    "Kullanimi:\n"
                    "/video <konu>\n\n"
                    "Ornek:\n"
                    "/video stres ve beyin sagliği\n"
                    "/video sabah rutini ipuclari\n"
                    "/video Happy Juice faydalari"
                )
            else:
                send_message(chat_id,
                    f"🎬 Video hazirlaniyor: '{topic}'\n"
                    "Script + ses + video olusturuluyor... (2-3 dk)"
                )
                t = threading.Thread(target=_generate_and_send_video, args=(chat_id, topic), daemon=True)
                t.start()

        elif text.startswith("/canva"):
            task = text.replace("/canva", "").strip()
            if not task:
                send_message(chat_id,
                    "🎨 Canva ontwerpen:\n\n"
                    "/canva auth — account koppelen\n\n"
                    "📸 Afbeeldingen:\n"
                    "/canva instagram <titel>\n"
                    "/canva story <titel>\n"
                    "/canva linkedin <titel>\n"
                    "/canva facebook <titel>\n"
                    "/canva flyer <titel>\n"
                    "/canva poster <titel>\n\n"
                    "🎬 Video:\n"
                    "/canva reels <titel>\n"
                    "/canva tiktok <titel>\n"
                    "/canva youtube <titel>\n\n"
                    "📤 Exporteren:\n"
                    "/canva export <design_id>"
                )
            else:
                is_export = task.startswith("export")
                wait_msg = "📤 Exporteren en downloaden... (kan 30-90 seconden duren)" if is_export else "🎨 Canva bezig..."
                send_message(chat_id, wait_msg)
                if _use_new_system:
                    try:
                        response = _new_handler.handle(text, chat_id=chat_id)
                        _send_canva_response(chat_id, response)
                    except Exception as _err:
                        send_message(chat_id, f"❌ Canva fout: {_err}")
                else:
                    send_message(chat_id, "❌ Canva agent niet beschikbaar.")

        elif text.startswith("/email"):
            task = text.replace("/email", "").strip()
            if not task:
                send_message(chat_id,
                    "❗ Voorbeeldgebruik:\n\n"
                    "/email 5-daagse nurture reeks voor nieuwe leads\n"
                    "/email Happy Juice introductie mail\n"
                    "/email welkomstmail voor nieuwe zakenpartner\n"
                    "/email follow-up mail voor niet-reagerende lead"
                )
            else:
                send_message(chat_id, "📧 Email wordt geschreven... (kan 30 seconden duren)")
                if _use_new_system:
                    try:
                        response = _new_handler.handle(text, chat_id=chat_id)
                        print(f"[Phase6] /email handled by new system")
                        send_message(chat_id, f"✉️ Email:\n{response}")
                    except Exception as _err:
                        print(f"[Phase6] New system error for /email — fallback: {_err}")
                        response = run_email(task)
                        send_message(chat_id, f"✉️ Email:\n{response}")
                else:
                    response = run_email(task)
                    send_message(chat_id, f"✉️ Email:\n{response}")
 
        elif text.startswith("/content"):
            task = text.replace("/content", "").strip()
            if not task:
                send_message(chat_id,
                    "❗ Voorbeeldgebruik:\n\n"
                    "/content Reels script voor drukke moeders over Happy Juice\n"
                    "/content Instagram carousel over MentaBiotics\n"
                    "/content Story reeks over energie tips\n"
                    "/content Caption voor foto met Happy Juice"
                )
            else:
                send_message(chat_id, "✍️ Content wordt gegenereerd... (kan 30 seconden duren)")
                if _use_new_system:
                    try:
                        response = _new_handler.handle(text, chat_id=chat_id)
                        print(f"[Phase5] /content handled by new system")
                        send_message(chat_id, f"📱 Content:\n{response}")
                    except Exception as _err:
                        print(f"[Phase5] New system error for /content — fallback: {_err}")
                        response = run_content(task)
                        send_message(chat_id, f"📱 Content:\n{response}")
                else:
                    response = run_content(task)
                    send_message(chat_id, f"📱 Content:\n{response}")

        elif text.startswith("/sales"):
            task = text.replace("/sales", "").strip()
            if not task:
                send_message(chat_id,
                    "❗ Voorbeeldgebruik:\n\n"
                    "/sales DM script voor drukke moeders\n"
                    "/sales closing bericht voor Happy Juice\n"
                    "/sales bezwaar: te duur"
                )
            else:
                send_message(chat_id, "💬 Sales script wordt geschreven... (kan 30 seconden duren)")
                if _use_new_system:
                    try:
                        response = _new_handler.handle(text, chat_id=chat_id)
                        print(f"[Phase5] /sales handled by new system")
                        send_message(chat_id, f"💬 Sales:\n{response}")
                    except Exception as _err:
                        print(f"[Phase5] New system error for /sales: {_err}")
                        send_message(chat_id, f"❌ Sales agent tijdelijk niet beschikbaar: {_err}")
                else:
                    send_message(chat_id, "❌ Sales agent niet beschikbaar (nieuw systeem niet geladen)")

        elif text.startswith("/research"):
            task = text.replace("/research", "").strip()
            if not task:
                send_message(chat_id,
                    "❗ Voorbeeldgebruik:\n\n"
                    "/research wellness markt Nederland trends\n"
                    "/research concurrent analyse Amare\n"
                    "/research doelgroep pijnpunten moeders"
                )
            else:
                send_message(chat_id, "🔍 Marktonderzoek bezig... (kan 30 seconden duren)")
                if _use_new_system:
                    try:
                        response = _new_handler.handle(text, chat_id=chat_id)
                        print(f"[Phase5] /research handled by new system")
                        send_message(chat_id, f"📊 Research:\n{response}")
                    except Exception as _err:
                        print(f"[Phase5] New system error for /research: {_err}")
                        send_message(chat_id, f"❌ Research agent tijdelijk niet beschikbaar: {_err}")
                else:
                    send_message(chat_id, "❌ Research agent niet beschikbaar (nieuw systeem niet geladen)")
 
        elif text.startswith("/idea"):
            send_message(chat_id, "🔥 Aan het denken...")
            response = run_cmo("Genereer een viraal video idee")
            send_message(chat_id, f"💡 Video Idee:\n{response}")
 
        elif text.startswith("/seo"):
            send_message(chat_id, "🔍 SEO analyse bezig...")
            response = run_cmo("Genereer SEO titel en tags voor YouTube")
            send_message(chat_id, f"📋 SEO:\n{response}")
 
        elif text.startswith("/script"):
            send_message(chat_id, "📝 Script schrijven...")
            response = run_cmo("Schrijf een kort video script")
            send_message(chat_id, f"🎬 Script:\n{response}")
 
        elif text.startswith("/hunt"):
            send_message(chat_id, "🔍 Hollanda wellness pazarı taranıyor, trendler güncelleniyor...")
            import hunt_trends
            if hunt_trends.hunt_trends():
                send_message(chat_id, "✅ Pazar trendleri başarıyla güncellendi! Bir sonraki videonuz bu taze bilgilerle üretilecek.")
            else:
                send_message(chat_id, "⚠️ Trendler güncellenirken bir hata oluştu.")

        elif text.startswith("/cmo"):
            task = text.replace("/cmo", "").strip()
            if not task:
                send_message(chat_id, "❗ Voorbeeld: /cmo Stel lead systeem op voor Nederland")
            else:
                send_message(chat_id, "🟣 CMO aan het denken... (kan 30 seconden duren)")
                if _use_new_system:
                    try:
                        response = _new_handler.handle(text, chat_id=chat_id)
                        print(f"[Phase3] /cmo handled by new system")
                        send_message(chat_id, f"🏢 CMO:\n{response}")
                    except Exception as _err:
                        print(f"[Phase3] New system error for /cmo — fallback: {_err}")
                        response = run_cmo(task)
                        send_message(chat_id, f"🏢 CMO:\n{response}")
                else:
                    response = run_cmo(task)
                    send_message(chat_id, f"🏢 CMO:\n{response}")
 
        elif text.startswith("/linkedin"):
            task = text.replace("/linkedin", "").strip()
            if not task:
                send_message(chat_id,
                    "❗ Voorbeeldgebruik:\n\n"
                    "/linkedin connectie bericht voor drukke moeders\n"
                    "/linkedin follow-up bericht na connectie\n"
                    "/linkedin waardebericht over Happy Juice\n"
                    "/linkedin zacht aanbod bericht"
                )
            else:
                send_message(chat_id, "🔗 LinkedIn bericht wordt voorbereid... (kan 30 seconden duren)")
                if _use_new_system:
                    try:
                        response = _new_handler.handle(text, chat_id=chat_id)
                        print(f"[Phase6] /linkedin handled by new system")
                        send_message(chat_id, f"💼 LinkedIn:\n{response}")
                    except Exception as _err:
                        print(f"[Phase6] New system error for /linkedin — fallback: {_err}")
                        response = run_linkedin(task)
                        send_message(chat_id, f"💼 LinkedIn:\n{response}")
                else:
                    response = run_linkedin(task)
                    send_message(chat_id, f"💼 LinkedIn:\n{response}")
 
        else:
            send_message(chat_id, f"Je schreef: {text}")
 
    except Exception as e:
        print(f"Verwerkingsfout: {e}")
        send_message(chat_id, f"❌ Fout: {e}")
 
def handle_command(chat_id, text):
    """Start commando verwerking in aparte thread"""
    thread = threading.Thread(target=process_command, args=(chat_id, text))
    thread.daemon = True
    thread.start()
 
def _start_canva_callback_server():
    """Start Flask OAuth callback server in background thread."""
    if not _flask_available:
        print("[Canva] Flask niet beschikbaar — OAuth callback server niet gestart.")
        return
    if not _use_new_system:
        print("[Canva] Nieuw systeem niet geladen — OAuth callback server niet gestart.")
        return

    from src.memory.memory_manager import MemoryManager
    from src.skills import canva_client

    app = Flask(__name__)

    @app.route("/canva/callback")
    def canva_callback():
        code = flask_request.args.get("code")
        state = flask_request.args.get("state")
        error = flask_request.args.get("error")

        if not state:
            # Fallback for the main admin user if redirect drops the state params
            print("[Canva callback] State was missing from request, defaulting to 812914122")
            state = "812914122"

        if error or not code:
            debug_info = f"<br><small>URL: {flask_request.url}<br>Args: {dict(flask_request.args)}</small>"
            return f"<h2>❌ Canva koppeling mislukt: {error or 'Geen auth code ontvangen'}</h2>{debug_info}", 400

        try:
            chat_id = int(state)
            mem = MemoryManager(namespace="canva_tokens")

            # Retrieve PKCE verifier from SQLite (stored by canva_agent._auth)
            code_verifier = mem.load(f"pkce_{chat_id}")
            print(f"[Canva callback] state={state!r} sqlite_found={bool(code_verifier)}")
            print(f"[Canva callback] All DB keys: {mem.all_keys()}")

            # Fallback: read from temp file if SQLite missed it
            if not code_verifier:
                import tempfile, pathlib
                _pkce_file = pathlib.Path(tempfile.gettempdir()) / f"canva_pkce_{chat_id}.tmp"
                print(f"[Canva callback] Trying temp file: {_pkce_file}")
                if _pkce_file.exists():
                    code_verifier = _pkce_file.read_text().strip()
                    print(f"[Canva callback] Verifier found in temp file!")

            if not code_verifier:
                return f"<h2>❌ PKCE verifier niet gevonden. Gebruik /canva auth opnieuw.</h2><small>DB keys: {mem.all_keys()}</small>", 400

            tokens = canva_client.exchange_code(code, code_verifier)

            mem.save("access_token", tokens["access_token"], chat_id=chat_id)
            if tokens.get("refresh_token"):
                mem.save("refresh_token", tokens["refresh_token"], chat_id=chat_id)
            # Clean up verifier after use
            mem.delete(f"pkce_{chat_id}")

            send_message(chat_id,
                "✅ Canva-account succesvol gekoppeld!\n\n"
                "Je kunt nu ontwerpen maken:\n"
                "/canva instagram <titel>\n"
                "/canva story <titel>\n"
                "/canva linkedin <titel>"
            )
            return "<h2>✅ Canva gekoppeld! Je kunt dit venster sluiten en terugkeren naar Telegram.</h2>"
        except Exception as e:
            print(f"[Canva callback] Fout: {e}")
            return f"<h2>❌ Fout bij koppelen: {e}</h2>", 500

    @app.route("/health")
    def health():
        return "OK"

    port = int(os.getenv("PORT", 8080))
    print(f"[Canva] OAuth callback server gestart op poort {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def main():
    """Hoofdloop voor Telegram bot"""
    print("🤖 Bot actief... Wacht op Telegram berichten.")
    last_update_id = None
 
    while True:
        try:
            updates = get_updates(last_update_id)
 
            for update in updates.get("result", []):
                last_update_id = update["update_id"] + 1

                # Handle callback queries (Inline Buttons)
                if "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    data = cb["data"]
                    
                    # Brand Selection Callback
                    if data.startswith("brand_"):
                        # brand_glow_video_topic
                        parts = data.split("_")
                        brand = parts[1] # glow or holisti
                        type = parts[2] # video or post
                        topic = "_".join(parts[3:]) if len(parts) > 3 else ""
                        
                        send_message(chat_id, f"📝 Marka: @{brand.capitalize()}NL | Tür: {type.upper()}\nPlanlama yapılıyor...")
                        
                        if type == "video":
                            # Trigger trend-aware production
                            threading.Thread(target=_run_agency_video, args=(chat_id, brand, topic), daemon=True).start()
                        elif type == "post":
                             threading.Thread(target=_run_agency_post, args=(chat_id, brand, topic), daemon=True).start()
                        
                        safe_request(f"{URL}/answerCallbackQuery", method="post", data={"callback_query_id": cb["id"]})
                        continue

                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"]["text"]
                    print("Ontvangen bericht:", text)
                    process_command(chat_id, text)
 
            time.sleep(1)
 
        except ConnectionError as e:
            print(f"🔴 Verbinding verloren: {e}")
            time.sleep(15)
        except Exception as e:
            print(f"🔴 Onverwachte fout: {e}")
            time.sleep(10)
 
if __name__ == "__main__":
    try:
        from src.config.settings import Settings
        Settings.validate()
    except ValueError as _ve:
        print(f"[STARTUP ERROR] {_ve}")
        sys.exit(1)

    # Start Canva OAuth callback server in background thread
    _canva_thread = threading.Thread(target=_start_canva_callback_server, daemon=True)
    _canva_thread.start()

    main()