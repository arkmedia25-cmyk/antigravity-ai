import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from skills import tts_skill, video_skill

def generate_poc_reel():
    print("🚀 Operation Cevher-1: Starting Generation...")
    
    # 1. Define Script Segments (Dutch - GlowUp Style)
    segments = [
        {"tag": "hook", "text": "Stop met het negeren van je heupen! Je lichaam schreeuwt om deze stretch."},
        {"tag": "content", "text": "Supta Konasana is het geheim voor een betere houding, minder rugpijn en een diepe ontspanning. Probeer het vandaag nog!"},
        {"tag": "cta", "text": "Wil jij elke dag stralen? Volg @GlowUpNL voor je dagelijkse dosis wellness-magie!"}
    ]
    
    # 2. Generate Audio Fragments (Nova, 1.15x)
    print("🎙️ Generating Nova 1.15x Voiceover...")
    audio_fragments = []
    for i, seg in enumerate(segments):
        filename = f"fragment_{i}_{seg['tag']}.mp3"
        # Using OpenAI TTS via our skill
        path = tts_skill.generate_dutch_audio(
            text=seg['text'],
            filename=filename,
            voice="nova",
            speed=1.15
        )
        audio_fragments.append({"tag": seg['tag'], "path": path, "text": seg['text']})
    
    # 3. Use the Generated Image
    image_path = r"C:\Users\mus-1\.gemini\antigravity\brain\3dbdae44-7314-4aa1-8a9d-3879dfa0c8a1\wellness_yoga_pose_aesthetic_1774967771702.png"
    
    # 4. Create the Reel
    print("🎬 Rendering Final POC Reel (Fragment-Sync Mode)...")
    output_path = video_skill.create_reel(
        fragments=audio_fragments,
        image_path=image_path,
        output_filename="glowup_poc_cevher1.mp4",
        font_path=r"C:\Windows\Fonts\arialbd.ttf" # Using bold arial
    )
    
    print(f"✅ MISSION ACCOMPLISHED! Video saved at: {output_path}")

if __name__ == "__main__":
    generate_poc_reel()
