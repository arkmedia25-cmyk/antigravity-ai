import os
import json
import uuid
import time
from typing import Dict, List, Optional
from src.core.logging import get_logger

logger = get_logger("core.task_queue")

class TaskQueue:
    def __init__(self, storage_path="outputs/task_queue.json"):
        self.storage_path = storage_path
        self.tasks: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
                logger.info(f"Loaded {len(self.tasks)} tasks from queue.")
            except Exception as e:
                logger.error(f"Failed to load task queue: {e}")
                self.tasks = {}

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save task queue: {e}")

    def add_task(self, chat_id, user_topic, brand, task_type="video") -> str:
        task_id = f"{int(time.time())}_{uuid.uuid4().hex[:4]}"
        self.tasks[task_id] = {
            "id": task_id,
            "chat_id": chat_id,
            "topic": user_topic,
            "brand": brand,
            "type": task_type,
            "status": "pending",
            "created_at": time.time(),
            "retry_count": 0
        }
        self._save()
        return task_id

    def update_status(self, task_id: str, status: str, error: str = None):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            if error:
                self.tasks[task_id]["last_error"] = error
            if status in ["completed", "failed"] and self.tasks[task_id].get("retry_count", 0) < 3:
                # We keep them for a while. If failed, might retry.
                pass 
            if status == "completed":
                del self.tasks[task_id] # Clean up completed tasks
            self._save()

    def get_pending_tasks(self) -> List[dict]:
        return [t for t in self.tasks.values() if t["status"] in ["pending", "in_progress"]]

task_queue = TaskQueue()
