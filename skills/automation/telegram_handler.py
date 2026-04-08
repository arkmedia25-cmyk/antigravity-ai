import time
import requests
import sys
import os
import threading
import re
from dotenv import load_dotenv
from datetime import datetime
import sys as _sys, os as _os
_project_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))
if _project_root not in _sys.path:
    _sys.path.insert(0, _project_root)

# ── ARK AGENTS PATH ──────────────────────────────────────────────────────────
_ark_root = _os.path.join(_project_root, "ark_agents")
# NOT: ark path'leri global sys.path'e eklenmez — handler'lar kendi import'larini yapar

# Önemli: .env dosyasındaki PEXELS_API_KEY gibi yeni anahtarları yükle
load_dotenv(os.path.join(_project_root, ".env"))

try:
    from src.skills.stats_skill import get_instagram_stats, format_stats_dashboard
except ImportError:
    def get_instagram_stats(business_id, access_token): return {"error": "stats_skill not loaded"}
    def format_stats_dashboard(a, b): return "📊 Stats geçici olarak kullanılamıyor."

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

# Legacy agent imports — graceful fallback so bot never crashes on import
try:
    from cmo_agent import run_cmo
except ImportError:
    def run_cmo(task): return "CMO agent niet beschikbaar."

try:
    from linkedin_agent import run_linkedin
except ImportError:
    def run_linkedin(task): return "LinkedIn agent niet beschikbaar."

try:
    from content_agent import run_content
except ImportError:
    def run_content(task): return "Content agent niet beschikbaar."

try:
    from email_agent import run_email
except ImportError:
    def run_email(task): return "Email agent niet beschikbaar."

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
    from skills.publisher_skill import publisher_skill
    from scheduler.content_scheduler import start_content_factory
    from skills.ai_client import ask_ai
    _video_pipeline_ok = True
    print("[Video] Pipeline geladen")
except Exception as _ve:
    _video_pipeline_ok = False
    print(f"[Video] Pipeline niet beschikbaar: {_ve}")
 
