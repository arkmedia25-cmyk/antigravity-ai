from agents.base_agent import BaseAgent
from agents.agent_utils import load_memory_context, load_agent_prompt, build_funnel_context
from memory.memory_manager import MemoryManager
from skills.ai_client import ask_ai

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
        self.memory = MemoryManager(namespace=self.name)
        self._system_prompt = load_agent_prompt("sales-agent", "sales_prompt.txt")

    def process(self, input_data: str, chat_id=None) -> str:
        self.logger.debug(f"Processing sales task: {input_data[:100]}")
        self.memory.track_last_tasks(chat_id, input_data)

        response = self._call_ai(input_data, chat_id=chat_id)

        self.memory.save("last_response", response, chat_id=chat_id)
        return response

    def _build_personalization_block(self, chat_id) -> str:
        """Build a personalization note based on the user's last 3 tasks."""
        if chat_id is None:
            return ""
        last_3 = self.memory.load("last_3_tasks", chat_id=chat_id) or []
        if not last_3:
            return ""
        combined = " ".join(last_3).lower()
        matched_products = []
        for category, keywords in _INTEREST_MAP.items():
            if any(kw in combined for kw in keywords):
                matched_products.append(_PRODUCT_LABELS[category])
        history_line = " | ".join(last_3[:3])
        block = f"=== KİŞİSELLEŞTİRME ===\nSon konular: {history_line}"
        if matched_products:
            block += f"\nÖnerilen ürünler: {', '.join(matched_products)}"
        return block

    def _call_ai(self, task: str, chat_id=None) -> str:
        try:
            memory_context = load_memory_context()
            funnel_context = build_funnel_context(chat_id)
            personalization = self._build_personalization_block(chat_id)

            funnel_block = f"\n{funnel_context}\n" if funnel_context else ""
            personal_block = f"\n{personalization}\n" if personalization else ""

            full_prompt = (
                f"{self._system_prompt}\n\n"
                f"=== SYSTEEMGEHEUGEN ===\n{memory_context}"
                f"{funnel_block}"
                f"{personal_block}\n"
                f"=== TAAK ===\n{task}"
            )

            return ask_ai(full_prompt)

        except Exception as e:
            self.logger.error(f"SalesAgent AI call failed: {e}")
            return f"Sales agent hatası: {e}"
