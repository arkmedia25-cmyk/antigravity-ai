from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.orchestrator import Orchestrator
import os

app = FastAPI(title="Antigravity Agency OS API")

# Enable CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

class RequestModel(BaseModel):
    input_text: str
    agent: Optional[str] = "cmo"
    chat_id: Optional[str] = "web_user"

@app.get("/health")
def health():
    return {"status": "ok", "service": "Antigravity AI Bot - OK"}

@app.post("/api/chat")
async def chat_endpoint(req: RequestModel):
    """
    Main API endpoint for the Agency OS Dashboard chat/command interface.
    """
    try:
        response = orchestrator.handle_request(
            input_text=req.input_text,
            agent=req.agent,
            chat_id=req.chat_id
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents")
async def get_agents():
    """Returns the list of available swarm agents."""
    return {"agents": list(orchestrator.agents.keys())}

# Serve the static dashboard files (we will create these next)
# app.mount("/", StaticFiles(directory="src/interfaces/web/dashboard", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
