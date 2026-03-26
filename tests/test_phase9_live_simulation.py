"""
Phase 9 — Live System Simulation
=================================
Runs 3 user scenarios through the real src/ stack (TelegramHandler → Orchestrator
→ Agent → AI). No Telegram network calls — transport stays in skills/automation/.

Because ANTHROPIC_API_KEY is not set in this environment, ask_ai is patched at
the start to use OpenAI (gpt-4.1-mini). All other logic — memory, funnel tracking,
prompt injection — is 100% real.

Scenarios
---------
1. Yeni Kullanıcı      (chat_id=9001)  — /start, /content, /sales, /research
2. Stage Değişimi      (chat_id=9002)  — 6 mesaj → awareness → interest
3. Intent Kullanıcısı  (chat_id=9003)  — 10 önceki etkileşim, sonra /sales
"""

import sys
import os
import textwrap
import time
from datetime import datetime

# ── Make sure src/ is importable ──────────────────────────────────────────────
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ── Patch ask_ai → OpenAI (Anthropic key not available) ───────────────────────
import src.skills.ai_client as _ai_mod
_orig_ask = _ai_mod.ask_ai
def _ask_openai(prompt: str, provider: str = "openai"):
    return _orig_ask(prompt, provider="openai")
_ai_mod.ask_ai = _ask_openai

# ── Now import the real system ─────────────────────────────────────────────────
from src.interfaces.telegram.handler import TelegramHandler
from src.memory.memory_manager import MemoryManager

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

SEP  = "─" * 70
SEP2 = "═" * 70

def _wrap(text: str, width: int = 66, indent: str = "    ") -> str:
    lines = text.splitlines()
    out = []
    for line in lines:
        if len(line) <= width:
            out.append(indent + line)
        else:
            for chunk in textwrap.wrap(line, width):
                out.append(indent + chunk)
    return "\n".join(out[:30]) + ("\n    [... afgekapt ...]" if len(out) > 30 else "")


def _funnel_profile(chat_id, funnel_mm) -> dict:
    return funnel_mm.get_user_profile(chat_id)


def _log_message(step: int, chat_id: int, command: str,
                 agent: str, handler: TelegramHandler,
                 response: str, before_stage: str, after_profile: dict):
    after_stage = after_profile.get("funnel:stage") or "—"
    count       = after_profile.get("funnel:interaction_count") or 0
    last_agent  = after_profile.get("funnel:last_agent") or "—"
    stage_arrow = f"{before_stage} → {after_stage}" if before_stage != after_stage else after_stage

    print(f"\n  [{step:02d}] KOMUT  : {command}")
    print(f"       AGENT   : {agent}")
    print(f"       STAGE   : {stage_arrow}  |  Etkileşim #{count}  |  Son agent: {last_agent}")
    print(f"       YANIT   :")
    print(_wrap(response))


def _cleanup(chat_id: int, handler: TelegramHandler):
    funnel = handler._funnel
    for key in ["funnel:first_seen", "funnel:last_active", "funnel:last_agent",
                "funnel:interaction_count", "funnel:stage"]:
        funnel.delete_user(chat_id, key)
    for agent in handler.orchestrator.agents.values():
        for key in ["last_task", "last_response"]:
            agent.memory.delete(key, chat_id=chat_id)


def _pre_stage(chat_id: int, handler: TelegramHandler) -> str:
    return handler._funnel.get_user_profile(chat_id).get("funnel:stage") or "—"


# ─────────────────────────────────────────────────────────────────────────────
# SENARYO 1 — Yeni Kullanıcı
# ─────────────────────────────────────────────────────────────────────────────

def scenario_1():
    print(f"\n{SEP2}")
    print("  SENARYO 1 — YENİ KULLANICI")
    print("  chat_id = 9001 | Komutlar: /start, /content, /sales, /research")
    print(SEP2)

    handler = TelegramHandler()
    chat_id = 9001

    steps = [
        ("/start",                          None),
        ("/content enerji düşüklüğü",        "content"),
        ("/sales Happy Juice satışı",         "sales"),
        ("/research Hollanda supplement market", "research"),
    ]

    for i, (cmd, agent_name) in enumerate(steps, 1):
        before = _pre_stage(chat_id, handler)
        response = handler.handle(cmd, chat_id=chat_id)
        after   = _funnel_profile(chat_id, handler._funnel)
        _log_message(i, chat_id, cmd, agent_name or "—(start)", handler, response, before, after)

    _cleanup(chat_id, handler)
    print(f"\n{SEP}")
    print("  ✓ Senaryo 1 tamamlandı")


