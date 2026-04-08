#!/usr/bin/env python3
"""
Wellness Video Producer — Dr. Priya Pipeline
Akış: Claude script → ElevenLabs ses → HeyGen video → Telegram
"""

import os
import sys
import json
import time
import re
import requests
from dotenv import load_dotenv

PROJECT_ROOT = "/root/antigravity-ai"
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

# ─── SCRIPT ───────────────────────────────────────────────────────────────────

def generate_script(topic: str, hook: str) -> str:
    prompt = f"""Maak een krachtig Instagram Reels script van 30 seconden voor dit wellness onderwerp.

Onderwerp: "{topic}"
Hook: "{hook}"

REGELS:
- Zin 1 (hook, eerste 2 seconden): Begin met een schokkend feit of statistiek. Niet met een vraag.
  Voorbeelden: "8 van de 10 mensen doen dit fout..." / "Dit kost je elke dag 2 uur slaap." / "Wetenschappers ontdekten dat 73% van de vrouwen..."
- Daarna: vloeiende wetenschappelijke uitleg, geen opsommingen, geen bullets.
- Maximaal 80 woorden. Nederlands. Begrijpelijk maar onderbouwd.
- Laatste zin (CTA): Eindig met één van deze varianten (wissel af):
  "Sla dit op — je hebt het vanavond nodig."
  "Stuur dit naar iemand die dit moet weten."
  "Bewaar dit voor later en deel het met je vrienden."

Geef ALLEEN de spreektekst terug, geen uitleg."""

    resp = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text.strip()


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

    audio_path = f"/tmp/priya_voice_{int(time.time())}.mp3"
    with open(audio_path, "wb") as f:
        f.write(resp.content)
    print(f"  [TTS] Ses kaydedildi: {audio_path} ({len(resp.content)/1024:.1f} KB)")
    return audio_path


# ─── HEYGEN VIDEO ─────────────────────────────────────────────────────────────

def create_heygen_video(script: str, audio_path: str) -> str:
    # Sesi HeyGen'e yükle
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
    print(f"  [HEYGEN] Ses yüklendi, asset_id: {asset_id}")

    # Video oluştur — kare format, deformasyon yok
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
    print(f"  [HEYGEN] Video oluşturuluyor, video_id: {video_id}")
    return video_id


def wait_for_video(video_id: str, timeout: int = 300) -> str:
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
            raise Exception(f"HeyGen video başarısız: {data}")

        time.sleep(10)

    raise Exception("HeyGen timeout — 5 dakika aşıldı")


def download_video(video_url: str) -> str:
    output_path = f"/tmp/drpriya_{int(time.time())}.mp4"
    resp = requests.get(video_url, timeout=120, stream=True)
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"  [VIDEO] İndirildi: {output_path} ({size_mb:.1f} MB)")
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


