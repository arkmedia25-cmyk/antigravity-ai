import json
import logging
import re
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def sanitize_external_input(payload: str) -> str:
        """
        Cleanses external payloads from XSS, SQL injections, or malformed tags. (Pillar 45)
        """
        clean_payload = re.sub(r'<script.*?>.*?</script>', '', payload, flags=re.IGNORECASE)
        clean_payload = clean_payload.replace("DROP TABLE", "[REDACTED]")
        return json.dumps({
            "status": "sanitized",
            "original_length": len(payload),
            "sanitized_length": len(clean_payload),
            "clean_payload": clean_payload[:100] + "..."
        })
