import os
import json
import time
import requests
import re
import logging
from typing import Any, Optional, List, Union
from openai import OpenAI
from anthropic import Anthropic, APIConnectionError, RateLimitError, InternalServerError

from src.config.settings import settings
from src.skills.cache_service import cache_service

logger = logging.getLogger(__name__)

# --- Models & Thresholds ---
MODEL_SONNET = "claude-3-5-sonnet-20240620"
MODEL_HAIKU = "claude-3-5-haiku-20241022"
MODEL_GPT4O = "gpt-4o"
MODEL_GPT4O_MINI = "gpt-4o-mini"

_COMPLEXITY_THRESHOLD = 1500  # chars. Above this, use Sonnet/GPT4o

# --- Clients ---
_openai_client = None
_anthropic_client = None

def _get_anthropic():
    global _anthropic_client
    if _anthropic_client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is missing!")
        _anthropic_client = Anthropic(api_key=api_key)
    return _anthropic_client

def _get_openai():
    global _openai_client
    if _openai_client is None:
        if not settings.OPENAI_API_KEY:
             raise ValueError("OPENAI_API_KEY is missing!")
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client

# --- Utilities ---

def call_with_retry(func, max_retries: int = 3):
    """Retries transient errors with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except (APIConnectionError, RateLimitError, InternalServerError, requests.exceptions.RequestException) as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            logger.warning(f"Transient error: {e}. Retrying in {wait}s...")
            time.sleep(wait)

def select_model(messages: Union[str, List[dict]], provider: str = "openai") -> str:
    """Selects the best model based on task complexity (input length)."""
    text_len = len(str(messages))
    
    if provider == "anthropic":
        return MODEL_SONNET if text_len > _COMPLEXITY_THRESHOLD else MODEL_HAIKU
    else:
        return MODEL_GPT4O if text_len > _COMPLEXITY_THRESHOLD else MODEL_GPT4O_MINI

def ask_ai(
    messages: Any, 
    provider: str = "openai", 
    is_json: bool = False, 
    use_cache: bool = True,
    model: str = None,
    tools: list = None,
    tool_choice: str = None
) -> Any:
    """
    Enhanced AI Client with:
    - Cost-aware model routing
    - Content-hash caching
    - Smart retries
    - Anthropic prompt caching
    - OpenAI tool-use support (backward compatible)
    """
    # 1. Prepare messages
    if isinstance(messages, str):
        msgs = [{"role": "user", "content": messages}]
    else:
        msgs = messages

    # Normalize provider alias ("claude" → "anthropic")
    if provider == "claude":
        provider = "anthropic"

    # 2. Cache Lookup (skip if tools are used — tool responses aren't cacheable)
    cache_key = json.dumps(msgs, sort_keys=True)
    if use_cache and not tools:
        cached_result = cache_service.get(cache_key)
        if cached_result:
            return _parse_json(cached_result) if is_json else cached_result

    # 3. Model Selection
    selected_model = model or select_model(msgs, provider)
    
    try:
        result_text = ""
        
        if provider == "anthropic":
            try:
                def _call_anthropic():
                    client = _get_anthropic()
                    system_msg = ""
                    final_msgs = []
                    for m in msgs:
                        if m["role"] == "system":
                            content = m["content"]
                            if len(content) > 1024:
                                system_msg = [{"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}]
                            else:
                                system_msg = content
                        else:
                            final_msgs.append(m)
                    
                    return client.messages.create(
                        model=selected_model,
                        max_tokens=4096,
                        system=system_msg,
                        messages=final_msgs
                    )

                response = call_with_retry(_call_anthropic)
                result_text = response.content[0].text
                
            except Exception as e:
                logger.error(f"Anthropic error: {e}. Falling back to OpenAI...")
                provider = "openai"
                selected_model = MODEL_GPT4O
        
        if provider == "openai":
            def _call_openai():
                client = _get_openai()
                kwargs = {
                    "model": selected_model,
                    "messages": msgs,
                }
                if is_json:
                    kwargs["response_format"] = {"type": "json_object"}
                if tools:
                    kwargs["tools"] = tools
                    if tool_choice:
                        kwargs["tool_choice"] = tool_choice
                return client.chat.completions.create(**kwargs)

            response = call_with_retry(_call_openai)
            message = response.choices[0].message
            # Return raw message object if tool calls are present
            if hasattr(message, 'tool_calls') and message.tool_calls:
                return message
            result_text = message.content

        # 4. Save to Cache (only for text results, not tool calls)
        if result_text and use_cache and not tools:
            cache_service.set(cache_key, result_text)

        if is_json:
            return _parse_json(result_text)
        return result_text

    except Exception as e:
        logger.error(f"[ask_ai] Final Failure: {e}")
        return {} if is_json else f"HATA: {str(e)}"

def _parse_json(text: str) -> Any:
    """Parse JSON from AI response, handling markdown code blocks."""
    clean_text = text.strip()
    match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
    if match:
        clean_text = match.group(1)
    
    try:
        return json.loads(clean_text)
    except:
        # Fallback to older robust parsing if simple load fails
        return _robust_json_parse(text)

def _robust_json_parse(text: str) -> Any:
    # (Existing robust parsing logic from original file)
    clean_text = text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text.split("```json", 1)[1]
    if clean_text.endswith("```"):
        clean_text = clean_text.rsplit("```", 1)[0]
    clean_text = clean_text.strip()
    match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
    if match:
        try: return json.loads(match.group(1))
        except: pass
    return {}

# --- Other Skills (Image, Audio, etc.) remain simplified but could be upgraded similarly if needed ---

def generate_image(prompt: str) -> str:
    try:
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"dalle_{int(time.time())}.png")
        
        def _call_dalle():
            return _get_openai().images.generate(
                model="dall-e-3", prompt=prompt, size="1024x1792", quality="standard", n=1
            )
        
        response = call_with_retry(_call_dalle)
        img_data = requests.get(response.data[0].url).content
        with open(filepath, 'wb') as f: f.write(img_data)
        return filepath
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return None

def transcribe_audio(file_path: str) -> str:
    try:
        with open(file_path, "rb") as audio_file:
            transcription = _get_openai().audio.transcriptions.create(model="whisper-1", file=audio_file)
            return transcription.text
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return ""

def generate_speech(text: str, output_path: str = None) -> str:
    try:
        if output_path is None:
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"speech_{int(time.time())}.mp3")
        response = _get_openai().audio.speech.create(model="tts-1", voice="nova", input=text, speed=1.0)
        response.stream_to_file(output_path)
        return output_path
    except Exception as e:
        logger.error(f"Speech generation error: {e}")
        return None
