#!/usr/bin/env python3
"""
Wellness Video Producer — Dr. Priya Pipeline
Akis: Claude script → ElevenLabs ses → HeyGen video → Telegram
"""

import os
import sys
import json
import time
import re
import requests
from dotenv import load_dotenv

# --- Path Fix for src imports ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) # scripts/automation
_PROJECT_ROOT = os.path.dirname(os.path.dirname(PROJECT_ROOT)) # actual project root

if _PROJECT_ROOT not in sys.path:
    sys.path.append(_PROJECT_ROOT)

load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

from src.skills.ai_client import ask_ai
from src.skills.content_engine_utils import content_engine
from src.skills.cache_service import cache_service
from src.skills.video_service import video_service

# ─── AYARLAR ──────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT    = os.getenv("TELEGRAM_CHAT_ID", "812914122")
HEYGEN_API_KEY   = os.getenv("HEYGEN_API_KEY")
HEYGEN_AVATAR_ID = os.getenv("HEYGEN_AVATAR_ID", "b261b5094cb44fd28ab47db80e41a8a6")
EL_API_KEY       = os.getenv("ELEVENLABS_API_KEY")
EL_VOICE_ID      = os.getenv("ELEVENLABS_VOICE_ID", "bH1SkJMbYirLovnne9JM")

# AI client is now centralized via ask_ai
# claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PEXELS_KEY = os.getenv("PEXELS_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# ─── SCRIPT ───────────────────────────────────────────────────────────────────

def generate_script(topic: str, hook: str) -> str:
    raw_prompt = f"""Maak een krachtig Instagram Reels script van 60 seconden voor dit wellness onderwerp.

Onderwerp: "{topic}"
Hook: "{hook}"

REGELS:
- Zin 1 (hook, eerste 3-4 seconden): Begin met een schokkend feit of statistiek.
- Daarna: vloeiende wetenschappelijke uitleg, geen opsommingen.
- Nederlands. Ongeveer 130-150 woorden.
- Laatste zin (CTA): Een sterke afsluiting.

Geef ALLEEN de spreektekst terug, geen uitleg."""

    full_prompt = content_engine.inject_rules(raw_prompt, "instagram")
    response_text = ask_ai(full_prompt, provider="anthropic", use_cache=True)
    return response_text.strip()


def generate_visual_plan(topic: str, script: str) -> list:
    """Claude determines the best visuals for the script segments."""
    prompt = f"""Je bent een visual director voor HolistiGlow Instagram Reels.
Onderwerp: "{topic}"
Script: "{script}"

Verdeel het script in 5 logische scenes en geef voor elke scene:
1. De tekst die op dat moment wordt uitgesproken.
2. Een zoekterm voor Pexels (Engels, realistisch, max 3 woorden).
3. Beslis: "pexels" (voor echte foto's) of "dalle" (voor abstracte/wetenschappelijke concepten).
4. Een DALL-E 3 prompt (Engels, cinematic, photorealistic, 25 woorden max).

ANTWOORD ALLEEN IN DIT JSON FORMAAT:
{{"scenes": [
  {{"text": "...", "source": "pexels", "query": "...", "dalle": "..."}},
  ...
]}}"""

    response_text = ask_ai(prompt, provider="anthropic", use_cache=True)
    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        return json.loads(match.group(0)).get("scenes", [])
    except:
        return []


