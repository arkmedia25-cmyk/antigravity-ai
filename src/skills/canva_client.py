import base64
import hashlib
import os
import secrets
import requests
from urllib.parse import urlencode, quote

CANVA_AUTH_URL = "https://www.canva.com/api/oauth/authorize"
CANVA_TOKEN_URL = "https://api.canva.com/rest/v1/oauth/token"
CANVA_API_BASE = "https://api.canva.com/rest/v1"
SCOPES = "design:content:read design:content:write design:meta:read"

# Kept for backward compat — no longer used for primary storage
_pending_verifiers: dict = {}

DESIGN_TYPES = {
    # Statische afbeeldingen
    "instagram": "INSTAGRAM_POST",
    "story": "INSTAGRAM_STORY",
    "facebook": "FACEBOOK_POST",
    "linkedin": "LINKEDIN_POST",
    "presentatie": "PRESENTATION_16_9",
    "flyer": "FLYER_PORTRAIT",
    "poster": "POSTER_PORTRAIT",
    # Video
    "video": "VIDEO_MESSAGE",
    "tiktok": "TIKTOK_VIDEO",
    "reels": "INSTAGRAM_REEL",
    "youtube": "YOUTUBE_VIDEO",
}

# Export formats per design type
EXPORT_FORMAT = {
    "video": "MP4",
    "tiktok": "MP4",
    "reels": "MP4",
    "youtube": "MP4",
}


def _get_client_id() -> str:
    val = os.getenv("CANVA_CLIENT_ID", "")
    if not val:
        raise ValueError("CANVA_CLIENT_ID is not set in .env")
    return val


def _get_client_secret() -> str:
    val = os.getenv("CANVA_CLIENT_SECRET", "")
    if not val:
        raise ValueError("CANVA_CLIENT_SECRET is not set in .env")
    return val


def _get_redirect_uri() -> str:
    val = os.getenv("CANVA_REDIRECT_URI", "")
    if not val:
        raise ValueError("CANVA_REDIRECT_URI is not set in .env")
    return val


def get_auth_url(state: str) -> tuple:
    """Generate Canva OAuth URL with PKCE.
    Returns (auth_url, code_verifier) — caller is responsible for storing the verifier.
    """
    client_id = _get_client_id()
    redirect_uri = _get_redirect_uri()

    code_verifier = secrets.token_urlsafe(64)
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": SCOPES,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f"{CANVA_AUTH_URL}?{urlencode(params, quote_via=quote)}"

    print(f"[Canva OAuth] client_id    = {client_id}")
    print(f"[Canva OAuth] redirect_uri = {redirect_uri}")
    print(f"[Canva OAuth] scope        = {SCOPES}")
    print(f"[Canva OAuth] state        = {state}")
    print(f"[Canva OAuth] full URL     = {auth_url}")

    return auth_url, code_verifier


def _basic_auth_header() -> dict:
    """Build HTTP Basic Auth header from client_id:client_secret."""
    credentials = base64.b64encode(
        f"{_get_client_id()}:{_get_client_secret()}".encode()
    ).decode()
    return {"Authorization": f"Basic {credentials}"}


def exchange_code(code: str, code_verifier: str) -> dict:
    """Exchange authorization code + PKCE verifier for tokens."""
    resp = requests.post(
        CANVA_TOKEN_URL,
        headers=_basic_auth_header(),
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": _get_redirect_uri(),
            "code_verifier": code_verifier,
        },
        timeout=30,
    )
    print(f"[Canva token] exchange status={resp.status_code}")
    print(f"[Canva token] response body={resp.text[:500]}")
    if not resp.ok:
        raise RuntimeError(f"Canva token error {resp.status_code}: {resp.text[:500]}")
    return resp.json()


def refresh_access_token(refresh_token: str) -> dict:
    """Refresh an expired access token."""
    resp = requests.post(
        CANVA_TOKEN_URL,
        headers=_basic_auth_header(),
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def create_design(access_token: str, design_type_key: str, title: str = "", template_id_override: str = "") -> dict:
    """Create a new Canva design. Returns full API response."""
    if template_id_override:
        json_data = {
            "design_type": {"type": "template", "asset_id": template_id_override},
            "title": title or "Antigravity Design",
        }
    else:
        preset_name = DESIGN_TYPES.get(design_type_key.lower(), "INSTAGRAM_POST")
        json_data = {
            "design_type": {"type": "preset", "name": preset_name},
            "title": title or "Antigravity Design",
        }
        
    resp = requests.post(
        f"{CANVA_API_BASE}/designs",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json_data,
        timeout=30,
    )
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Canva HTTP Error {resp.status_code}: {resp.text} - {e}")
    try:
        return resp.json()
    except Exception as e:
        raise RuntimeError(f"Canva JSON Error | Status: {resp.status_code} | Body: {resp.text[:500]} | Err: {e}")


def start_export(access_token: str, design_id: str, fmt: str = "PNG") -> dict:
    """Start an async export job. Returns job info with export_id."""
    resp = requests.post(
        f"{CANVA_API_BASE}/exports",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"design_id": design_id, "format": {"type": fmt}},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_export_status(access_token: str, export_id: str) -> dict:
    """Check export job status. Status: in_progress | success | failed."""
    resp = requests.get(
        f"{CANVA_API_BASE}/exports/{export_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def wait_for_export(access_token: str, export_id: str, timeout: int = 90) -> list:
    """Poll export status until done. Returns list of download URLs."""
    import time
    deadline = time.time() + timeout
    while time.time() < deadline:
        status = get_export_status(access_token, export_id)
        job = status.get("job", {})
        state = job.get("status", "")
        if state == "success":
            return job.get("urls", [])
        if state == "failed":
            raise RuntimeError(f"Export mislukt: {job.get('error', 'onbekende fout')}")
        time.sleep(3)
    raise TimeoutError("Export duurde te lang (>90 seconden).")
