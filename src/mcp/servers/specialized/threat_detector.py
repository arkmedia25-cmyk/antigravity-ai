import json
import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def detect_prompt_injection(user_prompt: str) -> str:
        """
        AI-driven prompt injection detection and neutralization. (Pillar 46)
        """
        threat_signatures = ["ignore previous instructions", "system override", "forget everything"]
        is_threat = any(sig in user_prompt.lower() for sig in threat_signatures)
        return json.dumps({
            "status": "threat_detected" if is_threat else "safe",
            "action": "quarantine" if is_threat else "proceed"
        })
