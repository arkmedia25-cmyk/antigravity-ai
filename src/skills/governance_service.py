import sqlite3
import time
import os
import json
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class GovernanceService:
    """Manages AI costs, rate limits, and cross-provider budget safety."""
    
    def __init__(self, db_path: str = "data/governance.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            # Table for tracking costs per model/day
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_spend (
                    day DATE PRIMARY KEY,
                    total_cost REAL DEFAULT 0,
                    request_count INTEGER DEFAULT 0
                )
            """)
            # Table for rate limits (Sliding window)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model TEXT,
                    tokens INTEGER,
                    timestamp REAL
                )
            """)

    def track_spend(self, cost: float):
        day = time.strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO daily_spend (day, total_cost, request_count) 
                VALUES (?, ?, 1)
                ON CONFLICT(day) DO UPDATE SET 
                total_cost = total_cost + excluded.total_cost,
                request_count = request_count + 1
            """, (day, cost))

    def get_daily_spend(self) -> float:
        day = time.strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT total_cost FROM daily_spend WHERE day = ?", (day,)).fetchone()
            return row[0] if row else 0.0

    def check_rate_limit(self, model: str, incoming_tokens: int, window_sec: int = 60) -> Tuple[bool, str]:
        """
        Implements a sliding window rate limit check.
        Returns (is_allowed, reason).
        """
        now = time.time()
        cutoff = now - window_sec
        
        # Hardcoded limits for Antigravity Tier (Example)
        LIMITS = {
            "gpt-4o": 30000,
            "gpt-4o-mini": 1000000,
            "claude-3-5-sonnet-20240620": 40000
        }
        limit = LIMITS.get(model, 10000)

        with sqlite3.connect(self.db_path) as conn:
            # Cleanup old logs
            conn.execute("DELETE FROM rate_logs WHERE timestamp < ?", (cutoff,))
            
            # Count current tokens
            row = conn.execute("SELECT SUM(tokens) FROM rate_logs WHERE model = ? AND timestamp >= ?", (model, cutoff)).fetchone()
            current_tokens = row[0] or 0
            
            if current_tokens + incoming_tokens > limit:
                wait_time = window_sec - (now - conn.execute("SELECT MIN(timestamp) FROM rate_logs WHERE model = ?", (model,)).fetchone()[0])
                return False, f"Rate limit reached for {model}. Wait {int(wait_time)}s. ({current_tokens}/{limit} tokens used)"
            
            # Log this request
            conn.execute("INSERT INTO rate_logs (model, tokens, timestamp) VALUES (?, ?, ?)", (model, incoming_tokens, now))
            return True, "Allowed"

# Global Instance
governance_service = GovernanceService()
