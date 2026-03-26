"""
Phase 5 Multi-Agent Tests
Verifies ContentAgent, SalesAgent, ResearchAgent, Orchestrator routing,
and TelegramHandler command dispatch.
No real AI calls — all LLM calls are mocked.
"""
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_ask_ai(response="mocked AI response"):
    """Patch ask_ai in all agent modules to return a fixed string."""
    from unittest.mock import patch as _patch
    from contextlib import ExitStack

    class _MultiPatch:
        def __enter__(self):
            self._stack = ExitStack()
            for mod in ("src.agents.content_agent", "src.agents.sales_agent",
                        "src.agents.research_agent", "src.agents.cmo_agent"):
                self._stack.enter_context(_patch(f"{mod}.ask_ai", return_value=response))
            return self

        def __exit__(self, *args):
            return self._stack.__exit__(*args)

    return _MultiPatch()


def _make_handler(mock_orchestrator_response="mock response"):
    from src.interfaces.telegram.handler import TelegramHandler
    handler = TelegramHandler()
    handler.orchestrator = MagicMock()
    handler.orchestrator.handle_request.return_value = mock_orchestrator_response
    return handler


# ---------------------------------------------------------------------------
# ContentAgent
# ---------------------------------------------------------------------------

def test_content_agent_initializes():
    from src.agents.content_agent import ContentAgent
    agent = ContentAgent()
    assert agent.name == "content"
    print("[OK] ContentAgent initializes")


def test_content_agent_process_returns_string():
    from src.agents.content_agent import ContentAgent
    with _mock_ask_ai("Instagram post content"), \
         patch("src.agents.agent_utils.load_memory_context", return_value=""):
        agent = ContentAgent()
        result = agent.process("Happy Juice için içerik üret")
    assert isinstance(result, str)
    assert len(result) > 0
    print("[OK] ContentAgent.process() returns string")


def test_content_agent_saves_to_memory():
    from src.agents.content_agent import ContentAgent
    with _mock_ask_ai("post"), \
         patch("src.agents.agent_utils.load_memory_context", return_value=""):
        agent = ContentAgent()
        agent.process("test task")
    assert agent.memory.load("last_task") == "test task"
    assert agent.memory.load("last_response") == "post"
    print("[OK] ContentAgent saves task/response to memory")


# ---------------------------------------------------------------------------
# SalesAgent
# ---------------------------------------------------------------------------

def test_sales_agent_initializes():
    from src.agents.sales_agent import SalesAgent
    agent = SalesAgent()
    assert agent.name == "sales"
    print("[OK] SalesAgent initializes")


def test_sales_agent_process_returns_string():
    from src.agents.sales_agent import SalesAgent
    with _mock_ask_ai("DM script output"), \
         patch("src.agents.agent_utils.load_memory_context", return_value=""):
        agent = SalesAgent()
        result = agent.process("Happy Juice için DM script yaz")
    assert isinstance(result, str)
    assert len(result) > 0
    print("[OK] SalesAgent.process() returns string")


def test_sales_agent_saves_to_memory():
    from src.agents.sales_agent import SalesAgent
    with _mock_ask_ai("closing msg"), \
         patch("src.agents.agent_utils.load_memory_context", return_value=""):
        agent = SalesAgent()
        agent.process("test sales task")
    assert agent.memory.load("last_task") == "test sales task"
    print("[OK] SalesAgent saves task to memory")


# ---------------------------------------------------------------------------
# ResearchAgent
# ---------------------------------------------------------------------------

def test_research_agent_initializes():
    from src.agents.research_agent import ResearchAgent
    agent = ResearchAgent()
    assert agent.name == "research"
    print("[OK] ResearchAgent initializes")


def test_research_agent_process_returns_string():
    from src.agents.research_agent import ResearchAgent
    with _mock_ask_ai("Market trends output"), \
         patch("src.agents.agent_utils.load_memory_context", return_value=""):
        agent = ResearchAgent()
        result = agent.process("Hollanda wellness market trendleri")
    assert isinstance(result, str)
    assert len(result) > 0
    print("[OK] ResearchAgent.process() returns string")


def test_research_agent_saves_to_memory():
    from src.agents.research_agent import ResearchAgent
    with _mock_ask_ai("research result"), \
         patch("src.agents.agent_utils.load_memory_context", return_value=""):
        agent = ResearchAgent()
        agent.process("test research task")
    assert agent.memory.load("last_task") == "test research task"
    print("[OK] ResearchAgent saves task to memory")


# ---------------------------------------------------------------------------
# Orchestrator routing
# ---------------------------------------------------------------------------

def test_orchestrator_has_all_agents():
    from src.orchestrator import Orchestrator
    orc = Orchestrator()
    assert "cmo" in orc.agents
    assert "content" in orc.agents
    assert "sales" in orc.agents
    assert "research" in orc.agents
    print("[OK] Orchestrator registers all 4 agents")


def test_orchestrator_routes_to_content():
    from src.orchestrator import Orchestrator
    orc = Orchestrator()
    orc.agents["content"] = MagicMock()
    orc.agents["content"].process.return_value = "content reply"
    result = orc.handle_request("test task", agent="content")
    orc.agents["content"].process.assert_called_once_with("test task", chat_id=None)
    assert result == "content reply"
    print("[OK] Orchestrator routes to ContentAgent")


