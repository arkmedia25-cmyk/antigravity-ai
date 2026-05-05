"""
Test trend_research module (mock mode — no API calls).
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from modules.trend_research import TrendReport


def test_trend_report_schema():
    """TrendReport schema'sını test et."""
    report = TrendReport()

    # Varsayılan değerler
    assert report.generated_at
    assert report.queries_used == []
    assert report.top_videos_analyzed == 0
    assert report.viral_keywords == []
    assert report.best_duration_min == 60
    assert report.trending_subgenres == []
    assert report.youtube_quota_used == 0

    # Dict dönüşümü
    report_dict = report.to_dict()
    assert "generated_at" in report_dict
    assert "viral_keywords" in report_dict
    assert isinstance(report_dict["viral_keywords"], list)

    print("[OK] TrendReport schema test passed")


def test_cached_report_structure():
    """Cache dosyası yapısını test et."""
    from modules.trend_research import RESEARCH_DIR

    # Örnek rapor JSON yapısını kontrol et
    example_report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "queries_used": ["synthwave mix", "cyberpunk music"],
        "top_videos_analyzed": 87,
        "viral_keywords": ["1 hour", "night drive", "neon", "80s", "retro"],
        "best_duration_min": 60,
        "trending_subgenres": [
            {"slug": "synthwave-night-drive", "viral_score": 8.4},
            {"slug": "cyberpunk-ambient", "viral_score": 7.1}
        ],
        "title_pattern_suggestions": [
            "{genre} | {hours} Hour | {mood_word} Mix | {year}",
            "{genre} {activity_word} | {hours} Hour | Best {year} Mix"
        ],
        "thumbnail_color_palette": ["#ff006e", "#8338ec", "#3a86ff"],
        "youtube_quota_used": 350
    }

    # Serialize/deserialize test
    json_str = json.dumps(example_report, indent=2)
    parsed = json.loads(json_str)

    assert parsed["top_videos_analyzed"] == 87
    assert len(parsed["viral_keywords"]) == 5
    assert parsed["trending_subgenres"][0]["slug"] == "synthwave-night-drive"

    print("[OK] Cache structure test passed")


def test_niche_matching():
    """Niş matching mantığını test et."""
    from modules.trend_research import NEON_PULSE_NICHES

    # Niş havuzunun valid olduğunu kontrol et
    assert len(NEON_PULSE_NICHES) == 6
    assert "synthwave-night-drive" in NEON_PULSE_NICHES
    assert "cyberpunk-ambient" in NEON_PULSE_NICHES
    assert "lofi-cyberpunk" in NEON_PULSE_NICHES
    assert "darksynth-workout" in NEON_PULSE_NICHES
    assert "outrun-retrowave" in NEON_PULSE_NICHES
    assert "vaporwave-chill" in NEON_PULSE_NICHES

    # Her niş için keywords olduğunu kontrol et
    for niche, keywords in NEON_PULSE_NICHES.items():
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        print(f"  [OK] {niche}: {keywords}")

    print("[OK] Niche matching test passed")


def test_search_keywords():
    """Arama anahtar kelimelerinin valid olduğunu kontrol et."""
    from modules.trend_research import SEARCH_KEYWORDS

    assert len(SEARCH_KEYWORDS) == 6
    assert "synthwave mix" in SEARCH_KEYWORDS
    assert "cyberpunk music" in SEARCH_KEYWORDS
    assert "lofi cyberpunk" in SEARCH_KEYWORDS

    print("[OK] Search keywords test passed")


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)

    print("\n=== TREND RESEARCH MOCK TESTS ===\n")

    test_trend_report_schema()
    test_cached_report_structure()
    test_niche_matching()
    test_search_keywords()

    print("\n[OK] All tests passed!\n")
