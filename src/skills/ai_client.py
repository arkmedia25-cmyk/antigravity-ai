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


def ask_ai(prompt: str, provider: str = "openai") -> str:
    try:
        if provider == "claude":
            response = _get_anthropic().messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        else:
            response = _get_openai().chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
    except Exception as e:
        return f"HATA: {str(e)}"

def generate_image(prompt: str) -> str:
    """Generates a high-quality DALL-E 3 image and returns the local path."""
    import os
    import time
    import requests
    from config.settings import settings
    
    try:
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"dalle_{int(time.time())}.png"
        filepath = os.path.join(output_dir, filename)
        
        response = _get_openai().images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1792", # Vertical aspect for Reels
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        img_data = requests.get(image_url).content
        with open(filepath, 'wb') as f:
            f.write(img_data)
            
        print(f"[ai_client] Image generated: {filepath}")
        return filepath
    except Exception as e:
        print(f"[ai_client] Image generation error: {e}")
        return None