TOKEN = os.getenv("TELEGRAM_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

# Gorsel degistirme icin bekleme durumu: {chat_id: {filename, session_path}}
_pending_regen = {}
 
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
            fname = os.path.basename(video_path)
            buttons = [
                [{"text": "🔄 Gorsel Degistir", "callback_data": f"regen_img_{fname}"}],
                [
                    {"text": "💾 Indir", "callback_data": f"dl_doc_{fname}"},
                    {"text": "🚀 Instagram", "callback_data": f"publish_ig_{fname}"},
                    {"text": "TikTok", "callback_data": f"publish_tt_{fname}"},
                ],
            ]
            reply_markup = {"inline_keyboard": buttons}
            
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
        agent_name = "Luna (GLW-01)" if brand == "glow" else "Zen (HLG-01)"
        send_message(chat_id, f"🎬 Ajan {agent_name} göreve başladı!\nKonu: {topic}\nStrateji: {brand.upper()} Manifestosu uygulanıyor...")
        
        brand_rules = (
            "BRAND VOICE [GLOWUP]: High-energy, pushy, result-oriented, zero-fluff. USE words like: Snel, Direct, Pak je winst, Energie. NEVER use: Misschien, Rustig, Balans."
            if brand == "glow" else
            "BRAND VOICE [HOLISTIGLOW]: Calm, wise, motherly, educational, slow-paced. USE words like: Balans, Wijsheid, Rust, Holistisch. NEVER use: Snel, Direct, Nu meteen, Hype."
        )

        prompt = (
            f"=== SQUAD MANIFESTO - ACT AS THIS TEAM ===\n{manifesto}\n\n"
            f"=== {brand_rules} ===\n\n"
            f"Role: Expert Wellness Content Creator. Brand: {brand_label}.\n"
            f"Topic: {topic}\n"
            "CRITICAL: YOUR OUTPUT MUST BE 100% IN DUTCH. NO TURKISH OR ENGLISH WORDS ALLOWED IN TITLE, SCRIPT OR CAPTION.\n"
            "CRITICAL: In the TITLE, write ALL time references in Dutch format (e.g. write '15:00 uur' not '3pm', '3 uur' not '3am').\n"
            "CRITICAL: The TITLE must be fully Dutch — no English words at all. Max 40 characters.\n"
            "GOAL: Create a distinct Instagram package. If GlowUp, be provocative and energetic. If HolistiGlow, be calm and trustworthy.\n"
            "STRUCTURE:\n"
            "1. HOOK (5-8 sec): Curiosity or problem-solving entrance.\n"
            "2. CONTENT (15-20 sec): 2-3 genuinely helpful tips.\n"
            "3. CTA (5 sec): Polite follow invitation.\n\n"
            "PROVIDE THESE 5 PARTS:\n"
            "---BROLL_QUERY---\n[STRICTLY ENGLISH - 1-2 words for an AESTHETIC, BRAND-FREE Pexels search. IMPORTANT: Only use healthy lifestyle terms. NEVER search for brands like Red Bull or Cola. Examples: 'aesthetic smoothie', 'natural energy', 'healthy fruits', 'minimalist gym', 'scandinavian interior']\n"
            "---TITLE---\n[STRICTLY DUTCH - Short, catchy title for the package]\n"
            "---SCRIPT---\n[STRICTLY DUTCH - Voiceover text only]\n"
            "---CAPTION---\n[STRICTLY DUTCH - Engaging Instagram caption]\n"
            "---TAGS---\n[Strategic Hashtags]\n"
        )
        full_response = ask_ai(prompt)
        
        # Parse response
        broll_query = "aesthetic wellness"
        if "---BROLL_QUERY---" in full_response:
            broll_query = full_response.split("---BROLL_QUERY---")[-1].split("---TITLE---")[0].strip().strip('"').strip("'")
            
        title_body = full_response.split("---TITLE---")[-1].split("---SCRIPT---")[0].strip()
        script = full_response.split("---SCRIPT---")[-1].split("---CAPTION---")[0].strip()
        caption_body = full_response.split("---CAPTION---")[-1].split("---TAGS---")[0].strip()
        tags = full_response.split("---TAGS---")[-1].strip()

        if not title_body: title_body = topic  # Fallback

        # Vertaal Engelse tijdsaanduidingen naar Nederlands in de titel
        def _nl_title(t: str) -> str:
            import re as _re
            # "3pm" → "15:00", "3am" → "03:00", "12pm" → "12:00"
            def _pm(m):
                h = int(m.group(1))
                return f"{(h % 12) + 12 if h != 12 else 12}:00"
            def _am(m):
                h = int(m.group(1))
                return f"{h % 12:02d}:00"
            t = _re.sub(r'\b(\d{1,2})\s*pm\b', _pm, t, flags=_re.IGNORECASE)
            t = _re.sub(r'\b(\d{1,2})\s*am\b', _am, t, flags=_re.IGNORECASE)
            # Veelvoorkomende Engelse woorden → Nederlands
            _map = {
                r'\bthe\b': 'de', r'\byour\b': 'jouw', r'\byou\b': 'jij',
                r'\bwhy\b': 'waarom', r'\bhow\b': 'hoe', r'\bwhat\b': 'wat',
                r'\bcrash\b': 'crash', r'\benergy\b': 'energie',
                r'\btips\b': 'tips', r'\bsleep\b': 'slaap',
                r'\bmorning\b': 'ochtend', r'\bevening\b': 'avond',
                r'\bnight\b': 'nacht', r'\bday\b': 'dag',
            }
            for eng, nl in _map.items():
                t = _re.sub(eng, nl, t, flags=_re.IGNORECASE)
            return t.strip()

        title_body = _nl_title(title_body)

        # Stap 2: Fragmented TTS (Zero Delay Mode)
        send_message(chat_id, f"Stap 2/3: {brand_label} seslendirme motoru çalışıyor (Kusursuz Akış & Enerji)...")
        
        # Split script into clean sentences with smart merging for short fragments (e.g. "Tip 1.")
        # Aggressive cleanup of AI technical labels and bullets
        def clean_line(s):
            # Aggressive cleanup of AI technical labels and markers
            # Handle [HOOK], **Hook:**, (Voiceover), etc.
            s = re.sub(r'(?i)\*\*.*?\*\*', '', s) # Strip bold markers
            s = re.sub(r'(?i)[\(\[].*?[\)\]]', '', s) # Strip anything in brackets/parens like [HOOK] or (Voiceover)
            # Strip common labels at start
            s = re.sub(r'(?i)^\s*(hook|content|cta|tip|stap|script|caption|tags|video description|voiceover|audio|scene|visual)\s*[:\-\]]*\s*', '', s).strip()
            # Strip bullet points and numbers
            s = re.sub(r'^\s*[\d]+[\.\)]\s*', '', s).strip()
            s = re.sub(r'^\s*[-•*]\s*', '', s).strip()
            return s.strip()

        raw_parts = re.split(r'(?<=[.!?])\s+', script.strip())
        clean_sentences = []
        temp_s = ""
        for s in raw_parts:
            s_clean = clean_line(s)
            if not s_clean: continue
            
            # If current sentence is too short (e.g. "Tip 1."), buffer it
            if len(s_clean) < 20: 
                temp_s = (temp_s + " " + s_clean).strip()
            else:
                # Merge buffered short text if exists
                full_s = (temp_s + " " + s_clean).strip()
                clean_sentences.append(full_s)
                temp_s = ""
        
        # Add any remaining buffer
        if temp_s:
            if clean_sentences: clean_sentences[-1] = (clean_sentences[-1] + " " + temp_s).strip()
            else: clean_sentences.append(clean_line(temp_s))

        if not clean_sentences:
            clean_sentences = ["Ontdek bugün daha iyi bir versiyonun için GlowUp!"]

        # Watermark Detector (Subtle Dutch Style)
        watermark_map = {
            "stres": "🌿", "rust": "🍃", "slaap": "🌙", "energie": "⚡", 
            "afvallen": "🍎", "gezond": "🥕", "papatya": "🌼", "thee": "🍵",
            "sport": "👟", "succes": "📈", "balans": "⚖️", "mindset": "🧠"
        }
        detected_icon = "✨" # Default
        for key, icon in watermark_map.items():
            if key in topic.lower() or key in script.lower():
                detected_icon = icon
                break

        if not clean_sentences:
            clean_sentences = ["Ontdek vandaag nog je beste zelf bij GlowUp!"]

        # Generate each audio fragment and store metadata
        fragment_data = []
        for i, text in enumerate(clean_sentences):
            f_name = f"audio_frag_{ts}_{i}.mp3"
            f_path = generate_dutch_audio(text, filename=f_name, voice="nova", speed=1.0)
            # Tag metadata for video_skill (0=hook, middle=content, last=cta)
            tag = "hook" if i == 0 else ("cta" if i == len(clean_sentences) - 1 else "content")
            fragment_data.append({"sentence": text, "audio": f_path, "tag": tag})

        # Fetch Pexels Image (Görsel Zeka)
        image_path = None
        pexels_key = os.environ.get("PEXELS_API_KEY", "").strip().strip('"')
        
        if pexels_key and broll_query:
            try:
                import requests
                send_message(chat_id, f"🔍 Luna Pexels'te '{broll_query}' araması başlattı...")
                
                query_url = f"https://api.pexels.com/v1/search"
                # Pexels API Request with strictly human-centric context
                pexels_key = os.getenv("PEXELS_API_KEY")
                # Ensure we search for humans, wellness and aesthetic (no windmills)
                safe_query = f"aesthetic human wellness {broll_query}"
                params = {
                    "query": safe_query,
                    "orientation": "portrait",
                    "per_page": 1
                }
                headers = {
                    "Authorization": pexels_key,
                    "User-Agent": "AntigravityBot/1.0 (Professional Content Creator)"
                }
                
                response = requests.get(query_url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("photos"):
                        img_url = data["photos"][0]["src"]["large2x"]
                        download_path = os.path.join(os.getcwd(), "outputs", f"broll_{ts}.jpg")
                        
                        # Resim indirme
                        img_res = requests.get(img_url, timeout=15)
                        if img_res.status_code == 200:
                            with open(download_path, "wb") as f:
                                f.write(img_res.content)
                            image_path = download_path
                            send_message(chat_id, f"✅ (Visual AI) '{broll_query}' görseli indirildi!")
                        else:
                            send_message(chat_id, "⚠️ (Visual AI) Görsel indirme hatası.")
                    else:
                        send_message(chat_id, f"⚠️ (Visual AI) Pexels sonuç bulamadı.")
                elif response.status_code == 403:
                    send_message(chat_id, "❌ (Visual AI) 403 Forbidden: Hâlâ erişim reddediliyor. Lütfen anahtarın doğruluğunu ve e-posta onayını kontrol et!")
                else:
                    send_message(chat_id, f"❌ (Visual AI) HTTP {response.status_code} Hatası.")
                    
            except Exception as e:
                send_message(chat_id, f"❌ (Visual AI) Sistem Hatası: {str(e)[:50]}")
                print(f"[Pexels Fetch Error] {e}")
        elif not pexels_key:
            send_message(chat_id, "❌ (Visual AI) Kritik Hata: PEXELS_API_KEY sunucu tarafından görülmüyor!")
        elif not broll_query:
             send_message(chat_id, "⚠️ (Visual AI) Arama kelimesi (Query) üretilemedi.")

        # Stap 3: Video renderen
        send_message(chat_id, "Stap 3/3: Video renderen (Sıfır Gecikme, Tam Senkronizasyon)...")
        output_filename = f"reel_{brand}_{ts}.mp4"
        video_path = create_reel(
            fragments=fragment_data,
            image_path=image_path,
            brand=brand,
            output_filename=output_filename,
            watermark_icon=detected_icon
        )

        # Session kaydet (gorsel degistirme icin)
        import json as _json
        session_data = {
            "brand": brand,
            "topic": topic,
            "broll_query": broll_query,
            "caption": caption_body,
            "tags": tags,
            "title": title_body,
            "fragments": [{"sentence": f["sentence"], "audio": f["audio"], "tag": f["tag"]} for f in fragment_data],
        }
        session_path = os.path.join(os.getcwd(), "outputs", f"session_{output_filename}.json")
        with open(session_path, "w", encoding="utf-8") as _sf:
            _json.dump(session_data, _sf, ensure_ascii=False)

        # Verstuur video
        final_caption = f"{brand_label} Video Hazir!\n\nCaption & tags asagida:"
        send_video(chat_id, video_path, caption=final_caption)
        
        # Send Copy-Paste Package (Title, Caption & Tags all in Dutch)
        package = (
            f"📝 **{title_body.upper()}**\n\n"
            f"{caption_body}\n\n"
            f"`{tags}`"
        )
        send_message(chat_id, package)

    except Exception as e:
        print(f"[Video] HATA: {e}")
        send_message(chat_id, f"Video olusturulirken hata: {e}")


def _regen_video_with_query(chat_id, query, regen_info):
    """Yeni Pexels gorseli ile videoyu yeniden render et."""
    import json as _json, requests as _req, time as _time
    try:
        session_path = regen_info["session_path"]
        old_filename = regen_info["filename"]

        with open(session_path, encoding="utf-8") as f:
            sess = _json.load(f)

        brand = sess["brand"]
        fragments = sess["fragments"]
        brand_label = "@GlowUpNL" if brand == "glow" else "@HolistiGlow"

        send_message(chat_id, f"Pexels'te '{query}' aranıyor...")

        # Yeni Pexels gorseli cek
        pexels_key = os.getenv("PEXELS_API_KEY", "").strip()
        new_image_path = None
        if pexels_key:
            try:
                ts = _time.strftime("%Y%m%d_%H%M%S")
                r = _req.get(
                    "https://api.pexels.com/v1/search",
                    headers={"Authorization": pexels_key},
                    params={"query": query, "orientation": "portrait", "per_page": 3, "page": 2},
                    timeout=10
                )
                if r.status_code == 200:
                    photos = r.json().get("photos", [])
                    if photos:
                        img_url = photos[0]["src"]["large2x"]
                        dl = _req.get(img_url, timeout=15)
                        if dl.status_code == 200:
                            new_image_path = os.path.join(os.getcwd(), "outputs", f"broll_regen_{ts}.jpg")
                            with open(new_image_path, "wb") as f:
                                f.write(dl.content)
                            send_message(chat_id, f"Gorsel bulundu! Yeniden render ediliyor...")
            except Exception as e:
                send_message(chat_id, f"Pexels hatası: {e} — varsayılan arka plan kullanılıyor.")

        # Videoyu yeniden render et
        ts = _time.strftime("%Y%m%d_%H%M%S")
        new_filename = f"reel_{brand}_regen_{ts}.mp4"
        new_video_path = create_reel(
            fragments=fragments,
            image_path=new_image_path,
            brand=brand,
            output_filename=new_filename
        )

        # Yeni session kaydet
        sess_new = dict(sess)
        with open(os.path.join(os.getcwd(), "outputs", f"session_{new_filename}.json"), "w", encoding="utf-8") as f:
            _json.dump(sess_new, f, ensure_ascii=False)

        send_video(chat_id, new_video_path, caption=f"{brand_label} — Gorsel Guncellendi!")

    except Exception as e:
        print(f"[regen] HATA: {e}")
        send_message(chat_id, f"Yeniden render hatası: {e}")


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
        "2. 'post': Kullanıcı statik feed görseli/post fazılmasını istiyor.\n"
        "3. 'story': Kullanıcı dikey story/hikaye paylaşımı istiyor.\n"
        "4. 'idea': Kullanıcı içerik fikri istiyor.\n"
        "5. 'research': Kullanıcı pazar/trend araştırması istiyor.\n"
        "6. 'chat': Sadece soru soruyor veya sohbet ediyor.\n\n"
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
        elif action == "story":
            import json
            # Ask which brand for story
            reply_markup = {
                "inline_keyboard": [[
                    {"text": "🔥 @GlowUpNL (Energetic)", "callback_data": f"brand_glow_story_{topic}"},
                    {"text": "🌿 @HolistiGlow (Calm)", "callback_data": f"brand_holisti_story_{topic}"}
                ]]
            }
            send_message_with_markup(chat_id, "Hangi kanal için dikey STORY hazırlayalım?", reply_markup)
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
        
        data = generate_autonomous_content(topic, brand=brand)
        if not data: return

        from src.skills.post_skill import create_static_post
        # Now passing the Dutch script to be drawn on the image
        post_path = create_static_post(brand=brand, topic=topic, description=data.get('dutch_script', ''))
        
        if not post_path: 
            send_message(chat_id, "❌ Post tasarımı üretilirken bir hata oluştu.")
            return
        
        send_document(chat_id, post_path, caption=f"🖼 @{brand.capitalize()}NL Statik Post Hazır!\n\n**İpucu:** Yazı görselin üzerine profesyonelce yerleştirildi! ✨\n\n**Açıklama:**\n{data.get('instagram_caption', '')}")
    except Exception as e:
        print(f"[_run_agency_post] HATA: {e}")
        send_message(chat_id, f"❌ Agency post hatası: {e}")

def _run_agency_story(chat_id, brand, topic):
    """Markaya ozel statik STORY uret."""
    try:
        import hunt_trends
        send_message(chat_id, f"🔍 @{brand.capitalize()}NL için dikey story planlanıyor...")
        hunt_trends.hunt_trends(brand=brand)
        
        from autonomous_producer import generate_autonomous_content
        send_message(chat_id, f"📱 @{brand.capitalize()}NL dikey story tasarımı (9:16) başlatıldı...")
        
        data = generate_autonomous_content(topic, brand=brand)
        if not data: return
        
        from src.skills.post_skill import create_static_story
        # Now passing the Dutch script to be drawn on the image with the sticker
        story_path = create_static_story(brand=brand, topic=topic, description=data.get('dutch_script', ''))
        
        if not story_path: 
            send_message(chat_id, "❌ Story tasarımı üretilirken bir hata oluştu.")
            return
        
        send_document(chat_id, story_path, caption=f"📱 @{brand.capitalize()}NL Story Görseli Hazır!\n\n**İpucu:** Hikayenize 'Link in Bio' çıkartması otomatik olarak eklendi! ✨\n\n**Metin Önerisi:**\n{data.get('dutch_script', '')}")
    except Exception as e:
        print(f"[_run_agency_story] HATA: {e}")
        send_message(chat_id, f"❌ Agency story hatası: {e}")


def process_command(chat_id, text):
    """Verwerk Telegram commando"""
    # NL Router for non-slash messages
    if not text.startswith("/"):
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
            start_content_factory(chat_id)
            send_message(chat_id,
                "Antigravity AI — Klaar!\n\n"
                "VIDEO MAKEN\n"
                "/luna <onderwerp>  — Luna maakt @GlowUpNL Reels (energiek, koraal)\n"
                "/zen <onderwerp>   — Zen maakt @HolistiGlow Reels (rustig, groen)\n\n"
                "Voorbeelden:\n"
                "/luna slaap tips voor meer energie\n"
                "/zen mindfulness ochtend routine\n\n"
                "OVERIGE COMMANDO'S\n"
                "/cmo         — Marketingstrategie advies\n"
                "/research    — Trend & marktanalyse\n"
                "/content     — Instagram / Reels teksten\n"
                "/idea        — Virale video ideeen\n"
                "/stats       — Instagram statistieken\n\n"
                "Of stuur gewoon een bericht — ik begrijp je!\n\n"
                "ARK AGENTS\n"
                "/bora <konu>  — CMO strateji\n"
                "/burak        — NL trend araştırması\n"
                "/duru <konu>  — Script / hook / caption\n"
                "/kaan         — Sistem durumu ve otomasyon"
            )

        elif text.startswith("/luna"):
            topic = text.replace("/luna", "").strip() or "Energie en gezondheid"
            send_message(chat_id, f"Luna (GLW-01) aan het werk voor @GlowUpNL...\nOnderwerp: {topic}")
            threading.Thread(target=_generate_and_send_video, args=(chat_id, topic, "glow"), daemon=True).start()

        elif text.startswith("/zen"):
            topic = text.replace("/zen", "").strip() or "Holistische wellness"
            send_message(chat_id, f"Zen (HLG-01) aan het werk voor @HolistiGlow...\nOnderwerp: {topic}")
            threading.Thread(target=_generate_and_send_video, args=(chat_id, topic, "holisti"), daemon=True).start()

        elif text.startswith("/video_glow"):
            topic = text.replace("/video_glow", "").strip() or "Gezondheid"
            threading.Thread(target=_generate_and_send_video, args=(chat_id, topic, "glow"), daemon=True).start()

        elif text.startswith("/video_holisti"):
            topic = text.replace("/video_holisti", "").strip() or "Wellness"
            threading.Thread(target=_generate_and_send_video, args=(chat_id, topic, "holisti"), daemon=True).start()

        elif text.startswith("/stats"):
            send_message(chat_id, "📊 Veriler çekiliyor, lütfen bekleyin...")
            
            # Get IDs and Tokens from Env
            token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
            id_glow = os.getenv("INSTAGRAM_BUSINESS_ID_GLOW", "")
            id_holisti = os.getenv("INSTAGRAM_BUSINESS_ID_HOLISTI", "")
            
            glow_data = get_instagram_stats(id_glow, token)
            holisti_data = get_instagram_stats(id_holisti, token)
            
            dash = format_stats_dashboard(glow_data, holisti_data)
            send_message(chat_id, dash)

        elif text.startswith("/gezellig"):
            # Otonom NL Wellness (Gezellig Vibe)
            topic = text.replace("/gezellig", "").strip()
            def run_otonom():
                try:
                    from autonomous_producer import run_production_line
                    from src.skills.video_skill import create_reel
                    
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
            clean_text = text.replace("/video", "").strip()
            topic = clean_text or "Wellness"
            
            # Marka algılama
            brand_choice = "holisti" # default
            if "@glowup" in clean_text.lower():
                brand_choice = "glow"
                topic = clean_text.lower().replace("@glowup", "").strip() or "Sabah Rutini"
            elif "@holistiglow" in clean_text.lower():
                brand_choice = "holisti"
                topic = clean_text.lower().replace("@holistiglow", "").strip() or "Wellness"
                
            if not topic:
                send_message(chat_id,
                    "🎬 Video olusturma:\n\n"
                    "Kullanimi:\n"
                    "/video @glowup <konu>\n"
                    "/video @holistiglow <konu>\n"
                )
            else:
                agent_name = "Luna (GLW-01)" if brand_choice == "glow" else "Zen (HLG-01)"
                send_message(chat_id,
                    f"🎬 {agent_name} görevi devraldı.\n"
                    f"Video hazirlaniyor: '{topic}'\n"
                    "Script + ses + video olusturuluyor... (2-3 dk)"
                )
                t = threading.Thread(target=_generate_and_send_video, args=(chat_id, topic, brand_choice), daemon=True)
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
 
        # ── ARK AGENTS (Bora / Burak / Duru / Kaan) ──────────────────────────
        elif text.startswith("/bora"):
            task = text.replace("/bora", "").strip() or "HolistiGlow içerik stratejisi"
            send_message(chat_id, f"🎯 Bora (CMO) düşünüyor...\nKonu: {task}")
            threading.Thread(target=_ark_bora, args=(chat_id, task), daemon=True).start()

        elif text.startswith("/burak"):
            send_message(chat_id, "🔍 Burak (Research) NL trendleri tarıyor... ~30 saniye")
            threading.Thread(target=_ark_burak, args=(chat_id,), daemon=True).start()

        elif text.startswith("/duru"):
            task = text.replace("/duru", "").strip()
            send_message(chat_id, f"✍️ Duru (Content) çalışıyor...")
            threading.Thread(target=_ark_duru, args=(chat_id, task), daemon=True).start()

        elif text.startswith("/kaan"):
            cmd = text.replace("/kaan", "").strip()
            threading.Thread(target=_ark_kaan, args=(chat_id, cmd), daemon=True).start()

        else:
            send_message(chat_id, f"Je schreef: {text}")

    except Exception as e:
        print(f"Verwerkingsfout: {e}")
        send_message(chat_id, f"❌ Fout: {e}")
 
# ── ARK AGENT HANDLERS ───────────────────────────────────────────────────────

def _ark_import(module_name):
    """ark_agents modüllerini çakışma olmadan import eder."""
    import importlib.util
    _agents_path = _os.path.join(_ark_root, "agents")
    _core_path   = _os.path.join(_ark_root, "core")
    # Hangi klasörde arayacağımızı belirle
    for folder in [_agents_path, _core_path]:
        full_path = _os.path.join(folder, f"{module_name}.py")
        if _os.path.exists(full_path):
            # Geçici sys.path ekle, import et, sonra temizle
            if _agents_path not in _sys.path:
                _sys.path.insert(0, _agents_path)
            if _core_path not in _sys.path:
                _sys.path.insert(0, _core_path)
            spec = importlib.util.spec_from_file_location(f"ark_{module_name}", full_path)
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise ImportError(f"ark modülü bulunamadı: {module_name}")


def _ark_bora(chat_id, task):
    try:
        cmo = _ark_import("cmo_agent")
        result = cmo.brainstorm(task)
        send_message(chat_id, f"🎯 <b>Bora (CMO):</b>\n\n{result}")
    except Exception as e:
        send_message(chat_id, f"❌ Bora hatası: {e}")


def _ark_burak(chat_id):
    try:
        research = _ark_import("research_agent")
        plan = research.research_trends()
        research.save_weekly_plan(plan)
        trends = "\n".join(f"• {t}" for t in plan.get("trends", []))
        topics = "\n".join(
            f"<b>Dag {t['dag']}:</b> {t['titel']} → {t['product']}"
            for t in plan.get("aanbevolen_topics", [])
        )
        send_message(chat_id,
            f"🔍 <b>Burak (Research):</b>\n\n"
            f"📊 <b>NL Trendler:</b>\n{trends}\n\n"
            f"🗓 <b>7 Günlük Plan:</b>\n{topics}\n\n"
            f"✅ Onaylamak için: <code>/kaan approve</code>")
    except Exception as e:
        send_message(chat_id, f"❌ Burak hatası: {e}")


def _ark_duru(chat_id, task):
    try:
        duru = _ark_import("aria_agent")
        low = task.lower()
        if "hook" in low:
            result = duru.write_hook(task.replace("hook", "").strip() or "gut-brain wellness")
        elif "caption" in low or "instagram" in low or "tiktok" in low:
            parts = task.split()
            platform = next((p for p in parts if p in ["instagram", "tiktok", "youtube"]), "instagram")
            topic = task.replace("caption", "").replace(platform, "").strip()
            result = duru.write_caption(topic or "gut-brain", "MentaBiotics", platform)
        elif "carousel" in low:
            result = duru.write_carousel(task.replace("carousel", "").strip() or "gut-brain en slaap", "MentaBiotics")
        else:
            result = duru.write_script(task or "gut-brain en energie", "MentaBiotics")
        send_message(chat_id, f"✍️ <b>Duru (Content):</b>\n\n{result}")
    except Exception as e:
        send_message(chat_id, f"❌ Duru hatası: {e}")


def _ark_kaan(chat_id, cmd):
    try:
        atlas = _ark_import("atlas_agent")
        low = cmd.lower().strip()

        if low in ("weekly", "haftalık", "research"):
            send_message(chat_id, "🌐 <b>Kaan — Haftalık döngü başlatılıyor...</b>\n⏳ ~30 saniye")
            result = atlas.run_weekly_cycle()
            plan = result["plan"]
            trends = "\n".join(f"• {t}" for t in plan.get("trends", []))
            topics = "\n".join(
                f"<b>Dag {t['dag']}:</b> {t['titel']} → {t['product']}"
                for t in plan.get("aanbevolen_topics", [])
            )
            send_message(chat_id,
                f"📊 <b>Trendler:</b>\n{trends}\n\n"
                f"🗓 <b>7 Günlük Plan:</b>\n{topics}\n\n"
                f"✅ Onaylamak için: <code>/kaan approve</code>")

        elif low in ("approve", "onayla"):
            result = atlas.approve_plan()
            msg = "✅ <b>Plan onaylandı!</b>" if result["ok"] else f"⚠️ {result['error']}"
            send_message(chat_id, msg)

        elif low in ("today", "bugün"):
            today = atlas.get_today_topic()
            if today:
                send_message(chat_id,
                    f"📌 <b>Bugünün Konusu:</b>\n<b>{today['titel']}</b>\n"
                    f"Hook: <i>{today.get('hook','—')}</i>\nÜrün: {today.get('product','—')}")
            else:
                send_message(chat_id, "⚠️ Onaylı plan yok. Önce <code>/kaan weekly</code>")

        else:
            status = atlas.get_status()
            agents_text = "".join(
                f"{'🟢' if a['active'] else '⚪'} <b>{a['name']}</b>: {a['turns']} konuşma\n"
                for a in status["agents"]
            )
            plan = status["weekly_plan"]
            plan_text = (
                f"✅ Onaylı ({plan['approved_at'][:10] if plan['approved_at'] else '?'})" if plan["approved"]
                else "⏳ Onay bekliyor" if plan["exists"] else "❌ Plan yok"
            )
            kaan_log = "\n".join(f"  • {e[:70]}" for e in status.get("kaan_memory", [])[:3])
            send_message(chat_id,
                f"🌐 <b>Kaan — Sistem Durumu</b>\n\n"
                f"<b>Agent'lar:</b>\n{agents_text}\n"
                f"<b>Haftalık Plan:</b> {plan_text}\n\n"
                f"<b>Son Aktiviteler:</b>\n{kaan_log or '  —'}\n\n"
                f"/kaan weekly — Araştırma\n"
                f"/kaan approve — Planı onayla\n"
                f"/kaan today — Bugünün konusu")
    except Exception as e:
        send_message(chat_id, f"❌ Kaan hatası: {e}")


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

    @app.route("/outputs/<path:filename>")
    def public_outputs(filename):
        """Serves generated videos for social media APIs (Instagram/TikTok needs a public URL)."""
        from flask import send_from_directory
        return send_from_directory(os.path.join(_project_root, "outputs"), filename)

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
                    
                    # Gorsel Degistir Callback
                    if data.startswith("regen_img_"):
                        filename = data.replace("regen_img_", "", 1)
                        session_path = os.path.join(os.getcwd(), "outputs", f"session_{filename}.json")
                        if os.path.exists(session_path):
                            _pending_regen[chat_id] = {"filename": filename, "session_path": session_path}
                            send_message(chat_id,
                                "Hangi gorsel istiyorsunuz?\n\n"
                                "Ornek:\n"
                                "- yoga woman sunrise\n"
                                "- green smoothie healthy\n"
                                "- meditation nature calm\n"
                                "- woman running energy\n\n"
                                "Ingilizce yaz, Pexels'te arayacagim."
                            )
                        else:
                            send_message(chat_id, "Oturum bulunamadi, lutfen yeni video uret.")
                        safe_request(f"{URL}/answerCallbackQuery", method="post", data={"callback_query_id": cb["id"]})
                        continue

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
                        elif type == "story":
                             threading.Thread(target=_run_agency_story, args=(chat_id, brand, topic), daemon=True).start()
                        
                        safe_request(f"{URL}/answerCallbackQuery", method="post", data={"callback_query_id": cb["id"]})
                        continue

                    # Download as Document Callback
                    if data.startswith("dl_doc_"):
                        filename = data.replace("dl_doc_", "", 1)
                        doc_path = os.path.join(os.getcwd(), "outputs", filename)
                        send_document(chat_id, doc_path, caption="📥 Video dosyası indiriliyor...")
                        safe_request(f"{URL}/answerCallbackQuery", method="post", data={"callback_query_id": cb["id"]})
                        continue

                    # Social Media Publishing Callback
                    if data.startswith("publish_"):
                        # publish_ig_filename.mp4
                        parts = data.split("_")
                        platform = parts[1] # ig or tt
                        filename = "_".join(parts[2:])

                        # Extract brand from filename (e.g. agency_glow_123.mp4 → glow)
                        pub_brand = "glow"
                        if "holisti" in filename.lower():
                            pub_brand = "holisti"
                        elif "glow" in filename.lower():
                            pub_brand = "glow"

                        send_message(chat_id, f"⏳ Video yükleniyor, lütfen bekleyin (1-2 dk)...")

                        def _do_publish(filename=filename, platform=platform, pub_brand=pub_brand, chat_id=chat_id):
                            try:
                                import sys
                                sys.path.insert(0, os.path.join(os.getcwd(), "src"))
                                from src.skills.uploader_skill import uploader
                                import requests as _req

                                local_path = os.path.join(os.getcwd(), "outputs", filename)
                                send_message(chat_id, f"📤 catbox.moe'ya yükleniyor...")
                                public_url = uploader.upload_file(local_path)

                                if not public_url:
                                    send_message(chat_id, "❌ Upload hatası: dosya yüklenemedi (catbox.moe)")
                                    return

                                send_message(chat_id, f"🔗 Yüklendi: {public_url}\n🚀 Make.com'a gönderiliyor...")

                                webhook_url = os.getenv("MAKE_WEBHOOK_URL")
                                if not webhook_url:
                                    send_message(chat_id, "❌ MAKE_WEBHOOK_URL .env'de tanımlı değil!")
                                    return

                                brand_map = {"glow": "GlowUpNL", "holisti": "HolistiGlow"}
                                brand_name = brand_map.get(pub_brand, "GlowUpNL")
                                payload = {
                                    "video_url": public_url,
                                    "brand": brand_name,
                                    "platform": platform,
                                    "caption": f"✨ {brand_name} | #wellness #health #tips"
                                }

                                r = _req.post(webhook_url, json=payload, timeout=30)
                                if r.status_code in [200, 202, 204]:
                                    send_message(chat_id, f"✅ Make.com'a gönderildi!\n📱 {platform.upper()} yayını başlıyor...\n\nMake.com cevabı: {r.text[:200]}")
                                else:
                                    send_message(chat_id, f"❌ Make.com hatası: HTTP {r.status_code}\n{r.text[:300]}")
                            except Exception as e:
                                send_message(chat_id, f"❌ Yayın hatası: {e}")

                        threading.Thread(target=_do_publish, daemon=True).start()
                        safe_request(f"{URL}/answerCallbackQuery", method="post", data={"callback_query_id": cb["id"]})
                        continue


                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    
                    # Handle Text Messages
                    if "text" in msg:
                        text = msg["text"]
                        print("Ontvangen bericht:", text)

                        # Gorsel degistirme bekleniyor mu?
                        if chat_id in _pending_regen:
                            regen_info = _pending_regen.pop(chat_id)
                            threading.Thread(
                                target=_regen_video_with_query,
                                args=(chat_id, text.strip(), regen_info),
                                daemon=True
                            ).start()
                        else:
                            process_command(chat_id, text)
                    
                    # Handle Voice Messages (Whisper STT)
                    elif "voice" in msg:
                        voice = msg["voice"]
                        file_id = voice["file_id"]
                        send_message(chat_id, "🎙️ Sesinizi dinliyorum, lütfen bekleyin...")
                        
                        try:
                            # 1. Get file path from Telegram
                            file_info = safe_request(f"{URL}/getFile", params={"file_id": file_id}).json()
                            file_path = file_info["result"]["file_path"]
                            file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
                            
                            # 2. Download the voice file
                            import requests
                            voice_data = requests.get(file_url).content
                            local_voice_path = os.path.join("tmp", f"voice_{int(time.time())}.ogg")
                            os.makedirs("tmp", exist_ok=True)
                            with open(local_voice_path, "wb") as f:
                                f.write(voice_data)
                            
                            # 3. Transcribe via OpenAI Whisper
                            from src.skills.ai_client import transcribe_audio
                            transcript = transcribe_audio(local_voice_path)
                            
                            if transcript:
                                send_message(chat_id, f"📝 Sizi şöyle anladım: \"{transcript}\"")
                                process_command(chat_id, transcript)
                            else:
                                send_message(chat_id, "❌ Sesinizi tam anlayamadım, lütfen tekrar dener misiniz?")
                            
                            # Clean up
                            if os.path.exists(local_voice_path):
                                os.remove(local_voice_path)
                                
                        except Exception as ve:
                            print(f"[Voice] Hata: {ve}")
                            send_message(chat_id, f"❌ Ses işlenirken bir hata oluştu: {ve}")

 
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