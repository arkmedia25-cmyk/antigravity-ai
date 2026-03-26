from unittest.mock import patch
from src.skills.ai_client import ask_ai


def test_ask_ai_openai():
    with patch("src.skills.ai_client._get_openai") as mock_client:
        mock_client.return_value.chat.completions.create.return_value.choices[0].message.content = (
            "3 virale video ideeën: 1. ... 2. ... 3. ..."
        )
        result = ask_ai("Geef me 3 virale video ideeën voor YouTube.", "openai")
    assert isinstance(result, str)
    assert len(result) > 0


def test_ask_ai_claude():
    with patch("src.skills.ai_client._get_anthropic") as mock_client:
        mock_client.return_value.messages.create.return_value.content[0].text = (
            "Claude response"
        )
        result = ask_ai("Test prompt", "claude")
    assert isinstance(result, str)
    assert len(result) > 0
