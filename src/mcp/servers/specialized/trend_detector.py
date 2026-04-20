import json
import logging
import time
from mcp.server.fastmcp import FastMCP
from src.skills.research_tools import research_tools
from src.skills.ai_client import ask_ai

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def detect_viral_trends(niche: str = "wellness") -> str:
        """
        Scans global trends for niche-specific viral potential. (Pillar 28)
        """
        query = f"trending {niche} topics and biohacking news {time.strftime('%Y')}"
        trends = research_tools.google_search(query, num_results=3)
        return json.dumps({
            "status": "trends_found",
            "niche": niche,
            "raw_data_points": len(trends),
            "data": trends
        })
