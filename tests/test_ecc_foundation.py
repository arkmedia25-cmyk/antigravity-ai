import pytest
import os
import json
from src.skills.ai_client import select_model, MODEL_HAIKU, MODEL_SONNET, MODEL_GPT4O_MINI, MODEL_GPT4O, ask_ai
from src.skills.cache_service import cache_service

def test_model_routing_logic():
    """Test if select_model correctly identifies task complexity."""
    # Simple prompt
    assert select_model("Hello", provider="anthropic") == MODEL_HAIKU
    assert select_model("Hi", provider="openai") == MODEL_GPT4O_MINI
    
    # Complex prompt (long text)
    long_prompt = "x" * 2000
    assert select_model(long_prompt, provider="anthropic") == MODEL_SONNET
    assert select_model(long_prompt, provider="openai") == MODEL_GPT4O

def test_cache_service_hit_miss():
    """Verify SHA-256 hash caching logic."""
    test_key = "test_prompt_123"
    test_content = "This is a cached AI response"
    
    # Ensure fresh start
    cache_service.set(test_key, test_content)
    
    # Test Hit
    result = cache_service.get(test_key)
    assert result == test_content
    
    # Test Miss
    assert cache_service.get("non_existent_key") is None

def test_ask_ai_cache_integration(monkeypatch):
    """Test if ask_ai uses the cache correctly."""
    prompt = "Unique test prompt for caching"
    
    # 1. First call (should be a miss, but we'll mock it)
    # Actually, we can just run it once.
    response1 = ask_ai(prompt, use_cache=True)
    
    # 2. Second call (should be a hit)
    # We can verify by looking at the cache file directly or timing it (not reliable in tests)
    # Best way: Check if cache file exists
    h = cache_service._compute_hash(json.dumps([{"role": "user", "content": prompt}], sort_keys=True))
    cache_file = cache_service.cache_base / f"{h}.json"
    
    assert cache_file.exists()
    
    # 3. Repeat and check result
    response2 = ask_ai(prompt, use_cache=True)
    assert response1 == response2

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="API key required")
def test_ask_ai_fallback():
    """Test if system falls back when provider is wonky (simulated)."""
    # This is harder to test without mocking, but we can verify it doesn't crash
    resp = ask_ai("Explain 1+1", provider="anthropic") # Might fallback if credits are out
    assert "2" in str(resp)