def fetch_visuals(scenes: list) -> list:
    """Fetches images from Pexels or DALL-E 3 based on the plan."""
    import openai
    oa_client = openai.OpenAI(api_key=OPENAI_KEY)
    
    final_visuals = []
    output_dir = os.path.join(os.environ.get("TEMP", "/tmp"), "visuals")
    os.makedirs(output_dir, exist_ok=True)

    for i, sc in enumerate(scenes):
        v_path = os.path.join(output_dir, f"scene_{i}.jpg")
        success = False
        
        if sc["source"] == "pexels":
            print(f"  [PEXELS] Zoeken naar: {sc['query']}")
            p_url = f"https://api.pexels.com/v1/search?query={requests.utils.quote(sc['query'])}&per_page=5&orientation=portrait"
            r = requests.get(p_url, headers={"Authorization": PEXELS_KEY}, timeout=15)
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    img_url = photos[0]["src"]["large2x"]
                    img_data = requests.get(img_url).content
                    with open(v_path, "wb") as f: f.write(img_data)
                    success = True
        
        if not success: # DALL-E fallback or direct
            print(f"  [DALL-E] Genereren scene {i}: {sc['dalle'][:50]}...")
            try:
                d_resp = oa_client.images.generate(
                    model="dall-e-3",
                    prompt=sc["dalle"] + " Cinematic portrait 9:16, high quality, photorealistic, no text.",
                    size="1024x1792", quality="standard", n=1
                )
                img_data = requests.get(d_resp.data[0].url).content
                with open(v_path, "wb") as f: f.write(img_data)
                success = True
            except Exception as e:
                print(f"  [DALL-E] Fout: {e}")

        if success:
            sc["image_path"] = v_path
            final_visuals.append(sc)
    
    return final_visuals


def generate_metadata(topic: str, script: str) -> dict:
    prompt = f"""Je bent een social media expert gespecialiseerd in virale wellness content voor Nederland.

Onderwerp: "{topic}"
Script: "{script}"

Genereer viral metadata voor YouTube/Instagram/TikTok. Geef EXACT dit formaat terug:

TITEL: [pakkende virale titel max 60 tekens, volledig in het Nederlands, met getal of vraag indien mogelijk — schrijf de VOLLEDIGE titel op één regel, niet afkappen]
DESCRIPTION: [2-3 zinnen beschrijving, call-to-action aan het einde, Nederlands]
TAGS: [15-20 relevante hashtags, mix van groot en niche, geen #, komma-gescheiden]

⚠️ REGELS: Gebruik GEEN Engelse tijdsnotatie (3pm, 2pm, 5pm). Schrijf '15:00' of 'drie uur' etc."""

    # Metadata is a simple task, we can use a cheaper model (auto-selected by ask_ai as gpt-4o-mini)
    text = ask_ai(prompt, provider="openai", use_cache=True)

    meta = {"titel": "", "description": "", "tags": ""}
    for line in text.splitlines():
        if line.startswith("TITEL:"):
            meta["titel"] = line.replace("TITEL:", "").strip()
        elif line.startswith("DESCRIPTION:"):
            meta["description"] = line.replace("DESCRIPTION:", "").strip()
        elif line.startswith("TAGS:"):
            meta["tags"] = line.replace("TAGS:", "").strip()
    return meta


# ─── SCRIPT CLEANING ──────────────────────────────────────────────────────────

def clean_script_for_tts(text: str) -> str:
    """Removes headers, emojis, and bracketed metadata for a clean voiceover."""
    # Remove lines starting with common headers
    headers = ["TITEL:", "TITLE:", "DESCRIPTION:", "TAGS:", "TOPIC:", "HOOK:", "CTA:", "SCENE:", "SCRIPT:"]
    lines = text.splitlines()
    clean_lines = []
    
    for line in lines:
        upper_line = line.strip().upper()
        if any(upper_line.startswith(h) for h in headers):
            continue
        # Remove anything like "Dr. Priya — Dag 7/30" or similar
        if "DR. PRIYA" in upper_line and ("DAG" in upper_line or "DAY" in upper_line):
            continue
        clean_lines.append(line)
    
    text = "\n".join(clean_lines)
    
    # Remove everything inside square brackets [SCENE 1] etc.
    text = re.sub(r'\[.*?\]', '', text)
    
    # Remove emojis
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Remove redundant whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# ─── ELEVENLABS TTS ───────────────────────────────────────────────────────────

