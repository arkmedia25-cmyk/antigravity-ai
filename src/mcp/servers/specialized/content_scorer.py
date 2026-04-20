import json
import logging
from mcp.server.fastmcp import FastMCP
from src.skills.ai_client import ask_ai

logger = logging.getLogger(__name__)

def register(mcp: FastMCP):
    @mcp.tool()
    def score_content_quality(content: str) -> str:
        """
        Pre-publish psychological and structural quality evaluation (Agent-Eval). (Pillar 18)
        """
        eval_prompt = f"Rate the neuro-linguistic impact of this text out of 10. Output only the number.\n\n{content}"
        msgs = [{"role": "system", "content": "You are a stringent content evaluator."}, {"role": "user", "content": eval_prompt}]
        score_resp = str(ask_ai(msgs, use_mcp=False)).strip()
        try:
            score = float(score_resp)
        except ValueError:
            score = 5.0
        return json.dumps({"status": "scored", "score": score, "verdict": "Pass" if score >= 7.0 else "Fail"})
