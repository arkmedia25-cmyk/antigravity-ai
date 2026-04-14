import os
import time
from typing import Optional
from src.config.settings import settings
from src.skills.ai_client import transcribe_audio, ask_ai
from elevenlabs.client import ElevenLabs

class VoiceAISkill:
    """
    Voice AI Skill: Whisper (Transcription) + Claude (Smart Logic) + ElevenLabs (Premium Voice).
    Designed for autonomous customer support and high-end video voiceovers.
    """
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "bH1SkJMbYirLovnne9JM")
        self.client = ElevenLabs(api_key=self.api_key) if self.api_key else None

    def generate_premium_audio(self, text: str, filename: str = None) -> Optional[str]:
        """
        Converts text to speech using ElevenLabs for premium quality.
        """
        if not self.client:
            print("[VoiceAI] ElevenLabs API Key missing!")
            return None
            
        try:
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            if not filename:
                filename = f"voice_premium_{int(time.time())}.mp3"
            output_path = os.path.join(output_dir, filename)

            print(f"[VoiceAI] Generating Five-Star Audio with ElevenLabs... {output_path}")
            
            response = self.client.generate(
                text=text,
                voice=self.voice_id,
                model="eleven_multilingual_v2"
            )
            
            # The new SDK returns an iterator of bytes
            with open(output_path, 'wb') as f:
                for chunk in response:
                    f.write(chunk)
            
            return output_path
        except Exception as e:
            print(f"[VoiceAI] ElevenLabs Error: {e}")
            return None

    def process_voice_support(self, incoming_audio_path: str, brand: str = "holisti") -> Optional[str]:
        """
        Unified Support Pipeline: 
        1. Transcribe (Whisper) 
        2. Respond (Claude + Persona) 
        3. Synthesize (ElevenLabs)
        """
        # 1. Transcription
        print(f"[VoiceAI] Transcribing incoming audio: {incoming_audio_path}")
        user_text = transcribe_audio(incoming_audio_path)
        if not user_text:
            return None
        
        print(f"[VoiceAI] User said: \"{user_text}\"")
        
        # 2. Response Logic (Claude)
        # Load personality
        persona_file = f"agents/{brand}_personality.txt"
        personality = ""
        if os.path.exists(persona_file):
            with open(persona_file, "r", encoding="utf-8") as f:
                personality = f.read()
        
        system_prompt = (
            f"You are the Voice of {brand.capitalize()}. \n"
            f"PERSONALITY GUIDELINES:\n{personality}\n\n"
            "INSTRUCTIONS:\n"
            "1. Respond directly to the user's voice message in a helpful and caring way.\n"
            "2. IMPORTANT: Automatically detect the user's language and respond in that SAME language.\n"
            "3. Keep the response concise (2-4 sentences) as it will be converted to a voice memo.\n"
            "4. Be professional but warm. No robotic boilerplate."
        )
        
        print(f"[VoiceAI] Getting smart response from Claude model (with OpenAI fallback)...")
        response_text = ask_ai(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User's Voice Message: {user_text}"}
            ],
            provider="anthropic"
        )
        
        # Fallback to OpenAI if Anthropic fails (e.g., credit balance issue)
        if "HATA" in response_text:
            print("[VoiceAI] Anthropic failed, falling back to OpenAI GPT-4o...")
            response_text = ask_ai(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User's Voice Message: {user_text}"}
                ],
                provider="openai"
            )
        
        print(f"[VoiceAI] Pipeline response: \"{response_text}\"")
        
        # 3. Voice Synthesis (ElevenLabs)
        response_audio_path = self.generate_premium_audio(response_text)
        return response_audio_path

# Static instance for easy access
voice_ai = VoiceAISkill()

if __name__ == "__main__":
    # Quick test (assuming a test file exists)
    _test_voice = "outputs/debug_test.mp3"
    if os.path.exists(_test_voice):
        result = voice_ai.process_voice_support(_test_voice, brand="holisti")
        print(f"Pipeline Result: {result}")
    else:
        print("No test audio found at outputs/debug_test.mp3")
