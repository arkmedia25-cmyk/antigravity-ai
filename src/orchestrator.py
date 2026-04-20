import re
from src.agents.cmo_agent import CmoAgent
from src.agents.content_agent import ContentAgent
from src.agents.sales_agent import SalesAgent
from src.agents.research_agent import ResearchAgent
from src.agents.email_agent import EmailAgent
from src.agents.linkedin_agent import LinkedInAgent
from src.agents.video_producer_agent import VideoProducerAgent
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
    "video_producer": VideoProducerAgent,
}

from src.core.protocol import SwarmMessage

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
            cleaned_text = text.replace(match.group(0), "").strip()
            return brand_name, cleaned_text
        return "glowup", text # Default brand

    def handle_request(self, input_text: str, agent: str = "cmo", chat_id=None) -> str:
        """
        Main entry point for the Agency Swarm.
        Handles both single agent requests and multi-agent chains.
        """
        brand_name, clean_text = self._extract_brand(input_text)
        
        # [MEMORY] Load user context
        context = {}
        if chat_id:
            # Shared memory between agents for this interaction
            interaction_data = {}
            
            history = self.memory.load("last_3_tasks", chat_id=chat_id) or []
            context["history"] = history
            context["user_profile"] = self.memory.get_user_profile(chat_id)
            
            self.memory.track_interaction(chat_id, agent, clean_text)
            self.memory.track_last_tasks(chat_id, clean_text)

        current_agent_name = agent
        current_input = clean_text
        accumulated_content = []
        final_data = {}
        chain_depth = 0
        max_depth = 5 

        final_message = None

        while current_agent_name and chain_depth < max_depth:
            logger.info(f"[Orchestrator] Turn {chain_depth+1}: Sending to [{current_agent_name}]")
            
            selected_agent = self.agents.get(current_agent_name)
            if not selected_agent:
                final_message = SwarmMessage(sender="system", content=f"Unknown agent: {current_agent_name}", status="error")
                break
            
            try:
                message = selected_agent.process(
                    current_input, 
                    chat_id=chat_id
                )
                
                # Accummulate content only if it's not a duplication of input
                if message.content and message.content not in accumulated_content:
                    accumulated_content.append(message.content)
                
                # Merge data payloads
                if hasattr(message, 'data') and message.data:
                    final_data.update(message.data)

                final_message = message

                # Check for delegation
                if hasattr(message, 'next_agent') and message.next_agent:
                    current_agent_name = message.next_agent
                    # Next agent only gets the LATEST content as input to stay focused
                    current_input = message.content 
                    chain_depth += 1
                    logger.info(f"[Orchestrator] Delegating to next agent: {current_agent_name}")
                else:
                    break
                    
            except Exception as e:
                logger.error(f"Error in agent chain [{current_agent_name}]: {e}", exc_info=True)
                final_message = SwarmMessage(sender="system", content=f"Sistem hatası ({current_agent_name}): {str(e)}", status="error")
                break

        if final_message:
            # JOIN all unique contents from the chain
            final_message.content = "\n\n---\n\n".join(accumulated_content)
            final_message.data = final_data
            
        return final_message
