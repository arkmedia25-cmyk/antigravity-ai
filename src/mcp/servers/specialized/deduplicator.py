import json
import logging
from mcp.server.fastmcp import FastMCP
from src.skills.dedup_service import dedup_service

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def check_for_duplicates(topic: str) -> str:
        """
        Prevents redundant actions and duplicated research globally. (Pillar 8)
        """
        if dedup_service.is_duplicate(topic):
             return json.dumps({"status": "duplicate", "action": "blocked", "topic": topic})
        
        # Log as new
        dedup_service.log_topic(topic)
        return json.dumps({"status": "unique", "action": "allowed", "topic": topic})
