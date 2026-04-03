import os
import sys
import time
import requests

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from skills.publisher_skill import publisher_skill
    from config.settings import settings
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)

def publish_now():
    print("--- 🎬 STARTING OTONOM PUSH (GlowUp Awareness) ---")
    
    video_path = "outputs/glowup_awareness_final.mp4"
    if not os.path.exists(video_path):
        print(f"ERROR: Video not found at {video_path}")
        return

    caption = (
        "Wil je meer energie in de ochtend zonder cafeine? "
        "Probeer deze 3 simpele tips voor een frisse start! Welke tip ga jij "
        "morgen proberen? Reageer hieronder!\n\n"
        "#GlowUpNL #WellnessNederland #NatuurlijkEnergie #GezondLeven #BiohackingNL "
        "#MorgenRoutine #Zelfzorg #Energie #MindsetNederland #AmareGlobal #GezondheidTips"
    )

    # 1. Temporary Hosting via catbox.moe
    print("Step 1: Uploading video to catbox.moe...")
    try:
        url = "https://catbox.moe/user/api.php"
        with open(video_path, "rb") as f:
            files = {
                "reqtype": (None, "fileupload"),
                "fileToUpload": (os.path.basename(video_path), f, "video/mp4")
            }
            r = requests.post(url, files=files)
        
        if r.status_code == 200:
            public_url = r.text.strip()
            print(f"✅ Public URL obtained: {public_url}")
            
            # 2. Instagram Publishing
            print("Step 2: Triggering Meta Graph API Publication...")
            final_res = publisher_skill.publish_to_instagram(public_url, caption)
            
            if final_res.get("success"):
                print(f"🎉 SUCCESS! Reels published. Media ID: {final_res.get('id')}")
            else:
                print(f"❌ PUBLISH FAILED: {final_res.get('error')}")
        else:
            print(f"❌ Upload failed (HTTP {r.status_code}): {r.text[:500]}")
    except Exception as e:
        print(f"⚠️ Exception during push: {e}")

if __name__ == "__main__":
    publish_now()
    print("--- PUSH OPERATION FINISHED ---")
