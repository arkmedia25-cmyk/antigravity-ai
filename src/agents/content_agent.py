import os
import re
from src.agents.base_agent import BaseAgent
from src.agents.agent_utils import load_memory_context, load_agent_prompt, build_funnel_context
from src.memory.memory_manager import MemoryManager
from src.core.brand_manager import BrandManager
from src.skills.ai_client import ask_ai
from src.core.logging import get_logger
from src.core.protocol import SwarmMessage

logger = get_logger("agents.content")

class ContentAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="content")
        self.brand_manager = BrandManager()
        self._system_prompt = load_agent_prompt("content-agent", "content_prompt.txt")

    def process(self, input_data: str, chat_id=None, brand: str = "glowup", context: dict = None) -> SwarmMessage:
        # Load brand-specific identity
        brand_config = self.brand_manager.get_brand(brand)
        if not brand_config:
            brand = "glowup"
            brand_config = self.brand_manager.get_brand(brand)

        logger.debug(f"Processing content task for brand [@{brand}]: {input_data[:100]}")

        # [MEMORY] Prepare history string
        history_str = ""
        if context and context.get("history"):
             history_str = "\nRecente Interacties:\n" + "\n".join([f"- {t}" for t in context["history"]])

        # Build persona-driven prompt
        personality_text = (
            f"Brand Name: {brand_config.get('brand_name')}\n"
            f"Voice Tone: {brand_config.get('voice_tone')}\n"
            f"Target Audience: {brand_config.get('target_audience')}\n"
            f"Language: {brand_config.get('language')}\n"
            f"Marketing Angles: {', '.join(brand_config.get('marketing_angles', []))}"
        )

        message = self._call_ai(input_data, personality_text, history=history_str, chat_id=chat_id, brand=brand)

        # ✨ KESİN ÇÖZÜM: Metin Temizleme Filtresi
        response = message.content
        cleaned_response = re.sub(r'\(.*?\)', '', response)
        cleaned_response = re.sub(r'(?i)(Tip \d+|Scene \d+|Hook|Call to action|Content|Caption|Video|Action):\s*', '', cleaned_response)
        cleaned_response = cleaned_response.replace('"', '').replace('\'', '')
        cleaned_response = cleaned_response.strip()

        message.content = cleaned_response
        
        # 🔗 Otomatik Delegasyon: Eğer içerikte video/reels ile ilgili bir şey varsa VideoProducer'a devret
        trigger_keywords = ["video", "reel", "reels", "hazırla", "üret", "anlat", "göster", "oluştur"]
        has_video_kw = any(kw in input_data.lower() for kw in trigger_keywords)
        
        # Check both cleaned and original response for specific markers
        reels_markers = [r"🎬\s*Reels-idee", r"Reels-idee", r"Video:", r"🎥\s*Video"]
        has_reels_marker = any(re.search(pattern, response, re.I) for pattern in reels_markers) or \
                           any(re.search(pattern, cleaned_response, re.I) for pattern in reels_markers)

        if has_video_kw and has_reels_marker:
            message.next_agent = "video_producer"
            logger.info(f"[ContentAgent] ✅ Video üretimi tetiklendi. Delegating to {message.next_agent}.")
        else:
            logger.debug(f"[ContentAgent] ℹ️ Delegasyon şartları oluşmadı. KW: {has_video_kw}, Marker: {has_reels_marker}")
        
        return message

    def _call_ai(self, task: str, personality_text: str, history: str = "", chat_id=None, brand: str = "glowup") -> SwarmMessage:
        try:
            memory_context = load_memory_context()
            funnel_context = build_funnel_context(chat_id)
            funnel_block = f"\n{funnel_context}\n" if funnel_context else ""

            full_prompt = (
                f"{self._system_prompt}\n\n"
                f"=== BRAND PERSONA - {brand.upper()} ===\n{personality_text}\n\n"
                f"=== SYSTEM MEMORY & KNOWLEDGE ===\n{memory_context}\n"
                f"{funnel_block}\n"
                f"=== CONVERSATION HISTORY ===\n{history}\n\n"
                f"=== TASK ===\n{task}"
            )

            response = ask_ai(full_prompt, provider="openai")
            return SwarmMessage(
                sender=self.name,
                content=response,
                status="success"
            )

        except Exception as e:
            logger.error(f"ContentAgent AI call failed: {e}")
            return SwarmMessage(
                sender=self.name,
                content=f"Content agent error: {e}",
                status="error"
            )
