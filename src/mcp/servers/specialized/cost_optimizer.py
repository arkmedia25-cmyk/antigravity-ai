import json
import logging
from mcp.server.fastmcp import FastMCP
from src.skills.governance_service import governance_service

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def check_daily_budget() -> str:
        """
        Verifies if current daily spend exceeds limits. (Pillar 3)
        """
        current_spend = governance_service.get_daily_spend()
        if current_spend > 5.0:
            return json.dumps({"status": "blocked", "reason": "Daily budget limit reached ($5).", "spend": current_spend})
        return json.dumps({"status": "allowed", "spend": current_spend})