def test_orchestrator_routes_to_sales():
    from src.orchestrator import Orchestrator
    orc = Orchestrator()
    orc.agents["sales"] = MagicMock()
    orc.agents["sales"].process.return_value = "sales reply"
    result = orc.handle_request("test task", agent="sales")
    orc.agents["sales"].process.assert_called_once_with("test task", chat_id=None)
    assert result == "sales reply"
    print("[OK] Orchestrator routes to SalesAgent")


def test_orchestrator_routes_to_research():
    from src.orchestrator import Orchestrator
    orc = Orchestrator()
    orc.agents["research"] = MagicMock()
    orc.agents["research"].process.return_value = "research reply"
    result = orc.handle_request("test task", agent="research")
    orc.agents["research"].process.assert_called_once_with("test task", chat_id=None)
    assert result == "research reply"
    print("[OK] Orchestrator routes to ResearchAgent")


def test_orchestrator_defaults_to_cmo():
    from src.orchestrator import Orchestrator
    orc = Orchestrator()
    orc.agents["cmo"] = MagicMock()
    orc.agents["cmo"].process.return_value = "cmo reply"
    result = orc.handle_request("test task")
    orc.agents["cmo"].process.assert_called_once_with("test task", chat_id=None)
    assert result == "cmo reply"
    print("[OK] Orchestrator defaults to CmoAgent")


def test_orchestrator_unknown_agent_returns_message():
    from src.orchestrator import Orchestrator
    orc = Orchestrator()
    result = orc.handle_request("test", agent="nonexistent")
    assert "Unknown agent" in result or "nonexistent" in result
    print("[OK] Orchestrator returns error for unknown agent")


# ---------------------------------------------------------------------------
# TelegramHandler command routing
# ---------------------------------------------------------------------------

def test_telegram_content_command_routes_correctly():
    handler = _make_handler("content response")
    result = handler.handle("/content Happy Juice için içerik", chat_id=1)
    handler.orchestrator.handle_request.assert_called_once_with(
        "Happy Juice için içerik", agent="content", chat_id=1
    )
    assert result == "content response"
    print("[OK] /content command routes to ContentAgent")


def test_telegram_sales_command_routes_correctly():
    handler = _make_handler("sales response")
    result = handler.handle("/sales DM script yaz", chat_id=1)
    handler.orchestrator.handle_request.assert_called_once_with(
        "DM script yaz", agent="sales", chat_id=1
    )
    assert result == "sales response"
    print("[OK] /sales command routes to SalesAgent")


def test_telegram_research_command_routes_correctly():
    handler = _make_handler("research response")
    result = handler.handle("/research Hollanda wellness market", chat_id=1)
    handler.orchestrator.handle_request.assert_called_once_with(
        "Hollanda wellness market", agent="research", chat_id=1
    )
    assert result == "research response"
    print("[OK] /research command routes to ResearchAgent")


def test_telegram_content_without_task_returns_usage():
    import src.interfaces.telegram.handler as _h
    _h._rate_store.clear()
    handler = _make_handler()
    result = handler.handle("/content", chat_id=1)
    handler.orchestrator.handle_request.assert_not_called()
    assert "Gebruik" in result
    print("[OK] /content without task returns usage hint")


def test_telegram_sales_without_task_returns_usage():
    import src.interfaces.telegram.handler as _h
    _h._rate_store.clear()
    handler = _make_handler()
    result = handler.handle("/sales", chat_id=1)
    handler.orchestrator.handle_request.assert_not_called()
    assert "Gebruik" in result
    print("[OK] /sales without task returns usage hint")


def test_telegram_research_without_task_returns_usage():
    import src.interfaces.telegram.handler as _h
    _h._rate_store.clear()
    handler = _make_handler()
    result = handler.handle("/research", chat_id=1)
    handler.orchestrator.handle_request.assert_not_called()
    assert "Gebruik" in result
    print("[OK] /research without task returns usage hint")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_content_agent_initializes,
        test_content_agent_process_returns_string,
        test_content_agent_saves_to_memory,
        test_sales_agent_initializes,
        test_sales_agent_process_returns_string,
        test_sales_agent_saves_to_memory,
        test_research_agent_initializes,
        test_research_agent_process_returns_string,
        test_research_agent_saves_to_memory,
        test_orchestrator_has_all_agents,
        test_orchestrator_routes_to_content,
        test_orchestrator_routes_to_sales,
        test_orchestrator_routes_to_research,
        test_orchestrator_defaults_to_cmo,
        test_orchestrator_unknown_agent_returns_message,
        test_telegram_content_command_routes_correctly,
        test_telegram_sales_command_routes_correctly,
        test_telegram_research_command_routes_correctly,
        test_telegram_content_without_task_returns_usage,
        test_telegram_sales_without_task_returns_usage,
        test_telegram_research_without_task_returns_usage,
    ]

    passed = 0
    failed = 0

    print("\n" + "=" * 55)
    print("PHASE 5 MULTI-AGENT TESTS")
    print("=" * 55 + "\n")

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1

    print("\n" + "=" * 55)
    print(f"RESULT: {passed} passed, {failed} failed")
    print("=" * 55)

    sys.exit(0 if failed == 0 else 1)
