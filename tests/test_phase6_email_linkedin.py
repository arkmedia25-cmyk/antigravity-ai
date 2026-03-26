"""
Phase 6 tests — EmailAgent, LinkedInAgent, persistent MemoryManager, routing.
"""
import os
import pytest
from unittest.mock import patch


# ---------------------------------------------------------------------------
# MemoryManager — SQLite persistence
# ---------------------------------------------------------------------------

def test_memory_manager_saves_and_loads():
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager()
    mm.save("phase6_test_key", "hello_sqlite")
    assert mm.load("phase6_test_key") == "hello_sqlite"
    mm.delete("phase6_test_key")


def test_memory_manager_survives_restart():
    """Save in one instance, load in a new instance (simulates restart)."""
    from src.memory.memory_manager import MemoryManager
    mm1 = MemoryManager()
    mm1.save("restart_test", {"value": 42})

    mm2 = MemoryManager()
    assert mm2.load("restart_test") == {"value": 42}
    mm2.delete("restart_test")


def test_memory_manager_delete_removes_entry():
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager()
    mm.save("del_test", "to_be_deleted")
    mm.delete("del_test")
    assert mm.load("del_test") is None


def test_memory_manager_all_keys():
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager()  # namespace="global"
    mm.save("keys_test_a", 1)
    mm.save("keys_test_b", 2)
    keys = mm.all_keys()
    # all_keys() returns raw DB keys — includes namespace prefix
    assert "global:keys_test_a" in keys
    assert "global:keys_test_b" in keys
    mm.delete("keys_test_a")
    mm.delete("keys_test_b")


# ---------------------------------------------------------------------------
# EmailAgent
# ---------------------------------------------------------------------------

def test_email_agent_initializes():
    from src.agents.email_agent import EmailAgent
    agent = EmailAgent()
    assert agent.name == "email"


def test_email_agent_process_returns_string():
    from src.agents.email_agent import EmailAgent
    agent = EmailAgent()
    with patch("src.agents.email_agent.ask_ai", return_value="mock email response"):
        result = agent.process("5-daagse nurture reeks")
    assert isinstance(result, str)
    assert len(result) > 0


def test_email_agent_saves_to_memory():
    from src.agents.email_agent import EmailAgent
    agent = EmailAgent()
    with patch("src.agents.email_agent.ask_ai", return_value="email output"):
        agent.process("welkomstmail test")
    assert agent.memory.load("last_task") == "welkomstmail test"
    assert agent.memory.load("last_response") == "email output"


# ---------------------------------------------------------------------------
# LinkedInAgent
# ---------------------------------------------------------------------------

def test_linkedin_agent_initializes():
    from src.agents.linkedin_agent import LinkedInAgent
    agent = LinkedInAgent()
    assert agent.name == "linkedin"


def test_linkedin_agent_process_returns_string():
    from src.agents.linkedin_agent import LinkedInAgent
    agent = LinkedInAgent()
    with patch("src.agents.linkedin_agent.ask_ai", return_value="mock linkedin response"):
        result = agent.process("connectie bericht voor moeders")
    assert isinstance(result, str)
    assert len(result) > 0


def test_linkedin_agent_saves_to_memory():
    from src.agents.linkedin_agent import LinkedInAgent
    agent = LinkedInAgent()
    with patch("src.agents.linkedin_agent.ask_ai", return_value="linkedin output"):
        agent.process("follow-up bericht test")
    assert agent.memory.load("last_task") == "follow-up bericht test"
    assert agent.memory.load("last_response") == "linkedin output"


# ---------------------------------------------------------------------------
# Orchestrator routing
# ---------------------------------------------------------------------------

def test_orchestrator_has_email_agent():
    from src.orchestrator import Orchestrator
    orc = Orchestrator()
    assert "email" in orc.agents


def test_orchestrator_has_linkedin_agent():
    from src.orchestrator import Orchestrator
    orc = Orchestrator()
    assert "linkedin" in orc.agents


def test_orchestrator_routes_to_email():
    from src.orchestrator import Orchestrator
    orc = Orchestrator()
    with patch("src.agents.email_agent.ask_ai", return_value="email via orchestrator"):
        result = orc.handle_request("nurture reeks", agent="email")
    assert isinstance(result, str)


def test_orchestrator_routes_to_linkedin():
    from src.orchestrator import Orchestrator
    orc = Orchestrator()
    with patch("src.agents.linkedin_agent.ask_ai", return_value="linkedin via orchestrator"):
        result = orc.handle_request("connectie bericht", agent="linkedin")
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# TelegramHandler command routing
# ---------------------------------------------------------------------------

def test_telegram_email_command_routes_correctly():
    from src.interfaces.telegram.handler import TelegramHandler
    handler = TelegramHandler()
    with patch("src.agents.email_agent.ask_ai", return_value="email result"):
        result = handler.handle("/email 5-daagse reeks")
    assert isinstance(result, str)


def test_telegram_linkedin_command_routes_correctly():
    from src.interfaces.telegram.handler import TelegramHandler
    handler = TelegramHandler()
    with patch("src.agents.linkedin_agent.ask_ai", return_value="linkedin result"):
        result = handler.handle("/linkedin connectie bericht")
    assert isinstance(result, str)


def test_telegram_email_without_task_returns_usage():
    from src.interfaces.telegram.handler import TelegramHandler
    handler = TelegramHandler()
    result = handler.handle("/email")
    assert "email" in result.lower() or "gebruik" in result.lower()


def test_telegram_linkedin_without_task_returns_usage():
    from src.interfaces.telegram.handler import TelegramHandler
    handler = TelegramHandler()
    result = handler.handle("/linkedin")
    assert "linkedin" in result.lower() or "gebruik" in result.lower()
