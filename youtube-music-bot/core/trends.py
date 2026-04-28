"""
Google Trends — nişin haftalık trend skoru.
Kütüphane: pytrends
"""
from pytrends.request import TrendReq


# Niş için arama anahtar kelimeleri
NICHE_KEYWORDS = {
    "deep-sleep-432hz":   ["432hz sleep music", "healing frequency sleep"],
    "rain-sleep":         ["rain sleep music", "rain sounds for sleeping"],
    "delta-waves-sleep":  ["delta waves sleep", "deep sleep music"],
    "piano-sleep":        ["piano sleep music", "relaxing piano"],
    "nature-sleep":       ["nature sounds sleep", "forest sounds sleep"],
    "528hz-healing":      ["528hz healing", "solfeggio frequencies"],
    "tibetan-bowls":      ["tibetan singing bowls", "meditation music"],
    "alpha-focus":        ["alpha waves focus", "binaural beats study"],
    "chakra-healing":     ["chakra healing music", "chakra meditation"],
    "spa-relaxation":     ["spa music", "relaxation music"],
    "epic-cinematic":     ["epic cinematic music", "trailer music"],
    "electronic-focus":   ["electronic focus music", "study beats"],
    "dark-cinematic":     ["dark cinematic music", "thriller soundtrack"],
    "energy-edm":         ["edm workout music", "energy music"],
    "futuristic-ambient": ["ambient music", "cyberpunk music"],
}

DEFAULT_KEYWORDS = ["relaxing music", "sleep music"]


def get_trend_score(niche_slug: str, geo: str = "") -> dict:
    """
    Niş için Google Trends skoru döndür (0-100).
    geo: "" = dünya, "NL" = Hollanda, "US" = ABD
    """
    keywords = NICHE_KEYWORDS.get(niche_slug, DEFAULT_KEYWORDS)

    try:
        pt = TrendReq(hl="en-US", tz=60, timeout=(10, 25))
        pt.build_payload(keywords[:5], cat=0, timeframe="now 7-d", geo=geo)
        df = pt.interest_over_time()

        if df.empty:
            return {"score": 0, "trend": "unknown", "keywords": keywords}

        scores = {kw: int(df[kw].mean()) for kw in keywords if kw in df.columns}
        avg_score = int(sum(scores.values()) / len(scores)) if scores else 0

        # Trend yönü: son 2 gün vs önceki 5 gün
        if len(df) >= 7:
            recent = df[keywords[0]].iloc[-2:].mean()
            older = df[keywords[0]].iloc[:-2].mean()
            trend = "up" if recent > older * 1.05 else ("down" if recent < older * 0.95 else "stable")
        else:
            trend = "stable"

        return {
            "score": avg_score,
            "trend": trend,
            "keywords": keywords,
            "scores": scores,
        }

    except Exception as e:
        return {"score": 0, "trend": "error", "error": str(e), "keywords": keywords}
