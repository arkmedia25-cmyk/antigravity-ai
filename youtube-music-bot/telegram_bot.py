"""
Telegram Bot — Listener + Komutlar.

Türkçe yorum, İngilizce kod. Type hints zorunlu.
Komutlar:
  /on        — Sistemi aç
  /off       — Sistemi kapat
  /status    — Durum + son run
  /run_now   — Manuel başlat
  /cancel    — İptal + state temizle
  /resume    — Hata sonrası devam et
  /history   — Son 10 video
  /tokens    — Suno API usage
  /skip      — Sıradaki niş atla
  /test      — Mock mode dry-run
  /trends    — Son trend raporu
  /research  — Manuel trend araştırması

Bot callbacks (inline buttons):
  approve_long    — ✅ Long video onayla
  reject_long     — ❌ Long video reddet
  regenerate_long — 🔄 Long video yeniden üret
  approve_short   — ✅ Short yayınla
  reject_short    — ❌ Short sil
"""

import logging
import os
import json
import subprocess
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from modules.state_manager import get_state_manager
from modules.trend_research import get_trend_researcher, RESEARCH_DIR

logger = logging.getLogger(__name__)

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

STATE_DIR = Path(__file__).parent / "state"
GENRES_HISTORY_FILE = STATE_DIR / "genres-history.json"


class TelegramBotHandler:
    """Telegram bot komutları."""

    def __init__(self) -> None:
        self.state_manager = get_state_manager()
        try:
            self.chat_id = int(TELEGRAM_CHAT_ID)
        except (ValueError, TypeError):
            logger.error("TELEGRAM_CHAT_ID must be a valid integer")
            self.chat_id = 0

    async def cmd_on(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sistemi aç."""
        try:
            self.state_manager.set_system_status("ON")
            await update.message.reply_text("✅ Sistem açıldı. Cron tetiklenebilir.")
            logger.info("Sistem ON yapıldı — /on komutu")
        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}")

    async def cmd_off(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sistemi kapat."""
        try:
            self.state_manager.set_system_status("OFF")
            await update.message.reply_text("❌ Sistem kapatıldı. Yeni run başlamayacak.")
            logger.info("Sistem OFF yapıldı — /off komutu")
        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}")

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sistem durumu."""
        try:
            state = self.state_manager.read()

            # Sistem durumu
            system_status = state.system_status
            status_emoji = "🟢" if system_status == "ON" else "🔴"

            # Son run
            last_run = state.last_successful_run
            last_run_text = "Henüz run yok"
            if last_run.id:
                last_run_text = f"{last_run.id}\n├─ Long: {last_run.long_url}\n└─ Short: {last_run.short_url}"

            # Devam eden run
            current_run = state.current_run
            current_run_text = "Çalışan run yok"
            if current_run.id:
                progress = f"{current_run.step_progress}/{current_run.step_total}" if current_run.step_total > 0 else "?"
                current_run_text = f"{current_run.id}\n├─ Step: {current_run.step} [{progress}]\n└─ Niş: {current_run.niche}"

            message = f"""
{status_emoji} SİSTEM DURUMU

Sistem: {system_status}

📊 Son Başarılı Run:
{last_run_text}

⚙️ Devam Eden Run:
{current_run_text}

