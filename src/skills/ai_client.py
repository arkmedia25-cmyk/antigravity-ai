import anthropic
from openai import OpenAI
from config.settings import settings


_anthropic_client = None
_openai_client = None


def _get_anthropic():
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _anthropic_client


def _get_openai():
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


def ask_ai(prompt: str, provider: str = "claude") -> str:
    try:
        if provider == "claude":
            response = _get_anthropic().messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        else:
            response = _get_openai().chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
    except Exception as e:
        return f"HATA: {str(e)}"
