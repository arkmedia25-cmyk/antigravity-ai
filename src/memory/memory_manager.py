"""
MemoryManager — SQLite-backed, thread-safe, namespace-scoped key-value store.

Key format in DB:
  - without chat_id : "{namespace}:{key}"
  - with    chat_id : "u{chat_id}:{namespace}:{key}"

Funnel stages (auto-assigned from interaction_count):
  0-1   → awareness
  2-4   → interest
  5-9   → consideration
  10+   → intent
"""

import json
import os
import sqlite3
import threading
from datetime import datetime, timezone

from core.logging import get_logger

logger = get_logger("memory.manager")

_DB_PATH = os.getenv(
    "MEMORY_DB_PATH",
    os.path.join(os.path.dirname(__file__), "storage", "memory.db"),
)

_FUNNEL_STAGES = [
    (0,  "awareness"),
    (2,  "interest"),
    (5,  "consideration"),
    (10, "intent"),
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _funnel_stage(count: int) -> str:
    stage = "awareness"
    for threshold, name in _FUNNEL_STAGES:
        if count >= threshold:
            stage = name
    return stage


def _ensure_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS memory (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    conn.commit()


class MemoryManager:
    def __init__(self, namespace: str = "global"):
        self.namespace = namespace
        os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        _ensure_db(self._conn)
        logger.debug(f"MemoryManager initialized (namespace={namespace})")

    # ------------------------------------------------------------------ #
    # Internal key builder                                                 #
    # ------------------------------------------------------------------ #

    def _key(self, key: str, chat_id=None) -> str:
        if chat_id is not None:
            return f"u{chat_id}:{self.namespace}:{key}"
        return f"{self.namespace}:{key}"

    # ------------------------------------------------------------------ #
    # Base operations                                                      #
    # ------------------------------------------------------------------ #

    def save(self, key: str, value, chat_id=None) -> None:
        full_key = self._key(key, chat_id)
        serialized = json.dumps(value, ensure_ascii=False)
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)",
                (full_key, serialized),
            )
            self._conn.commit()
        logger.debug(f"Saved: {full_key}")

    def load(self, key: str, chat_id=None):
        full_key = self._key(key, chat_id)
        with self._lock:
            row = self._conn.execute(
                "SELECT value FROM memory WHERE key = ?", (full_key,)
            ).fetchone()
        if row is None:
            logger.debug(f"Not found: {full_key}")
            return None
        return json.loads(row[0])

    def delete(self, key: str, chat_id=None) -> None:
        full_key = self._key(key, chat_id)
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM memory WHERE key = ?", (full_key,)
            )
            self._conn.commit()
        if cur.rowcount:
            logger.debug(f"Deleted: {full_key}")
        else:
            logger.debug(f"Delete skipped, not found: {full_key}")

    # ------------------------------------------------------------------ #
    # User-scoped shortcuts                                                #
    # ------------------------------------------------------------------ #

    def save_user(self, chat_id, key: str, value) -> None:
        """Save a value scoped to a specific user (chat_id)."""
        self.save(key, value, chat_id=chat_id)

    def load_user(self, chat_id, key: str):
        """Load a value scoped to a specific user (chat_id)."""
        return self.load(key, chat_id=chat_id)

    def delete_user(self, chat_id, key: str) -> None:
        """Delete a value scoped to a specific user (chat_id)."""
        self.delete(key, chat_id=chat_id)

    # ------------------------------------------------------------------ #
    # Funnel tracking (per user)                                           #
    # ------------------------------------------------------------------ #

    def track_interaction(self, chat_id, agent: str, task: str) -> None:
        """Record that a user interacted with an agent.
        Updates funnel stage, timestamps, interaction count, and last agent.
        Call this from TelegramHandler once chat_id wiring is in place.
        """
        # First seen (only set once)
        if self.load_user(chat_id, "funnel:first_seen") is None:
            self.save_user(chat_id, "funnel:first_seen", _now())

        self.save_user(chat_id, "funnel:last_active", _now())
        self.save_user(chat_id, "funnel:last_agent", agent)

        count = self.load_user(chat_id, "funnel:interaction_count") or 0
        count += 1
        self.save_user(chat_id, "funnel:interaction_count", count)
        self.save_user(chat_id, "funnel:stage", _funnel_stage(count))

    # ------------------------------------------------------------------ #
    # Task history (per user)                                              #
    # ------------------------------------------------------------------ #

    def track_last_tasks(self, chat_id, task: str) -> None:
        """Save last_task and maintain a rolling last_3_tasks list per user."""
        self.save("last_task", task, chat_id=chat_id)
        history = self.load("last_3_tasks", chat_id=chat_id) or []
        history.insert(0, task)
        self.save("last_3_tasks", history[:3], chat_id=chat_id)

    def get_user_profile(self, chat_id) -> dict:
        """Return a summary of all stored user memory for a given chat_id."""
        keys = [
            "funnel:first_seen",
            "funnel:last_active",
            "funnel:last_agent",
            "funnel:interaction_count",
            "funnel:stage",
        ]
        return {k: self.load_user(chat_id, k) for k in keys}

    # ------------------------------------------------------------------ #
    # Key inspection                                                       #
    # ------------------------------------------------------------------ #

    def all_keys(self) -> list:
        """Return all raw storage keys in the database (includes namespace prefix)."""
        with self._lock:
            rows = self._conn.execute("SELECT key FROM memory").fetchall()
        return [r[0] for r in rows]

    def user_keys(self, chat_id) -> list:
        """Return all raw storage keys that belong to a specific user."""
        prefix = f"u{chat_id}:"
        return [k for k in self.all_keys() if k.startswith(prefix)]