🕒 Zaman: {datetime.now(timezone.utc).isoformat()}
            """.strip()

            await update.message.reply_text(message)

        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}")

    async def cmd_run_now(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Manuel başlat."""
        try:
            if self.state_manager.is_run_in_progress():
                await update.message.reply_text("⚠️ Zaten bir run çalışıyor. /cancel ile iptal et veya bekle.")
                return

            await update.message.reply_text("🚀 Manual run başlatılıyor. Log'ları takip et...")
            logger.info("Manual run başlatılmış — /run_now komutu")

            subprocess.Popen(
                ["python3", "main_runner.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}")
            logger.error(f"run_now error: {e}")

    async def cmd_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Run'ı iptal et."""
        try:
            if not self.state_manager.is_run_in_progress():
                await update.message.reply_text("⚠️ Çalışan run yok.")
                return

            self.state_manager.reset_state()
            await update.message.reply_text("❌ Run iptal edildi ve state sıfırlandı.")
            logger.info("Run iptal edilmiş — /cancel komutu")

        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}")

    async def cmd_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Hata sonrası devam et."""
        try:
            state = self.state_manager.read()

            if state.system_status != "ERROR":
                await update.message.reply_text("⚠️ Sistem ERROR durumunda değil.")
                return

            # State'i ON yap, run devam edecek
            self.state_manager.set_system_status("ON")
            await update.message.reply_text("▶️ Run resume ediliyor...")
            logger.info("Run resume edilmiş — /resume komutu")

        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}")

    async def cmd_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Son 10 video."""
        try:
            history = json.loads(GENRES_HISTORY_FILE.read_text()) if GENRES_HISTORY_FILE.exists() else {}

            videos = []
            for niche, data in history.items():
                use_count = data.get("use_count", 0)
                last_used = data.get("last_used", "N/A")
                if use_count > 0:
                    videos.append(f"{niche} — {use_count}x, son: {last_used}")

            if videos:
                message = "📺 Niş History:\n\n" + "\n".join(videos[:10])
            else:
                message = "Henüz video yok"
            await update.message.reply_text(message)

        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}")

    async def cmd_tokens(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Suno API kullanım."""
        try:
            token_log_file = STATE_DIR / "token_log.json"
            if not token_log_file.exists():
                await update.message.reply_text("⚠️ Token log dosyası bulunamadı.")
                return

            token_log = json.loads(token_log_file.read_text())
            summary = token_log.get("monthly_summary", {})

            message = f"""
💰 SUNO API KULLANIM

Ay: {summary.get('month', 'N/A')}
├─ Tahmini maliyet: €{summary.get('estimated_cost_eur', 0):.2f}
├─ Çağrı (başarılı): {summary.get('calls_succeeded', 0)}
├─ Çağrı (başarısız): {summary.get('calls_failed', 0)}
└─ Toplam: {summary.get('calls_made', 0)}
            """.strip()

            await update.message.reply_text(message)

        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}")

    async def cmd_trends(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Son trend raporu."""
        try:
            today = datetime.now(timezone.utc).strftime("%Y%m%d")
            report_file = RESEARCH_DIR / f"trend_report_{today}.json"

            if not report_file.exists():
                await update.message.reply_text("⚠️ Bugünün trend raporu yok. /research komutunu çalıştır.")
                return

            report = json.loads(report_file.read_text())

            keywords = ", ".join(report.get("viral_keywords", [])[:5])
            niches = "\n".join(
                [f"  • {n.get('slug')} — score: {n.get('viral_score')}"
                 for n in report.get("trending_subgenres", [])[:3]]
            )

            message = f"""
📊 TREND RAPORU

Generated: {report.get('generated_at', 'N/A')[:10]}
Viral Keywords: {keywords}
Best Duration: {report.get('best_duration_min')} min
API Quota: {report.get('youtube_quota_used')} unit

Top Niches:
{niches}
            """.strip()

            await update.message.reply_text(message)

        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}")

    async def cmd_research(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Manuel trend araştırması."""
        try:
            if not YOUTUBE_API_KEY:
                await update.message.reply_text("❌ YOUTUBE_API_KEY .env'de tanımlanmalı.")
                return

            await update.message.reply_text("🔍 Trend araştırması başlamış. Lütfen bekle (2-3 dk)...")

            researcher = get_trend_researcher(YOUTUBE_API_KEY)
            report = researcher.research(force_refresh=True)

            message = f"✅ Araştırma tamamlandı. /trends ile sonuçları gör."
            await update.message.reply_text(message)
            logger.info("Manual trend research yapılmış — /research komutu")

        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}")
            logger.error(f"Research error: {e}")

    async def cmd_skip(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sıradaki nişi atla."""
        try:
            state = self.state_manager.read()
            if not state.current_run.id:
                await update.message.reply_text("⚠️ Çalışan run yok.")
                return

            current_niche = state.current_run.niche
            state.current_run.step = "niche_select"
            self.state_manager.write(state)

            await update.message.reply_text(f"⏭️ Niş '{current_niche}' atlandı. Sonraki niş seçiliyor...")
            logger.info(f"Niş atlandı: {current_niche} — /skip komutu")

        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}")

    async def cmd_test(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Mock mod dry-run."""
        try:
            if self.state_manager.is_run_in_progress():
                await update.message.reply_text("⚠️ Zaten bir run çalışıyor. /cancel ile iptal et.")
                return

            await update.message.reply_text("🧪 Mock test başlamış (Suno çağrısı YAPMAZ, token harcamaz)...")
            logger.info("Mock test başlatılmış — /test komutu")

            subprocess.Popen(
                ["python3", "main_runner.py", "--mock", "--reset-state"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}")
            logger.error(f"test error: {e}")

    async def callback_approve_long(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """✅ Long video onayla."""
        try:
            await update.callback_query.answer("✅ Video onaylandı!")
            state = self.state_manager.read()
            state.current_run.step = "youtube_upload"
            self.state_manager.write(state)
            logger.info("Long video onaylandı — button callback")
        except Exception as e:
            logger.error(f"Callback error: {e}")

    async def callback_reject_long(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """❌ Long video reddet."""
        try:
            await update.callback_query.answer("❌ Video reddedildi.")
            self.state_manager.end_run_error(
                step="telegram_review",
                message="Kullanıcı tarafından reddedildi",
                is_fatal=True,
            )
            logger.info("Long video reddedilmiş — button callback")
        except Exception as e:
            logger.error(f"Callback error: {e}")

    async def callback_regenerate_long(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """🔄 Long video yeniden üret."""
        try:
            await update.callback_query.answer("🔄 Yeniden üretiliyor... (token harcayacak!)")
            state = self.state_manager.read()
            state.current_run.step = "suno_generate"
            state.current_run.audio_files = []
            self.state_manager.write(state)
            logger.info("Long video yeniden üretim başlamış — button callback")
        except Exception as e:
            logger.error(f"Callback error: {e}")

    async def callback_approve_short(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """✅ Short video yayınla."""
        try:
            await update.callback_query.answer("✅ Short YouTube'a yayınlanıyor!")
            state = self.state_manager.read()
            state.current_run.step = "youtube_upload"
            self.state_manager.write(state)
            logger.info("Short video onaylandı — button callback")
        except Exception as e:
            logger.error(f"Callback error: {e}")

    async def callback_reject_short(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """❌ Short video sil."""
        try:
            await update.callback_query.answer("❌ Short reddedildi.")
            self.state_manager.end_run_error(
                step="telegram_review",
                message="Short video kullanıcı tarafından reddedildi",
                is_fatal=True,
            )
            logger.info("Short video reddedilmiş — button callback")
        except Exception as e:
            logger.error(f"Callback error: {e}")


async def main() -> None:
    """Bot'u başlat."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN .env'de tanımlanmalı")
        return

    logger.info("Telegram bot başlıyor...")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    handler = TelegramBotHandler()

    # Komut handlers
    app.add_handler(CommandHandler("on", handler.cmd_on))
    app.add_handler(CommandHandler("off", handler.cmd_off))
    app.add_handler(CommandHandler("status", handler.cmd_status))
    app.add_handler(CommandHandler("run_now", handler.cmd_run_now))
    app.add_handler(CommandHandler("cancel", handler.cmd_cancel))
    app.add_handler(CommandHandler("resume", handler.cmd_resume))
    app.add_handler(CommandHandler("history", handler.cmd_history))
    app.add_handler(CommandHandler("tokens", handler.cmd_tokens))
    app.add_handler(CommandHandler("trends", handler.cmd_trends))
    app.add_handler(CommandHandler("research", handler.cmd_research))
    app.add_handler(CommandHandler("skip", handler.cmd_skip))
    app.add_handler(CommandHandler("test", handler.cmd_test))

    # Callback handlers (inline buttons)
    app.add_handler(CallbackQueryHandler(handler.callback_approve_long, pattern="approve_long"))
    app.add_handler(CallbackQueryHandler(handler.callback_reject_long, pattern="reject_long"))
    app.add_handler(CallbackQueryHandler(handler.callback_regenerate_long, pattern="regenerate_long"))
    app.add_handler(CallbackQueryHandler(handler.callback_approve_short, pattern="approve_short"))
    app.add_handler(CallbackQueryHandler(handler.callback_reject_short, pattern="reject_short"))

    logger.info("Bot handlers kayıtlı")
    logger.info("Polling başlamış — signal almayı bekliyor...")

    await app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    import asyncio

    asyncio.run(main())
