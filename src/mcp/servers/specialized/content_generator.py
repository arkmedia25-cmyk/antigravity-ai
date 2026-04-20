import json
import logging
from mcp.server.fastmcp import FastMCP
from src.skills.ai_client import ask_ai

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def generate_viral_content(topic: str, structure: str = "Hook-Body-CTA") -> str:
        """
        Generates structured, high-impact content scripts. (Pillar 11)
        """
        msgs = [
            {"role": "system", "content": f"You produce viral content following '{structure}' format."},
            {"role": "user", "content": f"Topic: {topic}"}
        ]
        script = ask_ai(msgs)
        return json.dumps({
            "status": "generated",
            "topic": topic,
            "structure": structure,
            "script": str(script)
        })
