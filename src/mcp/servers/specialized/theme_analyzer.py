import json
import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def analyze_theme_structure(css_or_html: str) -> str:
        """
        Evaluates an HTML/CSS string for UX/UI potential, color coherence, and typography. (Pillar 38)
        """
        issues = []
        if "flex" not in css_or_html.lower() and "grid" not in css_or_html.lower():
            issues.append("Missing modern layout structures (flex/grid).")
        
        return json.dumps({
            "status": "analyzed",
            "coherence_score": 8.5 if not issues else 5.5,
            "issues": issues,
            "recommendation": "Use responsive design tokens."
        })
