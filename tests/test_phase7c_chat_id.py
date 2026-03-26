"""
Phase 7C tests — chat_id wiring through the full stack.

Verifies:
- Agents accept chat_id and store data user-scoped
- Orchestrator passes chat_id to agents
- TelegramHandler passes chat_id through the chain
- Funnel is tracked when chat_id is provided
- Everything still works when chat_id is None (backward compat)
"""
from unittest.mock import patch


# ------------------------------------------------------------------ #
# Agent-level: chat_id scopes the stored keys                        #
# ------------------------------------------------------------------ #

def test_agent_stores_task_under_user_key_when_chat_id_given():
    from src.agents.email_agent import EmailAgent
    agent = EmailAgent()
    with patch("src.agents.email_agent.ask_ai", return_value="response"):
        agent.process("test task", chat_id=9001)
    # User-scoped load
    assert agent.memory.load("last_task", chat_id=9001) == "test task"
    # Cleanup
    agent.memory.delete("last_task", chat_id=9001)
    agent.memory.delete("last_response", chat_id=9001)


def test_agent_stores_task_under_namespace_key_when_no_chat_id():
    from src.agents.email_agent import EmailAgent
    agent = EmailAgent()
    with patch("src.agents.email_agent.ask_ai", return_value="response"):
        agent.process("no-user task")
    # Namespace-scoped load (no chat_id)
    assert agent.memory.load("last_task") == "no-user task"
    # Cleanup
    agent.memory.delete("last_task")
    agent.memory.delete("last_response")


def test_two_users_have_separate_last_tasks():
    from src.agents.sales_agent import SalesAgent
    agent = SalesAgent()
    with patch("src.agents.sales_agent.ask_ai", return_value="r"):
        agent.process("task user A", chat_id=1111)
        agent.process("task user B", chat_id=2222)
    assert agent.memory.load("last_task", chat_id=1111) == "task user A"
    assert agent.memory.load("last_task", chat_id=2222) == "task user B"
    for cid in [1111, 2222]:
        agent.memory.delete("last_task", chat_id=cid)
        agent.memory.delete("last_response", chat_id=cid)


# ------------------------------------------------------------------ #
# Orchestrator: passes chat_id to agent                              #
# ------------------------------------------------------------------ #

def test_orchestrator_passes_chat_id_to_agent():
    from src.orchestrator import Orchestrator
    orc = Orchestrator()
    with patch("src.agents.cmo_agent.ask_ai", return_value="cmo response"):
        orc.handle_request("strategie test", agent="cmo", chat_id=5050)
    assert orc.agents["cmo"].memory.load("last_task", chat_id=5050) == "strategie test"
    orc.agents["cmo"].memory.delete("last_task", chat_id=5050)
    orc.agents["cmo"].memory.delete("last_response", chat_id=5050)


def test_orchestrator_without_chat_id_still_works():
    from src.orchestrator import Orchestrator
    orc = Orchestrator()
    with patch("src.agents.cmo_agent.ask_ai", return_value="cmo response"):
        result = orc.handle_request("strategie test no user", agent="cmo")
    assert isinstance(result, str)


# ------------------------------------------------------------------ #
# TelegramHandler: full chain with chat_id                           #
# ------------------------------------------------------------------ #

def test_telegram_handler_passes_chat_id_through_chain():
    from src.interfaces.telegram.handler import TelegramHandler
    handler = TelegramHandler()
    with patch("src.agents.content_agent.ask_ai", return_value="content result"):
        result = handler.handle("/content Happy Juice reel", chat_id=7777)
    assert isinstance(result, str)
    # Verify agent stored the task under user key
    task = handler.orchestrator.agents["content"].memory.load("last_task", chat_id=7777)
    assert task == "Happy Juice reel"
    handler.orchestrator.agents["content"].memory.delete("last_task", chat_id=7777)
    handler.orchestrator.agents["content"].memory.delete("last_response", chat_id=7777)


def test_telegram_handler_chat_id_zero_treated_as_none():
    """chat_id=0 (default) must NOT trigger user-scoped storage."""
    from src.interfaces.telegram.handler import TelegramHandler
    handler = TelegramHandler()
    with patch("src.agents.cmo_agent.ask_ai", return_value="ok"):
        handler.handle("/cmo some task", chat_id=0)
    # Must NOT be stored under user key for chat_id=0
    assert handler.orchestrator.agents["cmo"].memory.load("last_task", chat_id=0) is None


def test_telegram_handler_funnel_tracked_with_real_chat_id():
    from src.interfaces.telegram.handler import TelegramHandler
    handler = TelegramHandler()
    with patch("src.agents.research_agent.ask_ai", return_value="research result"):
        handler.handle("/research wellness trends", chat_id=8888)
    profile = handler._funnel.get_user_profile(chat_id=8888)
    assert profile["funnel:interaction_count"] == 1
    assert profile["funnel:last_agent"] == "research"
    assert profile["funnel:stage"] == "awareness"
    # Cleanup
    for key in ["funnel:first_seen", "funnel:last_active", "funnel:last_agent",
                "funnel:interaction_count", "funnel:stage"]:
        handler._funnel.delete_user(chat_id=8888, key=key)


def test_telegram_handler_funnel_not_tracked_without_chat_id():
    """No funnel entry should be created when chat_id=0."""
    from src.interfaces.telegram.handler import TelegramHandler
    handler = TelegramHandler()
    with patch("src.agents.linkedin_agent.ask_ai", return_value="ok"):
        handler.handle("/linkedin connectie bericht", chat_id=0)
    # chat_id=0 treated as None — no funnel record
    profile = handler._funnel.get_user_profile(chat_id=0)
    assert profile["funnel:interaction_count"] is None


def test_telegram_multiple_interactions_advance_funnel():
    from src.interfaces.telegram.handler import TelegramHandler
    handler = TelegramHandler()
    for i in range(5):
        with patch("src.agents.sales_agent.ask_ai", return_value="ok"):
            handler.handle(f"/sales dm script {i}", chat_id=6666)
    profile = handler._funnel.get_user_profile(chat_id=6666)
    assert profile["funnel:interaction_count"] == 5
    assert profile["funnel:stage"] == "consideration"
    for key in ["funnel:first_seen", "funnel:last_active", "funnel:last_agent",
                "funnel:interaction_count", "funnel:stage"]:
        handler._funnel.delete_user(chat_id=6666, key=key)
    for i in range(5):
        handler.orchestrator.agents["sales"].memory.delete("last_task", chat_id=6666)
        handler.orchestrator.agents["sales"].memory.delete("last_response", chat_id=6666)