def compose_reel(avatar_path: str, script: str, baslik: str) -> str:
    """
    HolistiGlow Premium Reel (1080x1920):
    ─ Zemin: koyu yeşil (#162E20)
    ─ Dr. Priya: 960x960, ortalanmış, mat altın çerçeve
    ─ Üst: HolistiGlow logo + altın çizgi
    ─ Alt: konu başlığı + CTA
    ─ Son 0.8s kırp + fade-out
    ─ End card (4s): logo + Kaydet / Beğen / Abone Ol / Paylaş
    """
    import subprocess

    output_path = f"/tmp/reel_final_{int(time.time())}.mp4"
    duration     = get_duration(avatar_path)
    trim_dur     = duration          # konuşmanın tamamı korunur
    fade_start   = trim_dur - 0.6   # son 0.6s fade → göz kapanma artifactı gizlenir
    endcard_dur  = 6.0   # 6 saniye — mesajlar 2s görünür, sonra fade

    hook_text = baslik[:38]
    logo_text = "HolistiGlow"
    cta_text  = "Sla op · Deel · Abonneer"

    font_bold = "/root/antigravity-ai/assets/fonts/PlayfairDisplay-Bold.ttf"
    font_med  = "/root/antigravity-ai/assets/fonts/Montserrat-Regular.ttf"
    if not os.path.exists(font_bold):
        font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font_med  = font_bold

    def esc(t):
        return t.replace("'", "\u2019").replace(":", "\\:").replace("@", "\\@")

    BG    = "#2A5C45"   # marka yeşili (açık, HolistiGlow primary)
    GOLD  = "#C8A97A"   # mat altın
    WHITE = "white"

    AV_SIZE = 960
    AV_X    = (1080 - AV_SIZE) // 2   # 60
    AV_Y    = 310       # Dr. Priya daha aşağıda → logo ile arası açık
    FR      = 14        # kalın altın çerçeve

    # Layout (1080x1920):
    # y=0   → 265  : Logo alanı
    # y=210 : Altın çizgi
    # y=265 → 310  : Boşluk (45px)
    # y=296 → 1270 : Dr. Priya (altın çerçeve FR=14 dahil: 296..1284)
    # y=1270→ 1330 : Boşluk
    # y=1330→ 1920 : Alt alan (hook + cta)

    fc = (
        # ── MAIN VIDEO ────────────────────────────────────────────────────────
        f"[0:v]trim=duration={trim_dur:.2f},setpts=PTS-STARTPTS,"
        f"crop=iw*0.80:ih*0.90:(iw-iw*0.80)/2:(ih-ih*0.90)/2,"
        f"scale={AV_SIZE}:{AV_SIZE}[priya];"

        f"color=c={BG}:s=1080x1920:r=30:d={trim_dur:.2f}[bg];"
        f"[bg][priya]overlay={AV_X}:{AV_Y}[v1];"

        # Kalın mat altın çerçeve
        f"[v1]drawbox=x={AV_X-FR}:y={AV_Y-FR}:w={AV_SIZE+FR*2}:h={AV_SIZE+FR*2}:"
        f"color={GOLD}@0.9:t={FR}[v2];"

        # Üst logo alanı (AV_Y-FR = 296 → h=296 ile tamamen kapla)
        f"[v2]drawbox=x=0:y=0:w=1080:h={AV_Y-FR}:color={BG}@1.0:t=fill[v3];"
        f"[v3]drawtext=fontfile='{font_bold}':text='{esc(logo_text)}':"
        f"fontcolor={WHITE}:fontsize=62:x=(w-text_w)/2:y=88:"
        f"shadowcolor=black@0.2:shadowx=1:shadowy=1[v4];"
        f"[v4]drawbox=x=80:y=210:w=920:h=3:color={GOLD}@0.85:t=fill[v5];"

        # Alt alan (Dr. Priya'nın altından itibaren)
        f"[v5]drawbox=x=0:y={AV_Y+AV_SIZE+FR+40}:w=1080:h=640:color={BG}@1.0:t=fill[v6];"
        f"[v6]drawtext=fontfile='{font_bold}':text='{esc(hook_text)}':"
        f"fontcolor={WHITE}:fontsize=44:x=(w-text_w)/2:y={AV_Y+AV_SIZE+FR+60}:"
        f"shadowcolor=black@0.2:shadowx=1:shadowy=1[v7];"
        f"[v7]drawbox=x=80:y={AV_Y+AV_SIZE+FR+160}:w=920:h=2:color={GOLD}@0.75:t=fill[v8];"
        f"[v8]drawtext=fontfile='{font_med}':text='{esc(cta_text)}':"
        f"fontcolor={GOLD}:fontsize=30:x=(w-text_w)/2:y={AV_Y+AV_SIZE+FR+195}[v9];"

        # Fade-out
        f"[v9]fade=t=out:st={fade_start:.2f}:d=0.5[main_v];"
        f"[0:a]atrim=duration={trim_dur:.2f},asetpts=PTS-STARTPTS,"
        f"afade=t=out:st={fade_start:.2f}:d=0.5[main_a];"

        # ── END CARD (4 saniye) — Hollandaca ──────────────────────────────────
        f"color=c={BG}:s=1080x1920:r=30:d={endcard_dur}[ec_bg];"

        f"[ec_bg]drawtext=fontfile='{font_bold}':text='{esc(logo_text)}':"
        f"fontcolor={WHITE}:fontsize=90:x=(w-text_w)/2:y=660:"
        f"shadowcolor=black@0.3:shadowx=2:shadowy=2[ec1];"

        f"[ec1]drawbox=x=140:y=810:w=800:h=3:color={GOLD}@0.9:t=fill[ec2];"

        f"[ec2]drawtext=fontfile='{font_bold}':text='Vind ik leuk':"
        f"fontcolor={GOLD}:fontsize=42:x=(w-text_w)/2:y=860[ec3];"

        f"[ec3]drawtext=fontfile='{font_bold}':text='Abonneer':"
        f"fontcolor={WHITE}:fontsize=42:x=(w-text_w)/2:y=940[ec4];"

        f"[ec4]drawtext=fontfile='{font_bold}':text='Deel  &  Sla op':"
        f"fontcolor={GOLD}:fontsize=42:x=(w-text_w)/2:y=1020[ec5];"

        f"[ec5]drawbox=x=140:y=1110:w=800:h=2:color={GOLD}@0.75:t=fill[ec6];"

        f"[ec6]drawtext=fontfile='{font_med}':text='Dagelijkse wellness wetenschap':"
        f"fontcolor={GOLD}@0.85:fontsize=30:x=(w-text_w)/2:y=1150[ec7];"

        f"[ec7]fade=t=in:st=0:d=0.6,fade=t=out:st={endcard_dur-1.2}:d=1.0[end_v];"

        f"[1:a]atrim=duration={endcard_dur},asetpts=PTS-STARTPTS[end_a];"

        f"[main_v][main_a][end_v][end_a]concat=n=2:v=1:a=1[out_v][out_a]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", avatar_path,
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-filter_complex", fc,
        "-map", "[out_v]",
        "-map", "[out_a]",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [FFMPEG] Hata:\n{result.stderr[-600:]}")
        return avatar_path

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"  [FFMPEG] Reel hazır: {output_path} ({size_mb:.1f} MB)")
    return output_path


