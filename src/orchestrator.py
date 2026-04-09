import re
from src.agents.cmo_agent import CmoAgent
from src.agents.content_agent import ContentAgent
from src.agents.sales_agent import SalesAgent
from src.agents.research_agent import ResearchAgent
from src.agents.email_agent import EmailAgent
from src.agents.linkedin_agent import LinkedInAgent
from src.core.brand_manager import BrandManager
from src.memory.memory_manager import MemoryManager
from src.core.logging import get_logger

logger = get_logger("orchestrator")

_AGENTS = {
    "cmo": CmoAgent,
    "content": ContentAgent,
    "sales": SalesAgent,
    "research": ResearchAgent,
    "email": EmailAgent,
    "linkedin": LinkedInAgent,
}

class Orchestrator:
    def __init__(self):
        self.brand_manager = BrandManager()
        self.memory = MemoryManager(namespace="agency")
        self.agents = {name: cls() for name, cls in _AGENTS.items()}
        logger.debug(f"Orchestrator initialized with brands: {self.brand_manager.list_brands()}")

    def _extract_brand(self, text: str):
        """Extracts @brand from text. Returns (brand_name, cleaned_text)."""
        match = re.search(r"@(\w+)", text)
        if match:
            brand_name = match.group(1).lower()
            # Remove @brand from text
            cleaned_text = text.replace(match.group(0), "").strip()
            return brand_name, cleaned_text
        return "glowup", text # Default brand

    def handle_request(self, input_text: str, agent: str = "cmo", chat_id=None) -> str:
        brand_name, clean_text = self._extract_brand(input_text)
        brand_config = self.brand_manager.get_brand(brand_name)
        
        if not brand_config:
            logger.warning(f"Requested brand '{brand_name}' not found. Falling back to default.")
            brand_name = "glowup"
            brand_config = self.brand_manager.get_brand(brand_name)

        # [MEMORY] Load user context
        context = {}
        if chat_id:
            # Load last 3 tasks
            history = self.memory.load("last_3_tasks", chat_id=chat_id) or []
            context["history"] = history
            
            # Load funnel stage
            profile = self.memory.get_user_profile(chat_id)
            context["user_profile"] = profile
            
            # Track this interaction
            self.memory.track_interaction(chat_id, agent, clean_text)
            self.memory.track_last_tasks(chat_id, clean_text)

        logger.debug(f"Routing request to [{agent}] for brand [@{brand_name}] (chat_id={chat_id})")

        if not clean_text:
            return "[Orchestrator] Empty input — nothing to process."

        selected = self.agents.get(agent)
        if selected is None:
            return f"[Orchestrator] Unknown agent: '{agent}'."

        return selected.process(clean_text, chat_id=chat_id, brand=brand_name, context=context)
