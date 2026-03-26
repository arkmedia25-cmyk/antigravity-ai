"""
Phase 2 Telegram Bridge Tests
Verifies routing logic between TelegramHandler and Orchestrator.
No real Telegram API calls. No network dependency.
Old telegram_handler.py is NOT imported or modified.
"""
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def _make_handler(mock_response="Mock orchestrator response"):
    """Helper: returns a TelegramHandler with a mocked Orchestrator."""
    from src.interfaces.telegram.handler import TelegramHandler
    handler = TelegramHandler()
    handler.orchestrator = MagicMock()
    handler.orchestrator.handle_request.return_value = mock_response
    return handler


def test_handler_initializes():
    """TelegramHandler must initialize without errors."""
    from src.interfaces.telegram.handler import TelegramHandler
    handler = TelegramHandler()
    assert handler.orchestrator is not None
    print("[OK] TelegramHandler initializes correctly")


def test_cmo_command_routes_to_orchestrator():
    """/cmo command must extract task and route to orchestrator."""
    handler = _make_handler("CMO response")
    result = handler.handle("/cmo Lead systeem opzetten in Nederland", chat_id=1)
    handler.orchestrator.handle_request.assert_called_once_with(
        "Lead systeem opzetten in Nederland", agent="cmo", chat_id=1
    )
    assert result == "CMO response"
    print("[OK] /cmo routes correctly to orchestrator")


def test_cmo_command_without_task_returns_usage():
    """/cmo without task must return usage hint, not call orchestrator."""
    handler = _make_handler()
    result = handler.handle("/cmo", chat_id=1)
    handler.orchestrator.handle_request.assert_not_called()
    assert "Gebruik" in result
    print("[OK] /cmo without task returns usage hint")


def test_plain_text_routes_to_orchestrator():
    """Plain text (no command) must route directly to orchestrator."""
    handler = _make_handler("Orchestrator reply")
    result = handler.handle("Wat zijn de beste producten?", chat_id=2)
    handler.orchestrator.handle_request.assert_called_once_with(
        "Wat zijn de beste producten?", chat_id=2
    )
    assert result == "Orchestrator reply"
    print("[OK] Plain text routes correctly to orchestrator")


def test_empty_input_returns_message():
    """Empty input must return a message without calling orchestrator."""
    handler = _make_handler()
    result = handler.handle("", chat_id=3)
    handler.orchestrator.handle_request.assert_not_called()
    assert isinstance(result, str)
    assert len(result) > 0
    print("[OK] Empty input handled gracefully")


def test_whitespace_only_input():
    """Whitespace-only input must be treated as empty."""
    handler = _make_handler()
    result = handler.handle("   ", chat_id=4)
    handler.orchestrator.handle_request.assert_not_called()
    assert isinstance(result, str)
    print("[OK] Whitespace-only input handled gracefully")


def test_unknown_command_returns_message():
    """Unknown command (e.g. /foo) must return a descriptive message."""
    handler = _make_handler()
    result = handler.handle("/foo bar baz", chat_id=5)
    handler.orchestrator.handle_request.assert_not_called()
    assert "Onbekend" in result or "commando" in result.lower()
    print("[OK] Unknown command returns descriptive message")


def test_chat_id_does_not_affect_routing():
    """Different chat_ids must not affect routing behavior."""
    handler = _make_handler("Same response")
    result_a = handler.handle("/cmo test taak", chat_id=100)
    handler.orchestrator.handle_request.reset_mock()
    handler.orchestrator.handle_request.return_value = "Same response"
    result_b = handler.handle("/cmo test taak", chat_id=999)
    assert result_a == result_b
    print("[OK] chat_id does not affect routing")


def test_old_telegram_handler_not_imported():
    """Old telegram_handler.py must NOT be imported by the new bridge."""
    import sys
    # Ensure the new handler is loaded
    from src.interfaces.telegram import handler as new_handler
    loaded_modules = list(sys.modules.keys())
    for mod in loaded_modules:
        assert "skills.automation.telegram_handler" not in mod, (
            "Old telegram_handler.py must not be imported by Phase 2"
        )
    print("[OK] Old telegram_handler.py not imported by Phase 2 bridge")


if __name__ == "__main__":
    tests = [
        test_handler_initializes,
        test_cmo_command_routes_to_orchestrator,
        test_cmo_command_without_task_returns_usage,
        test_plain_text_routes_to_orchestrator,
        test_empty_input_returns_message,
        test_whitespace_only_input,
        test_unknown_command_returns_message,
        test_chat_id_does_not_affect_routing,
        test_old_telegram_handler_not_imported,
    ]

    passed = 0
    failed = 0

    print("\n" + "=" * 50)
    print("PHASE 2 TELEGRAM BRIDGE TESTS")
    print("=" * 50 + "\n")

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"RESULT: {passed} passed, {failed} failed")
    print("=" * 50)

    sys.exit(0 if failed == 0 else 1)
