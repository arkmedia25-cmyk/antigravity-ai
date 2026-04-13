#!/usr/bin/env python3
"""Test FFmpeg compose without any project imports."""
import subprocess, os, time

avatar = "C:/Users/mus-1/AppData/Local/Temp/drpriya_1775734174.mp4"
vis    = "C:/Users/mus-1/AppData/Local/Temp/visuals"
out    = "D:/OneDrive/Bureaublad/Antigravity/outputs/test_compose_fix.mp4"
W, H   = 1080, 1920
AD     = 320
AX     = (W - AD) // 2
AY     = H - AD - 60
GREEN  = "#829678"

r = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", avatar],
    capture_output=True, text=True
)
total_dur = float(r.stdout.strip())
n = 5
sdur = total_dur / n
print(f"Duration: {total_dur:.1f}s, scene_dur: {sdur:.1f}s")

# Font paths (FFmpeg Windows format)
root = "D:/OneDrive/Bureaublad/Antigravity"
fb = root.replace(":", "\\:") + "/assets/fonts/PlayfairDisplay-Bold.ttf"
fm = root.replace(":", "\\:") + "/assets/fonts/Montserrat-Medium.ttf"
fr = root.replace(":", "\\:") + "/assets/fonts/Montserrat-Regular.ttf"

cmd = ["ffmpeg", "-y", "-i", avatar]
for i in range(n):
    cmd += ["-loop", "1", "-framerate", "30", "-i", f"{vis}/scene_{i}.jpg"]

f = []  # filters list

# 1. Ken Burns via scale+crop pan (FAST — no zoompan)
pan_xy = [
    (f"(iw-ow)*(t/{sdur:.4f})", f"(ih-oh)*0.3"),
    (f"(iw-ow)*0.3",             f"(ih-oh)*(t/{sdur:.4f})"),
    (f"(iw-ow)*(1-t/{sdur:.4f})",f"(ih-oh)*0.7"),
    (f"(iw-ow)*0.7",             f"(ih-oh)*(1-t/{sdur:.4f})"),
    (f"(iw-ow)*0.5",             f"(ih-oh)*0.5"),
]
for i in range(n):
    dur  = sdur if i < n - 1 else total_dur - i * sdur
    px, py = pan_xy[i % len(pan_xy)]
    f.append(
        f"[{i+1}:v]scale=1188:2112:flags=lanczos,setsar=1"
        f",fps=30,crop={W}:{H}:'{px}':'{py}'"
        f",trim=duration={dur:.4f},setpts=PTS-STARTPTS[bg{i}]"
    )

f.append("".join(f"[bg{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[full_bg]")

# 2. Bottom dark gradient
f.append(f"[full_bg]drawbox=x=0:y={H//2}:w={W}:h={H//2}:color=black@0.55:t=fill[dark_bg]")

# 3. Avatar circle + ring
R = AD // 2
CX, CY = AX + R, AY + R
f.append(
    f"[0:v]scale={AD}:{AD},format=rgba"
    f",geq=r='r(X\\,Y)':g='g(X\\,Y)':b='b(X\\,Y)'"
    f":a='255*lt(hypot(X-{R}\\,Y-{R})\\,{R-2})'[av_c]"
)
f.append(
    f"color=c=white@0.0:s={W}x{H}:r=30,format=rgba"
    f",geq=r='130':g='150':b='120'"
    f":a='220*gt(hypot(X-{CX}\\,Y-{CY})\\,{R})*lt(hypot(X-{CX}\\,Y-{CY})\\,{R+8})'[ring]"
)
f.append(f"[dark_bg][av_c]overlay={AX}:{AY}[wa]")
f.append(f"[wa][ring]overlay=0:0[base]")

# 4. Hook (0 - 4.5s)
f.append(f"[base]drawbox=x=90:y=580:w=900:h=5:color={GREEN}@1.0:t=fill:enable='between(t\\,0\\,4.5)'[vh1]")
f.append(
    f"[vh1]drawtext=fontfile='{fb}':text='WERKSTRESS'"
    f":fontcolor=white:fontsize=96:x=(w-text_w)/2:y=600"
    f":shadowcolor=black@0.7:shadowx=4:shadowy=4:enable='between(t\\,0\\,4.5)'[vh2]"
)
f.append(
    f"[vh2]drawtext=fontfile='{fb}':text='DE STILLE EPIDEMIE'"
    f":fontcolor={GREEN}:fontsize=64:x=(w-text_w)/2:y=726"
    f":shadowcolor=black@0.5:shadowx=3:shadowy=3:enable='between(t\\,0\\,4.5)'[vh3]"
)
f.append(f"[vh3]drawbox=x=90:y=830:w=900:h=5:color={GREEN}@1.0:t=fill:enable='between(t\\,0\\,4.5)'[vhooked]")

# 5. Subtitles
SUB_BOX_H = 210
SUB_BOX_Y = AY - SUB_BOX_H - 24
SUB_L1_Y  = SUB_BOX_Y + 28
SUB_L2_Y  = SUB_BOX_Y + 112

subs = [
    ("73% van Nederlanders ervaart werkstress", "Je cortisol stijgt 2x boven normaal"),
    ("Verhoogd risico op burn-out met 60%", ""),
    ("3 minuten ademhaling reset het zenuwstelsel", ""),
    ("Je productiviteit stijgt door beter te herstellen", ""),
    ("Sla dit op en probeer het vanavond", ""),
]

current = "[vhooked]"
for i in range(n):
    ts  = max(i * sdur, 4.5) if i == 0 else i * sdur
    te  = (i + 1) * sdur if i < n - 1 else total_dur
    l1, l2 = subs[i] if i < len(subs) else ("", "")
    en = f"between(t\\,{ts:.4f}\\,{te:.4f})"

    f.append(f"{current}drawbox=x=40:y={SUB_BOX_Y}:w={W-80}:h={SUB_BOX_H}:color=black@0.55:t=fill:enable='{en}'[vb{i}]")
    f.append(f"[vb{i}]drawbox=x=40:y={SUB_BOX_Y}:w=6:h={SUB_BOX_H}:color={GREEN}@1.0:t=fill:enable='{en}'[vs{i}]")
    f.append(f"[vs{i}]drawtext=fontfile='{fm}':text='{l1}':fontcolor=white:fontsize=42:x=(w-text_w)/2:y={SUB_L1_Y}:enable='{en}'[vl1_{i}]")
    f.append(f"[vl1_{i}]drawtext=fontfile='{fr}':text='{l2}':fontcolor=white@0.85:fontsize=38:x=(w-text_w)/2:y={SUB_L2_Y}:enable='{en}'[vsub{i}]")
    current = f"[vsub{i}]"

f.append(
    f"{current}drawtext=fontfile='{fm}':text='@HolistiGlow'"
    f":fontcolor=white@0.80:fontsize=32:x=w-text_w-36:y=44"
    f":shadowcolor=black@0.5:shadowx=2:shadowy=2[vbrand]"
)
f.append("[vbrand]setsar=1[out]")

cmd += ["-filter_complex", ";".join(f)]
cmd += ["-map", "[out]", "-map", "0:a"]
cmd += ["-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p"]
cmd += ["-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"]
cmd.append(out)

print("Running FFmpeg render...")
t0 = time.time()
res = subprocess.run(cmd, capture_output=True, text=True)
elapsed = time.time() - t0

if res.returncode == 0:
    size = os.path.getsize(out) / 1024 / 1024
    print(f"SUCCESS: {out} ({size:.1f} MB) in {elapsed:.0f}s")
else:
    print(f"ERROR after {elapsed:.0f}s:")
    print(res.stderr[-3000:])
