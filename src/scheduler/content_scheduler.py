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


def _send_telegram_message(chat_id: str, text: str, reply_markup=None, video_path=None, caption=None):
    """Send a message (text or video) via Telegram HTTP API with markup support."""
    token = os.getenv("TELEGRAM_TOKEN", "")
    if not token:
        logger.error("[Scheduler] TELEGRAM_TOKEN not set.")
        return
        
    try:
        # 1. If video_path is provided, send as video
        if video_path and os.path.exists(video_path):
            url = f"https://api.telegram.org/bot{token}/sendVideo"
            with open(video_path, "rb") as vf:
                payload = {
                    "chat_id": chat_id,
                    "caption": caption or text,
                    "parse_mode": "Markdown"
                }
                if reply_markup:
                    payload["reply_markup"] = json.dumps(reply_markup)
                
                requests.post(url, data=payload, files={"video": vf}, timeout=60)
                return

        # 2. Otherwise send as text
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
            
        requests.post(url, data=payload, timeout=10)
        
    except Exception as e:
        logger.error(f"[Scheduler] Telegram send error: {e}")


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
        "15:53": (
            "@glowup Maak een premium wellnessvideo met daktilo effect en een rustgevende achtergrond.",
            "glow",
            "🚀 Final Sync Test (Daktilo Fixed)"
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
                            # Get rich SwarmMessage from orchestrator
                            msg = orchestrator.handle_request(p, agent="content", chat_id=chat_id)
                            response_text = msg.content
                            
                            # Prepare interactive buttons if video was produced
                            reply_markup = None
                            video_path = None
                            
                            if msg.data and msg.data.get("video_path"):
                                video_path = msg.data.get("video_path")
                                public_url = msg.data.get("public_url", "#")
                                
                                # Standard Interactive Buttons
                                reply_markup = {
                                    "inline_keyboard": [
                                        [
                                            {"text": "📥 İndir", "url": public_url},
                                            {"text": "📸 Instagram", "callback_data": f"pub_{video_path}_{b}_ig"}
                                        ],
                                        [
                                            {"text": "📱 TikTok", "callback_data": f"pub_{video_path}_{b}_tt"},
                                            {"text": "🎥 YouTube", "callback_data": f"pub_{video_path}_{b}_yt"}
                                        ]
                                    ]
                                }
                                
                                # For video messages, we use a separate success notification or just send the video
                                _send_telegram_message(
                                    chat_id,
                                    f"✅ *{lbl} tamamlandı!*",
                                    video_path=video_path,
                                    reply_markup=reply_markup,
                                    caption=f"✅ *{lbl} hazır!*\n\n{response_text}"
                                )
                            else:
                                # Standard text response
                                _send_telegram_message(
                                    chat_id,
                                    f"✅ *{lbl} tamamlandı!*\n\n{response_text}",
                                    reply_markup=reply_markup
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
