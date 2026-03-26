import time
import requests
import sys
import os
import threading
from dotenv import load_dotenv

try:
    from flask import Flask, request as flask_request
    _flask_available = True
except ImportError:
    _flask_available = False

# Windows konsolunda UTF-8 emoji destegi
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
 
load_dotenv()
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../agents/linkedin-agent"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../agents/content-agent"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../agents/email-agent"))

# Phase 3: add project root so src/ is importable
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
 
from cmo_agent import run_cmo
from linkedin_agent import run_linkedin
from content_agent import run_content
from email_agent import run_email

# Phase 3: try to load new src/ system — bot keeps working if this fails
try:
    from src.interfaces.telegram.handler import TelegramHandler as _NewHandler
    _new_handler = _NewHandler()
    _use_new_system = True
    print("[Phase3] New src/ system loaded successfully")
except Exception as _e:
    _new_handler = None
    _use_new_system = False
    print(f"[Phase3] New src/ system unavailable — fallback active: {_e}")
 
TOKEN = os.getenv("TELEGRAM_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"
 
def safe_request(url, method="get", **kwargs):
    """Veilige API request met retry logic"""
    for i in range(5):
        try:
            if method == "get":
                response = requests.get(url, timeout=30, **kwargs)
            else:
                response = requests.post(url, timeout=30, **kwargs)
            if not response.ok:
                # Log the full Telegram error body before raising
                print(f"[safe_request] HTTP {response.status_code} — Telegram zegt: {response.text}")
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Verbindingsfout (poging {i+1}): {e}")
            if i < 4:
                time.sleep(2)
    return None
 
def get_updates(offset=None):
    """Haal Telegram updates op"""
    params = {"timeout": 20}
    if offset is not None:
        params["offset"] = offset
    response = safe_request(f"{URL}/getUpdates", method="get", params=params)
    if response:
        return response.json()
    return {"result": []}
 
_TELEGRAM_MAX_LEN = 4096


def _safe_text(text) -> str:
    """Convert any value to a plain, non-empty string."""
    if not isinstance(text, str):
        text = str(text)
    text = text.strip()
    return text if text else "(geen inhoud)"


def send_message(chat_id, text):
    """Stuur bericht naar Telegram chat — splits automatisch bij >4096 tekens."""
    text = _safe_text(text)

    # Debug log: length + first 300 chars before every send
    print(f"[send_message] chat_id={chat_id} | len={len(text)} | preview: {text[:300]!r}")

    # Split into chunks so Telegram never receives a payload that is too long
    chunks = [text[i:i + _TELEGRAM_MAX_LEN] for i in range(0, len(text), _TELEGRAM_MAX_LEN)]

    for chunk in chunks:
        data = {"chat_id": chat_id, "text": chunk}
        safe_request(f"{URL}/sendMessage", method="post", data=data)
 
_CANVA_FILE_MARKER = "CANVA_FILE:"


def _send_canva_response(chat_id, response: str):
    """Send Canva agent response. If it contains a file URL, send the file via Telegram."""
    if _CANVA_FILE_MARKER in response:
        lines = response.split("\n")
        file_line = next((l for l in lines if l.startswith(_CANVA_FILE_MARKER)), None)
        text_lines = [l for l in lines if not l.startswith(_CANVA_FILE_MARKER)]
        text_body = "\n".join(text_lines).strip()

        if text_body:
            send_message(chat_id, text_body)

        if file_line:
            payload = file_line[len(_CANVA_FILE_MARKER):]
            parts = payload.split("|")
            file_url = parts[0].strip()
            fmt = parts[1].strip().lower() if len(parts) > 1 else "png"

            if fmt == "mp4":
                safe_request(f"{URL}/sendVideo", method="post",
                             data={"chat_id": chat_id, "video": file_url,
                                   "caption": "🎬 Canva video export"})
            else:
                safe_request(f"{URL}/sendDocument", method="post",
                             data={"chat_id": chat_id, "document": file_url,
                                   "caption": "🖼 Canva export"})
    else:
        send_message(chat_id, response)


def process_command(chat_id, text):
    """Verwerk Telegram commando"""
    try:
        if text.startswith("/start"):
            send_message(chat_id,
                "🚀 Antigravity AI Bot klaar!\n\n"
                "🧠 STRATEGIE\n"
                "/cmo - marketingstrategie & advies\n\n"
                "📱 CONTENT\n"
                "/content - Instagram/Reels content genereren\n"
                "/idea - viraal video idee\n"
                "/seo - YouTube titel en tags\n"
                "/script - video script\n\n"
                "💬 SALES\n"
                "/sales - DM scripts & closing berichten\n\n"
                "📊 ONDERZOEK\n"
                "/research - markttrends & doelgroep analyse\n\n"
                "📧 COMMUNICATIE\n"
                "/email - email reeks schrijven\n"
                "/linkedin - LinkedIn berichten\n\n"
                "🎨 DESIGN & VIDEO\n"
                "/canva - Canva ontwerpen & video's maken\n\n"
                "Voorbeeld: /cmo Stel lead systeem op voor Nederland"
            )

        elif text.startswith("/canva"):
            task = text.replace("/canva", "").strip()
            if not task:
                send_message(chat_id,
                    "🎨 Canva ontwerpen:\n\n"
                    "/canva auth — account koppelen\n\n"
                    "📸 Afbeeldingen:\n"
                    "/canva instagram <titel>\n"
                    "/canva story <titel>\n"
                    "/canva linkedin <titel>\n"
                    "/canva facebook <titel>\n"
                    "/canva flyer <titel>\n"
                    "/canva poster <titel>\n\n"
                    "🎬 Video:\n"
                    "/canva reels <titel>\n"
                    "/canva tiktok <titel>\n"
                    "/canva youtube <titel>\n\n"
                    "📤 Exporteren:\n"
                    "/canva export <design_id>"
                )
            else:
                is_export = task.startswith("export")
                wait_msg = "📤 Exporteren en downloaden... (kan 30-90 seconden duren)" if is_export else "🎨 Canva bezig..."
                send_message(chat_id, wait_msg)
                if _use_new_system:
                    try:
                        response = _new_handler.handle(text, chat_id=chat_id)
                        _send_canva_response(chat_id, response)
                    except Exception as _err:
                        send_message(chat_id, f"❌ Canva fout: {_err}")
                else:
                    send_message(chat_id, "❌ Canva agent niet beschikbaar.")

        elif text.startswith("/email"):
            task = text.replace("/email", "").strip()
            if not task:
                send_message(chat_id,
                    "❗ Voorbeeldgebruik:\n\n"
                    "/email 5-daagse nurture reeks voor nieuwe leads\n"
                    "/email Happy Juice introductie mail\n"
                    "/email welkomstmail voor nieuwe zakenpartner\n"
                    "/email follow-up mail voor niet-reagerende lead"
                )
            else:
                send_message(chat_id, "📧 Email wordt geschreven... (kan 30 seconden duren)")
                if _use_new_system:
                    try:
                        response = _new_handler.handle(text, chat_id=chat_id)
                        print(f"[Phase6] /email handled by new system")
                        send_message(chat_id, f"✉️ Email:\n{response}")
                    except Exception as _err:
                        print(f"[Phase6] New system error for /email — fallback: {_err}")
                        response = run_email(task)
                        send_message(chat_id, f"✉️ Email:\n{response}")
                else:
                    response = run_email(task)
                    send_message(chat_id, f"✉️ Email:\n{response}")
 
        elif text.startswith("/content"):
            task = text.replace("/content", "").strip()
            if not task:
                send_message(chat_id,
                    "❗ Voorbeeldgebruik:\n\n"
                    "/content Reels script voor drukke moeders over Happy Juice\n"
                    "/content Instagram carousel over MentaBiotics\n"
                    "/content Story reeks over energie tips\n"
                    "/content Caption voor foto met Happy Juice"
                )
            else:
                send_message(chat_id, "✍️ Content wordt gegenereerd... (kan 30 seconden duren)")
                if _use_new_system:
                    try:
                        response = _new_handler.handle(text, chat_id=chat_id)
                        print(f"[Phase5] /content handled by new system")
                        send_message(chat_id, f"📱 Content:\n{response}")
                    except Exception as _err:
                        print(f"[Phase5] New system error for /content — fallback: {_err}")
                        response = run_content(task)
                        send_message(chat_id, f"📱 Content:\n{response}")
                else:
                    response = run_content(task)
                    send_message(chat_id, f"📱 Content:\n{response}")

        elif text.startswith("/sales"):
            task = text.replace("/sales", "").strip()
            if not task:
                send_message(chat_id,
                    "❗ Voorbeeldgebruik:\n\n"
                    "/sales DM script voor drukke moeders\n"
                    "/sales closing bericht voor Happy Juice\n"
                    "/sales bezwaar: te duur"
                )
            else:
                send_message(chat_id, "💬 Sales script wordt geschreven... (kan 30 seconden duren)")
                if _use_new_system:
                    try:
                        response = _new_handler.handle(text, chat_id=chat_id)
                        print(f"[Phase5] /sales handled by new system")
                        send_message(chat_id, f"💬 Sales:\n{response}")
                    except Exception as _err:
                        print(f"[Phase5] New system error for /sales: {_err}")
                        send_message(chat_id, f"❌ Sales agent tijdelijk niet beschikbaar: {_err}")
                else:
                    send_message(chat_id, "❌ Sales agent niet beschikbaar (nieuw systeem niet geladen)")

        elif text.startswith("/research"):
            task = text.replace("/research", "").strip()
            if not task:
                send_message(chat_id,
                    "❗ Voorbeeldgebruik:\n\n"
                    "/research wellness markt Nederland trends\n"
                    "/research concurrent analyse Amare\n"
                    "/research doelgroep pijnpunten moeders"
                )
            else:
                send_message(chat_id, "🔍 Marktonderzoek bezig... (kan 30 seconden duren)")
                if _use_new_system:
                    try:
                        response = _new_handler.handle(text, chat_id=chat_id)
                        print(f"[Phase5] /research handled by new system")
                        send_message(chat_id, f"📊 Research:\n{response}")
                    except Exception as _err:
                        print(f"[Phase5] New system error for /research: {_err}")
                        send_message(chat_id, f"❌ Research agent tijdelijk niet beschikbaar: {_err}")
                else:
                    send_message(chat_id, "❌ Research agent niet beschikbaar (nieuw systeem niet geladen)")
 
        elif text.startswith("/idea"):
            send_message(chat_id, "🔥 Aan het denken...")
            response = run_cmo("Genereer een viraal video idee")
            send_message(chat_id, f"💡 Video Idee:\n{response}")
 
        elif text.startswith("/seo"):
            send_message(chat_id, "🔍 SEO analyse bezig...")
            response = run_cmo("Genereer SEO titel en tags voor YouTube")
            send_message(chat_id, f"📋 SEO:\n{response}")
 
        elif text.startswith("/script"):
            send_message(chat_id, "📝 Script schrijven...")
            response = run_cmo("Schrijf een kort video script")
            send_message(chat_id, f"🎬 Script:\n{response}")
 
        elif text.startswith("/cmo"):
            task = text.replace("/cmo", "").strip()
            if not task:
                send_message(chat_id, "❗ Voorbeeld: /cmo Stel lead systeem op voor Nederland")
            else:
                send_message(chat_id, "🟣 CMO aan het denken... (kan 30 seconden duren)")
                if _use_new_system:
                    try:
                        response = _new_handler.handle(text, chat_id=chat_id)
                        print(f"[Phase3] /cmo handled by new system")
                        send_message(chat_id, f"🏢 CMO:\n{response}")
                    except Exception as _err:
                        print(f"[Phase3] New system error for /cmo — fallback: {_err}")
                        response = run_cmo(task)
                        send_message(chat_id, f"🏢 CMO:\n{response}")
                else:
                    response = run_cmo(task)
                    send_message(chat_id, f"🏢 CMO:\n{response}")
 
        elif text.startswith("/linkedin"):
            task = text.replace("/linkedin", "").strip()
            if not task:
                send_message(chat_id,
                    "❗ Voorbeeldgebruik:\n\n"
                    "/linkedin connectie bericht voor drukke moeders\n"
                    "/linkedin follow-up bericht na connectie\n"
                    "/linkedin waardebericht over Happy Juice\n"
                    "/linkedin zacht aanbod bericht"
                )
            else:
                send_message(chat_id, "🔗 LinkedIn bericht wordt voorbereid... (kan 30 seconden duren)")
                if _use_new_system:
                    try:
                        response = _new_handler.handle(text, chat_id=chat_id)
                        print(f"[Phase6] /linkedin handled by new system")
                        send_message(chat_id, f"💼 LinkedIn:\n{response}")
                    except Exception as _err:
                        print(f"[Phase6] New system error for /linkedin — fallback: {_err}")
                        response = run_linkedin(task)
                        send_message(chat_id, f"💼 LinkedIn:\n{response}")
                else:
                    response = run_linkedin(task)
                    send_message(chat_id, f"💼 LinkedIn:\n{response}")
 
        else:
            send_message(chat_id, f"Je schreef: {text}")
 
    except Exception as e:
        print(f"Verwerkingsfout: {e}")
        send_message(chat_id, f"❌ Fout: {e}")
 
def handle_command(chat_id, text):
    """Start commando verwerking in aparte thread"""
    thread = threading.Thread(target=process_command, args=(chat_id, text))
    thread.daemon = True
    thread.start()
 
def _start_canva_callback_server():
    """Start Flask OAuth callback server in background thread."""
    if not _flask_available:
        print("[Canva] Flask niet beschikbaar — OAuth callback server niet gestart.")
        return
    if not _use_new_system:
        print("[Canva] Nieuw systeem niet geladen — OAuth callback server niet gestart.")
        return

    from src.memory.memory_manager import MemoryManager
    from src.skills import canva_client

    app = Flask(__name__)

    @app.route("/canva/callback")
    def canva_callback():
        code = flask_request.args.get("code")
        state = flask_request.args.get("state")
        error = flask_request.args.get("error")

        if error or not code or not state:
            return f"<h2>❌ Canva koppeling mislukt: {error or 'ontbrekende parameters'}</h2>", 400

        try:
            chat_id = int(state)
            mem = MemoryManager(namespace="canva_tokens")

            # Retrieve PKCE verifier from SQLite (stored by canva_agent._auth)
            code_verifier = mem.load(f"pkce_{chat_id}")
            print(f"[Canva callback] state={state!r} code_verifier_found={bool(code_verifier)}")
            if not code_verifier:
                return "<h2>❌ PKCE verifier niet gevonden. Gebruik /canva auth opnieuw.</h2>", 400

            tokens = canva_client.exchange_code(code, code_verifier)

            mem.save("access_token", tokens["access_token"], chat_id=chat_id)
            if tokens.get("refresh_token"):
                mem.save("refresh_token", tokens["refresh_token"], chat_id=chat_id)
            # Clean up verifier after use
            mem.delete(f"pkce_{chat_id}")

            send_message(chat_id,
                "✅ Canva-account succesvol gekoppeld!\n\n"
                "Je kunt nu ontwerpen maken:\n"
                "/canva instagram <titel>\n"
                "/canva story <titel>\n"
                "/canva linkedin <titel>"
            )
            return "<h2>✅ Canva gekoppeld! Je kunt dit venster sluiten en terugkeren naar Telegram.</h2>"
        except Exception as e:
            print(f"[Canva callback] Fout: {e}")
            return f"<h2>❌ Fout bij koppelen: {e}</h2>", 500

    @app.route("/health")
    def health():
        return "OK"

    port = int(os.getenv("PORT", 8080))
    print(f"[Canva] OAuth callback server gestart op poort {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def main():
    """Hoofdloop voor Telegram bot"""
    print("🤖 Bot actief... Wacht op Telegram berichten.")
    last_update_id = None
 
    while True:
        try:
            updates = get_updates(last_update_id)
 
            for update in updates.get("result", []):
                last_update_id = update["update_id"] + 1
 
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"]["text"]
                    print("Ontvangen bericht:", text)
                    handle_command(chat_id, text)
 
            time.sleep(1)
 
        except ConnectionError as e:
            print(f"🔴 Verbinding verloren: {e}")
            time.sleep(15)
        except Exception as e:
            print(f"🔴 Onverwachte fout: {e}")
            time.sleep(10)
 
if __name__ == "__main__":
    try:
        from src.config.settings import Settings
        Settings.validate()
    except ValueError as _ve:
        print(f"[STARTUP ERROR] {_ve}")
        sys.exit(1)

    # Start Canva OAuth callback server in background thread
    _canva_thread = threading.Thread(target=_start_canva_callback_server, daemon=True)
    _canva_thread.start()

    main()