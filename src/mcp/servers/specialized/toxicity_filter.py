import json
import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def check_toxicity(content: str) -> str:
        """
        Safety screening and brand tone alignment barrier. (Pillar 24)
        """
        # Basic check
        unsafe = any(word in content.lower() for word in ["cure", "guarantee", "miracle", "drug"])
        return json.dumps({
            "status": "flagged" if unsafe else "clean",
            "action": "revise" if unsafe else "approve",
            "reason": "Contains restricted medical claims." if unsafe else "Safe"
        })
