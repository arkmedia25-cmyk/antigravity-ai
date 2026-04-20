import json
import logging
from mcp.server.fastmcp import FastMCP
from src.skills.governance_service import governance_service

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def check_rate_limits(model: str, estimated_tokens: int) -> str:
        """
        Verifies if API constraints (TPM/RPM) allow this task. (Pillar 7)
        """
        allowed, msg = governance_service.check_rate_limit(model, estimated_tokens)
        if not allowed:
            return json.dumps({"status": "blocked", "reason": msg})
        return json.dumps({"status": "allowed", "model": model})
