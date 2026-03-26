"""
Phase 0 Import Verification Tests
Verifies that the new src/ foundation loads correctly in isolation.
Does NOT test existing skills/, agents/, or telegram_handler.py.
"""
import sys
import os

# Add project root to path so src/ is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_settings_import():
    """Settings module must import without errors."""
    from src.config.settings import settings, Settings
    assert settings is not None
    assert hasattr(settings, "OPENAI_API_KEY")
    assert hasattr(settings, "ANTHROPIC_API_KEY")
    assert hasattr(settings, "TELEGRAM_TOKEN")
    print("[OK] settings import passed")


def test_settings_validate_method():
    """Settings.validate() raises ValueError when required keys are missing."""
    import pytest
    from src.config.settings import Settings
    import unittest.mock as mock
    with mock.patch.object(Settings, "ANTHROPIC_API_KEY", ""), \
         mock.patch.object(Settings, "TELEGRAM_TOKEN", "test-token"):
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            Settings.validate()
    print("[OK] settings.validate() raises ValueError on missing keys")


def test_logging_import():
    """Logging module must import without errors."""
    from src.core.logging import get_logger
    assert callable(get_logger)
    print("[OK] logging import passed")


def test_get_logger_returns_logger():
    """get_logger() must return a usable logger."""
    import logging
    from src.core.logging import get_logger
    logger = get_logger("test.phase0")
    assert isinstance(logger, logging.Logger)
    logger.debug("Phase 0 logger test message")
    print("[OK] get_logger() works correctly")


def test_no_circular_imports():
    """Importing settings then logging must not cause circular import errors."""
    from src.config import settings as s_mod
    from src.core import logging as l_mod
    assert s_mod is not None
    assert l_mod is not None
    print("[OK] no circular imports detected")


def test_package_structure():
    """All src/ packages must be importable as packages."""
    import src
    import src.config
    import src.core
    import src.memory
    import src.agents
    import src.skills
    import src.interfaces
    print("[OK] all src/ packages importable")


if __name__ == "__main__":
    tests = [
        test_settings_import,
        test_settings_validate_method,
        test_logging_import,
        test_get_logger_returns_logger,
        test_no_circular_imports,
        test_package_structure,
    ]

    passed = 0
    failed = 0

    print("\n" + "=" * 50)
    print("PHASE 0 IMPORT VERIFICATION")
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
