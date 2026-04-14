import time
import datetime
import threading
import os
import requests
import pytz
from src.orchestrator import Orchestrator
from src.core.logging import get_logger

# Initialize logger
logger = get_logger("scheduler.content_scheduler")

# Global flag to stop scheduler if needed
_STOP_SCHEDULER = False


def _send_telegram_message(chat_id: str, text: str):
    """Send a message via Telegram HTTP API directly (thread-safe, no asyncio)."""
    token = os.getenv("TELEGRAM_TOKEN", "")
    if not token:
        logger.error("[Scheduler] TELEGRAM_TOKEN not set, cannot send message.")
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=10
        )
    except Exception as e:
        logger.error(f"[Scheduler] Failed to send Telegram message: {e}")


def start_content_factory(chat_id, bot=None):
    """
    Automated Content Factory:
    Triggers content generation for both brands at Amsterdam Peak Hours (CET/CEST).

    Peak Hours (Amsterdam Time):
    - 08:00  → @holistiglow (Sabah Wellness)
    - 12:30  → @glowup     (Öğle Enerjisi)
    - 20:15  → @glowup     (Akşam Rutini)
    - 22:00  → @holistiglow (Gece Ritüelleri)
    """

    # Amsterdam Peak Hours Production Schedule
    SCHEDULE = {
        "08:00": (
            "@holistiglow Sabah huzuru ve bütünsel wellness felsefesi üzerine ilham verici bir video üret.",
            "holisti",
            "🌅 Sabah Paylaşımı (HolistiGlow)"
        ),
        "12:30": (
            "@glowup Öğle enerjisi ve sağlıklı yaşam ipuçları üzerine dinamik bir video hazırla.",
            "glow",
            "☀️ Öğle Paylaşımı (GlowUp)"
        ),
        "20:15": (
            "@glowup Gün sonu cilt bakımı ve gece öncesi rutin üzerine premium bir wellness videosu hazırla.",
            "glow",
            "🌆 Akşam Paylaşımı (GlowUp)"
        ),
        "22:00": (
            "@holistiglow Gece huzuru, meditasyon ve uyku öncesi wellness ritüelleri üzerine sakinleştirici bir video üret.",
            "holisti",
            "🌙 Gece Paylaşımı (HolistiGlow)"
        ),
    }

    def run_scheduler():
        logger.info(f"[Scheduler] ✅ Content Factory started. Amsterdam Peak Hours active. Chat: {chat_id}")

        orchestrator = Orchestrator()
        amsterdam_tz = pytz.timezone("Europe/Amsterdam")
        heartbeat_timestamp = time.time()

        while not _STOP_SCHEDULER:
            try:
                # 1. Get current Amsterdam time
                now = datetime.datetime.now(amsterdam_tz)
                current_time = now.strftime("%H:%M")

                # 2. Heartbeat every 10 minutes
                if time.time() - heartbeat_timestamp >= 600:
                    logger.info(f"[Scheduler ♥] Active. Amsterdam Time: {current_time}")
                    heartbeat_timestamp = time.time()

                # 3. Check schedule
                if current_time in SCHEDULE:
                    prompt, brand, label = SCHEDULE[current_time]
                    logger.info(f"[Scheduler] 🚀 TRIGGERED: {label} at {current_time} Amsterdam Time")

                    def execute_production(p=prompt, b=brand, lbl=label):
                        try:
                            _send_telegram_message(
                                chat_id,
                                f"🤖 *{lbl} başladı...*\n⏳ İçerik üretimi devam ediyor, lütfen bekleyin."
                            )
                            response = orchestrator.handle_request(p, agent="content", chat_id=chat_id)
                            _send_telegram_message(
                                chat_id,
                                f"✅ *{lbl} tamamlandı!*\n\n{response}"
                            )
                        except Exception as e:
                            logger.error(f"[Scheduler] Production error: {e}", exc_info=True)
                            _send_telegram_message(chat_id, f"❌ *{lbl} hatası:* {e}")

                    threading.Thread(target=execute_production, daemon=True).start()

                    # Sleep 65s to prevent double-trigger within the same minute
                    logger.debug("[Scheduler] Sleeping 65s to prevent double trigger.")
                    time.sleep(65)

                # Poll every 30 seconds
                time.sleep(30)

            except Exception as e:
                logger.error(f"[Scheduler Loop Error] {e}", exc_info=True)
                time.sleep(60)

    thread = threading.Thread(target=run_scheduler, name="ContentSchedulerThread", daemon=True)
    thread.start()
    return thread
