import sqlite3
import time
import os
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class PromptService:
    """Manages the lifecycle, versioning, and retrieval of agent prompts."""
    
    def __init__(self, db_path: str = "data/prompts_vcs.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    is_active INTEGER DEFAULT 1,
                    created_at REAL,
                    description TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_prompt_name ON prompts(name)")

    def save_prompt(self, name: str, content: str, description: str = "") -> int:
        """Saves a new version of a prompt and sets it as active."""
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            # Deactivate previous versions
            conn.execute("UPDATE prompts SET is_active = 0 WHERE name = ?", (name,))
            
            # Get next version number
            row = conn.execute("SELECT MAX(version) FROM prompts WHERE name = ?", (name,)).fetchone()
            next_version = (row[0] or 0) + 1
            
            cursor = conn.execute("""
                INSERT INTO prompts (name, content, version, is_active, created_at, description)
                VALUES (?, ?, ?, 1, ?, ?)
            """, (name, content, next_version, now, description))
            return cursor.lastrowid

    def get_prompt(self, name: str, version: Optional[int] = None) -> Optional[str]:
        """Retrieves an active or specific version of a prompt."""
        with sqlite3.connect(self.db_path) as conn:
            if version:
                row = conn.execute("SELECT content FROM prompts WHERE name = ? AND version = ?", (name, version)).fetchone()
            else:
                row = conn.execute("SELECT content FROM prompts WHERE name = ? AND is_active = 1", (name,)).fetchone()
            return row[0] if row else None

    def list_history(self, name: str) -> List[Dict]:
        """Returns the version history of a prompt."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT version, created_at, description FROM prompts WHERE name = ? ORDER BY version DESC", (name,)).fetchall()
            return [{"version": r[0], "created_at": r[1], "description": r[2]} for r in rows]

# Global Instance
prompt_service = PromptService()
