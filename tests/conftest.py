import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_settings():
    """Returns a mock settings object with dummy API keys."""
    settings = MagicMock()
    settings.OPENAI_API_KEY = "test-openai-key"
    settings.ANTHROPIC_API_KEY = "test-anthropic-key"
    settings.GEMINI_API_KEY = "test-gemini-key"
    settings.TELEGRAM_TOKEN = "test-telegram-token"
    settings.validate.return_value = []
    return settings


@pytest.fixture
def mock_ai_client():
    """Returns a mock AI client that returns a fixed response."""
    client = MagicMock()
    client.ask.return_value = "Mock AI response for testing."
    return client
