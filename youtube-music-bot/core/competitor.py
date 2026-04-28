"""
YouTube Search API — rakip kanal analizi.
Bu hafta nişte hangi videolar yüklendi, kaç view aldı?
"""
import pickle
from pathlib import Path
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build


def _build_service(token_file: Path):
    with open(token_file, "rb") as f:
        creds = pickle.load(f)
    return build("youtube", "v3", credentials=creds)


def get_trending_videos(token_file: Path, query: str, max_results: int = 10) -> list[dict]:
    """
    Verilen arama sorgusunda son 7 günde yüklenen videoları bul.
    Sıralama: viewCount (en çok izlenen önce)
    """
    svc = _build_service(token_file)

    published_after = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    search_resp = svc.search().list(
        q=query,
        part="snippet",
        type="video",
        videoCategoryId="10",  # Music
        order="viewCount",
        publishedAfter=published_after,
        maxResults=max_results,
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]
    if not video_ids:
        return []

    # Video istatistiklerini çek
    stats_resp = svc.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids),
    ).execute()

    videos = []
    for item in stats_resp.get("items", []):
        stats = item.get("statistics", {})
        snippet = item.get("snippet", {})
        videos.append({
            "video_id": item["id"],
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "published": snippet.get("publishedAt", "")[:10],
            "url": f"https://youtu.be/{item['id']}",
        })

    return sorted(videos, key=lambda v: v["views"], reverse=True)


def get_competitor_summary(token_file: Path, niche_slug: str, search_query: str) -> dict:
    """Niş için rakip özeti döndür."""
    videos = get_trending_videos(token_file, search_query)
    if not videos:
        return {"niche": niche_slug, "top_videos": [], "avg_views": 0, "insight": "Veri yok"}

    avg_views = sum(v["views"] for v in videos) // len(videos)
    top3 = videos[:3]

    return {
        "niche": niche_slug,
        "query": search_query,
        "top_videos": top3,
        "avg_views": avg_views,
        "total_found": len(videos),
        "insight": f"Bu hafta '{search_query}' için ortalama {avg_views:,} görüntülenme",
    }