def generate_voice(text: str) -> str:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{EL_VOICE_ID}"
    headers = {
        "xi-api-key": EL_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.3,
            "use_speaker_boost": True
        }
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        # FALLBACK: Use OpenAI TTS if ElevenLabs fails
        print(f"[ALERT] ElevenLabs hatasi ({resp.status_code}). OpenAI TTS'e geciliyor...")
        try:
            # Local import and initialization to avoid NameError
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            fallback_client = OpenAI(api_key=api_key)
            o_resp = fallback_client.audio.speech.create(
                model="tts-1",
                voice="nova", # Professional & warm voice
                input=text
            )
            audio_path = os.path.join(os.environ.get("TEMP", "/tmp"), f"priya_voice_{int(time.time())}.mp3")
            o_resp.stream_to_file(audio_path)
            print(f"  [TTS-FALLBACK] Ses OpenAI ile uretildi: {audio_path}")
            return audio_path
        except Exception as oe:
            raise Exception(f"Hem ElevenLabs hem OpenAI TTS basarisiz: {oe}")

    audio_path = os.path.join(os.environ.get("TEMP", "/tmp"), f"priya_voice_{int(time.time())}.mp3")
    with open(audio_path, "wb") as f:
        f.write(resp.content)
    print(f"  [TTS] Ses kaydedildi: {audio_path} ({len(resp.content)/1024:.1f} KB)")
    return audio_path


# ─── HEYGEN VIDEO ─────────────────────────────────────────────────────────────

def create_heygen_video(script: str, audio_path: str) -> str:
    # Sesi HeyGen'e yukle
    upload_url = "https://upload.heygen.com/v1/asset"
    with open(audio_path, "rb") as f:
        upload_resp = requests.post(
            upload_url,
            headers={
                "X-Api-Key": HEYGEN_API_KEY,
                "Content-Type": "audio/mpeg"
            },
            data=f,
            timeout=60
        )

    if upload_resp.status_code != 200:
        raise Exception(f"HeyGen upload hata: {upload_resp.status_code} — {upload_resp.text[:200]}")

    asset_id = upload_resp.json().get("data", {}).get("id")
    print(f"  [HEYGEN] Ses yuklendi, asset_id: {asset_id}")

    # Video olustur — kare format, deformasyon yok
    video_payload = {
        "video_inputs": [{
            "character": {
                "type": "talking_photo",
                "talking_photo_id": HEYGEN_AVATAR_ID,
                "scale": 1.0
            },
            "voice": {
                "type": "audio",
                "audio_asset_id": asset_id
            },
            "background": {
                "type": "color",
                "value": "#F4FAF6"
            }
        }],
        "dimension": {"width": 1080, "height": 1080},
        "aspect_ratio": "1:1"
    }

    create_resp = requests.post(
        "https://api.heygen.com/v2/video/generate",
        headers={
            "X-Api-Key": HEYGEN_API_KEY,
            "Content-Type": "application/json"
        },
        json=video_payload,
        timeout=60
    )

    if create_resp.status_code != 200:
        raise Exception(f"HeyGen video hata: {create_resp.text[:200]}")

    video_id = create_resp.json().get("data", {}).get("video_id")
    print(f"  [HEYGEN] Video olusturuluyor, video_id: {video_id}")
    return video_id


def wait_for_video(video_id: str, timeout: int = 900) -> str:
    url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    headers = {"X-Api-Key": HEYGEN_API_KEY}
    start = time.time()

    while time.time() - start < timeout:
        resp = requests.get(url, headers=headers, timeout=30)
        data = resp.json().get("data", {})
        status = data.get("status")
        print(f"  [HEYGEN] Durum: {status}")

        if status == "completed":
            return data.get("video_url")
        elif status == "failed":
            raise Exception(f"HeyGen video basarisiz: {data}")

        time.sleep(10)

    raise Exception(f"HeyGen timeout — {timeout // 60} dakika asildi")


