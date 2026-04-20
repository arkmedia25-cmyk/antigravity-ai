import json
import logging
import os
import sys
from typing import List, Dict, Optional

# Ensure root is in path
_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_FILE_DIR, "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mcp.server.fastmcp import FastMCP
from src.skills.graph_service import graph_service

logger = logging.getLogger(__name__)

def register_graph_db_tools(mcp: FastMCP):
    """Registers standalone Pillar 30 tools for Knowledge Mapping and Lineage."""

    @mcp.tool()
    def add_node(node_id: str, node_type: str, label: str, data: Optional[Dict] = None) -> str:
        """
        Registers a new entity node in the Knowledge Graph. (Pillar 30)
        Types: 'research', 'script', 'video', 'budget'.
        """
        graph_service.add_node(node_id, node_type, label, data)
        return json.dumps({"status": "created", "id": node_id, "type": node_type})

    @mcp.tool()
    def map_task_relationship(parent_id: str, child_id: str, relation_type: str) -> str:
        """
        Creates a semantic link between two entities (e.g. Research linked to Script). (Pillar 30)
        """
        success = graph_service.add_relation(parent_id, child_id, relation_type)
        return json.dumps({
            "status": "linked" if success else "failed",
            "parent": parent_id,
            "child": child_id,
            "relation": relation_type
        })

    @mcp.tool()
    def query_task_lineage(entity_id: str) -> str:
        """
        Retrieves the full production history for an asset. 
        Shows all parent and child nodes in the Graph. (Pillar 9/30)
        """
        lineage = graph_service.get_lineage(entity_id)
        return json.dumps({"origin": entity_id, "lineage": lineage})

    @mcp.tool()
    def get_collective_memory(topic: str) -> str:
        """
        Searches the Graph DB for everything the system knows about a specific topic. (Pillar 30)
        Returns the collective knowledge of all past tasks.
        """
        knowledge = graph_service.query_knowledge(topic)
        return json.dumps({
            "query": topic,
            "system_knowledge": knowledge,
            "context": "Recall successful. Context injected into current task loop."
        })

logger.info("Graph DB tools registered successfully.")
