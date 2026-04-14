from src.agents.base_agent import BaseAgent
from src.agents.agent_utils import load_memory_context, load_agent_prompt, build_funnel_context
from src.memory.memory_manager import MemoryManager
from src.skills.ai_client import ask_ai
from src.core.protocol import SwarmMessage

# Keyword → product mapping for personalization
_INTEREST_MAP = {
    "energy": ["energy", "energie", "moe", "vermoeid", "tired", "vitaliteit", "vitality", "happy juice"],
    "weight": ["afvallen", "gewicht", "weight", "slim", "fit"],
    "immunity": ["immuun", "immunity", "weerstand", "ziek", "sick"],
}
_PRODUCT_LABELS = {
    "energy": "Happy Juice (energie & vitaliteit)",
    "weight": "Trim (gewichtsbeheer)",
    "immunity": "Color Burst (antioxidanten)",
}


class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="sales")
        self._system_prompt = load_agent_prompt("sales-agent", "sales_prompt.txt")

    def process(self, input_data: str, chat_id=None, brand: str = "glowup", context: dict = None) -> SwarmMessage:
        self.logger.debug(f"Processing sales task for @{brand}: {input_data[:100]}")
        
        return self._call_ai(input_data, chat_id=chat_id, brand=brand, context=context)

    def _build_personalization_block(self, context: dict) -> str:
        """Build a personalization note based on the user's history from context."""
        if not context or not context.get("history"):
            return ""
        last_3 = context["history"]
        combined = " ".join(last_3).lower()
        matched_products = []
        for category, keywords in _INTEREST_MAP.items():
            if any(kw in combined for kw in keywords):
                matched_products.append(_PRODUCT_LABELS[category])
        history_line = " | ".join(last_3[:3])
        block = f"=== PERSONALISATIE ===\nLaatste onderwerpen: {history_line}"
        if matched_products:
            block += f"\nAanbevolen producten: {', '.join(matched_products)}"
        return block

    def _call_ai(self, task: str, chat_id=None, brand: str = "glowup", context: dict = None) -> SwarmMessage:
        try:
            memory_context = load_memory_context()
            funnel_context = build_funnel_context(chat_id)
            personalization = self._build_personalization_block(context)

            funnel_block = f"\n{funnel_context}\n" if funnel_context else ""
            personal_block = f"\n{personalization}\n" if personalization else ""

            full_prompt = (
                f"{self._system_prompt}\n\n"
                f"=== MERK INFO ===\nBrand: {brand}\n\n"
                f"=== SYSTEEMGEHEUGEN ===\n{memory_context}"
                f"{funnel_block}"
                f"{personal_block}\n"
                f"=== TAAK ===\n{task}"
            )

            response = ask_ai(full_prompt)
            return SwarmMessage(
                sender=self.name,
                content=response,
                status="success"
            )

        except Exception as e:
            self.logger.error(f"SalesAgent AI call failed: {e}")
            return SwarmMessage(
                sender=self.name,
                content=f"Sales agent hatası: {e}",
                status="error"
            )
