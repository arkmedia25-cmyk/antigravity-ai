import os
import time
from collections import defaultdict
from orchestrator import Orchestrator
from memory.memory_manager import MemoryManager
from core.logging import get_logger

_RATE_LIMIT_MAX = 5       # max requests
_RATE_LIMIT_WINDOW = 30   # seconds
_rate_store: dict = defaultdict(list)  # chat_id → [timestamps]


def _is_rate_limited(chat_id) -> bool:
    if chat_id is None:
        return False
    now = time.monotonic()
    timestamps = _rate_store[chat_id]
    # Drop timestamps outside the window
    _rate_store[chat_id] = [t for t in timestamps if now - t < _RATE_LIMIT_WINDOW]
    if len(_rate_store[chat_id]) >= _RATE_LIMIT_MAX:
        return True
    _rate_store[chat_id].append(now)
    return False

logger = get_logger("interfaces.telegram.handler")

_START_MESSAGE = (
    "Antigravity AI Bot klaar!\n\n"
    "STRATEGIE\n"
    "/cmo - marketingstrategie & advies\n\n"
    "CONTENT\n"
    "/content - Instagram/Reels content genereren\n\n"
    "SALES\n"
    "/sales - DM scripts & closing berichten\n\n"
    "ONDERZOEK\n"
    "/research - markttrends & doelgroep analyse\n\n"
    "COMMUNICATIE\n"
    "/email - email reeks schrijven\n"
    "/linkedin - LinkedIn berichten\n\n"
    "Voorbeeld: /cmo Stel lead systeem op voor Nederland"
)

_COMMAND_AGENT_MAP = {
    "/cmo": "cmo",
    "/content": "content",
    "/sales": "sales",
    "/research": "research",
    "/email": "email",
    "/linkedin": "linkedin",
    "/canva": "canva",
}

_USAGE_HINTS = {
    "/cmo": "Gebruik: /cmo <taak beschrijving>",
    "/content": "Gebruik: /content <onderwerp of product>",
    "/sales": "Gebruik: /sales <scenario of product>",
    "/research": "Gebruik: /research <markt of onderwerp>",
    "/email": "Gebruik: /email <type of reeks beschrijving>",
    "/linkedin": "Gebruik: /linkedin <bericht type of scenario>",
    "/canva": (
        "Gebruik:\n"
        "/canva auth — Canva-account koppelen\n\n"
        "Afbeeldingen:\n"
        "/canva instagram <titel>\n"
        "/canva story <titel>\n"
        "/canva linkedin <titel>\n"
        "/canva facebook <titel>\n"
        "/canva flyer <titel>\n"
        "/canva poster <titel>\n\n"
        "Video:\n"
        "/canva reels <titel>\n"
        "/canva tiktok <titel>\n"
        "/canva youtube <titel>\n\n"
        "Exporteren:\n"
        "/canva export <design_id>"
    ),
}


class TelegramHandler:
    """
    Isolated Telegram message router.
    Accepts raw message text, routes to Orchestrator, returns response string.
    No real Telegram API calls — transport layer stays in skills/automation/telegram_handler.py.
    """

    def __init__(self):
        self.orchestrator = Orchestrator()
        self._funnel = MemoryManager(namespace="funnel")
        logger.debug("TelegramHandler initialized")

    async def handle(self, update, context) -> None:
        text = update.message.text
        chat_id = update.message.chat_id
        response = self._process_message(text, chat_id)
        await update.message.reply_text(response)

    def _process_message(self, text: str, chat_id: int = 0) -> str:
        logger.debug(f"Incoming message [chat_id={chat_id}]: {text[:100]}")

        if not text or not text.strip():
            return "Lege invoer ontvangen."

        if len(text) > 1000:
            return "Message too long. Please shorten your input."

        # Treat 0 as "unknown" — no user tracking
        _cid = chat_id if chat_id else None

        if _is_rate_limited(_cid):
            return "Too many requests. Please wait a few seconds."

        if text.strip() == "/start":
            return _START_MESSAGE

        for command, agent in _COMMAND_AGENT_MAP.items():
            if text.startswith(command):
                return self._handle_agent_command(text, command, agent, chat_id=_cid)

        if text.startswith("/"):
            return self._handle_unknown_command(text)

        return self.orchestrator.handle_request(text, chat_id=_cid)

    def _handle_agent_command(self, text: str, command: str, agent: str, chat_id=None) -> str:
        task = text[len(command):].strip()
        if not task:
            return _USAGE_HINTS[command]

        logger.debug(f"Routing {command} task to [{agent}] (chat_id={chat_id}): {task[:100]}")

        response = self.orchestrator.handle_request(task, agent=agent, chat_id=chat_id)

        # Track funnel interaction after successful response
        if chat_id is not None:
            try:
                self._funnel.track_interaction(chat_id=chat_id, agent=agent, task=task)
            except Exception as _e:
                logger.warning(f"Funnel tracking failed (non-critical): {_e}")

        return response

    def _handle_unknown_command(self, text: str) -> str:
        command = text.split()[0]
        logger.debug(f"Unknown command received: {command}")
        return f"Onbekend commando: {command}"


def start_telegram_bot():
    import asyncio
    from telegram.ext import Application, MessageHandler, filters

    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("ERROR: TELEGRAM_TOKEN bulunamadi!")
        return

    async def run():
        try:
            handler = TelegramHandler()
            application = Application.builder().token(token).build()
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle))
            print("Telegram bot baslatildi!")
            async with application:
                await application.start()
                await application.updater.start_polling()
                await asyncio.Event().wait()
        except Exception as e:
            print(f"Bot hatasi: {e}")
            import traceback
            traceback.print_exc()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run())
