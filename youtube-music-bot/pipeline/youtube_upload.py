import os
import datetime
import pytz
import pickle
from pathlib import Path
from dotenv import load_dotenv

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = Path("token.pickle")

CLIENT_CONFIG = {
    "installed": {
        "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
        "redirect_uris": ["http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

GLOBAL_TAGS = [
    "no ads", "no interruptions", "relaxing music", "ambient music",
    "instrumental music", "background music", "ai music",
]


def _get_credentials(token_file: Path):
    creds = None
    if token_file.exists():
        with open(token_file, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)

    return creds


def _pick_title(genre: dict, duration_min: int) -> tuple[str, str]:
    """Ana baslik ve A/B test basligini don. Rotation index'e gore hangisinin kullanildigini logla."""
    year = datetime.datetime.now().year
    title_a = genre["title"].format(duration=duration_min, year=year)
    title_ab = genre.get("title_ab", title_a).format(duration=duration_min, year=year)

    # Gün çift → A, tek → AB (basit A/B rotasyonu)
    day = datetime.datetime.now().day
    if day % 2 == 0:
        chosen, variant = title_a, "A"
    else:
        chosen, variant = title_ab, "AB"

    print(f"[youtube] Başlık variant {variant}: {chosen}")
    return chosen, variant


def _build_tags(genre: dict) -> list[str]:
    """Genre-spesifik + global tag'leri birleştir, max 500 karakter."""
    genre_tags = genre.get("tags", [])
    combined = genre_tags + [t for t in GLOBAL_TAGS if t not in genre_tags]
    # YouTube tag limiti: toplam 500 karakter
    result, total = [], 0
    for tag in combined:
        if total + len(tag) + 2 > 500:
            break
        result.append(tag)
        total += len(tag) + 2
    return result


def _build_description(genre: dict, duration_min: int, title_variant: str) -> str:
    hook = genre.get("hook", "Pure AI-generated music for focus, sleep, and relaxation.")
    use_cases = genre.get("use_cases", "relaxation, sleep, focus, meditation")
    hashtags = genre.get("hashtags", "#relaxingmusic #ambientmusic #noads")

    return f"""{hook}

Perfect for: {use_cases}.
No ads. No interruptions. Just pure music.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎵 New videos every day — Subscribe for daily music
📧 Business: info@kbmedia.nl
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{hashtags}

[Title variant: {title_variant}]
"""


def upload(
    video_path: Path,
    thumbnail_path: Path,
    genre: dict,
    duration_min: int,
    token_file: Path = TOKEN_FILE,
    publish_hour: int | None = None,
) -> str:
    creds = _get_credentials(token_file)
    youtube = build("youtube", "v3", credentials=creds)

    title, title_variant = _pick_title(genre, duration_min)
    description = _build_description(genre, duration_min, title_variant)
    tags = _build_tags(genre)

    status_body: dict = {"selfDeclaredMadeForKids": False}

    # publish_hour: parametre > genre ayarı > public (hemen)
    effective_hour = publish_hour if publish_hour is not None else genre.get("publish_hour_cest")

    if genre.get("force_private"):
        status_body["privacyStatus"] = "private"
    elif effective_hour is not None:
        tz = pytz.timezone("Europe/Amsterdam")
        now = datetime.datetime.now(tz)
        publish_dt = now.replace(hour=effective_hour, minute=0, second=0, microsecond=0)
        if publish_dt <= now:
            publish_dt += datetime.timedelta(days=1)
        publish_utc = publish_dt.astimezone(pytz.utc)
        status_body["privacyStatus"] = "private"
        status_body["publishAt"] = publish_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        print(f"[youtube] Zamanlanmış yayın: {publish_dt.strftime('%d %b %H:%M')} Amsterdam")
    else:
        status_body["privacyStatus"] = "public"

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "10",
        },
        "status": status_body,
    }

    print(f"[youtube] Tags ({len(tags)}): {tags[:5]}...")
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[youtube] Yükleniyor: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"[youtube] Yüklendi: https://youtu.be/{video_id}")

    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
        ).execute()
        print(f"[youtube] Thumbnail eklendi")
    except Exception as e:
        print(f"[youtube] Thumbnail eklenemedi (kanal yeni olabilir): {e}")

    return f"https://youtu.be/{video_id}"


def run(
    video_path: Path,
    thumbnail_path: Path,
    genre: dict,
    duration_min: int,
    token_file: Path = TOKEN_FILE,
    publish_hour: int | None = None,
) -> str:
    return upload(video_path, thumbnail_path, genre, duration_min, token_file, publish_hour)
