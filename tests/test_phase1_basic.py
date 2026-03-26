"""
Phase 1 Basic Tests
Tests core architecture in isolation: agents, memory, orchestrator.
Does NOT test existing telegram_handler.py, ai_client.py, or cmo_agent.py.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_base_agent_cannot_be_instantiated():
    """BaseAgent is abstract and must not be instantiatable directly."""
    from src.agents.base_agent import BaseAgent
    try:
        BaseAgent("test")
        assert False, "Should have raised TypeError"
    except TypeError:
        pass
    print("[OK] BaseAgent is correctly abstract")


def test_cmo_agent_initializes():
    """CmoAgent must initialize with correct name and memory."""
    from src.agents.cmo_agent import CmoAgent
    agent = CmoAgent()
    assert agent.name == "cmo"
    assert agent.memory is not None
    print("[OK] CmoAgent initializes correctly")


def test_cmo_agent_process_returns_string():
    """CmoAgent.process() must return a non-empty string."""
    from src.agents.cmo_agent import CmoAgent
    agent = CmoAgent()
    result = agent.process("Test taak voor CMO agent")
    assert isinstance(result, str)
    assert len(result) > 0
    print(f"[OK] CmoAgent.process() returned: {result[:80]}...")


def test_memory_save_and_load():
    """MemoryManager must save and load values correctly."""
    from src.memory.memory_manager import MemoryManager
    mem = MemoryManager()
    mem.save("test_key", "test_value")
    result = mem.load("test_key")
    assert result == "test_value"
    print("[OK] MemoryManager save/load works")


def test_memory_delete():
    """MemoryManager must delete keys correctly."""
    from src.memory.memory_manager import MemoryManager
    mem = MemoryManager()
    mem.save("to_delete", 42)
    mem.delete("to_delete")
    assert mem.load("to_delete") is None
    print("[OK] MemoryManager delete works")


def test_memory_load_missing_key():
    """MemoryManager must return None for missing keys."""
    from src.memory.memory_manager import MemoryManager
    mem = MemoryManager()
    assert mem.load("nonexistent") is None
    print("[OK] MemoryManager returns None for missing key")


def test_orchestrator_initializes():
    """Orchestrator must initialize without errors."""
    from src.orchestrator import Orchestrator
    orch = Orchestrator()
    assert orch.cmo is not None
    print("[OK] Orchestrator initializes correctly")


def test_orchestrator_routes_to_cmo():
    """Orchestrator.handle_request() must return a non-empty string."""
    from src.orchestrator import Orchestrator
    orch = Orchestrator()
    result = orch.handle_request("Hollanda'da lead sistemi kur")
    assert isinstance(result, str)
    assert len(result) > 0
    print(f"[OK] Orchestrator routed correctly: {result[:80]}...")


def test_orchestrator_handles_empty_input():
    """Orchestrator must handle empty input gracefully."""
    from src.orchestrator import Orchestrator
    orch = Orchestrator()
    result = orch.handle_request("")
    assert isinstance(result, str)
    assert "Empty input" in result
    print("[OK] Orchestrator handles empty input gracefully")


if __name__ == "__main__":
    tests = [
        test_base_agent_cannot_be_instantiated,
        test_cmo_agent_initializes,
        test_cmo_agent_process_returns_string,
        test_memory_save_and_load,
        test_memory_delete,
        test_memory_load_missing_key,
        test_orchestrator_initializes,
        test_orchestrator_routes_to_cmo,
        test_orchestrator_handles_empty_input,
    ]

    passed = 0
    failed = 0

    print("\n" + "=" * 50)
    print("PHASE 1 BASIC TESTS")
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