def download_video(video_url: str, notify=None) -> str:
    if notify: notify("📥 Video indiriliyor...")
    output_path = os.path.join(os.environ.get("TEMP", "/tmp"), f"drpriya_{int(time.time())}.mp4")
    resp = requests.get(video_url, timeout=120, stream=True)
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"  [VIDEO] Indirildi: {output_path} ({size_mb:.1f} MB)")
    return output_path


# ─── FFMPEG COMPOSE ──────────────────────────────────────────────────────────

def get_duration(video_path: str) -> float:
    import subprocess
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", video_path],
        capture_output=True, text=True
    )
    return float(r.stdout.strip())


def _esc(text: str) -> str:
    """Escape text for FFmpeg drawtext filter."""
    text = text.replace('\\', '\\\\')
    text = text.replace("'", "\u2019")   # typographic apostrophe — safe in drawtext
    text = text.replace(':', '\\:')
    text = text.replace('%', '\\%')
    text = text.replace('[', '\\[').replace(']', '\\]')
    text = text.replace(',', '\\,')
    return text


def _fpath(path: str) -> str:
    """Convert any path to FFmpeg-safe font path (handles Windows drive letters)."""
    path = path.replace('\\', '/')
    if len(path) >= 2 and path[1] == ':':
        path = path[0] + '\\:' + path[2:]
    return path


