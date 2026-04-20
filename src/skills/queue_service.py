import sqlite3
import json
import time
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class QueueService:
    """A robust SQLite-based priority queue for managing autonomous tasks."""
    
    def __init__(self, db_path: str = "data/jobs_v2.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    task_type TEXT NOT NULL,
                    brand TEXT,
                    payload TEXT NOT NULL,
                    priority INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'pending',
                    progress INTEGER DEFAULT 0,
                    result TEXT,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    retries INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3
                )
            """)
            # Index for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status_priority ON jobs(status, priority DESC, created_at ASC)")

    def enqueue(self, task_type: str, payload: Dict, brand: str = "general", priority: int = 1) -> str:
        job_id = f"job-{int(time.time() * 1000)}"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO jobs (job_id, task_type, brand, payload, priority) VALUES (?, ?, ?, ?, ?)",
                (job_id, task_type, brand, json.dumps(payload), priority)
            )
        logger.info(f"📥 Job {job_id} enqueued (Priority: {priority})")
        return job_id

    def get_next_job(self) -> Optional[Dict]:
        """Fetches the highest priority pending job."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM jobs WHERE status = 'pending' ORDER BY priority DESC, created_at ASC LIMIT 1"
            )
            row = cursor.fetchone()
            if row:
                job = dict(row)
                job['payload'] = json.loads(job['payload'])
                # Mark as processing immediately to avoid double fetching
                conn.execute("UPDATE jobs SET status = 'processing', updated_at = CURRENT_TIMESTAMP WHERE job_id = ?", (job['job_id'],))
                return job
        return None

    def update_status(self, job_id: str, status: str, progress: int = None, result: Any = None, error: str = None):
        with sqlite3.connect(self.db_path) as conn:
            query = "UPDATE jobs SET status = ?, updated_at = CURRENT_TIMESTAMP"
            params = [status]
            if progress is not None:
                query += ", progress = ?"
                params.append(progress)
            if result is not None:
                query += ", result = ?"
                params.append(json.dumps(result))
            if error is not None:
                query += ", error = ?"
                params.append(error)
            
            query += " WHERE job_id = ?"
            params.append(job_id)
            conn.execute(query, tuple(params))

    def get_job_status(self, job_id: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
            row = cursor.fetchone()
            if row:
                job = dict(row)
                job['payload'] = json.loads(job['payload'])
                if job['result']: job['result'] = json.loads(job['result'])
                return job
        return None

# Global Instance
queue_service = QueueService()
