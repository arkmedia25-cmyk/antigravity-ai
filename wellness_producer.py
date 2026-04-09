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

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from anthropic import Anthropic

# ─── AYARLAR ──────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT    = os.getenv("TELEGRAM_CHAT_ID", "812914122")
HEYGEN_API_KEY   = os.getenv("HEYGEN_API_KEY")
HEYGEN_AVATAR_ID = os.getenv("HEYGEN_AVATAR_ID", "b261b5094cb44fd28ab47db80e41a8a6")
EL_API_KEY       = os.getenv("ELEVENLABS_API_KEY")
EL_VOICE_ID      = os.getenv("ELEVENLABS_VOICE_ID", "bH1SkJMbYirLovnne9JM")

claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PEXELS_KEY = os.getenv("PEXELS_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# ─── SCRIPT ───────────────────────────────────────────────────────────────────

def generate_script(topic: str, hook: str) -> str:
    prompt = f"""Maak een krachtig Instagram Reels script van 60 seconden voor dit wellness onderwerp.

Onderwerp: "{topic}"
Hook: "{hook}"

REGELS:
- Zin 1 (hook, eerste 3-4 seconden): Begin met een schokkend feit of statistiek. Niet met een vraag.
  Voorbeelden: "8 van de 10 mensen doen dit fout..." / "Dit kost je her seferinde 2 uur slaap." / "Wetenschappers ontdekten dat 73% van de vrouwen..."
- Daarna: vloeiende wetenschappelijke uitleg, geen opsommingen, geen bullets.
- Ongeveer 130-150 woorden. Nederlands. Begrijpelijk maar onderbouwd.
- Laatste zin (CTA): Eindig met één van deze varianten (wissel af):
  "Sla dit op — je hebt het vanavond nodig."
  "Stuur dit naar iemand die dit moet weten."
  "Bewaar dit voor later en deel het met je vrienden."

Geef ALLEEN de spreektekst terug, geen uitleg."""

    resp = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text.strip()


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

    resp = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        match = re.search(r'\{.*\}', resp.content[0].text, re.DOTALL)
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
            print(f"  [DALL-E] Genereren: {sc['dalle'][:50]}...")
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

    resp = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip()

    meta = {"titel": "", "description": "", "tags": ""}
    for line in text.splitlines():
        if line.startswith("TITEL:"):
            meta["titel"] = line.replace("TITEL:", "").strip()
        elif line.startswith("DESCRIPTION:"):
            meta["description"] = line.replace("DESCRIPTION:", "").strip()
        elif line.startswith("TAGS:"):
            meta["tags"] = line.replace("TAGS:", "").strip()
    return meta


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
        raise Exception(f"ElevenLabs hata: {resp.status_code} — {resp.text[:200]}")

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


def download_video(video_url: str) -> str:
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


def send_to_telegram(video_path: str, baslik: str, gun_no: int, script: str, meta: dict = None):
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
                {"text": "⬇️ Indir", "url": download_url},
                {"text": "✏️ Tekrar Duzenle", "callback_data": f"redo_{vid}"}
            ],
            [
                {"text": "📸 Instagram'a Gonder", "callback_data": f"instagram_{vid}"},
                {"text": "🎵 TikTok'a Gonder",    "callback_data": f"tiktok_{vid}"}
            ]
        ]
    })

    with open(video_path, "rb") as f:
        resp = requests.post(
            url,
            data={
                "chat_id":      TELEGRAM_CHAT,
                "caption":      caption,
                "parse_mode":   "HTML",
                "reply_markup": reply_markup
            },
            files={"video": ("drpriya.mp4", f, "video/mp4")},
            timeout=120
        )
    if resp.status_code == 200:
        print(f"  [TELEGRAM] Gonderildi [OK] (vid={vid})")
    else:
        print(f"  [TELEGRAM] Hata: {resp.status_code} — {resp.text[:200]}")


# ─── ANA ──────────────────────────────────────────────────────────────────────

