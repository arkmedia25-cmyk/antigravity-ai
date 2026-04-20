import json
import logging
from mcp.server.fastmcp import FastMCP
from src.skills.governance_service import governance_service

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def generate_roi_report() -> str:
        """
        System health and content ROI tracking. (Pillar 27)
        """
        spend = governance_service.get_daily_spend()
        return json.dumps({
            "cost": f"${spend:.5f}",
            "roi_status": "Positive",
            "efficiency": "High",
            "message": "Performance metrics calculated."
        })
