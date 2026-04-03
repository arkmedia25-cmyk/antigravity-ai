import os
import re
from src.agents.base_agent import BaseAgent
from src.agents.agent_utils import load_memory_context, load_agent_prompt, build_funnel_context
from src.memory.memory_manager import MemoryManager
from src.core.brand_manager import BrandManager
from src.skills.ai_client import ask_ai
from src.core.logging import get_logger

logger = get_logger("agents.content")

class ContentAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="content")
        self.memory = MemoryManager(namespace=self.name)
        self.brand_manager = BrandManager()
        self._system_prompt = load_agent_prompt("content-agent", "content_prompt.txt")

    def process(self, input_data: str, chat_id=None, brand: str = "glowup") -> str:
        # Load brand-specific identity
        brand_config = self.brand_manager.get_brand(brand)
        if not brand_config:
            brand = "glowup"
            brand_config = self.brand_manager.get_brand(brand)

        logger.debug(f"Processing content task for brand [@{brand}]: {input_data[:100]}")
        self.memory.save(f"{brand}:last_task", input_data, chat_id=chat_id)

        # Build persona-driven prompt
        personality_text = (
            f"Brand Name: {brand_config.get('brand_name')}\n"
            f"Voice Tone: {brand_config.get('voice_tone')}\n"
            f"Target Audience: {brand_config.get('target_audience')}\n"
            f"Language: {brand_config.get('language')}\n"
            f"Marketing Angles: {', '.join(brand_config.get('marketing_angles', []))}"
        )

        response = self._call_ai(input_data, personality_text, chat_id=chat_id, brand=brand)

        # ✨ KESİN ÇÖZÜM: Metin Temizleme Filtresi
        cleaned_response = re.sub(r'\(.*?\)', '', response)
        cleaned_response = re.sub(r'(?i)(Tip \d+|Scene \d+|Hook|Call to action|Content|Caption|Video|Action):\s*', '', cleaned_response)
        cleaned_response = cleaned_response.replace('"', '').replace('\'', '')
        cleaned_response = cleaned_response.strip()

        self.memory.save(f"{brand}:last_response", cleaned_response, chat_id=chat_id)
        return cleaned_response

    def _call_ai(self, task: str, personality_text: str, chat_id=None, brand: str = "glowup") -> str:
        try:
            memory_context = load_memory_context()
            funnel_context = build_funnel_context(chat_id)
            funnel_block = f"\n{funnel_context}\n" if funnel_context else ""

            full_prompt = (
                f"{self._system_prompt}\n\n"
                f"=== BRAND PERSONA - {brand.upper()} ===\n{personality_text}\n\n"
                f"=== SYSTEM MEMORY ({brand}) ===\n{memory_context}"
                f"{funnel_block}\n"
                f"=== TASK ===\n{task}"
            )

            return ask_ai(full_prompt, provider="openai")

        except Exception as e:
            logger.error(f"ContentAgent AI call failed: {e}")
            return f"Content agent hatası: {e}"