def compose_reel(avatar_path: str, scenes: list, baslik: str) -> str:
    """
    HolistiGlow Native Layout (1080x1920):
    ─ Arka Plan: Hibrit gorseller (Ken Burns effect) - Zaman bazlı geçiş
    ─ Dr. Priya: Altta dairesel kesim (circular crop) - Sabit overlay
    ─ Hook & Altyazı: Sahneye göre değişen metinler
    """
    import subprocess

    out_final = os.path.join(PROJECT_ROOT, "outputs", f"reel_final_{int(time.time())}.mp4")
    os.makedirs(os.path.join(PROJECT_ROOT, "outputs"), exist_ok=True)
    
    total_dur = get_duration(avatar_path)
    num_scenes = len(scenes)
    scene_dur = total_dur / num_scenes if num_scenes else total_dur
    
    font_bold = os.path.join(PROJECT_ROOT, "assets", "fonts", "PlayfairDisplay-Bold.ttf")
    font_med  = os.path.join(PROJECT_ROOT, "assets", "fonts", "Montserrat-Regular.ttf")
    
    if not os.path.exists(font_bold):
        import platform
        if platform.system() == "Windows":
            font_bold = "C:/Windows/Fonts/arialbd.ttf"
            font_med  = "C:/Windows/Fonts/arial.ttf"
        else:
            font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            font_med  = font_bold

    GREEN = "#829678"
    DARK  = "#282C2D"
    W, H  = 1080, 1920
    
    # Avatar settings
    AD = 240   # Diameter
    AX = (W - AD) // 2
    AY = H - AD - 100

    # Build FFmpeg command
    # Inputs: [0:v] Avatar, [1:v] Image 0, [2:v] Image 1, ...
    cmd = ["ffmpeg", "-y"]
    cmd.extend(["-i", avatar_path])
    
    for sc in scenes:
        cmd.extend(["-i", sc["image_path"]])
    
    # Filter Complex
    filters = []
    
    # 1. Prepare Background Layers (Ken Burns per scene)
    # We create a full-length background by overlaying scene segments
    for i in range(num_scenes):
        start = i * scene_dur
        # Ensure the last scene covers the remaining time exactly
        end = (i + 1) * scene_dur if i < num_scenes - 1 else total_dur
        dur = end - start
        
        # Ken Burns for this specific scene
        # We use 'zoompan' on the specific input. input index is i+1 (0 is avatar)
        # Note: zoompan s parameter should match output size
        input_idx = i + 1
        filters.append(
            f"[{input_idx}:v]scale=1920:3413:flags=lanczos,crop={W}:{H}:(iw-{W})/2:(ih-{H})/2"
            f",zoompan=z='zoom+0.0005':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(total_dur*30)}:s={W}x{H}:fps=30"
            f",trim=duration={dur},setpts=PTS-STARTPTS[bg{i}]"
        )

    # Concat background segments
    bg_inputs = "".join([f"[bg{i}]" for i in range(num_scenes)])
    filters.append(f"{bg_inputs}concat=n={num_scenes}:v=1:a=0[full_bg]")
    
    # 2. Base Grade (Darken background)
    filters.append(f"[full_bg]drawbox=x=0:y=0:w={W}:h={H}:color=black@0.4:t=fill[dark_bg]")
    
    # 3. Add Dr. Priya Avatar (Circular Crop)
    # We take the avatar once and apply the crop
    filters.append(
        f"[0:v]scale={AD}:{AD},format=rgba"
        f",geq=r='r(X,Y)':a='255*lt(hypot(X-{AD//2},Y-{AD//2}),{AD//2})'[avatar_circle]"
    )
    
    # Avatar Ring
    filters.append(
        f"color=c=white@0.0:s={W}x{H}:r=30,format=rgba"
        f",geq=r='255':g='255':b='255'"
        f":a='255*gt(hypot(X-{AX+AD//2},Y-{AY+AD//2}),{AD//2})*lt(hypot(X-{AX+AD//2},Y-{AY+AD//2}),{AD//2+6})'[ring]"
    )
    
    # Overlay Avatar and Ring on Background
    filters.append(f"[dark_bg][avatar_circle]overlay={AX}:{AY}[with_avatar]")
    filters.append(f"[with_avatar][ring]overlay=0:0[base_video]")
    
    # 4. Text Overlays (Hook and Subtitles)
    current_v = "[base_video]"
    
    # Hook (First scene only)
    h_parts = baslik.split(' ')
    h_l1 = " ".join(h_parts[:3]).upper()[:18]
    h_l2 = " ".join(h_parts[3:]).upper()[:22]
    
    # Proper escaping for FFmpeg text
    h_l1 = h_l1.replace("'", "\u2019").replace(":", "\\:")
    h_l2 = h_l2.replace("'", "\u2019").replace(":", "\\:")
    
    # Apply Hook on first scene duration
    hook_end = min(4.0, scene_dur) # Hook max 4 seconds or first scene length
    filters.append(
        f"{current_v}drawbox=x=80:y=620:w=920:h=6:color={GREEN}@1.0:t=fill:enable='between(t,0,{hook_end})'[v_h1];"
        f"[v_h1]drawtext=fontfile='{font_bold}':text='{h_l1}':fontcolor=white:fontsize=88:x=(w-text_w)/2:y=650"
        f":shadowcolor=black@0.6:shadowx=3:shadowy=3:enable='between(t,0,{hook_end})'[v_h2];"
        f"[v_h2]drawtext=fontfile='{font_bold}':text='{h_l2}':fontcolor={GREEN}:fontsize=68:x=(w-text_w)/2:y=760"
        f":shadowcolor=black@0.6:shadowx=3:shadowy=3:enable='between(t,0,{hook_end})'[v_h3];"
        f"[v_h3]drawbox=x=80:y=860:w=920:h=6:color={GREEN}@1.0:t=fill:enable='between(t,0,{hook_end})'[v_hooked]"
    )
    current_v = "[v_hooked]"
    
    # Subtitles (Scene by scene)
    for i, sc in enumerate(scenes):
        start = i * scene_dur
        end = (i + 1) * scene_dur if i < num_scenes - 1 else total_dur
        # Don't show subtitles during hook if they overlap
        if i == 0 and start < hook_end:
            start = hook_end
            
        sub = sc["text"].replace("'", "\u2019").replace(":", "\\:")
        v_tag = f"[v_sub{i}]"
        filters.append(
            f"{current_v}drawbox=x=50:y={AY-170}:w=980:h=130:color=white@0.85:t=fill:enable='between(t,{start},{end})'[v_b{i}];"
            f"[v_b{i}]drawtext=fontfile='{font_bold}':text='{sub}':fontcolor={DARK}:fontsize=36:x=(w-text_w)/2:y={AY-145}"
            f":shadowcolor=black@0.05:shadowx=1:shadowy=1:enable='between(t,{start},{end})'{v_tag}"
        )
        current_v = v_tag

    # 5. Brand Tag
    filters.append(
        f"{current_v}drawtext=fontfile='{font_med}':text='@HolistiGlow':fontcolor=white@0.7:fontsize=28:x=w-text_w-30:y=40[out]"
    )

    cmd.extend(["-filter_complex", ";".join(filters)])
    cmd.extend(["-map", "[out]", "-map", "0:a"]) # Use original audio from avatar
    cmd.extend(["-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p"])
    cmd.extend(["-c:a", "aac", "-b:a", "192k"]) # High quality audio
    cmd.append(out_final)
    
    print(f"  [FFMPEG] Render basliyor (Süre: {total_dur:.1f}s)...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  [FFMPEG] Hata: {res.stderr[-1000:]}")
        return avatar_path # Fail gracefully to original if render fails

    # Music Mix
    music_path = os.path.join(PROJECT_ROOT, "assets", "music", "background_holisti.mp3")
    if os.path.exists(music_path):
        out_music = out_final.replace(".mp4", "_music.mp4")
        mix_cmd = [
            "ffmpeg", "-y", "-i", out_final, "-i", music_path,
            "-filter_complex", "[1:a]volume=0.15,aloop=loop=-1:size=2e+09[bg];[0:a][bg]amix=inputs=2:duration=first[aout]",
            "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out_music
        ]
        subprocess.run(mix_cmd, capture_output=True)
        return out_music

    return out_final


def main(topic: str, hook: str, baslik: str, gun_no: int = 1):
    print(f"\n[1/6] Script uretiliyor...")
    script = generate_script(topic, hook)
    meta = generate_metadata(topic, script)
    
    print("[2/6] Gorsel plan hazirlaniyor...")
    scenes = generate_visual_plan(topic, script)
    scenes = fetch_visuals(scenes)
    
    print("[3/6] Seslendirme...")
    audio_path = generate_voice(script)
    
    print("[4/6] HeyGen Avatar Video...")
    video_id = create_heygen_video(script, audio_path)
    video_url = wait_for_video(video_id)
    video_path = download_video(video_url)
    
    print("[5/6] FFmpeg Compose...")
    reel_path = compose_reel(video_path, scenes, baslik)
    
    print("[6/6] Telegrama gonderiliyor...")
    send_to_telegram(reel_path, baslik, gun_no, script, meta)
    return reel_path


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Kullanim: python3 wellness_producer.py '<topic>' '<hook>' '<baslik>' [gun_no]")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 1)
