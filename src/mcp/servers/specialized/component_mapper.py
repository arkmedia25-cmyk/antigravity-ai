import json
import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def map_cms_components(raw_content: dict, cms_schema: str) -> str:
        """
        Maps unstructured generated text (Hooks, CTAs) into strict CMS object schemas. (Pillar 41)
        """
        mapped = {
             "hero_title": raw_content.get("hook", "Default Hook"),
             "body_html": f"<p>{raw_content.get('body', '')}</p>",
             "cta_button": raw_content.get("cta", "Click Here")
        }
        return json.dumps({"status": "mapped", "schema": cms_schema, "cms_payload": mapped})
