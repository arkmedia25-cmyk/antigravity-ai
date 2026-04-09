import os
from src.agents.base_agent import BaseAgent
from src.memory.memory_manager import MemoryManager
from src.core.logging import get_logger
from src.skills.ai_client import ask_ai

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def _load_cmo_prompt() -> str:
    path = os.path.join(PROJECT_ROOT, "agents", "cmo_agent", "cmo.txt")
    if not os.path.exists(path):
        raise FileNotFoundError(f"CMO prompt bulunamadi: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

class CmoAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="cmo")

    def process(self, input_data: str, chat_id=None, brand: str = "glowup", context: dict = None) -> str:
        self.logger.debug(f"Processing task for @{brand}: {input_data[:100]}")
        
        # [MEMORY] Prepare history and profile context
        history_str = ""
        if context and context.get("history"):
             history_str = "\nConversation History:\n" + "\n".join([f"- {t}" for t in context["history"]])
        
        profile_str = ""
        if context and context.get("user_profile"):
            up = context["user_profile"]
            profile_str = f"User Status: Brand={brand}, Interactions={up.get('funnel:interaction_count', 0)}"

        response = self._call_ai(input_data, history=history_str, profile=profile_str)
        return response

    def _call_ai(self, task: str, history: str = "", profile: str = "") -> str:
        try:
            system_prompt = (
                "You are AntiGravity CMO AI - a marketing strategy assistant for Dutch health products. "
                "You help create platform-specific content strategies (IG, TikTok). "
                "Use the provided conversation history to maintain context."
            )
            
            full_prompt = (
                f"{system_prompt}\n"
                f"{profile}\n"
                f"{history}\n\n"
                f"User Message: {task}\n"
                "Respond in Dutch (or the user's language). Be conversational and strategic."
            )
            return ask_ai(full_prompt)
        except Exception as e:
            self.logger.error(f"AI call failed: {e}")
            return f"CMO agent hatasi: {e}"
