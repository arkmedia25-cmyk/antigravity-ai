import json
import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def check_execution_permission(role: str, action: str) -> str:
        """
        Restricts destructive actions to Admin-level Swarm roles (RBAC). (Pillar 44)
        """
        destructive_actions = ["drop_table", "delete_file", "broadcast_email"]
        if action in destructive_actions and role != "admin":
             return json.dumps({"status": "denied", "reason": "Insufficient clearance for destructive action."})
        return json.dumps({"status": "granted", "action": action})
