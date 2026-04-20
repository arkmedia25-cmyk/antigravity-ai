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
from src.skills.observation_service import observation_service
from src.skills.mcp_client import mcp_bridge

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

def select_model(messages: Union[str, List[dict]], provider: str = "openai") -> dict:
    """Uses the MCP Model Router to select the best provider and model."""
    if mcp_bridge:
        try:
            task_text = str(messages)
            decision_json = mcp_bridge.call_tool("route_model", {"task_description": task_text})
            if hasattr(decision_json, 'content') and decision_json.content:
                try:
                    text_content = decision_json.content[0].text
                    return json.loads(text_content)
                except (json.JSONDecodeError, AttributeError, IndexError) as e:
                    logger.warning(f"MCP Routing JSON parse failed: {e}")
        except Exception as e:
            logger.warning(f"MCP Routing tool call failed, using fallback: {e}")
            
    # Fallback legacy logic
    text_len = len(str(messages))
    if provider == "anthropic":
        model = MODEL_SONNET if text_len > _COMPLEXITY_THRESHOLD else MODEL_HAIKU
        return {"provider": "anthropic", "model": model}
    else:
        model = MODEL_GPT4O if text_len > _COMPLEXITY_THRESHOLD else MODEL_GPT4O_MINI
        return {"provider": "openai", "model": model}

def ask_ai(
    messages: Any, 
    provider: str = "openai", 
    is_json: bool = False, 
    use_cache: bool = True,
    model: str = None,
    tools: list = None,
    tool_choice: str = None,
    thinking_budget: int = 0,
    use_mcp: bool = True
) -> Any:
    """
    Enhanced AI Client with:
    - Cost-aware model routing (if use_mcp=True)
    - Content-hash caching
    - Smart retries
    - Strict Dutch language enforcement
    - Recursion protection (Pillar 18)
    """
    # 1. Prepare messages and Enforce Dutch Language
    if isinstance(messages, str):
        msgs = [{"role": "user", "content": messages}]
    else:
        msgs = messages
        
    # Inject Dutch Language Enforcement
    dutch_enforcement = "IMPORTANT: ALWAYS output in Dutch (Nederlands). NEVER use English unless specifically asked for a translation."
    if msgs[0]["role"] == "system":
        msgs[0]["content"] += f"\n\n{dutch_enforcement}"
    else:
        msgs.insert(0, {"role": "system", "content": dutch_enforcement})

    # Normalize provider alias ("claude" → "anthropic")
    if provider == "claude":
        provider = "anthropic"

    # 2. Cache Lookup (skip if tools are used — tool responses aren't cacheable)
    cache_key = json.dumps(msgs, sort_keys=True)
    if use_cache and not tools:
        cached_result = cache_service.get(cache_key)
        if cached_result:
            return _parse_json(cached_result) if is_json else cached_result

    # 3. Model Selection & Routing
    if (not model or model == "auto") and use_mcp:
        routing = select_model(msgs, provider)
        provider = routing.get("provider", provider)
        selected_model = routing.get("model", MODEL_GPT4O)
    else:
        selected_model = model or MODEL_GPT4O_MINI

    # 4. Governance & Safety Check (Skip if use_mcp=False to avoid deadlock)
    if mcp_bridge and use_mcp:
        # Estimate tokens (simple heuristic: 4 chars = 1 token)
        est_tokens = len(str(msgs)) // 4
        safety_resp = mcp_bridge.call_tool("check_safety_limits", {
            "model": selected_model, 
            "estimated_tokens": est_tokens
        })
        # Check if bridge returned a response with content
        if hasattr(safety_resp, 'content') and safety_resp.content:
            try:
                 safety_data = json.loads(safety_resp.content[0].text)
                 if safety_data.get("status") == "blocked":
                     logger.error(f"🚨 Governance Block: {safety_data.get('reason')}")
                     return f"Hata: {safety_data.get('reason')}"
            except (json.JSONDecodeError, AttributeError, IndexError) as e:
                logger.warning(f"MCP Safety JSON parse failed (bypassing): {e}")
    
    # 5. Integrate MCP Tools (Skip if use_mcp=False)
    all_tools = tools or []
    if mcp_bridge and use_mcp:
        mcp_tools = mcp_bridge.get_tools()
        if mcp_tools:
            tool_names = [t["function"]["name"] for t in all_tools]
            for mt in mcp_tools:
                if mt["function"]["name"] not in tool_names:
                    all_tools.append(mt)
    
    try:
        result_text = ""
        # ... (rest of the calling logic)
        
        if provider == "anthropic":
            try:
                def _call_anthropic():
                    client = _get_anthropic()
                    system_msg = ""
                    final_msgs = []
                    for m in msgs:
                        if m["role"] == "system":
                            content = m["content"]
                            # Modern Prompt Caching for blocks over 1024 tokens
                            if len(content) > 1024:
                                system_msg = [{"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}]
                            else:
                                system_msg = content
                        else:
                            final_msgs.append(m)
                    
                    kwargs = {
                        "model": selected_model,
                        "max_tokens": 4096,
                        "system": system_msg,
                        "messages": final_msgs
                    }
                    if tools:
                        kwargs["tools"] = tools # Note: Native Anthropic tool format mapping might be needed
                    
                    if thinking_budget > 0:
                        kwargs["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}
                        kwargs["max_tokens"] = max(kwargs["max_tokens"], thinking_budget + 2048)
                    
                    return client.messages.create(**kwargs)

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

        # 5. Record Observation for Brain
        observation_service.record(
            provider=provider,
            model=selected_model,
            messages=msgs,
            result=result_text,
            metadata={"is_json": is_json, "cached": False}
        )

        # --- 11. Final Cost Tracking (Antigravity OS Pillar 2/3) ---
        try:
            from src.skills.governance_service import governance_service
            # Simplified Cost Calculation: Prices per 1M tokens
            prices = {"gpt-4o": 10.0, "gpt-4o-mini": 0.30, "claude-3-5-sonnet-20240620": 10.0}
            p = prices.get(selected_model, 0.30)
            in_tokens = len(str(msgs)) // 4
            out_tokens = len(result_text) // 4
            total_cost = (in_tokens + out_tokens) / 1_000_000 * p
            
            governance_service.track_spend(total_cost)
            logger.info(f"💰 Cost tracked: ${total_cost:.6f} for model {selected_model}")
        except Exception as te:
            logger.debug(f"Spend tracking failed (non-critical): {te}")

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
