from openai import OpenAI
from anthropic import Anthropic
from src.config.settings import settings
import json
import os
import time
import requests
import re

_openai_client = None
_anthropic_client = None

def _get_anthropic():
    global _anthropic_client
    if _anthropic_client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is missing in .env file!")
        _anthropic_client = Anthropic(api_key=api_key)
    return _anthropic_client

def _get_openai():
    global _openai_client
    if _openai_client is None:
        if not settings.OPENAI_API_KEY:
             raise ValueError("OPENAI_API_KEY is missing in .env file!")
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client

def ask_ai(messages: any, provider: str = "openai", is_json: bool = False, tools: list = None, tool_choice: str = None) -> any:
    """Sends messages (list or str) to AI. Auto-falls back to OpenAI if Anthropic fails."""
    try:
        # If it's a string, convert to list of messages
        if isinstance(messages, str):
            msgs = [{"role": "user", "content": messages}]
        else:
            msgs = messages

        # Try Anthropic if explicitly requested
        if provider == "anthropic":
            try:
                client = _get_anthropic()
                system_msg = ""
                final_msgs = []
                for m in msgs:
                    if m["role"] == "system":
                        system_msg = m["content"]
                    else:
                        final_msgs.append(m)
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=2048,
                    system=system_msg,
                    messages=final_msgs
                )
                text = response.content[0].text
                if is_json:
                    return _parse_json(text)
                return text
            except Exception as anthropic_err:
                print(f"[ask_ai] Anthropic failed ({anthropic_err}), falling back to OpenAI gpt-4o...")
                # Fall through to OpenAI below

        # OpenAI (default + fallback)
        client = _get_openai()
        kwargs = {
            "model": "gpt-4o",
            "messages": msgs,
        }
        if is_json:
            kwargs["response_format"] = {"type": "json_object"}
        if tools:
            kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice

        response = client.chat.completions.create(**kwargs)
        message = response.choices[0].message
        if hasattr(message, 'tool_calls') and message.tool_calls:
            return message
        text = message.content

        if is_json:
            return _parse_json(text)
        return text

    except Exception as e:
        print(f"[ask_ai] Critical Error: {e}")
        return {} if is_json else f"HATA: {str(e)}"


def _parse_json(text: str) -> any:
    """Parse JSON from AI response, handling markdown code blocks."""
    clean_text = text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text.split("```json", 1)[1]
    if clean_text.endswith("```"):
        clean_text = clean_text.rsplit("```", 1)[0]
    clean_text = clean_text.strip()
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError as e:
        if "Extra data" in str(e):
            match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
            if match:
                content = match.group(1)
                for i in range(len(content), 0, -1):
                    if content[i-1] == '}':
                        try:
                            return json.loads(content[:i])
                        except:
                            continue
        match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        raise


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
