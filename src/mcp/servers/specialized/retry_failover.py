import json
import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def trigger_failover(provider: str, error_message: str) -> str:
        """
        Manages the fallback logic when an AI provider fails. (Pillars 5-6)
        """
        fallbacks = {"anthropic": "openai", "openai": "google", "google": "anthropic"}
        new_provider = fallbacks.get(provider, "openai")
        return json.dumps({
            "status": "recovering",
            "original_error": error_message,
            "fallback_provider": new_provider,
            "action": "Retrying task..."
        })
