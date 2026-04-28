"""
Orchestrator — tüm kanal raporlarını toplar, öncelik belirler.
Claude API ile stratejik karar üretir, Telegram'a özet gönderir.
"""
import json
import os
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv()

from core import notifier

CLAUDE_MODEL = "claude-sonnet-4-6"
PROMPT_FILE = Path(__file__).parent / "prompts" / "orchestrator.md"
REPORTS_DIR = Path("logs/agent_reports")


def _save_report(slug: str, report: dict) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / f"{slug}_{date.today()}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))


def _load_all_channels() -> list[str]:
    """channels/ altındaki tüm kanal slug'larını döndür."""
    return [
        d.name for d in Path("channels").iterdir()
        if d.is_dir() and (d / "channel.json").exists()
    ]


def run(channel_slugs: list[str] | None = None) -> dict:
    """
    Tüm kanalları analiz et, orkestratör kararını üret.
    channel_slugs: belirtilmezse tüm kanallar çalışır.
    """
    from agents import channel_agent  # circular import önlemi

    slugs = channel_slugs or _load_all_channels()
    print(f"[orchestrator] {len(slugs)} kanal analiz ediliyor: {slugs}")

    # 1. Her kanal için agent çalıştır
    channel_reports = {}
    for slug in slugs:
        try:
            report = channel_agent.run(slug)
            channel_reports[slug] = report
            _save_report(slug, report)
        except Exception as e:
            print(f"[orchestrator] {slug} hatası: {e}")
            channel_reports[slug] = {"error": str(e), "channel": slug}

    # 2. Orkestratör prompt'u hazırla
    system_prompt = PROMPT_FILE.read_text(encoding="utf-8")
    week = date.today().isocalendar()
    week_str = f"{week.year}-W{week.week:02d}"

    user_message = f"""
Hafta: {week_str}

Kanal raporları:

```json
{json.dumps(channel_reports, indent=2, ensure_ascii=False)}
```

Bu raporları değerlendir ve orkestratör kararını üret.
"""

    # 3. Claude API — orkestratör kararı
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = next(b.text for b in response.content if hasattr(b, "text")).strip()

    try:
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        decision = json.loads(raw)
    except Exception:
        decision = {"raw": raw, "parse_error": True, "week": week_str}

    # 4. Orkestratör raporunu kaydet
    _save_report("orchestrator", decision)

    # 5. Telegram'a özet gönder
    summary = decision.get("telegram_summary", str(decision))
    notifier.orchestrator_summary(summary)

    print(f"[orchestrator] Karar üretildi. Öncelikli kanal: {decision.get('priority_channel', '?')}")
    return decision
