from openai import OpenAI
from src.config.settings import settings
import json
import os
import time
import requests
import re

_openai_client = None

def _get_openai():
    global _openai_client
    if _openai_client is None:
        if not settings.OPENAI_API_KEY:
             raise ValueError("OPENAI_API_KEY is missing in .env file!")
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client

def ask_ai(prompt: str, provider: str = "openai", is_json: bool = False) -> str:
    """Sends a prompt to AI. Forced to GPT-4o for consistency and reliability."""
    try:
        # We force OpenAI GPT-4o even if provider is 'claude' to avoid 401 errors
        kwargs = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
        }
        if is_json:
            kwargs["response_format"] = {"type": "json_object"}
            
        client = _get_openai()
        response = client.chat.completions.create(**kwargs)
        text = response.choices[0].message.content
        
        if is_json:
            # Clean up markdown markers if present
            clean_text = text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text.split("```json", 1)[1]
            if clean_text.endswith("```"):
                clean_text = clean_text.rsplit("```", 1)[0]
            clean_text = clean_text.strip()
            
            try:
                return json.loads(clean_text)
            except json.JSONDecodeError as e:
                # If "Extra data", try to parse only the part before the extra data
                if "Extra data" in str(e):
                    try:
                        # Extract the part that was successfully parsed (or looks like JSON)
                        # Find the first { and the matching last }
                        match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
                        if match:
                             # We use a more careful approach to find the FIRST complete JSON object
                             # if there are multiples.
                             content = match.group(1)
                             # Try to find the last '}' that actually completes the first object
                             # Simple heuristic: try to parse prefixes of the content
                             for i in range(len(content), 0, -1):
                                 if content[i-1] == '}':
                                     try:
                                         return json.loads(content[:i])
                                     except:
                                         continue
                    except:
                        pass
                
                # Fallback: original regex-based extraction (legacy)
                import re
                match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group(1))
                    except:
                        pass
                raise
        return text
    except Exception as e:
        print(f"[ask_ai] Critical Error: {e}")
        return {} if is_json else f"HATA: {str(e)}"

def generate_image(prompt: str) -> str:
    """Generates a high-quality DALL-E 3 image."""
    try:
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"dalle_{int(time.time())}.png"
        filepath = os.path.join(output_dir, filename)
        
        response = _get_openai().images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1792",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        img_data = requests.get(image_url).content
        with open(filepath, 'wb') as f:
            f.write(img_data)
        return filepath
    except Exception as e:
        print(f"[ai_client] Image generation error: {e}")
        return None

def transcribe_audio(file_path: str) -> str:
    """Transcribes audio file using OpenAI Whisper."""
    try:
        with open(file_path, "rb") as audio_file:
            transcription = _get_openai().audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
            return transcription.text
    except Exception as e:
        print(f"[ai_client] Transcription error: {e}")
        return ""

def generate_speech(text: str, output_path: str = None) -> str:
    """Generates speech from text using OpenAI TTS."""
    try:
        if output_path is None:
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"speech_{int(time.time())}.mp3")
            
        response = _get_openai().audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text,
            speed=1.0
        )
        response.stream_to_file(output_path)
        return output_path
    except Exception as e:
        print(f"[ai_client] Speech generation error: {e}")
        return None
