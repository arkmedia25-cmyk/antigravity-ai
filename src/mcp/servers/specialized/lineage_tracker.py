import json
import logging
from mcp.server.fastmcp import FastMCP
from src.skills.graph_service import graph_service

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def track_asset_lineage(entity_id: str) -> str:
        """
        Provides full traceability of every project's production history. (Pillar 9)
        """
        lineage = graph_service.get_lineage(entity_id)
        if not lineage:
            return json.dumps({"status": "error", "message": "No lineage found."})
        return json.dumps({"status": "success", "entity": entity_id, "lineage": lineage})
