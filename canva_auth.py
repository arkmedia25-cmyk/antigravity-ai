"""
Standalone Canva OAuth helper — run this directly to authorize Canva.

Usage (on the DigitalOcean server):
    python canva_auth.py

It will:
1. Print the authorization URL — open it in your browser and authorize.
2. Canva redirects to https://arkmediaflow.com/canva/callback?code=...
3. Copy the FULL URL from your browser address bar and paste it here.
4. The script exchanges the code for tokens and saves them to the DB.
"""

import os
import sys
import json
import pathlib

# Auto-load .env
from dotenv import load_dotenv
load_dotenv()

# Make src/ importable
_root = pathlib.Path(__file__).parent
sys.path.insert(0, str(_root))

from src.skills import canva_client
from src.memory.memory_manager import MemoryManager

CHAT_ID = 812914122  # Admin chat_id
_PKCE_FILE = pathlib.Path("/tmp") / f"canva_pkce_{CHAT_ID}.json"


def step1_generate_url():
    auth_url, code_verifier = canva_client.get_auth_url(state=str(CHAT_ID))

    # Save verifier to file
    _PKCE_FILE.write_text(json.dumps({"verifier": code_verifier}))
    print(f"\n✅ PKCE verifier opgeslagen in: {_PKCE_FILE}")

    # Also save to SQLite
    mem = MemoryManager(namespace="canva_tokens")
    mem.save(f"pkce_{CHAT_ID}", code_verifier)
    print("✅ PKCE verifier ook opgeslagen in SQLite")

    print("\n" + "="*60)
    print("STAP 1: Open deze URL in je browser en geef toegang aan Canva:")
    print("="*60)
    print(f"\n{auth_url}\n")
    print("="*60)
    print("\nNa het goedkeuren word je teruggestuurd naar arkmediaflow.com.")
    print("Kopieer de VOLLEDIGE URL uit je browser adresbalk en plak hem hier:\n")


def step2_exchange_code(full_callback_url: str):
    from urllib.parse import urlparse, parse_qs

    parsed = urlparse(full_callback_url)
    params = parse_qs(parsed.query)

    code = params.get("code", [None])[0]
    if not code:
        print(f"❌ Geen 'code' gevonden in URL: {full_callback_url}")
        sys.exit(1)

    # Load verifier
    code_verifier = None
    if _PKCE_FILE.exists():
        data = json.loads(_PKCE_FILE.read_text())
        code_verifier = data.get("verifier")
        print("✅ PKCE verifier geladen uit bestand")

    if not code_verifier:
        mem = MemoryManager(namespace="canva_tokens")
        code_verifier = mem.load(f"pkce_{CHAT_ID}")
        if code_verifier:
            print("✅ PKCE verifier geladen uit SQLite")

    if not code_verifier:
        print("❌ PKCE verifier niet gevonden. Voer stap 1 opnieuw uit.")
        sys.exit(1)

    print("\nTokens worden uitgewisseld met Canva...")
    tokens = canva_client.exchange_code(code, code_verifier)

    access_token = tokens["access_token"]
    refresh_token = tokens.get("refresh_token", "")

    mem = MemoryManager(namespace="canva_tokens")
    mem.save("access_token", access_token, chat_id=CHAT_ID)
    if refresh_token:
        mem.save("refresh_token", refresh_token, chat_id=CHAT_ID)

    # Clean up verifier
    if _PKCE_FILE.exists():
        _PKCE_FILE.unlink()
    mem.delete(f"pkce_{CHAT_ID}")

    print("\n" + "="*60)
    print("✅ Canva succesvol gekoppeld!")
    print(f"Access token (eerste 30 tekens): {access_token[:30]}...")
    print("Je kunt nu /canva instagram <titel> gebruiken in Telegram.")
    print("="*60)


def main():
    step1_generate_url()

    callback_url = input("Plak hier de volledige callback URL: ").strip()
    if not callback_url:
        print("❌ Geen URL ingevoerd.")
        sys.exit(1)

    step2_exchange_code(callback_url)


if __name__ == "__main__":
    main()