# ─── TELEGRAM ─────────────────────────────────────────────────────────────────

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

    # video_id: dosya adından çıkar (reel_final_1234567890.mp4 → 1234567890)
    vid = os.path.splitext(os.path.basename(video_path))[0].split("_")[-1]

    # Videoyu public static klasöre kopyala → direkt indirilebilir URL
    import shutil
    static_name = f"reel_{vid}.mp4"
    static_path = f"/opt/n8n/static/{static_name}"
    shutil.copy2(video_path, static_path)
    download_url = f"https://arkmediaflow.com/media/{static_name}"

    # Metadata kaydet → bot_handler.py Make.com'a gönderirken kullanır
    if meta:
        meta_path = f"/opt/n8n/static/meta_{vid}.json"
        with open(meta_path, "w") as mf:
            json.dump({**meta, "video_url": download_url, "baslik": baslik}, mf, ensure_ascii=False)

    reply_markup = json.dumps({
        "inline_keyboard": [
            [
                {"text": "⬇️ İndir",          "url": download_url},
                {"text": "✏️ Tekrar Düzenle", "callback_data": f"redo_{vid}"}
            ],
            [
                {"text": "📸 Instagram'a Gönder", "callback_data": f"instagram_{vid}"},
                {"text": "🎵 TikTok'a Gönder",    "callback_data": f"tiktok_{vid}"}
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
        print(f"  [TELEGRAM] Gönderildi ✅  (vid={vid})")
    else:
        print(f"  [TELEGRAM] Hata: {resp.status_code} — {resp.text[:200]}")


# ─── ANA ──────────────────────────────────────────────────────────────────────

def main(topic: str, hook: str, baslik: str, gun_no: int = 1):
    print(f"\n{'='*55}")
    print(f"  DR. PRIYA PRODUCER — Dag {gun_no}")
    print(f"  Konu: {baslik}")
    print(f"{'='*55}\n")

    print("[1/5] Script + metadata üretiliyor (Claude)...")
    script = generate_script(topic, hook)
    print(f"  Script ({len(script.split())} kelime):\n  {script[:100]}...\n")
    meta = generate_metadata(topic, script)
    print(f"  Titel: {meta['titel']}")
    print(f"  Tags:  {meta['tags'][:80]}...\n")

    print("[2/5] Seslendirme (ElevenLabs — Priya)...")
    audio_path = generate_voice(script)

    print("\n[3/5] HeyGen video oluşturuluyor...")
    video_id = create_heygen_video(script, audio_path)

    print("\n[4/5] Video hazırlanıyor (bekle)...")
    video_url = wait_for_video(video_id)
    video_path = download_video(video_url)

    print("\n[4.5/5] FFmpeg ile reel compose ediliyor...")
    reel_path = compose_reel(video_path, script, baslik)

    print("\n[5/5] Telegram'a gönderiliyor...")
    send_to_telegram(reel_path, baslik, gun_no, script, meta)

    print(f"\n✅ Tamamlandı: {baslik}\n")
    return video_path


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Kullanım: python3 wellness_producer.py '<topic>' '<hook>' '<baslik>' [gun_no]")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 1)
