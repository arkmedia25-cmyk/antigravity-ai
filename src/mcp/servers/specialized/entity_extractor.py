import json
import logging
from mcp.server.fastmcp import FastMCP
from src.skills.ai_client import ask_ai

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def extract_entities(text: str) -> str:
        """
        Identifies key concepts, wellness terms, and critical data points. (Pillar 17)
        """
        msgs = [{"role": "system", "content": "Extract core entities as CSV."}, {"role": "user", "content": text}]
        entities = ask_ai(msgs)
        return json.dumps({"status": "extracted", "entities": str(entities).split(',')})
