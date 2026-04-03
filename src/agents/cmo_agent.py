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
        self.memory = MemoryManager(namespace=self.name)

    def process(self, input_data: str, chat_id=None) -> str:
        self.logger.debug(f"Processing task: {input_data[:100]}")
        self.memory.save("last_task", input_data, chat_id)

        response = self._call_ai(input_data, chat_id=chat_id)

        self.memory.save("last_response", response, chat_id)
        return response

    def _call_ai(self, task: str, chat_id=None, prev_context="") -> str:
        try:
            system_prompt = (
                "You are AntiGravity CMO AI - a marketing strategy assistant for Dutch health products. "
                "You help create Instagram Reels, TikTok, and YouTube Shorts content. "
                "Remember the user's previous requests and build on them. "
                "If they say 'but change X to Y', apply changes to previous ideas. "
                "Always respond in user's language. Be conversational and helpful."
            )
            
            full_prompt = (
                f"{system_prompt}\n\n"
                f"Previous context: {prev_context}\n"
                f"User message: {task}\n"
                f"Respond naturally and conversationally."
            )
            return ask_ai(full_prompt)
        except Exception as e:
            self.logger.error(f"AI call failed: {e}")
            return f"CMO agent hatasi: {e}"
