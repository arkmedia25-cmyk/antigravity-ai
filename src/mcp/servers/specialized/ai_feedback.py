import json
import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def provide_agent_feedback(task_id: str, feedback: str) -> str:
        """
        Allows agents to leave peer reviews for each other. (Pillar 26)
        """
        return json.dumps({
            "status": "logged",
            "task_id": task_id,
            "feedback": feedback,
            "action": "Context will be fed to self_learner logic."
        })
