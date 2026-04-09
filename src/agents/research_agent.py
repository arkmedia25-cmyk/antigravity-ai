from src.agents.base_agent import BaseAgent
from src.agents.agent_utils import load_memory_context, load_agent_prompt, build_funnel_context
from src.memory.memory_manager import MemoryManager
from src.skills.ai_client import ask_ai


class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="research")
        self._system_prompt = load_agent_prompt("research-agent", "research_prompt.txt")

    def process(self, input_data: str, chat_id=None, brand: str = "glowup", context: dict = None) -> str:
        self.logger.debug(f"Processing research task: {input_data[:100]}")
        
        history_str = ""
        if context and context.get("history"):
             history_str = "\nConversation History:\n" + "\n".join([f"- {t}" for t in context["history"]])

        response = self._call_ai(input_data, history=history_str, chat_id=chat_id)
        return response

    def _call_ai(self, task: str, history: str = "", chat_id=None) -> str:
        try:
            memory_context = load_memory_context()
            funnel_context = build_funnel_context(chat_id)

            funnel_block = f"\n{funnel_context}\n" if funnel_context else ""

            full_prompt = (
                f"{self._system_prompt}\n\n"
                f"=== SYSTEM KNOWLEDGE ===\n{memory_context}"
                f"{funnel_block}\n"
                f"=== CONVERSATION HISTORY ===\n{history}\n\n"
                f"=== RESEARCH TOPIC ===\n{task}"
            )

            return ask_ai(full_prompt)

        except Exception as e:
            self.logger.error(f"ResearchAgent AI call failed: {e}")
            return f"Research agent hatası: {e}"
