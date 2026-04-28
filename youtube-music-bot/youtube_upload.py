import os
import datetime
from pathlib import Path
from dotenv import load_dotenv

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = Path("token.pickle")  # varsayılan, run() üzerinden override edilir

CLIENT_CONFIG = {
    "installed": {
        "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
        "redirect_uris": ["http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

TAGS = [
    "sleep music", "432hz", "healing frequencies", "no ads",
    "relaxing music", "study music", "ambient", "meditation music",
    "deep sleep", "focus music", "lofi", "binaural beats"
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


def _build_description(genre: dict) -> str:
    hook = genre.get("hook", "Pure AI-generated music for focus, sleep, and relaxation.")
    use_cases = genre.get("use_cases", "sleep, study, meditation, and relaxation")
    hashtags = genre.get("hashtags", "#sleepmusic #relaxingmusic #studymusic #432hz #ambientmusic")
    
    return f"""{hook}

Perfect for: {use_cases}
No ads. No interruptions. Just pure music.

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎵 New videos every day — Subscribe for daily music
👍 Like this video to support the channel
💬 Let us know your experience in the comments
📧 Business: info@kbmedia.nl
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{hashtags}
"""


def upload(video_path: Path, thumbnail_path: Path, genre: dict, duration_min: int, token_file: Path = TOKEN_FILE) -> str:
    creds = _get_credentials(token_file)
    youtube = build("youtube", "v3", credentials=creds)

    year = datetime.datetime.now().year
    title = genre["title"].format(duration=duration_min, year=year)
    description = _build_description(genre)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": genre.get("tags", TAGS),
            "categoryId": "10",  # Music
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[youtube] Yükleniyor: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"[youtube] Yüklendi: https://youtu.be/{video_id}")

    # Thumbnail yükle
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
    ).execute()
    print(f"[youtube] Thumbnail eklendi")

    return f"https://youtu.be/{video_id}"


def run(video_path: Path, thumbnail_path: Path, genre: dict, duration_min: int, token_file: Path = TOKEN_FILE) -> str:
    return upload(video_path, thumbnail_path, genre, duration_min, token_file)