# ─────────────────────────────────────────────────────────────────────────────
# SENARYO 2 — Stage Değişimi (awareness → interest)
# ─────────────────────────────────────────────────────────────────────────────

def scenario_2():
    print(f"\n{SEP2}")
    print("  SENARYO 2 — STAGE DEĞİŞİMİ  (awareness → interest)")
    print("  chat_id = 9002 | 5 mesaj gönderilecek, stage geçişi izlenecek")
    print(SEP2)

    handler = TelegramHandler()
    chat_id = 9002

    messages = [
        ("/content enerji düşüklüğü için Instagram post",     "content"),
        ("/content mutlu anneler için Reels fikri",           "content"),
        ("/sales MentaBiotics için DM script",                "sales"),
        ("/content Happy Juice için carousel",                "content"),
        ("/sales EDGE+ için kapanış mesajı",                  "sales"),
    ]

    for i, (cmd, agent_name) in enumerate(messages, 1):
        before = _pre_stage(chat_id, handler)
        response = handler.handle(cmd, chat_id=chat_id)
        after   = _funnel_profile(chat_id, handler._funnel)
        stage_label = after.get("funnel:stage") or "—"
        count       = after.get("funnel:interaction_count") or 0

        print(f"\n  [{i:02d}] {cmd[:55]}")
        print(f"       Stage: {before} → {stage_label}  |  #{count}")
        # Show only first 150 chars of response
        short = response[:150].replace("\n", " ") + ("..." if len(response) > 150 else "")
        print(f"       Yanıt: {short}")

    final = _funnel_profile(chat_id, handler._funnel)
    print(f"\n  ÖZET: {final.get('funnel:interaction_count')} etkileşim | "
          f"Final stage: {final.get('funnel:stage').upper()}")

    _cleanup(chat_id, handler)
    print(f"\n{SEP}")
    print("  ✓ Senaryo 2 tamamlandı")


# ─────────────────────────────────────────────────────────────────────────────
# SENARYO 3 — Intent Kullanıcısı
# ─────────────────────────────────────────────────────────────────────────────

def scenario_3():
    print(f"\n{SEP2}")
    print("  SENARYO 3 — SATINALAMAYA YAKLAŞAN KULLANICI (intent stage)")
    print("  chat_id = 9003 | 10 önceki etkileşim simüle edilecek, sonra /sales")
    print(SEP2)

    handler = TelegramHandler()
    chat_id = 9003

    # Pre-seed funnel with 10 interactions so user is in "intent" stage
    print("\n  [SİMÜLASYON] 10 önceki etkileşim yükleniyor...")
    for j in range(10):
        handler._funnel.track_interaction(chat_id=chat_id, agent="cmo", task=f"prev_task_{j}")

    before_profile = _funnel_profile(chat_id, handler._funnel)
    print(f"  Başlangıç stage: {before_profile.get('funnel:stage').upper()} "
          f"| Etkileşim sayısı: {before_profile.get('funnel:interaction_count')}")

    # Now send a real message — AI should see INTENT stage in prompt
    print(f"\n  [{11}] KOMUT  : /sales Happy Juice — ik wil bestellen")
    before = _pre_stage(chat_id, handler)
    response = handler.handle("/sales Happy Juice — ik wil bestellen", chat_id=chat_id)
    after = _funnel_profile(chat_id, handler._funnel)
    print(f"       STAGE   : {before} → {after.get('funnel:stage')}  "
          f"|  Etkileşim #{after.get('funnel:interaction_count')}")
    print(f"       YANIT   :")
    print(_wrap(response))

    _cleanup(chat_id, handler)
    print(f"\n{SEP}")
    print("  ✓ Senaryo 3 tamamlandı")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{SEP2}")
    print("  PHASE 9 — LIVE SYSTEM SIMULATION")
    print(f"  Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  AI provider: OpenAI gpt-4.1-mini  (ANTHROPIC_API_KEY eksik)")
    print(f"  Stack: TelegramHandler → Orchestrator → Agent → OpenAI")
    print(SEP2)

    start = time.time()

    scenario_1()
    scenario_2()
    scenario_3()

    elapsed = time.time() - start
    print(f"\n{SEP2}")
    print(f"  SİMÜLASYON TAMAMLANDI  ({elapsed:.1f}s)")
    print(SEP2)
