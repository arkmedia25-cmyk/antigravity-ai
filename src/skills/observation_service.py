import os
import json
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ObservationService:
    """Records AI interactions to enable continuous learning (Phase 5)."""
    
    def __init__(self, log_dir: str = ".brain/observations"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        # Unique log file per session to avoid lock contention
        self.current_log = os.path.join(self.log_dir, f"obs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl")

    def record(self, provider: str, model: str, messages: list, result: str, metadata: dict = None):
        """Records a single AI interaction."""
        observation = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "messages": messages,
            "result": str(result)[:2000],  # Truncate very long results in logs
            "metadata": metadata or {}
        }
        
        try:
            with open(self.current_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(observation) + "\n")
        except Exception as e:
            logger.error(f"Failed to record observation: {e}")

# Global instance
observation_service = ObservationService()
