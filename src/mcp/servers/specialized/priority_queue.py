import json
import logging
from mcp.server.fastmcp import FastMCP
from src.skills.queue_service import queue_service

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def enqueue_job(task_type: str, payload: dict, priority: int = 1) -> str:
        """
        Adds a task to the priority queue for robust background execution. (Pillar 4)
        """
        job_id = queue_service.enqueue(task_type, payload, priority=priority)
        return json.dumps({"status": "queued", "job_id": job_id, "priority": priority})
