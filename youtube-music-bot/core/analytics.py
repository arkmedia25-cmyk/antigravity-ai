"""
YouTube Analytics API — kanal performans verisi.
Gerekli scope: youtube.readonly + yt-analytics.readonly
"""
import pickle
from pathlib import Path
from datetime import date, timedelta
from googleapiclient.discovery import build


def _build_service(token_file: Path):
    with open(token_file, "rb") as f:
        creds = pickle.load(f)
    return build("youtubeAnalytics", "v2", credentials=creds)


def get_weekly_stats(token_file: Path, channel_id: str) -> dict:
    """Son 7 günün temel metriklerini döndür."""
    svc = _build_service(token_file)

    end = date.today()
    start = end - timedelta(days=7)

    result = svc.reports().query(
        ids=f"channel=={channel_id}",
        startDate=str(start),
        endDate=str(end),
        metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost",
        dimensions="",
    ).execute()

    rows = result.get("rows", [[0, 0, 0, 0, 0]])
    row = rows[0] if rows else [0, 0, 0, 0, 0]

    return {
        "views": int(row[0]),
        "watch_minutes": int(row[1]),
        "avg_duration_sec": int(row[2]),
        "subs_gained": int(row[3]),
        "subs_lost": int(row[4]),
        "net_subs": int(row[3]) - int(row[4]),
        "period": f"{start} → {end}",
    }


def get_top_videos(token_file: Path, channel_id: str, n: int = 5) -> list[dict]:
    """Son 30 günün en çok izlenen videolarını döndür."""
    svc = _build_service(token_file)

    end = date.today()
    start = end - timedelta(days=30)

    result = svc.reports().query(
        ids=f"channel=={channel_id}",
        startDate=str(start),
        endDate=str(end),
        metrics="views,estimatedMinutesWatched,averageViewDuration",
        dimensions="video",
        sort="-views",
        maxResults=n,
    ).execute()

    videos = []
    for row in result.get("rows", []):
        videos.append({
            "video_id": row[0],
            "views": int(row[1]),
            "watch_minutes": int(row[2]),
            "avg_duration_sec": int(row[3]),
            "url": f"https://youtu.be/{row[0]}",
        })
    return videos
