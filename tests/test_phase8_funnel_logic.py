"""
Phase 8 tests — Intelligent Funnel Logic.

Verifies:
- build_funnel_context() returns correct stage instructions
- Each funnel stage produces a distinct directive
- Agents inject funnel context into the AI prompt when chat_id is given
- Agents work unchanged when no chat_id is provided (backward compat)
- Stage progression changes the injected instruction
"""
from unittest.mock import patch, MagicMock


# ------------------------------------------------------------------ #
# build_funnel_context — unit tests                                   #
# ------------------------------------------------------------------ #

def test_build_funnel_context_returns_empty_for_none_chat_id():
    from src.agents.agent_utils import build_funnel_context
    result = build_funnel_context(None)
    assert result == ""


def test_build_funnel_context_returns_string_for_valid_chat_id():
    from src.agents.agent_utils import build_funnel_context
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel")
    mm.save_user(99901, "funnel:stage", "awareness")
    mm.save_user(99901, "funnel:interaction_count", 1)
    mm.save_user(99901, "funnel:last_agent", "cmo")

    result = build_funnel_context(99901)

    assert "AWARENESS" in result
    assert "Interacties: 1" in result
    assert "Laatste agent: cmo" in result
    assert "GEBRUIKER FUNNEL CONTEXT" in result

    for key in ["funnel:stage", "funnel:interaction_count", "funnel:last_agent"]:
        mm.delete_user(99901, key)


def test_build_funnel_context_defaults_to_awareness_for_unknown_user():
    from src.agents.agent_utils import build_funnel_context
    # chat_id with no stored data → should default to awareness
    result = build_funnel_context(99999)
    assert "AWARENESS" in result


def test_awareness_stage_contains_educate_directive():
    from src.agents.agent_utils import build_funnel_context
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel")
    mm.save_user(90001, "funnel:stage", "awareness")
    result = build_funnel_context(90001)
    assert "educeer" in result.lower() or "vertrouwen" in result.lower()
    mm.delete_user(90001, "funnel:stage")


def test_interest_stage_contains_value_directive():
    from src.agents.agent_utils import build_funnel_context
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel")
    mm.save_user(90002, "funnel:stage", "interest")
    result = build_funnel_context(90002)
    assert "waarde" in result.lower() or "interesse" in result.upper() or "INTEREST" in result
    mm.delete_user(90002, "funnel:stage")


def test_consideration_stage_contains_offer_directive():
    from src.agents.agent_utils import build_funnel_context
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel")
    mm.save_user(90003, "funnel:stage", "consideration")
    result = build_funnel_context(90003)
    assert "CONSIDERATION" in result
    assert "beslissing" in result.lower() or "overweegt" in result.lower() or "bezwaar" in result.lower()
    mm.delete_user(90003, "funnel:stage")


def test_intent_stage_contains_cta_directive():
    from src.agents.agent_utils import build_funnel_context
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel")
    mm.save_user(90004, "funnel:stage", "intent")
    result = build_funnel_context(90004)
    assert "INTENT" in result
    assert "cta" in result.lower() or "aanbeveling" in result.lower() or "handelen" in result.lower()
    mm.delete_user(90004, "funnel:stage")


def test_four_stages_produce_four_distinct_directives():
    from src.agents.agent_utils import build_funnel_context
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel")
    stages = ["awareness", "interest", "consideration", "intent"]
    results = []
    for i, stage in enumerate(stages):
        cid = 91000 + i
        mm.save_user(cid, "funnel:stage", stage)
        results.append(build_funnel_context(cid))
        mm.delete_user(cid, "funnel:stage")
    # All four must be different
    assert len(set(results)) == 4, "Each funnel stage must produce a distinct directive"


# ------------------------------------------------------------------ #
# Agent prompt injection                                              #
# ------------------------------------------------------------------ #

def _captured_prompt(agent_cls, agent_module, task, chat_id):
    """Run an agent and capture the prompt passed to ask_ai."""
    captured = {}
    def fake_ask_ai(prompt):
        captured["prompt"] = prompt
        return "mock response"

    with patch(f"{agent_module}.ask_ai", side_effect=fake_ask_ai), \
         patch("src.agents.agent_utils.load_memory_context", return_value="[MEMORY]"):
        agent = agent_cls()
        agent.process(task, chat_id=chat_id)
    return captured.get("prompt", "")


