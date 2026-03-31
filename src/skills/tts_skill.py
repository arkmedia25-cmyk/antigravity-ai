import os
from openai import OpenAI
from config.settings import settings

_OUTPUT_DIR = "outputs"
_DEFAULT_VOICE = "nova"

def generate_dutch_audio(
    text: str,
    filename: str,
    voice: str = "nova",
    speed: float = 1.15,
) -> str:
    """
    Convert text to Dutch speech using OpenAI TTS API.
    Saves the result as an MP3 in the outputs/ folder with custom speed.
    """
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(_OUTPUT_DIR, filename)
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice if voice else _DEFAULT_VOICE,
        speed=speed,
        input=text
    )
    
    response.write_to_file(output_path)
    print(f"[tts_skill] Audio saved via OpenAI: {output_path} | voice={voice or _DEFAULT_VOICE} | speed={speed}")
    return output_path

if __name__ == "__main__":
    _path = generate_dutch_audio("Hallo allemaal, leuk dat je er bent!", "test_audio_openai.mp3")
    print(f"Test klaar: {_path}")
