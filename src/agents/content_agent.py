from agents.base_agent import BaseAgent
from agents.agent_utils import load_memory_context, load_agent_prompt, build_funnel_context
from memory.memory_manager import MemoryManager
from skills.ai_client import ask_ai


class ContentAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="content")
        self.memory = MemoryManager(namespace=self.name)
        self._system_prompt = load_agent_prompt("content-agent", "content_prompt.txt")

    def process(self, input_data: str, chat_id=None, brand: str = "holisti") -> str:
        self.logger.debug(f"Processing content task for {brand}: {input_data[:100]}")
        self.memory.save(f"{brand}:last_task", input_data, chat_id=chat_id)

        response = self._call_ai(input_data, chat_id=chat_id, brand=brand)

        self.memory.save(f"{brand}:last_response", response, chat_id=chat_id)
        return response

    def _call_ai(self, task: str, chat_id=None, brand: str = "holisti") -> str:
        try:
            memory_context = load_memory_context()
            funnel_context = build_funnel_context(chat_id)
            
            # Load Brand-Specific Personality
            personality_file = f"{brand}_personality.txt"
            personality_path = os.path.join(os.getcwd(), "agents", personality_file)
            personality_text = ""
            if os.path.exists(personality_path):
                with open(personality_path, "r", encoding="utf-8") as f:
                    personality_text = f.read()

            funnel_block = f"\n{funnel_context}\n" if funnel_context else ""

            full_prompt = (
                f"{self._system_prompt}\n\n"
                f"=== SQUAD MANIFESTO - ACT AS THIS SQUAD ===\n{personality_text}\n\n"
                f"=== SYSTEEMGEHEUGEN ({brand}) ===\n{memory_context}"
                f"{funnel_block}\n"
                f"=== TAAK ===\n{task}"
            )

            return ask_ai(full_prompt)

        except Exception as e:
            self.logger.error(f"ContentAgent AI call failed: {e}")
            return f"Content agent hatası: {e}"
