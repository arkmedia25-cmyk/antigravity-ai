#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os, json, subprocess, requests, re
from dotenv import load_dotenv

load_dotenv(r"c:\Users\mus-1\OneDrive\Bureaublad\Antigravity\.env")

OPENAI_KEY    = os.getenv("OPENAI_API_KEY")
PEXELS_KEY    = os.getenv("PEXELS_API_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
OUTPUT_DIR    = r"c:\Users\mus-1\OneDrive\Bureaublad\Antigravity\outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1080, 1920
TOPIC  = "werkstress"
SCRIPT = (
    "73 procent van de Nederlanders ervaart dagelijks werkstress. "
    "Je lichaam maakt dan tot twee keer zoveel cortisol aan als normaal. "
    "Dit verhoogt je risico op burn-out met 60 procent. "
    "Maar drie minuten ademhaling per dag reset je zenuwstelsel volledig. "
    "Sla dit op en probeer het vanavond."
)

HOOK_L1  = "73% VAN DE"
HOOK_L2  = "NEDERLANDERS"
HOOK_L3  = "HEEFT WERKSTRESS"
HOOK_SUB = "Wetenschappelijk aangetoond"

font_bold = r"C:\Windows\Fonts\arialbd.ttf"
font_med  = r"C:\Windows\Fonts\arial.ttf"
fb = font_bold.replace('\\', '/').replace(':', '\\:')
fm = font_med.replace('\\', '/').replace(':', '\\:')
GREEN = "#829678"
DARK  = "#282C2D"
AD = 220
AX = (W - AD) // 2
AY = H - AD - 80
seg_dur = 4.0

# ── STAP 1: Claude analyseert het onderwerp ──────────────────────────────────
print("\n[1/4] Claude: Gorsel strateji belirleniyor (werkstress)...")
import anthropic
claude = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

prompt = f"""Je bent een visual director voor Instagram Reels wellness content.

Onderwerp: "{TOPIC}"
Script: "{SCRIPT}"

Geef voor PRECIES 4 visuele momenten de beste beelden:
- source: "pexels" als het een realistische foto kan zijn, anders "dalle"
- pexels_query: Engels, max 3 woorden
- dalle_prompt: Engels, 25 woorden max, filmisch fotorealistisch

ANTWOORD alleen in JSON:
{{"visuals":[
  {{"moment":1,"source":"pexels","pexels_query":"...","dalle_prompt":"..."}},
  {{"moment":2,"source":"dalle","pexels_query":"","dalle_prompt":"..."}},
  {{"moment":3,"source":"pexels","pexels_query":"...","dalle_prompt":"..."}},
  {{"moment":4,"source":"pexels","pexels_query":"...","dalle_prompt":"..."}}
]}}"""

resp = claude.messages.create(
    model="claude-haiku-4-5-20251001", max_tokens=600,
    messages=[{"role": "user", "content": prompt}]
)
raw = resp.content[0].text.strip()
match = re.search(r'\{.*\}', raw, re.DOTALL)
analysis = json.loads(match.group(0)) if match else {"visuals": []}
visuals = analysis.get("visuals", [])

for v in visuals:
    src = v.get("source","?")
    q   = v.get("pexels_query") or v.get("dalle_prompt","")[:50]
    print(f"  [{src.upper()}] Moment {v.get('moment')}: {q}")

# ── STAP 2: Afbeeldingen ophalen ─────────────────────────────────────────────
print("\n[2/4] Gorseller indiriliyor...")

def pexels_search(query, n=8):
    url = f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page={n}&orientation=portrait"
    r = requests.get(url, headers={"Authorization": PEXELS_KEY}, timeout=15)
    if r.status_code != 200: return []
    return [p["src"]["large2x"] for p in r.json().get("photos", [])]

def download(url, path):
    r = requests.get(url, timeout=30, stream=True)
    if r.status_code == 200:
        with open(path, "wb") as f:
            for c in r.iter_content(8192): f.write(c)
        return True
    return False

def dalle(prompt, path):
    import openai
    client = openai.OpenAI(api_key=OPENAI_KEY)
    resp = client.images.generate(
        model="dall-e-3",
        prompt=prompt + " Vertical portrait 9:16, cinematic lighting, photorealistic.",
        size="1024x1792", quality="standard", n=1
    )
    return download(resp.data[0].url, path)

image_paths = []
for i, v in enumerate(visuals[:4]):
    path = os.path.join(OUTPUT_DIR, f"stress_visual_{i+1}.jpg")
    source = v.get("source", "dalle")
    ok = False

    if source == "pexels":
        query = v.get("pexels_query", TOPIC)
        print(f"  [Pexels] '{query}' aranıyor...")
        urls = pexels_search(query)
        if len(urls) >= 3:
            ok = download(urls[min(i, len(urls)-1)], path)
            if ok: print(f"  [Pexels] Indirildi")
        if not ok:
            print(f"  [Pexels] Yetersiz → DALL-E 3")
            source = "dalle"

    if source == "dalle":
        dp = v.get("dalle_prompt", f"wellness {TOPIC} concept")
        print(f"  [DALL-E 3] '{dp[:55]}...'")
        ok = dalle(dp, path)
        if ok: print(f"  [DALL-E 3] Uretildi")

    if ok:
        image_paths.append(path)

print(f"\n  {len(image_paths)} gorsel hazir")

# ── STAP 3: FFmpeg compose ────────────────────────────────────────────────────
print("\n[3/4] Video render ediliyor...")

subtitles = [
    "Je cortisol stijgt 2x bij werkstress",
    "Burn-out risico verhoogt met 60 procent",
    "3 minuten ademhaling reset je zenuwstelsel",
    "Sla op en probeer het vanavond!"
]

output_mp4  = os.path.join(OUTPUT_DIR, "demo_stress_v1.mp4")
seg_list    = os.path.join(OUTPUT_DIR, "stress_seg_list.txt")
clips = []

circle_f = (
    f"color=c={GREEN}:s={AD}x{AD}:r=30,format=rgba[av_raw]"
    f";[av_raw]geq=r='r(X,Y)':a='255*lt(hypot(X-{AD//2},Y-{AD//2}),{AD//2})'[av_circle]"
)
ring_f = (
    f"color=c=white@0.0:s={W}x{H}:r=30,format=rgba[rb]"
    f";[rb]geq=r='255':g='255':b='255'"
    f":a='255*gt(hypot(X-{AX+AD//2},Y-{AY+AD//2}),{AD//2})*lt(hypot(X-{AX+AD//2},Y-{AY+AD//2}),{AD//2+6})'[ring]"
)
wm = f"[vring]drawtext=fontfile='{fm}':text='@HolistiGlow':fontcolor=white@0.75:fontsize=28:x=w-text_w-30:y=40[out]"

for idx, img_path in enumerate(image_paths):
    clip_out = os.path.join(OUTPUT_DIR, f"stress_clip_{idx}.mp4")
    img_ff   = img_path.replace('\\', '/').replace(':', '\\:')
    sub      = (subtitles[idx] if idx < len(subtitles) else "").replace("'", "\u2019")
    is_hook  = (idx == 0)

    zoom = (
        f"movie='{img_ff}'"
        f",scale=1920:3413:flags=lanczos"
        f",crop={W}:{H}:(iw-{W})/2:(ih-{H})/2"
        f",zoompan=z='zoom+0.0005':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(seg_dur*30)}:s={W}x{H}:fps=30"
        f"[bg]"
    )

    if is_hook:
        fc = ";".join([
            zoom,
            f"color=c=black@0.65:s={W}x{H}:r=30,format=rgba[dk]",
            f"[bg][dk]overlay=0:0[v1]",
            f"[v1]drawbox=x=80:y=620:w=920:h=6:color={GREEN}@1.0:t=fill[v2]",
            f"[v2]drawtext=fontfile='{fb}':text='{HOOK_L1}':fontcolor=white:fontsize=88:x=(w-text_w)/2:y=648:shadowcolor=black@0.6:shadowx=3:shadowy=3[v3]",
            f"[v3]drawtext=fontfile='{fb}':text='{HOOK_L2}':fontcolor=white:fontsize=88:x=(w-text_w)/2:y=788:shadowcolor=black@0.6:shadowx=3:shadowy=3[v4]",
            f"[v4]drawtext=fontfile='{fb}':text='{HOOK_L3}':fontcolor={GREEN}:fontsize=68:x=(w-text_w)/2:y=928:shadowcolor=black@0.7:shadowx=3:shadowy=3[v5]",
            f"[v5]drawbox=x=80:y=1040:w=920:h=6:color={GREEN}@1.0:t=fill[v6]",
            f"[v6]drawtext=fontfile='{fm}':text='{HOOK_SUB}':fontcolor=white@0.85:fontsize=32:x=(w-text_w)/2:y=1062[v7]",
            circle_f,
            f"[v7][av_circle]overlay={AX}:{AY}[vav]",
            ring_f,
            f"[vav][ring]overlay=0:0[vring]",
            wm,
        ])
    else:
        fc = ";".join([
            zoom,
            f"color=c=black@0.48:s={W}x{H}:r=30,format=rgba[dk]",
            f"[bg][dk]overlay=0:0[v1]",
            f"[v1]drawbox=x=50:y={AY-170}:w=980:h=130:color=white@0.85:t=fill[v2]",
            f"[v2]drawtext=fontfile='{fb}':text='{sub}':fontcolor={DARK}:fontsize=36:x=(w-text_w)/2:y={AY-148}:shadowcolor=black@0.05:shadowx=1:shadowy=1[v3]",
            circle_f,
            f"[v3][av_circle]overlay={AX}:{AY}[vav]",
            ring_f,
            f"[vav][ring]overlay=0:0[vring]",
            wm,
        ])

    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-filter_complex", fc,
        "-map", "[out]", "-map", "0:a",
        "-t", str(seg_dur),
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", clip_out
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        clips.append(clip_out)
        print(f"  Klip {idx+1}/{len(image_paths)} hazir [{'HOOK' if is_hook else 'icerik'}]")
    else:
        print(f"  Klip {idx+1} HATA:\n{r.stderr[-300:]}")

print("\n[4/4] Birlestiriliyor...")
if clips:
    with open(seg_list, "w") as f:
        for c in clips: f.write(f"file '{c.replace(chr(92), '/')}'\n")
    r2 = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", seg_list,
        "-c:v", "copy", "-c:a", "copy", output_mp4
    ], capture_output=True, text=True)
    if r2.returncode == 0:
        size = os.path.getsize(output_mp4) / 1024 / 1024
        print(f"\nDEMO HAZIR: {output_mp4} ({size:.1f} MB)")
    else:
        print(f"Concat HATA:\n{r2.stderr[-300:]}")
