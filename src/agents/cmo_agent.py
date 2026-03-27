import os

from agents.base_agent import BaseAgent
from agents.agent_utils import load_memory_context, build_funnel_context
from memory.memory_manager import MemoryManager
from skills.ai_client import ask_ai

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _load_cmo_prompt() -> str:
    path = os.path.join(_PROJECT_ROOT, "agents", "cmo-agent", "cmo.txt")
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
        self.memory.save("last_task", input_data, chat_id=chat_id)

        response = self._call_ai(input_data, chat_id=chat_id)

        self.memory.save("last_response", response, chat_id=chat_id)
        return response

    def _call_ai(self, task: str, chat_id=None) -> str:
        try:
            cmo_prompt = _load_cmo_prompt()
            memory_context = load_memory_context()
            funnel_context = build_funnel_context(chat_id)

            funnel_block = f"\n{funnel_context}\n" if funnel_context else ""

            full_prompt = (
                f"{cmo_prompt}\n\n"
                f"=== SYSTEEMGEHEUGEN ===\n{memory_context}"
                f"{funnel_block}\n"
                f"=== TAAK ===\n{task}\n\n"
                f"Respond in a structured way:\n"
                f"1. Summary\n"
                f"2. Strategy Options\n"
                f"3. Best Recommendation\n"
                f"4. Next Action Steps"
            )

            return ask_ai(full_prompt)

        except Exception as e:
            self.logger.error(f"AI call failed: {e}")
            return f"CMO agent hatasi: {e}"
