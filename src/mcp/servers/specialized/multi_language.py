import json
import logging
from mcp.server.fastmcp import FastMCP
from src.skills.ai_client import ask_ai

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def translate_content(text: str, target_language: str) -> str:
        """
        Provides high-context localization and translation. (Pillar 15)
        """
        msgs = [
            {"role": "system", "content": "You are a senior localizer. Retain tone and context."},
            {"role": "user", "content": f"Translate to {target_language}:\n\n{text}"}
        ]
        translated = ask_ai(msgs)
        return json.dumps({
            "status": "translated",
            "target_language": target_language,
            "text": str(translated)
        })
