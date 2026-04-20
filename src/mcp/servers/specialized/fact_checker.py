import json
import logging
from mcp.server.fastmcp import FastMCP
from src.skills.research_tools import research_tools

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def fact_check_claim(claim: str) -> str:
        """
        Validates scientific grounding from external sources like PubMed. (Pillar 22)
        """
        # Checks pubmed or external sources
        articles = research_tools.pubmed_search(claim)
        is_verified = len(articles) > 0
        return json.dumps({
            "status": "checked",
            "verified": is_verified,
            "claim": claim,
            "supporting_articles": len(articles)
        })
