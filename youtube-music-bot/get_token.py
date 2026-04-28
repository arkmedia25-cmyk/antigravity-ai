"""
YouTube OAuth token — headless server compatible.
Usage: python get_token.py --channel sleepwave
Token is saved to: channels/{slug}/token.pickle
"""
import os
import sys
import pickle
import argparse
from pathlib import Path
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

CLIENT_CONFIG = {
    "installed": {
        "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", required=True, help="Channel slug (neonpulse, sleepwave, ...)")
    args = parser.parse_args()

    token_path = Path(f"channels/{args.channel}/token.pickle")
    token_path.parent.mkdir(parents=True, exist_ok=True)

    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)

    print(f"\n{'='*60}")
    print(f"Channel: {args.channel}")
    print(f"Token target: {token_path}")
    print(f"{'='*60}")
    print("\nBrowser will not open automatically — copy the URL below and open it manually.\n")

    creds = flow.run_local_server(port=8080, prompt="select_account", open_browser=False)

    with open(token_path, "wb") as f:
        pickle.dump(creds, f)

    print(f"\nToken saved: {token_path}")
    print(f"   Channel {args.channel} is now authorized to upload.\n")


if __name__ == "__main__":
    main()
