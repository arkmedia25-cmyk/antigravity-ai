"""Shared utilities for all agents — memory context, prompt loading, funnel context."""
import json
import os
from datetime import datetime, timezone, timedelta

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

_FUNNEL_PROMPTS_DIR = os.path.join(_PROJECT_ROOT, "prompts", "funnel")
_KNOWN_STAGES = ("awareness", "interest", "consideration", "intent")


def _load_funnel_instruction(stage: str) -> str:
    """Load the behavioral directive for a funnel stage from prompts/funnel/<stage>.txt.
    Falls back to awareness if the file is missing or the stage is unknown.
    """
    if stage not in _KNOWN_STAGES:
        stage = "awareness"
    path = os.path.join(_FUNNEL_PROMPTS_DIR, f"{stage}.txt")
    if not os.path.exists(path):
        return f"(funnel prompt not found for stage: {stage})"
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def build_funnel_context(chat_id) -> str:
    """Return a stage-aware behavior block for injection into agent prompts.

    Loads the stage directive dynamically from prompts/funnel/<stage>.txt.
    Returns an empty string when chat_id is None so agents work unchanged
    without a known user (backward compatible).
    """
    if chat_id is None:
        return ""

    # Lazy import to avoid circular dependency at module load time
    from memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel")

    stage = mm.load_user(chat_id, "funnel:stage") or "awareness"
    count = mm.load_user(chat_id, "funnel:interaction_count") or 0
    last_agent = mm.load_user(chat_id, "funnel:last_agent") or "—"

    instruction = _load_funnel_instruction(stage)

    return (
        f"=== GEBRUIKER FUNNEL CONTEXT ===\n"
        f"Fase: {stage.upper()} | Interacties: {count} | Laatste agent: {last_agent}\n"
        f"Gedragsrichtlijn: {instruction}"
    )


def get_reengagement_status(chat_id) -> str | None:
    """Check how long a user has been inactive.

    Returns:
        '7d'  — inactive 7+ days (second follow-up)
        '48h' — inactive 48+ hours (first follow-up)
        None  — active or no data
    """
    if chat_id is None:
        return None
    from memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel")
    last_active_str = mm.load_user(chat_id, "funnel:last_active")
    if not last_active_str:
        return None
    last_active = datetime.fromisoformat(last_active_str)
    delta = datetime.now(timezone.utc) - last_active
    if delta >= timedelta(days=7):
        return "7d"
    if delta >= timedelta(hours=48):
        return "48h"
    return None


def load_agent_prompt(agent_dir: str, filename: str) -> str:
    """Load a system prompt .txt file from agents/<agent_dir>/<filename>.

    Args:
        agent_dir:  subdirectory name under agents/, e.g. "email-agent"
        filename:   file name, e.g. "email_prompt.txt"

    Raises:
        FileNotFoundError if the file does not exist.
    """
    path = os.path.join(_PROJECT_ROOT, "agents", agent_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def _load_json(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}


def load_memory_context() -> str:
    """Load brand/product/audience/learned memory and return as formatted string."""
    mem = os.path.join(_PROJECT_ROOT, "memory")
    brand = _load_json(os.path.join(mem, "brand.json"))
    products = _load_json(os.path.join(mem, "products.json"))
    audience = _load_json(os.path.join(mem, "audience.json"))
    learned = _load_json(os.path.join(mem, "learned.json"))

    return (
        f"=== MERKINFO ===\n{json.dumps(brand, ensure_ascii=False, indent=2)}\n\n"
        f"=== PRODUCTEN ===\n{json.dumps(products, ensure_ascii=False, indent=2)}\n\n"
        f"=== DOELGROEP ===\n{json.dumps(audience, ensure_ascii=False, indent=2)}\n\n"
        f"=== GELEERDE INZICHTEN ===\n"
        f"Goedgekeurde hooks: {learned.get('approved_hooks', [])}\n"
        f"Afgewezen stijlen: {learned.get('rejected_styles', [])}\n"
        f"Goedgekeurde CTA's: {learned.get('approved_ctas', [])}\n"
    )
