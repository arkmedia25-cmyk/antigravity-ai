import json
import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def route_model(task_description: str) -> str:
        """
        Intelligently selects the best-suited AI model (Cost vs Quality). (Pillar 1-2)
        """
        text_len = len(task_description)
        if any(kw in task_description.lower() for kw in ["video", "reel", "üret", "render"]):
            result = {"provider": "openai", "model": "gpt-4o", "reason": "Complex media task."}
        elif text_len > 3000:
            result = {"provider": "anthropic", "model": "claude-3-5-sonnet-20240620", "reason": "High context load."}
        else:
            result = {"provider": "openai", "model": "gpt-4o-mini", "reason": "Daily simple task."}
        return json.dumps(result)
