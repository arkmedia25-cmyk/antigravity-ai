from src.agents.cmo_agent import CmoAgent
from src.agents.content_agent import ContentAgent
from src.agents.sales_agent import SalesAgent
from src.agents.research_agent import ResearchAgent
from src.agents.email_agent import EmailAgent
from src.agents.linkedin_agent import LinkedInAgent
from src.agents.canva_agent import CanvaAgent
from src.core.logging import get_logger

logger = get_logger("orchestrator")

_AGENTS = {
    "cmo": CmoAgent,
    "content": ContentAgent,
    "sales": SalesAgent,
    "research": ResearchAgent,
    "email": EmailAgent,
    "linkedin": LinkedInAgent,
    "canva": CanvaAgent,
}


class Orchestrator:
    def __init__(self):
        self.agents = {name: cls() for name, cls in _AGENTS.items()}
        logger.debug(f"Orchestrator initialized with agents: {list(self.agents.keys())}")

    @property
    def cmo(self):
        """Backward-compatible access to the CMO agent."""
        return self.agents["cmo"]

    def handle_request(self, input_text: str, agent: str = "cmo", chat_id=None) -> str:
        logger.debug(f"Routing request to [{agent}] (chat_id={chat_id}): {input_text[:100]}")

        if not input_text or not input_text.strip():
            logger.debug("Empty input received")
            return "[Orchestrator] Empty input — nothing to process."

        selected = self.agents.get(agent)
        if selected is None:
            logger.warning(f"Unknown agent requested: {agent}")
            return f"[Orchestrator] Unknown agent: '{agent}'. Available: {', '.join(self.agents)}"

        return selected.process(input_text, chat_id=chat_id)
