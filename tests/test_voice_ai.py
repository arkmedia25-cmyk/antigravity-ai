import sys
import os

# Add project root to sys.path
_ROOT = r"c:\Users\mus-1\OneDrive\Bureaublad\Antigravity"
if _ROOT not in sys.path:
    sys.path.append(_ROOT)

from src.skills.voice_ai_skill import voice_ai

def verify_voice_pipeline():
    # Use a small audio file for testing
    test_audio = os.path.join(_ROOT, "outputs", "debug_test.mp4")
    
    if not os.path.exists(test_audio):
        print(f"FAILED: Test audio missing: {test_audio}")
        return

    print("Starting... Testing Full Voice AI Pipeline (Whisper -> Claude -> ElevenLabs)...")
    try:
        # Start the pipeline
        result_path = voice_ai.process_voice_support(test_audio, brand="holisti")
        
        if result_path and os.path.exists(result_path):
            size = os.path.getsize(result_path)
            print(f"SUCCESS: Voice response generated at {result_path} (Size: {size} bytes)")
            # Generate a public URL using our new uploader logic for sharing
            from src.skills.uploader_skill import uploader
            public_url = uploader.upload_file(result_path)
            print(f"🔗 Public Link for Verification: {public_url}")
        else:
            print("FAILED: No output file generated.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verify_voice_pipeline()
