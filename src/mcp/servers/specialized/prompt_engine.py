import json
import logging
from mcp.server.fastmcp import FastMCP
from src.skills.prompt_service import prompt_service

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def get_golden_prompt(prompt_name: str) -> str:
        """
        Retrieves a 'Golden Prompt' from the centralized repository. (Pillar 13)
        """
        content = prompt_service.get_prompt(prompt_name)
        if not content:
            return json.dumps({"status": "error", "message": f"Prompt {prompt_name} not found"})
        return json.dumps({"status": "success", "name": prompt_name, "content": content})

    @mcp.tool()
    def rollback_prompt_version(prompt_name: str, target_version: int) -> str:
        """
        Rolls back a prompt to a previous stable state. (Pillar 14)
        """
        old_content = prompt_service.get_prompt(prompt_name, version=target_version)
        if not old_content:
            return json.dumps({"status": "error", "message": "Version not found."})
        
        # Save as the new active state
        new_id = prompt_service.save_prompt(prompt_name, old_content, f"Rolled back to v{target_version}")
        return json.dumps({"status": "rolled_back", "prompt_name": prompt_name, "active_id": new_id})
