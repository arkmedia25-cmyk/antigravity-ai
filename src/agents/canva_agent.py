from agents.base_agent import BaseAgent
from memory.memory_manager import MemoryManager
from skills import canva_client
from core.logging import get_logger

logger = get_logger("agents.canva")

# Marker prefix so telegram_handler can detect file URLs in the response
_FILE_MARKER = "CANVA_FILE:"


class CanvaAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="canva")
        self.memory = MemoryManager(namespace="canva")
        self._tokens = MemoryManager(namespace="canva_tokens")
        self._designs = MemoryManager(namespace="canva_designs")

    def process(self, input_data: str, chat_id=None) -> str:
        parts = input_data.strip().split(None, 1)
        subcommand = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        if subcommand == "auth":
            return self._auth(chat_id)

        if subcommand == "export":
            return self._export(args, chat_id)

        return self._create_design(subcommand, args, chat_id)

    # ------------------------------------------------------------------ auth

    def _auth(self, chat_id) -> str:
        if chat_id is None:
            return "❌ Canva koppelen werkt alleen via Telegram."
        try:
            auth_url, code_verifier = canva_client.get_auth_url(state=str(chat_id))
        except ValueError as e:
            return f"❌ Canva configuratiefout: {e}"

        # Store verifier in SQLite — survives thread boundaries and restarts
        self._tokens.save(f"pkce_{chat_id}", code_verifier)
        print(f"[CanvaAgent] PKCE verifier opgeslagen voor chat_id={chat_id}")
        print(f"[CanvaAgent] OAuth link: {auth_url}")
        return (
            "🎨 Koppel je Canva-account:\n\n"
            f"{auth_url}\n\n"
            "Klik op de link en geef toegang. Je ontvangt een bevestiging zodra de koppeling klaar is."
        )

    # --------------------------------------------------------------- create

    def _create_design(self, design_type_key: str, title: str, chat_id) -> str:
        if chat_id is None:
            return "❌ Ontwerpen maken werkt alleen via Telegram."

        access_token = self._get_token(chat_id)
        if isinstance(access_token, str) and access_token.startswith("❌"):
            return access_token

        if design_type_key not in canva_client.DESIGN_TYPES:
            types = ", ".join(canva_client.DESIGN_TYPES.keys())
            return (
                f"❌ Onbekend ontwerp-type: '{design_type_key}'\n\n"
                f"Beschikbare types:\n{types}\n\n"
                "Voorbeeld: /canva instagram Happy Juice post"
            )

        try:
            from config.settings import settings
            template_id_override = settings.CANVA_TEMPLATE_INSTAGRAM if design_type_key.lower() == "instagram" else ""
            result = canva_client.create_design(access_token, design_type_key, title, template_id_override=template_id_override)
            design = result.get("design", {})
            design_id = design.get("id", "")
            edit_url = design.get("urls", {}).get("edit_url", "")

            if not edit_url:
                return "❌ Ontwerp aangemaakt maar geen bewerkingslink ontvangen."

            # Store last design_id so user can export without specifying it
            if design_id and chat_id is not None:
                self._designs.save("last_design_id", design_id, chat_id=chat_id)
                self._designs.save("last_design_type", design_type_key, chat_id=chat_id)

            is_video = design_type_key in canva_client.EXPORT_FORMAT
            export_hint = (
                f"\n\n🎬 Video exporteren?\n/canva export {design_id}"
                if is_video else
                f"\n\n🖼 Exporteren als afbeelding?\n/canva export {design_id}"
            )

            return (
                f"🎨 Canva ontwerp klaar!\n\n"
                f"📐 Type: {design_type_key.capitalize()}\n"
                f"📝 Titel: {title or '—'}\n\n"
                f"✏️ Bewerken in Canva:\n{edit_url}"
                f"{export_hint}"
            )

        except Exception as e:
            logger.error(f"CanvaAgent create_design failed: {e}")
            return f"❌ Canva fout: {e}"

    # --------------------------------------------------------------- export

    def _export(self, args: str, chat_id) -> str:
        if chat_id is None:
            return "❌ Exporteren werkt alleen via Telegram."

        access_token = self._get_token(chat_id)
        if isinstance(access_token, str) and access_token.startswith("❌"):
            return access_token

        # args can be: "<design_id>" or empty (use last design)
        design_id = args.strip() or self._designs.load("last_design_id", chat_id=chat_id)
        if not design_id:
            return (
                "❌ Geen ontwerp-ID opgegeven.\n\n"
                "Gebruik: /canva export <design_id>\n"
                "Of maak eerst een ontwerp aan."
            )

        # Determine export format: MP4 for video types, PNG otherwise
        last_type = self._designs.load("last_design_type", chat_id=chat_id) or ""
        fmt = canva_client.EXPORT_FORMAT.get(last_type, "PNG")

        try:
            job = canva_client.start_export(access_token, design_id, fmt)
            export_id = job.get("job", {}).get("id") or job.get("id", "")
            if not export_id:
                return "❌ Export gestart maar geen job-ID ontvangen."

            logger.debug(f"Export job started: {export_id} (format={fmt})")

            # Poll until done (max 90s)
            urls = canva_client.wait_for_export(access_token, export_id)
            if not urls:
                return "❌ Export afgerond maar geen download-URL ontvangen."

            download_url = urls[0]
            fmt_label = "🎬 Video (MP4)" if fmt == "MP4" else "🖼 Afbeelding (PNG)"

            # CANVA_FILE: marker is parsed by telegram_handler to send as file
            return (
                f"✅ Export klaar!\n\n"
                f"Formaat: {fmt_label}\n"
                f"Ontwerp-ID: {design_id}\n\n"
                f"Het bestand wordt naar je gestuurd...\n"
                f"{_FILE_MARKER}{download_url}|{fmt.lower()}"
            )

        except TimeoutError:
            return "⏱ Export duurt te lang. Probeer het later opnieuw."
        except Exception as e:
            logger.error(f"CanvaAgent export failed: {e}")
            return f"❌ Export fout: {e}"

    # ------------------------------------------------------------ helpers

    def _get_token(self, chat_id) -> str:
        """Return access token, refreshing if needed. Returns error string on failure."""
        token = self._tokens.load("access_token", chat_id=chat_id)
        if not token:
            return "❌ Canva is nog niet gekoppeld. Gebruik: /canva auth"
        return token

    def _refresh_and_retry(self, chat_id) -> str:
        refresh_token = self._tokens.load("refresh_token", chat_id=chat_id)
        if not refresh_token:
            return "❌ Sessie verlopen. Gebruik /canva auth om opnieuw te koppelen."
        try:
            new_tokens = canva_client.refresh_access_token(refresh_token)
            access_token = new_tokens["access_token"]
            self._tokens.save("access_token", access_token, chat_id=chat_id)
            if "refresh_token" in new_tokens:
                self._tokens.save("refresh_token", new_tokens["refresh_token"], chat_id=chat_id)
            return access_token
        except Exception as e:
            return f"❌ Token vernieuwen mislukt: {e}"
