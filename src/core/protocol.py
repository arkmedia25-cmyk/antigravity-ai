from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class SwarmMessage(BaseModel):
    """
    Standard communication protocol for Antigravity Agency Swarm.
    Allows agents to pass data, results, and delegation requests.
    """
    sender: str = Field(..., description="The name of the agent sending the message.")
    recipient: str = Field("orchestrator", description="The intended recipient (agent name or 'orchestrator').")
    content: str = Field(..., description="The textual response or instruction.")
    data: Dict[str, Any] = Field(default_factory=dict, description="Structured data payload (e.g., search results, video paths).")
    next_agent: Optional[str] = Field(None, description="Request to pass control to another agent.")
    status: str = Field("success", description="Status of the agent's work (success, error, need_info).")
    
    def to_json(self):
        return self.model_dump()
