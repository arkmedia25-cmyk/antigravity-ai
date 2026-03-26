"""
Phase 7B tests — namespaced MemoryManager, per-user storage, funnel tracking.
"""
from unittest.mock import patch


# ------------------------------------------------------------------ #
# Namespace scoping                                                   #
# ------------------------------------------------------------------ #

def test_namespace_is_stored_in_key():
    """Keys are stored with namespace prefix in DB."""
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="test_ns")
    mm.save("mykey", "myval")
    raw_keys = mm.all_keys()
    assert "test_ns:mykey" in raw_keys
    mm.delete("mykey")


def test_two_namespaces_dont_collide():
    """Same logical key in different namespaces stores independently."""
    from src.memory.memory_manager import MemoryManager
    mm_a = MemoryManager(namespace="agent_a")
    mm_b = MemoryManager(namespace="agent_b")
    mm_a.save("last_task", "task from A")
    mm_b.save("last_task", "task from B")
    assert mm_a.load("last_task") == "task from A"
    assert mm_b.load("last_task") == "task from B"
    mm_a.delete("last_task")
    mm_b.delete("last_task")


def test_agent_namespaces_are_isolated():
    """Each agent uses its own namespace — no cross-agent key pollution."""
    from src.agents.email_agent import EmailAgent
    from src.agents.linkedin_agent import LinkedInAgent
    with patch("src.agents.email_agent.ask_ai", return_value="email response"):
        email_agent = EmailAgent()
        email_agent.process("test email task")
    with patch("src.agents.linkedin_agent.ask_ai", return_value="linkedin response"):
        li_agent = LinkedInAgent()
        li_agent.process("test linkedin task")
    # Each agent's last_task should be its own
    assert email_agent.memory.load("last_task") == "test email task"
    assert li_agent.memory.load("last_task") == "test linkedin task"
    # Cross-namespace isolation: email's last_task not visible from linkedin namespace
    assert li_agent.memory.load("last_task") != "test email task"


# ------------------------------------------------------------------ #
# Per-user (chat_id) storage                                          #
# ------------------------------------------------------------------ #

def test_save_user_and_load_user():
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="user_test")
    mm.save_user(chat_id=1001, key="pref", value="dark_mode")
    assert mm.load_user(chat_id=1001, key="pref") == "dark_mode"
    mm.delete_user(chat_id=1001, key="pref")


def test_different_users_dont_share_data():
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="user_test")
    mm.save_user(chat_id=1001, key="name", value="Alice")
    mm.save_user(chat_id=1002, key="name", value="Bob")
    assert mm.load_user(chat_id=1001, key="name") == "Alice"
    assert mm.load_user(chat_id=1002, key="name") == "Bob"
    mm.delete_user(chat_id=1001, key="name")
    mm.delete_user(chat_id=1002, key="name")


def test_user_data_not_visible_without_chat_id():
    """A key saved with chat_id is not returned by load() without chat_id."""
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="user_test")
    mm.save_user(chat_id=5555, key="secret", value="hidden")
    assert mm.load("secret") is None          # no chat_id → different DB key
    mm.delete_user(chat_id=5555, key="secret")


def test_user_keys_filters_by_chat_id():
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="ukey_test")
    mm.save_user(chat_id=777, key="a", value=1)
    mm.save_user(chat_id=777, key="b", value=2)
    mm.save_user(chat_id=888, key="a", value=3)
    keys_777 = mm.user_keys(chat_id=777)
    keys_888 = mm.user_keys(chat_id=888)
    assert all(k.startswith("u777:") for k in keys_777)
    assert all(k.startswith("u888:") for k in keys_888)
    assert len([k for k in keys_777 if "ukey_test" in k]) == 2
    assert len([k for k in keys_888 if "ukey_test" in k]) == 1
    mm.delete_user(chat_id=777, key="a")
    mm.delete_user(chat_id=777, key="b")
    mm.delete_user(chat_id=888, key="a")


# ------------------------------------------------------------------ #
# Funnel tracking                                                     #
# ------------------------------------------------------------------ #

def test_track_interaction_sets_first_seen():
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel_test")
    mm.track_interaction(chat_id=2001, agent="cmo", task="strategy")
    profile = mm.get_user_profile(chat_id=2001)
    assert profile["funnel:first_seen"] is not None
    assert profile["funnel:last_agent"] == "cmo"
    # Cleanup
    for key in ["funnel:first_seen", "funnel:last_active", "funnel:last_agent",
                "funnel:interaction_count", "funnel:stage"]:
        mm.delete_user(chat_id=2001, key=key)


def test_track_interaction_increments_count():
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel_count")
    for i in range(3):
        mm.track_interaction(chat_id=2002, agent="content", task=f"task {i}")
    profile = mm.get_user_profile(chat_id=2002)
    assert profile["funnel:interaction_count"] == 3
    for key in ["funnel:first_seen", "funnel:last_active", "funnel:last_agent",
                "funnel:interaction_count", "funnel:stage"]:
        mm.delete_user(chat_id=2002, key=key)


def test_funnel_stage_awareness_at_start():
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel_stage")
    mm.track_interaction(chat_id=3001, agent="cmo", task="first")
    assert mm.get_user_profile(3001)["funnel:stage"] == "awareness"
    for key in ["funnel:first_seen", "funnel:last_active", "funnel:last_agent",
                "funnel:interaction_count", "funnel:stage"]:
        mm.delete_user(chat_id=3001, key=key)


def test_funnel_stage_progresses_to_interest():
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel_interest")
    for i in range(3):  # 3 interactions → interest
        mm.track_interaction(chat_id=3002, agent="sales", task=f"task {i}")
    assert mm.get_user_profile(3002)["funnel:stage"] == "interest"
    for key in ["funnel:first_seen", "funnel:last_active", "funnel:last_agent",
                "funnel:interaction_count", "funnel:stage"]:
        mm.delete_user(chat_id=3002, key=key)


def test_funnel_stage_progresses_to_consideration():
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel_consid")
    for i in range(7):  # 7 interactions → consideration
        mm.track_interaction(chat_id=3003, agent="research", task=f"task {i}")
    assert mm.get_user_profile(3003)["funnel:stage"] == "consideration"
    for key in ["funnel:first_seen", "funnel:last_active", "funnel:last_agent",
                "funnel:interaction_count", "funnel:stage"]:
        mm.delete_user(chat_id=3003, key=key)


def test_funnel_stage_reaches_intent():
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel_intent")
    for i in range(12):  # 12 interactions → intent
        mm.track_interaction(chat_id=3004, agent="cmo", task=f"task {i}")
    assert mm.get_user_profile(3004)["funnel:stage"] == "intent"
    for key in ["funnel:first_seen", "funnel:last_active", "funnel:last_agent",
                "funnel:interaction_count", "funnel:stage"]:
        mm.delete_user(chat_id=3004, key=key)


def test_get_user_profile_returns_all_fields():
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel_profile")
    mm.track_interaction(chat_id=4001, agent="email", task="nurture reeks")
    profile = mm.get_user_profile(4001)
    expected_keys = [
        "funnel:first_seen",
        "funnel:last_active",
        "funnel:last_agent",
        "funnel:interaction_count",
        "funnel:stage",
    ]
    for k in expected_keys:
        assert k in profile, f"Missing key: {k}"
    for key in expected_keys:
        mm.delete_user(chat_id=4001, key=key)