def _wrap(text: str, max_chars: int = 38) -> list:
    """Split text into lines of max_chars for subtitle overlay (max 2 lines)."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if len(test) <= max_chars:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:2]


def send_to_telegram(video_path: str, baslik: str, gun_no: int, script: str, meta: dict = None, chat_id: str = None):
    target_chat = chat_id or TELEGRAM_CHAT
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"

    if meta:
        tags_fmt = " ".join(f"#{t.strip()}" for t in meta["tags"].split(",") if t.strip())
        caption = (
            f"🎬 <b>Dr. Priya — Dag {gun_no}/30</b>\n\n"
            f"🔥 <b>{meta['titel']}</b>\n\n"
            f"📝 {meta['description']}\n\n"
            f"🏷 <code>{tags_fmt}</code>\n\n"
            f"Controleer en publiceer! 🌿"
        )
    else:
        caption = (
            f"🎬 <b>Dr. Priya — Dag {gun_no}/30</b>\n\n"
            f"📹 {baslik}\n\n"
            f"📝 <i>{script[:100]}...</i>\n\n"
            f"Controleer en publiceer! 🌿"
        )

    # video_id: dosya adindan cikar (reel_final_1234567890.mp4 → 1234567890)
    vid = os.path.splitext(os.path.basename(video_path))[0].split("_")[-1]

    # Videoyu public static klasore kopyala → direkt indirilebilir URL
    import shutil
    static_dir = os.path.join(PROJECT_ROOT, "static")
    os.makedirs(static_dir, exist_ok=True)

    static_name = f"reel_{vid}.mp4"
    static_path = os.path.join(static_dir, static_name)
    shutil.copy2(video_path, static_path)
    
    # Sunucu urlsini sadece eger Linux ise boyle yap, yoksa yerel kullan
    import platform
    if platform.system() == "Linux":
        download_url = f"https://arkmediaflow.com/media/{static_name}"
    else:
        # For Windows/local, use a dummy or skip public link
        download_url = f"https://static.arkmediaflow.com/media/{static_name}"

    # Metadata kaydet → bot_handler.py Make.com'a gonderirken kullanir
    if meta:
        meta_path = os.path.join(static_dir, f"meta_{vid}.json")
        with open(meta_path, "w") as mf:
            json.dump({**meta, "video_url": download_url, "baslik": baslik}, mf, ensure_ascii=False)

    reply_markup = json.dumps({
        "inline_keyboard": [
            [
                {"text": "Download", "url": download_url},
                {"text": "Re-Edit", "callback_data": f"redo_{vid}"}
            ],
            [
                {"text": "Post to Instagram", "callback_data": f"instagram_{vid}"},
                {"text": "Post to TikTok",    "callback_data": f"tiktok_{vid}"}
            ]
        ]
    })

    # --- Phase 4: Pro Video Enhancement (VideoDB) ---
    if os.getenv("VIDEO_DB_API_KEY"):
        print("\n[FLEET] Phase 4: VideoDB ile profesyonel duzenleme basliyor...")
        try:
            # 1. Upload
            v_obj = video_service.upload_video(video_path)
            if v_obj:
                # 2. Reframe & Subtitles
                print("[ACTION] Video dikey formata cevriliyor ve altyazi ekleniyor...")
                # We do subtitles first, then reframe
                subbed_url = video_service.add_subtitles(v_obj.id)
                final_url = video_service.reframe_to_vertical(v_obj.id)
                
                if final_url:
                    print(f"[DONE] Profesyonel Video Hazir: {final_url}")
                    # notify(context, f"🎬 VideoDB Pro Video Hazır!\n\n🔗 Link: {final_url}", chat_id)
        except Exception as e:
            print(f"[ALERT] VideoDB duzenleme hatasi (devam ediliyor): {e}")

    # --- Send as Video (Visual) ---
    with open(video_path, "rb") as f:
        resp = requests.post(
            url,
            data={
                "chat_id":      target_chat,
                "caption":      caption,
                "parse_mode":   "HTML",
                "reply_markup": reply_markup
            },
            files={"video": ("drpriya.mp4", f, "video/mp4")},
            timeout=120
        )
    
    # --- Also Send as Document (For easy PC download on Windows) ---
    doc_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    with open(video_path, "rb") as f:
        requests.post(
            doc_url,
            data={
                "chat_id":    target_chat,
                "caption":    "⬇️ Download-versie (Hoge kwaliteit for PC)",
            },
            files={"document": (os.path.basename(video_path), f)},
            timeout=120
        )
    if resp.status_code == 200:
        print(f"  [TELEGRAM] Gonderildi [OK] (vid={vid})")
    else:
        print(f"  [TELEGRAM] Hata: {resp.status_code} — {resp.text[:200]}")


# ─── ANA ──────────────────────────────────────────────────────────────────────

def compose_reel(avatar_path: str, scenes: list, baslik: str, audio_path: str) -> str:
    """
    HolistiGlow Native Layout v2 (1080x1920):
    ─ Arka Plan : Hibrit gorseller (Ken Burns) — sahneye gore gecis
    ─ Dr. Priya : Buyuk dairesel overlay (alt-orta)
    ─ Altyazı   : 2-satir wrapped, glassmorphism kutu
    ─ Hook      : Ilk 4sn — buyuk bold tipografi
    ─ Gradient  : Alt kisim karanlik vignette (okunabilirlik)
    """
    import subprocess

    out_final = os.path.join(PROJECT_ROOT, "outputs", f"reel_final_{int(time.time())}.mp4")
    os.makedirs(os.path.join(PROJECT_ROOT, "outputs"), exist_ok=True)

    # Anchoring duration specifically to the audio file if possible
    total_dur = get_duration(audio_path)
    if total_dur <= 0:
        total_dur = get_duration(avatar_path)
    
    num_scenes = max(len(scenes), 1)
    scene_dur  = total_dur / num_scenes

    # ── Fonts ────────────────────────────────────────────────────────────────
    font_bold_raw = os.path.join(PROJECT_ROOT, "assets", "fonts", "PlayfairDisplay-Bold.ttf")
    font_med_raw  = os.path.join(PROJECT_ROOT, "assets", "fonts", "Montserrat-Medium.ttf")
    font_reg_raw  = os.path.join(PROJECT_ROOT, "assets", "fonts", "Montserrat-Regular.ttf")

    import platform
    if not os.path.exists(font_bold_raw):
        if platform.system() == "Windows":
            font_bold_raw = "C:/Windows/Fonts/arialbd.ttf"
            font_med_raw  = "C:/Windows/Fonts/arialbd.ttf"
            font_reg_raw  = "C:/Windows/Fonts/arial.ttf"
        else:
            font_bold_raw = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            font_med_raw  = font_bold_raw
            font_reg_raw  = font_bold_raw

    fb = _fpath(font_bold_raw)
    fm = _fpath(font_med_raw)
    fr = _fpath(font_reg_raw)

    # ── Layout constants ─────────────────────────────────────────────────────
    GREEN  = "#829678"
    CREAM  = "#FDF6EE"
    DARK   = "#1A1A1A"
    W, H   = 1080, 1920
    AD     = 320          # Avatar diameter (larger)
    AX     = (W - AD) // 2
    AY     = H - AD - 60  # Avatar Y position

    # Subtitle box sits above avatar
    SUB_BOX_H  = 210      # tall enough for 2 lines
    SUB_BOX_Y  = AY - SUB_BOX_H - 24
    SUB_L1_Y   = SUB_BOX_Y + 28
    SUB_L2_Y   = SUB_BOX_Y + 112

    # ── Build FFmpeg inputs ───────────────────────────────────────────────────
    # Use -loop 1 + -framerate 30 so images generate frames at 30fps
    # Check if avatar_path is an image (fallback)
    is_image = avatar_path.lower().endswith(('.jpg', '.jpeg', '.png'))
    
    # Build FFmpeg command. Input 0 = Avatar, Input 1+ = Scenes, Last = Audio
    cmd = ["ffmpeg", "-y"]
    
    # Input 0: Avatar
    if is_image:
        cmd += ["-loop", "1", "-framerate", "30", "-t", str(total_dur), "-i", avatar_path]
    else:
        cmd += ["-i", avatar_path]
        
    # Inputs 1+: Scenes
    for sc in scenes:
        cmd.extend(["-loop", "1", "-framerate", "30", "-i", sc.get("image_path", "")])
        
    # Last Input: Audio
    audio_idx = 1 + len(scenes)
    cmd.extend(["-i", audio_path])

    filters = []

    # ── 1. Ken Burns backgrounds (scale+crop pan — FAST, no zoompan) ─────────
    # Pan directions alternate per scene for visual variety
    pan_xy = [
        (f"(iw-ow)*(t/{scene_dur:.4f})", f"(ih-oh)*0.3"),   # pan right
        (f"(iw-ow)*0.3",                  f"(ih-oh)*(t/{scene_dur:.4f})"),  # pan down
        (f"(iw-ow)*(1-t/{scene_dur:.4f})",f"(ih-oh)*0.7"),  # pan left
        (f"(iw-ow)*0.7",                  f"(ih-oh)*(1-t/{scene_dur:.4f})"), # pan up
        (f"(iw-ow)*0.5",                  f"(ih-oh)*0.5"),   # center
    ]

    for i in range(num_scenes):
        dur = scene_dur if i < num_scenes - 1 else (total_dur - i * scene_dur)
        idx = i + 1 # Avatar=0, Scenes start at 1
        px, py = pan_xy[i % len(pan_xy)]
        # Scale to 110% of output, then crop with pan expression
        filters.append(
            f"[{idx}:v]scale=1188:2112:flags=lanczos,setsar=1"
            f",fps=30,crop={W}:{H}:'{px}':'{py}'"
            f",trim=duration={dur:.4f},setpts=PTS-STARTPTS[bg{i}]"
        )

    bg_inputs = "".join(f"[bg{i}]" for i in range(num_scenes))
    filters.append(f"{bg_inputs}concat=n={num_scenes}:v=1:a=0[full_bg]")

    # ── 2. Bottom dark gradient for readability ───────────────────────────────
    filters.append(
        f"[full_bg]drawbox=x=0:y={H//2}:w={W}:h={H//2}:color=black@0.55:t=fill[dark_bg]"
    )

    # ── 3. Avatar (Simple Rect for speed) ───────────────────────────────────
    filters.append(f"[0:v]scale={AD}:{AD},format=rgba[avatar_simple]")
    filters.append(f"[dark_bg][avatar_simple]overlay={AX}:{AY}[base_video]")

    # ── 4. Hook (first 4s) ────────────────────────────────────────────────────
    current_v = "[base_video]"
    hook_end  = min(4.5, scene_dur)

    words  = baslik.split()
    mid    = max(1, len(words) // 2)
    h_l1   = _esc(" ".join(words[:mid]).upper())
    h_l2   = _esc(" ".join(words[mid:]).upper())

    filters.append(
        # Accent bar top
        f"{current_v}drawbox=x=90:y=580:w=900:h=5:color={GREEN}@1.0:t=fill:enable='between(t,0,{hook_end})'[vh1]"
    )
    filters.append(
        f"[vh1]drawtext=fontfile='{fb}':text='{h_l1}'"
        f":fontcolor={CREAM}:fontsize=96:x=(w-text_w)/2:y=600"
        f":shadowcolor=black@0.7:shadowx=4:shadowy=4:enable='between(t,0,{hook_end})'[vh2]"
    )
    filters.append(
        f"[vh2]drawtext=fontfile='{fb}':text='{h_l2}'"
        f":fontcolor={GREEN}:fontsize=72:x=(w-text_w)/2:y=726"
        f":shadowcolor=black@0.5:shadowx=3:shadowy=3:enable='between(t,0,{hook_end})'[vh3]"
    )
    # Accent bar bottom
    filters.append(
        f"[vh3]drawbox=x=90:y=830:w=900:h=5:color={GREEN}@1.0:t=fill:enable='between(t,0,{hook_end})'[v_hooked]"
    )
    current_v = "[v_hooked]"

    # ── 5. Subtitles — wrapped 2-line glassmorphism ───────────────────────────
    for i, sc in enumerate(scenes):
        t_start = i * scene_dur
        t_end   = (i + 1) * scene_dur if i < num_scenes - 1 else total_dur
        if i == 0:
            t_start = max(t_start, hook_end)

        lines = _wrap(_esc(sc.get("text", "")), max_chars=36)
        l1 = lines[0] if len(lines) > 0 else ""
        l2 = lines[1] if len(lines) > 1 else ""

        en = f"between(t,{t_start:.4f},{t_end:.4f})"
        vtag = f"[vsub{i}]"

        # Semi-transparent frosted box
        filters.append(
            f"{current_v}drawbox=x=40:y={SUB_BOX_Y}:w={W-80}:h={SUB_BOX_H}"
            f":color=black@0.55:t=fill:enable='{en}'[vbox{i}]"
        )
        # Left accent stripe
        filters.append(
            f"[vbox{i}]drawbox=x=40:y={SUB_BOX_Y}:w=6:h={SUB_BOX_H}"
            f":color={GREEN}@1.0:t=fill:enable='{en}'[vstripe{i}]"
        )
        # Line 1
        filters.append(
            f"[vstripe{i}]drawtext=fontfile='{fm}':text='{l1}'"
            f":fontcolor=white:fontsize=44:x=(w-text_w)/2:y={SUB_L1_Y}"
            f":enable='{en}'[vl1_{i}]"
        )
        # Line 2 (empty if only 1 line)
        filters.append(
            f"[vl1_{i}]drawtext=fontfile='{fr}':text='{l2}'"
            f":fontcolor=white@0.85:fontsize=40:x=(w-text_w)/2:y={SUB_L2_Y}"
            f":enable='{en}'{vtag}"
        )
        current_v = vtag

    # ── 6. Brand watermark (top-right) ────────────────────────────────────────
    filters.append(
        f"{current_v}drawtext=fontfile='{fm}':text='@HolistiGlow'"
        f":fontcolor=white@0.80:fontsize=32:x=w-text_w-36:y=44"
        f":shadowcolor=black@0.5:shadowx=2:shadowy=2[vbrand]"
    )

    # ── 7. SAR fix (square pixels) ───────────────────────────────────────────
    filters.append("[vbrand]setsar=1[out]")

    cmd.extend(["-filter_complex", ";".join(filters)])
    cmd.extend(["-map", "[out]", "-map", f"{audio_idx}:a"])
    cmd.extend(["-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", "-pix_fmt", "yuv420p"])
    cmd.extend(["-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"])
    cmd.append(out_final)

    print(f"  [FFMPEG] Render basliyor (Sure: {total_dur:.1f}s)...")
    # Avoid deadlock by not capturing huge stderr logs into a pipe
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode != 0:
        print(f"  [FFMPEG] Hata (Kod {res.returncode})")
        return avatar_path

    # ── 8. Music Mix ─────────────────────────────────────────────────────────
    music_path = os.path.join(PROJECT_ROOT, "assets", "music", "background_holisti.mp3")
    if os.path.exists(music_path):
        out_music = out_final.replace(".mp4", "_music.mp4")
        mix_cmd = [
            "ffmpeg", "-y", "-i", out_final, "-i", music_path,
            "-filter_complex",
            "[1:a]volume=0.12,aloop=loop=-1:size=2e+09[bg];[0:a][bg]amix=inputs=2:duration=first[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out_music
        ]
        r2 = subprocess.run(mix_cmd, capture_output=True)
        if r2.returncode == 0:
            return out_music

    return out_final


def main(topic: str, hook: str, baslik: str, gun_no: int = 1, chat_id: str = None):
    def notify(msg):
        if not chat_id: return
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": f"⏳ {msg}"}, timeout=10)
        except: pass

    print(f"\n[1/6] Script uretiliyor...")
    notify("1/6: Senaryo ve Meta detayları hazırlanıyor...")
    script = generate_script(topic, hook)
    meta = generate_metadata(topic, script)
    
    print("[2/6] Gorsel plan hazirlaniyor...")
    notify("2/6: Görsel plan oluşturuluyor...")
    scenes = generate_visual_plan(topic, script)
    scenes = fetch_visuals(scenes)
    
    print("[3/6] Seslendirme...")
    notify("3/6: AI Seslendirme yapılıyor (ElevenLabs)...")
    clean_text = clean_script_for_tts(script)
    audio_path = generate_voice(clean_text)
    
    print("[4/6] HeyGen Avatar Video...")
    try:
        notify("4/6: HeyGen Avatar video üretimi başlatıldı...")
        video_id = create_heygen_video(script, audio_path)
        video_url = wait_for_video(video_id)
        video_path = download_video(video_url, notify=notify)
    except Exception as e:
        print(f"[ALERT] HeyGen Hatasi: {e}. Fallback moduna geciliyor (Statik Avatar)...")
        notify("HeyGen kredisi yetersiz veya hata olustu. Statik avatar ve dinamik gorsellerle kurgu devam ediyor...")
        # Fallback: Use static image if exists, else first scene image
        video_path = os.path.join(PROJECT_ROOT, "assets", "images", "avatar_static.jpg")
        if not os.path.exists(video_path) and scenes:
             video_path = scenes[0].get("image_path")
        if not video_path:
             video_path = audio_path # last resort (might still fail FFmpeg but better than None)
    
    # 5. FFmpeg
    reel_path = compose_reel(video_path, scenes, baslik, audio_path)
    
    print("[6/6] Telegrama gonderiliyor...")
    notify("6/6: Video hazır! Dosya yükleniyor...")
    send_to_telegram(reel_path, baslik, gun_no, script, meta, chat_id=chat_id)
    return reel_path


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Kullanim: python3 wellness_producer.py '<topic>' '<hook>' '<baslik>' [gun_no]")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 1)
