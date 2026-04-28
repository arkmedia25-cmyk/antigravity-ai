"""
ChannelAgent — tek bir YouTube kanalını analiz eder.
Her hafta çalışır, Claude API ile rapor üretir.
"""
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv()

from core import analytics, trends, competitor

CLAUDE_MODEL = "claude-sonnet-4-6"
PROMPT_FILE = Path(__file__).parent / "prompts" / "channel.md"


def _load_prompt(channel_name: str, niche_desc: str) -> str:
    template = PROMPT_FILE.read_text(encoding="utf-8")
    return template.replace("{channel_name}", channel_name).replace("{niche_description}", niche_desc)


def _collect_data(channel: dict, genres: list) -> dict:
    """Analytics + Trends + Competitor verisi topla."""
    token_file = Path(channel["token_file"])
    channel_id = channel.get("youtube_channel_id", "")

    # 1. YouTube Analytics (kanal doğrulanmışsa)
    stats = {}
    if channel_id and token_file.exists():
        try:
            stats = analytics.get_weekly_stats(token_file, channel_id)
        except Exception as e:
            stats = {"error": str(e)}

    # 2. Google Trends — her niş için skor
    trend_scores = []
    for genre in genres[:3]:  # İlk 3 nişi kontrol et
        score = trends.get_trend_score(genre["slug"])
        trend_scores.append({"slug": genre["slug"], **score})

    # 3. Rakip analizi — en iyi nişin arama terimi
    top_genre = genres[0]
    search_query = " ".join(top_genre["prompt"].split(",")[:3]).strip()
    comp = {}
    if token_file.exists():
        try:
            comp = competitor.get_competitor_summary(token_file, top_genre["slug"], search_query)
        except Exception as e:
            comp = {"error": str(e)}

    return {
        "channel": channel["name"],
        "weekly_analytics": stats,
        "trend_scores": trend_scores,
        "competitor_summary": comp,
        "genres": [g["slug"] for g in genres],
    }


def run(channel_slug: str) -> dict:
    """Kanal analizi yap, Claude ile rapor üret, döndür."""
    channel_dir = Path(f"channels/{channel_slug}")
    channel = json.loads((channel_dir / "channel.json").read_text())
    genres = json.loads((channel_dir / "genres.json").read_text())

    print(f"[channel_agent] {channel['name']} analizi başlıyor...")

    # Veri topla
    data = _collect_data(channel, genres)
    niche_desc = f"Nişler: {', '.join(data['genres'])}"

    # Claude API ile analiz
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    system_prompt = _load_prompt(channel["name"], niche_desc)

    user_message = f"""
Haftalık veriler:

```json
{json.dumps(data, indent=2, ensure_ascii=False)}
```

Bu verileri analiz et ve rapor üret.
"""

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = next(b.text for b in response.content if hasattr(b, "text")).strip()

    # JSON parse
    try:
        # Kod bloğu varsa temizle
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        report = json.loads(raw)
    except Exception:
        report = {"channel": channel["name"], "raw": raw, "parse_error": True}

    report["_raw_data"] = data
    print(f"[channel_agent] {channel['name']} raporu hazır. Skor: {report.get('week_score', '?')}")
    return report