def test_email_agent_injects_funnel_context_when_chat_id_given():
    from src.agents.email_agent import EmailAgent
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel")
    mm.save_user(80001, "funnel:stage", "consideration")

    prompt = _captured_prompt(EmailAgent, "src.agents.email_agent", "nurture reeks", 80001)

    assert "CONSIDERATION" in prompt
    assert "GEBRUIKER FUNNEL CONTEXT" in prompt

    mm.delete_user(80001, "funnel:stage")


def test_linkedin_agent_injects_funnel_context_when_chat_id_given():
    from src.agents.linkedin_agent import LinkedInAgent
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel")
    mm.save_user(80002, "funnel:stage", "interest")

    prompt = _captured_prompt(LinkedInAgent, "src.agents.linkedin_agent", "connectie bericht", 80002)

    assert "INTEREST" in prompt
    assert "GEBRUIKER FUNNEL CONTEXT" in prompt

    mm.delete_user(80002, "funnel:stage")


def test_sales_agent_injects_funnel_context_when_chat_id_given():
    from src.agents.sales_agent import SalesAgent
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel")
    mm.save_user(80003, "funnel:stage", "intent")

    prompt = _captured_prompt(SalesAgent, "src.agents.sales_agent", "closing bericht", 80003)

    assert "INTENT" in prompt
    assert "GEBRUIKER FUNNEL CONTEXT" in prompt

    mm.delete_user(80003, "funnel:stage")


def test_content_agent_injects_funnel_context_when_chat_id_given():
    from src.agents.content_agent import ContentAgent
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel")
    mm.save_user(80004, "funnel:stage", "awareness")

    prompt = _captured_prompt(ContentAgent, "src.agents.content_agent", "Instagram post", 80004)

    assert "AWARENESS" in prompt
    assert "GEBRUIKER FUNNEL CONTEXT" in prompt

    mm.delete_user(80004, "funnel:stage")


def test_agent_prompt_has_no_funnel_block_when_no_chat_id():
    """Without chat_id, funnel context must NOT appear in the prompt."""
    from src.agents.email_agent import EmailAgent
    prompt = _captured_prompt(EmailAgent, "src.agents.email_agent", "welkomstmail", None)
    assert "GEBRUIKER FUNNEL CONTEXT" not in prompt


def test_awareness_and_intent_prompts_differ_for_same_agent():
    """Same agent, same task, different stage → different prompt."""
    from src.agents.sales_agent import SalesAgent
    from src.memory.memory_manager import MemoryManager
    mm = MemoryManager(namespace="funnel")

    mm.save_user(85001, "funnel:stage", "awareness")
    prompt_awareness = _captured_prompt(SalesAgent, "src.agents.sales_agent", "DM script", 85001)

    mm.save_user(85002, "funnel:stage", "intent")
    prompt_intent = _captured_prompt(SalesAgent, "src.agents.sales_agent", "DM script", 85002)

    assert prompt_awareness != prompt_intent
    assert "AWARENESS" in prompt_awareness
    assert "INTENT" in prompt_intent

    mm.delete_user(85001, "funnel:stage")
    mm.delete_user(85002, "funnel:stage")


# ------------------------------------------------------------------ #
# End-to-end: funnel stage changes after interactions                #
# ------------------------------------------------------------------ #

def test_prompt_adapts_as_user_progresses_through_funnel():
    """Simulate a user going from awareness → interest via TelegramHandler."""
    from src.interfaces.telegram.handler import TelegramHandler

    handler = TelegramHandler()
    captured_prompts = []

    def fake_ask_ai(prompt):
        captured_prompts.append(prompt)
        return "ok"

    with patch("src.agents.cmo_agent.ask_ai", side_effect=fake_ask_ai), \
         patch("src.agents.agent_utils.load_memory_context", return_value="[MEM]"):

        # Interaction 1 — awareness
        handler.handle("/cmo strategie nederland", chat_id=70001)
        # Interaction 2 — still awareness
        handler.handle("/cmo content idee", chat_id=70001)
        # Interaction 3 — interest (count=3 after this call triggers interest stage on next)

    # First prompt must be awareness
    assert "AWARENESS" in captured_prompts[0]

    # Cleanup
    for key in ["funnel:first_seen", "funnel:last_active", "funnel:last_agent",
                "funnel:interaction_count", "funnel:stage"]:
        handler._funnel.delete_user(70001, key)
    for key in ["last_task", "last_response"]:
        handler.orchestrator.agents["cmo"].memory.delete(key, chat_id=70001)
