from src.agents.base_agent import BaseAgent
from src.agents.agent_utils import load_memory_context, load_agent_prompt, build_funnel_context
from src.skills.ai_client import ask_ai
from src.core.protocol import SwarmMessage

class LinkedInAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="linkedin")
        self._system_prompt = load_agent_prompt("linkedin-agent", "linkedin_prompt.txt")

    def process(self, input_data: str, chat_id=None, brand: str = "glowup", context: dict = None) -> SwarmMessage:
        self.logger.debug(f"Processing LinkedIn task: {input_data[:100]}")
        
        history_str = ""
        if context and context.get("history"):
             history_str = "\nConversation History:\n" + "\n".join([f"- {t}" for t in context["history"]])

        return self._call_ai(input_data, history=history_str, chat_id=chat_id)

    def _call_ai(self, task: str, history: str = "", chat_id=None) -> SwarmMessage:
        try:
            memory_context = load_memory_context()
            funnel_context = build_funnel_context(chat_id)

            funnel_block = f"\n{funnel_context}\n" if funnel_context else ""

            full_prompt = (
                f"{self._system_prompt}\n\n"
                f"=== SYSTEM KNOWLEDGE ===\n{memory_context}"
                f"{funnel_block}\n"
                f"=== CONVERSATION HISTORY ===\n{history}\n\n"
                f"TAAK: {task}\n\n"
                f"Geef een volledig uitgewerkt LinkedIn bericht of strategie."
            )

            response = ask_ai(full_prompt)
            return SwarmMessage(
                sender=self.name,
                content=response,
                status="success"
            )

        except Exception as e:
            self.logger.error(f"LinkedIn AI call failed: {e}")
            return SwarmMessage(
                sender=self.name,
                content=f"LinkedIn agent fout: {e}",
                status="error"
            )
