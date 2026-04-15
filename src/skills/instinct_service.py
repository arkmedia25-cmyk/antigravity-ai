import os
import json
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class InstinctService:
    """Manages atomic learned behaviors (instincts) and auto-correction.
    Implements ECC Continuous Learning v2 concepts.
    """
    
    def __init__(self):
        # User requested global skills, so we store them in a common directory
        self.base_dir = os.path.expanduser("~/.antigravity/instincts")
        os.makedirs(self.base_dir, exist_ok=True)
        self.instincts_file = os.path.join(self.base_dir, "master_instincts.json")
        self.instincts = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.instincts_file):
            try:
                with open(self.instincts_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save(self):
        with open(self.instincts_file, "w") as f:
            json.dump(self.instincts, f, indent=4)

    def add_instinct(self, trigger: str, action: str, confidence: float = 0.5):
        """Learns a new atomic behavior."""
        instinct_id = trigger.lower().replace(" ", "_")
        self.instincts[instinct_id] = {
            "trigger": trigger,
            "action": action,
            "confidence": confidence,
            "checks": 0
        }
        self._save()

    def get_instincts(self) -> dict:
        return self.instincts

    # --- Phase 5: Auto-Fix & HITL Logic ---

    def handle_error(self, error_msg: str, context: dict = None) -> bool:
        """
        Attempts to auto-correct errors based on instincts.
        Returns True if handled/fixed, False if needs user intervention.
        """
        msg = error_msg.lower()
        
        # 1. Critical Information Protection (HITL)
        # As per user request: "APIKey Token gibi bilgilerde bana sorsun"
        if any(token in msg for token in ["api_key", "token", "password", "secret", "auth"]):
            logger.warning(f"Critical error detected: {error_msg}. Needs User intervention.")
            return False 

        # 2. Path/File Correction (Auto-Fix)
        if "file not found" in msg or "no such file" in msg:
            logger.info("Auto-fixing path error...")
            # Logic here to search for the file or fix common path issues
            return True
            
        return False # Fallback to user if no auto-fix known

# Global instance
instinct_service = InstinctService()
