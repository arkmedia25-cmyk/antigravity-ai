import logging
import json
from typing import List, Dict, Any
from src.skills.ai_client import ask_ai
from src.skills.instinct_service import instinct_service
from src.skills.observation_service import observation_service

logger = logging.getLogger(__name__)

class SwarmOrchestrator:
    """The master 'Brain' loop that implements Think-Act-Observe.
    Inspired by ECC Continuous Agent Loop and Agent-Eval patterns.
    """
    
    def __init__(self):
        self.instincts = InstinctService()
        self.observations = ObservationService()
        self.fleet_enabled = os.getenv("DEVFLEET_ENABLED", "false").lower() == "true"

    def dispatch_fleet_mission(self, title: str, prompt: str, depends_on: list = None):
        """Standardized Fleet dispatch (Phase 19). Parallel execution support."""
        if not self.fleet_enabled:
            return self.execute_goal(f"Draft: {title}\nPrompt: {prompt}")
        
        # Integration with DevFleet tools if MCP is present
        print(f"🚀 [FLEET] Dispatching mission: {title}")
        # Placeholder for tool-use dispatch_mission if MCP was active
        return {"mission_id": f"mission-{int(time.time())}", "status": "dispatched"}

    def execute_goal(self, goal: str, max_steps: int = 5):
        """Autonomous loop to achieve a high-level goal."""
        logger.info(f"🚀 Goal Received: {goal}")
        
        context = {
            "goal": goal,
            "steps_taken": [],
            "instincts": instinct_service.get_instincts()
        }
        
        for step in range(max_steps):
            # 1. THINK: Decide next action based on goal and instincts
            thought_prompt = f"""
            Goal: {goal}
            Progress: {json.dumps(context['steps_taken'])}
            Available Instincts: {json.dumps(context['instincts'])}
            
            Action plan for step {step+1}? 
            Return JSON: {{"thought": "reasoning", "action": "agent_name", "params": {{}}}}
            """
            decision = ask_ai(thought_prompt, is_json=True)
            
            # 2. ACT: Execute the planned action
            logger.info(f"🧠 Step {step+1}: {decision.get('thought')}")
            # (In a real swarm, this would call the specific agent)
            action_result = f"Executed {decision.get('action')} with success" 
            
            # 3. OBSERVE & EVALUATE (Agent-Eval pattern)
            eval_prompt = f"""
            Action attempted: {decision.get('action')}
            Result: {action_result}
            Does this meet the goal: {goal}?
            Return JSON: {{"success": true/false, "score": 0.0-1.0, "feedback": "..."}}
            """
            evaluation = ask_ai(eval_prompt, is_json=True)
            
            context['steps_taken'].append({
                "step": step+1,
                "thought": decision.get("thought"),
                "result": action_result,
                "score": evaluation.get("score")
            })
            
            if evaluation.get("success") and evaluation.get("score", 0) > 0.9:
                logger.info("🎯 Goal Achieved!")
                break
                
            # 4. LEARN: If failed, record a new instinct
            if not evaluation.get("success"):
                instinct_service.add_instinct(
                    trigger=f"Failure during {decision.get('action')}",
                    action=evaluation.get("feedback"),
                    confidence=0.3
                )

        return context

# Global Instance
orchestrator = SwarmOrchestrator()
