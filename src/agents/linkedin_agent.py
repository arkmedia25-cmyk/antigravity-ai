from src.agents.base_agent import BaseAgent
from src.agents.agent_utils import load_memory_context, load_agent_prompt, build_funnel_context
from src.memory.memory_manager import MemoryManager
from src.skills.ai_client import ask_ai


class LinkedInAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="linkedin")
        self.memory = MemoryManager(namespace=self.name)
        self._system_prompt = load_agent_prompt("linkedin-agent", "linkedin_prompt.txt")

    def process(self, input_data: str, chat_id=None) -> str:
        self.logger.debug(f"Processing LinkedIn task: {input_data[:100]}")
        self.memory.save("last_task", input_data, chat_id=chat_id)

        response = self._call_ai(input_data, chat_id=chat_id)

        self.memory.save("last_response", response, chat_id=chat_id)
        return response

    def _call_ai(self, task: str, chat_id=None) -> str:
        try:
            memory_context = load_memory_context()
            funnel_context = build_funnel_context(chat_id)

            funnel_block = f"\n{funnel_context}\n" if funnel_context else ""

            full_prompt = (
                f"{self._system_prompt}\n\n"
                f"=== MERK & PRODUCT CONTEXT ===\n{memory_context}"
                f"{funnel_block}\n"
                f"TAAK: {task}\n\n"
                f"Geef een volledig uitgewerkt LinkedIn bericht of strategie."
            )

            return ask_ai(full_prompt)

        except Exception as e:
            self.logger.error(f"LinkedIn AI call failed: {e}")
            return f"LinkedIn agent fout: {e}"
