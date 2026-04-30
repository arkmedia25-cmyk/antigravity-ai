import os
import requests
import base64
import json
from pathlib import Path

# API KEY buraya gelecek veya ortam değişkeninden alınacak
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "BURAYA_API_KEY_GELECEK")

def generate_thumbnail(prompt: str, output_path: str):
    """NVIDIA NIM kullanarak thumbnail üretir"""
    print(f"[Thumbnail] Üretiliyor: {prompt}")
    
    # Not: Model endpointi seçilen modele göre değişebilir (sana, bria-2.3, sdxl vb.)
    invoke_url = "https://ai.api.nvidia.com/v1/genai/stabilityai/sdxl-turbo"
    
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text_prompts": [{"text": prompt, "weight": 1}],
        "seed": 0,
        "steps": 4
    }

    response = requests.post(invoke_url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        image_data = base64.b64decode(data.get("artifacts")[0].get("base64"))
        with open(output_path, "wb") as f:
            f.write(image_data)
        print(f"[Thumbnail] Başarıyla kaydedildi: {output_path}")
    else:
        print(f"Hata: {response.status_code} - {response.text}")

if __name__ == "__main__":
    if NVIDIA_API_KEY == "BURAYA_API_KEY_GELECEK":
        print("Lütfen API Key'i ayarlayın!")
    else:
        generate_thumbnail("Dark moody neon cyberpunk cityscape, highly detailed, 4k", "test_thumb.jpg")
