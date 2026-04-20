import sqlite3
import hashlib
import time
import os
import json
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class DedupService:
    """Prevents redundant AI production by tracking content hashes."""
    
    def __init__(self, db_path: str = "data/dedup.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS content_hashes (
                    hash TEXT PRIMARY KEY,
                    content_type TEXT NOT NULL, -- 'script', 'image', 'research'
                    created_at REAL,
                    metadata_json TEXT
                )
            """)

    def _generate_hash(self, content: str) -> str:
        return hashlib.sha256(content.strip().encode('utf-8')).hexdigest()

    def is_duplicate(self, content: str) -> bool:
        """Checks if the exact content has been produced before."""
        h = self._generate_hash(content)
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT hash FROM content_hashes WHERE hash = ?", (h,)).fetchone()
            return row is not None

    def register_content(self, content: str, content_type: str, metadata: Optional[Dict] = None):
        """Registers a new piece of content to prevent future duplicates."""
        h = self._generate_hash(content)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR IGNORE INTO content_hashes (hash, content_type, created_at, metadata_json)
                VALUES (?, ?, ?, ?)
            """, (h, content_type, time.time(), json.dumps(metadata or {})))

# Global Instance
dedup_service = DedupService()
