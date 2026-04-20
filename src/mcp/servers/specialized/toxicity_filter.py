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

    @mcp.tool()
    def check_safety_limits(model: str, estimated_tokens: int) -> str:
        """
        Enforces token limits and brand safety rules per model. (Pillar 19)
        """
        limits = {
            "gpt-4o-mini": 50000,
            "gpt-4o": 20000,
            "claude-3-5-sonnet-20240620": 30000
        }
        max_limit = limits.get(model, 10000)
        
        is_blocked = estimated_tokens > max_limit
        return json.dumps({
            "status": "blocked" if is_blocked else "ok",
            "reason": f"Estimated tokens {estimated_tokens} exceeds limit {max_limit} for {model}" if is_blocked else "Safe"
        })
