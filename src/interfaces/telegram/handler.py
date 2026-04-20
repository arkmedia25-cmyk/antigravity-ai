import sys
import os
import random
from typing import Optional, List, Dict, Any

# --- Path Fix for Server/Local Consistency ---
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _ROOT not in sys.path:
    sys.path.append(_ROOT)

# Add automation and wordpress scripts to path
_AUTO = os.path.join(_ROOT, "scripts", "automation")
_WP = os.path.join(_ROOT, "scripts", "wordpress")
for _p in [_AUTO, _WP]:
    if _p not in sys.path:
        sys.path.append(_p)
# ---------------------------------------------


import logging
import threading
import asyncio
import os
import requests
import json
import time
from collections import defaultdict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, ContextTypes, filters
from src.orchestrator import Orchestrator
from src.memory.memory_manager import MemoryManager
from src.skills.uploader_skill import uploader
from src.skills.dedup_service import dedup_service
from src.core.logging import get_logger
from src.scheduler.content_scheduler import start_content_factory, _generate_dynamic_topic
from src.core.health_monitor import health_monitor
from src.core.task_queue import task_queue

# Video pipeline
try:
    from src.skills.tts_skill import generate_dutch_audio
    from src.skills.video_skill import create_reel
    from src.skills.ai_client import ask_ai
    _video_ok = True
except Exception as _ve:
    _video_ok = False
    print(f"[Video] Pipeline niet beschikbaar: {_ve}")

# Per-brand in-memory topic history to prevent /zen and /luna from repeating
_handler_used_topics: dict = {"glow": [], "holisti": []}

_RATE_LIMIT_MAX = 10
_RATE_LIMIT_WINDOW = 30
_rate_store: dict = defaultdict(list)

def _is_rate_limited(chat_id) -> bool:
    if chat_id is None: return False
    now = time.monotonic()
    _rate_store[chat_id] = [t for t in _rate_store[chat_id] if now - t < _RATE_LIMIT_WINDOW]
    if len(_rate_store[chat_id]) >= _RATE_LIMIT_MAX: return True
    _rate_store[chat_id].append(now)
    return False

logger = get_logger("interfaces.telegram.handler")

_START_MESSAGE = (
    "🚀 *Antigravity AI Agency OS* aktif!\n\n"
    "🎥 *VİDEO KOMUTLARI:*\n"
    "/luna <konu> - @GlowUpNL için video üretir (enerjik)\n"
    "/zen <konu> - @HolistiGlow için video üretir (sakin)\n"
    "/priya <konu> - Dr. Priya (HeyGen) gelişmiş video üretir\n\n"
    "💬 *DİĞER KOMUTLAR:*\n"
    "/content @marka <konu> - İçerik stratejisi yazar\n"
    "/cmo <soru> - Stratejik danışmanlık verir\n\n"
    "💡 *VİDEO YÖNETİMİ:*\n"
    "Video üretildiğinde altındaki butonlarla:\n"
    "📥 *Download:* Videoyu indir\n"
    "✍️ *Revise:* Değişiklik iste\n"
    "🚀 *Publish:* Instagram'a gönder"
)

class TelegramHandler:
    def __init__(self):
        self.orchestrator = Orchestrator()
        try:
            self.memory = MemoryManager(namespace="telegram")
            logger.info("TelegramHandler: MemoryManager initialized.")
        except Exception as e:
            logger.error(f"TelegramHandler: MemoryManager init failed: {e}")
            self.memory = None # Final fallback to avoid crash
        self._user_state = {} 

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
            
        chat_id = update.effective_chat.id
        text = update.message.text
        logger.info(f"📥 [Telegram] New message from {chat_id}: {text}")
        
        # Load conversation context (prevents context-related errors)
        prev_context = self.memory.load(f"chat_{chat_id}_context") or ""

        if _is_rate_limited(chat_id):
            await update.message.reply_text("Sakin ol şampiyon! Çok hızlı gidiyorsun. 🛑")
            return

        if chat_id in self._user_state and self._user_state[chat_id] == "awaiting_revision":
            await self._process_revision(update, context)
            return

        if text.startswith("/start"):
            await update.message.reply_text(_START_MESSAGE, parse_mode="Markdown")
            return

        if text.startswith("/ping"):
            await update.message.reply_text("🏓 Pong! Bot çevrimiçi ve mesajları alabiliyor.")
            return

        if text.startswith("/status"):
            hb = "outputs/heartbeat.txt"
            last_hb = "Bilinmiyor"
            if os.path.exists(hb):
                with open(hb, "r") as f: last_hb = f.read()
            
            pending = len(task_queue.tasks)
            status_msg = (
                "🛡️ *Agency Swarm OS Sistem Özeti*\n\n"
                f"✅ *Bot:* Aktif\n"
                f"💓 *Son Kalp Atışı:* `{last_hb}`\n"
                f"📥 *Kuyruktaki Görevler:* `{pending}`\n"
                f"🧠 *AI Client:* Hazır\n"
                f"🎥 *Video Pipeline:* Safe Mode Aktif\n"
                f"📅 *Scheduler:* Çalışıyor"
            )
            await update.message.reply_text(status_msg, parse_mode="Markdown")
            return

        if text.startswith("/luna"):
            # Flexible parsing: catch /luna_video_Topic or /luna Topic
            user_topic = text.replace("/luna", "").replace("_video_", "").strip()
            brand = "glow"
            if not user_topic:
                user_topic = _generate_dynamic_topic(brand, "user request", _handler_used_topics[brand])
            if dedup_service.is_duplicate(user_topic):
                user_topic = _generate_dynamic_topic(brand, "user request", _handler_used_topics[brand] + [user_topic])
            dedup_service.register_content(user_topic, content_type="topic", metadata={"brand": brand, "source": "manual"})
            _handler_used_topics[brand].append(user_topic)
            await update.message.reply_text(f"🔥 Luna @GlowUpNL için çalışıyor...\n📌 Konu: _{user_topic}_")
            asyncio.create_task(self._generate_video_async(chat_id, user_topic, brand, context))
            return

        if text.startswith("/zen"):
            # Flexible parsing: catch /zen_video_Topic or /zen Topic
            user_topic = text.replace("/zen", "").replace("_video_", "").strip()
            brand = "holisti"
            if not user_topic:
                user_topic = _generate_dynamic_topic(brand, "user request", _handler_used_topics[brand])
            
            # [PERSISTENCE] Add to queue before starting
            task_id = task_queue.add_task(chat_id, user_topic, brand)
            
            dedup_service.register_content(user_topic, content_type="topic", metadata={"brand": brand, "source": "manual"})
            _handler_used_topics[brand].append(user_topic)
            await update.message.reply_text(f"🌿 Zen @HolistiGlow için çalışıyor...\n📌 Görev No: `{task_id}`\n📌 Konu: _{user_topic}_")
            asyncio.create_task(self._process_task_async(task_id, context))
            return

        if text.startswith("/priya"):
            topic = text.replace("/priya", "").replace("_video_", "").strip() or "Holistische wellness"
            await update.message.reply_text(f"🧘 Dr. Priya @HolistiGlow için gelişmiş video hazırlıyor...\nKonu: {topic}")
            threading.Thread(target=self._generate_priya_sync, args=(chat_id, topic, context), daemon=True).start()
            return

        for cmd, agent in {"/cmo": "cmo", "/content": "content", "/sales": "sales", "/priya": "content"}.items():
            if text.startswith(cmd):
                task = text[len(cmd):].strip()
                await self._execute_task(update, context, agent, task)
                return

        # Manual Scheduler Trigger for Testing
        if text.startswith("/trigger"):
            await update.message.reply_text("⏳ Manüel içerik tetikleyicisi başlatılıyor... 🚀")
            default_chat = os.getenv("TELEGRAM_CHAT_ID", "812914122")
            # We trigger the morning glowup job as a test
            threading.Thread(
                target=self._generate_video_sync, 
                args=(chat_id, "@glowup Manüel Test: Harika bir gün için enerji dolu bir wellness videosu hazırlayalım.", "glow", context), 
                daemon=True
            ).start()
            return

        await self._execute_task(update, context, "cmo", text)

    def handle(self, text, chat_id=None):
        """
        Backward compatibility bridge for legacy systems (e.g. skills/automation/telegram_handler.py).
        Routes raw text commands to the Orchestrator.
        """
        agent = "cmo"
        clean_text = text
        
        # Simple command mapping
        if text.startswith("/cmo"):
            agent = "cmo"
            clean_text = text[4:].strip()
        elif text.startswith("/content"):
            agent = "content"
            clean_text = text[8:].strip()
        elif text.startswith("/sales"):
            agent = "sales"
            clean_text = text[6:].strip()
        elif text.startswith("/research"):
            agent = "research"
            clean_text = text[9:].strip()
        elif text.startswith("/linkedin"):
            agent = "linkedin"
            clean_text = text[9:].strip()
        elif text.startswith("/email"):
            agent = "email"
            clean_text = text[6:].strip()

        # Route to orchestrator (synchronous call for the bridge)
        msg = self.orchestrator.handle_request(clean_text, agent=agent, chat_id=chat_id)
        return msg.content if hasattr(msg, 'content') else str(msg)

    def _generate_priya_sync(self, chat_id, topic, context):
        """Advanced Dr. Priya pipeline (HeyGen + ElevenLabs)"""
        import os
        _token = os.getenv("TELEGRAM_TOKEN", "")
        _api = f"https://api.telegram.org/bot{_token}"
        try:
            import wellness_producer
            parts = topic.split("|")
            t = parts[0].strip() or "Wellness"
            h = parts[1].strip() if len(parts) > 1 else "Ontdek de kracht van holistische gezondheid."
            b = parts[2].strip() if len(parts) > 2 else t
            # Full pipeline: Claude -> ElevenLabs -> HeyGen -> FFmpeg -> Telegram
            wellness_producer.main(t, h, b, chat_id=chat_id)
        except Exception as e:
            err = str(e).encode("utf-8", errors="ignore").decode("utf-8")
            logger.error(f"Priya pipeline error: {e}", exc_info=True)
            requests.post(f"{_api}/sendMessage", data={"chat_id": chat_id, "text": f"❌ Priya hatası: {err}"})

    async def _process_task_async(self, task_id: str, context: Optional[ContextTypes.DEFAULT_TYPE]):
        """Robustly processes a task from the persistent queue."""
        task = task_queue.tasks.get(task_id)
        if not task: return
        
        chat_id = task["chat_id"]
        user_topic = task["topic"]
        brand = task["brand"]
        
        task_queue.update_status(task_id, "in_progress")
        
        try:
            # Re-use the existing generation logic
            await self._generate_video_async(chat_id, user_topic, brand, context, task_id=task_id)
            task_queue.update_status(task_id, "completed")
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}", exc_info=True)
            task_queue.update_status(task_id, "failed", error=str(e))
            if context and context.bot:
                await context.bot.send_message(chat_id, f"❌ Görev #{task_id} başarısız oldu: {str(e)[:100]}")

    async def _generate_video_async(self, chat_id, user_topic, brand, context, task_id=None):
        """Asynchronous video production flow."""
        # Use existing logic but ensure bot instance is available
        bot = context.bot if context else None
        if not bot:
            # Fallback to direct HTTP if context is missing (resumed tasks)
            from src.scheduler.content_scheduler import _send_telegram_message
            def send_msg(txt): _send_telegram_message(chat_id, txt)
        else:
            async def send_msg(txt): await bot.send_message(chat_id, txt, parse_mode="Markdown")
        
        import datetime, re, os, asyncio

        def _safe(txt):
            """Remove surrogate/non-encodable chars so Telegram API never crashes."""
            if not txt:
                return ""
            return txt.encode("utf-8", errors="ignore").decode("utf-8")

        _token = os.getenv("TELEGRAM_TOKEN", "")
        _api = f"https://api.telegram.org/bot{_token}"

        if not _video_ok:
            requests.post(f"{_api}/sendMessage", data={"chat_id": chat_id, "text": "Video pipeline yuklenemedi."})
            return
        try:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            brand_label = "@GlowUpNL" if brand == "glow" else "@HolistiGlow"
            tone = "energetic, direct, result-oriented" if brand == "glow" else "calm, wise, holistic"

            prompt = (
                f"Role: Expert Dutch Wellness Content Creator. Brand: {brand_label}. Tone: {tone}.\n"
                f"Topic: {topic}\n"
                "CRITICAL: ALL output must be 100% in DUTCH. No English or Turkish.\n"
                "CRITICAL: TITLE max 40 characters, fully Dutch, no English time notations.\n"
                "STRUCTURE:\n"
                "---TITLE---\n[Short Dutch title, max 40 chars]\n"
                "---SCRIPT---\n[Dutch voiceover, 3-4 sentences, conversational and emotional]\n"
                "---CAPTION---\n[Dutch Instagram caption with strong hook]\n"
                "---TAGS---\n[Hashtags]\n"
            )

            # Content Scorer quality gate (Pillar 18) — regenerate if script score < 6.5
            script = ""
            title = topic
            caption = ""
            tags = ""
            for _attempt in range(2):
                # Use to_thread to keep event loop free
                response = await asyncio.to_thread(ask_ai, prompt)
                title   = response.split("---TITLE---")[-1].split("---SCRIPT---")[0].strip() or topic
                script  = response.split("---SCRIPT---")[-1].split("---CAPTION---")[0].strip()
                caption = response.split("---CAPTION---")[-1].split("---TAGS---")[0].strip()
                tags    = response.split("---TAGS---")[-1].strip()

                # Score the script (Pillar 18)
                try:
                    _eval = await asyncio.to_thread(ask_ai, f"Rate script quality 1-10 (number only): {script}", use_mcp=False)
                    _m = re.search(r'\d+(?:\.\d+)?', _eval.strip().replace(",", "."))
                    _score = float(_m.group()) if _m else 5.0
                    if _score >= 6.5: break
                except Exception:
                    break


            # TTS per zin
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', script.strip()) if s.strip()]
            if not sentences:
                sentences = [script]

            fragment_data = []
            for i, sentence in enumerate(sentences):
                fname = f"audio_frag_{ts}_{i}.mp3"
                fpath = generate_dutch_audio(sentence, filename=fname)
                tag = "hook" if i == 0 else ("cta" if i == len(sentences) - 1 else "content")
                fragment_data.append({"sentence": sentence, "audio": fpath, "tag": tag})

            # --- Fetch a Pexels background image for the topic ---
            pexels_key = os.getenv("PEXELS_API_KEY", "")
            image_path = None
            if pexels_key:
                try:
                    query = re.sub(r'[^a-zA-Z\s]', '', topic).strip()[:40] or "wellness"
                    px_resp = requests.get(
                        f"https://api.pexels.com/v1/search?query={query}&per_page=1&orientation=portrait",
                        headers={"Authorization": pexels_key}, timeout=10
                    )
                    if px_resp.ok:
                        photos = px_resp.json().get("photos", [])
                        if photos:
                            img_url = photos[0]["src"]["large2x"]
                            img_fname = f"bg_{ts}.jpg"
                            os.makedirs("outputs", exist_ok=True)
                            img_dest = os.path.join("outputs", img_fname)
                            with requests.get(img_url, stream=True, timeout=15) as r:
                                with open(img_dest, "wb") as f:
                                    for chunk in r.iter_content(8192):
                                        f.write(chunk)
                            image_path = img_dest
                except Exception as px_err:
                    print(f"[handler] Pexels gorsel alinamadi: {px_err}")

            output_filename = f"reel_{brand}_{ts}.mp4"
            video_path = create_reel(
                fragments=fragment_data,
                image_path=image_path,
                brand=brand,
                output_filename=output_filename,
            )

            # Use short video_id for callback_data (Telegram max 64 chars)
            video_id = f"{brand}_{ts}"

            safe_title   = _safe(title.upper())
            safe_caption = _safe(caption)
            safe_tags    = _safe(tags)
            safe_brand   = _safe(brand_label)

            pkg = f"[TITEL]\n{safe_title}\n\n[CAPTION]\n{safe_caption}\n\n[TAGS]\n{safe_tags}"

            reply_markup_json = json.dumps({"inline_keyboard": [
                [{"text": "Downloaden",              "callback_data": f"dl_{video_id}"},
                 {"text": "Herzien",                 "callback_data": f"rev_{video_id}"}],
                [{"text": f"Instagram ({safe_brand})",  "callback_data": f"ig_{video_id}"},
                 {"text": f"TikTok ({safe_brand})",     "callback_data": f"tt_{video_id}"}]
            ]})

            if os.path.exists(video_path):
                with open(video_path, "rb") as vf:
                    requests.post(f"{_api}/sendVideo", data={
                        "chat_id": chat_id,
                        "caption": f"{safe_brand} - Video Klaar!",
                        "reply_markup": reply_markup_json
                    }, files={"video": vf})
                requests.post(f"{_api}/sendMessage", data={"chat_id": chat_id, "text": pkg})
            else:
                requests.post(f"{_api}/sendMessage", data={"chat_id": chat_id, "text": f"Fout: Video niet gevonden: {video_path}"})

        except Exception as e:
            err = _safe(str(e))
            requests.post(f"{_api}/sendMessage", data={"chat_id": chat_id, "text": f"Video fout: {err}"})

    async def _execute_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE, agent: str, task: str):
        chat_id = update.effective_chat.id
        
        # Determine persona message based on brand mention
        persona_msg = "⏳ Luna mesajı aldı, çalışmaya başladı... ✍️"
        if "@holisti" in task.lower():
            persona_msg = "⏳ Zen mesajı aldı, çalışmaya başladı... 🌿"
        elif "@glow" in task.lower():
            persona_msg = "⏳ Luna mesajı aldı, çalışmaya başladı... ✍️"
            
        msg_status = await update.message.reply_text(persona_msg)
        
        swarm_msg = self.orchestrator.handle_request(task, agent=agent, chat_id=chat_id)
        response = swarm_msg.content if hasattr(swarm_msg, 'content') else str(swarm_msg)
        
        # Check if video data is attached to the SwarmMessage
        if swarm_msg.data and swarm_msg.data.get("video_path"):
            await self._send_video_with_controls(update, context, swarm_msg.data.get("video_path"))
            await msg_status.delete() 
        elif ".mp4" in response.lower() or "outputs/" in response:
            await self._send_video_with_controls(update, context, response)
            await msg_status.delete() 
        else:
            await msg_status.edit_text(response)

    async def _send_video_with_controls(self, update: Update, context: ContextTypes.DEFAULT_TYPE, video_path: str):
        # Extract clean path from potential text wrapper
        clean_path = video_path.split("outputs/")[-1].strip()
        final_path = os.path.join("outputs", clean_path)
        
        # Determine brand from path (reels_brand_timestamp.mp4)
        brand = "glowup"
        if "reels_" in clean_path:
            brand = clean_path.split("_")[1]

        keyboard = [
            [
                InlineKeyboardButton("📥 Download", callback_data=f"dl_{final_path}"),
                InlineKeyboardButton("✍️ Revise", callback_data=f"rev_{final_path}_{brand}")
            ],
            [
                InlineKeyboardButton("📸 Instagram", callback_data=f"pub_{final_path}_{brand}_ig"),
                InlineKeyboardButton("📱 TikTok", callback_data=f"pub_{final_path}_{brand}_tt"),
                InlineKeyboardButton("🎥 YouTube", callback_data=f"pub_{final_path}_{brand}_yt")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if os.path.exists(final_path):
            with open(final_path, "rb") as video:
                await update.message.reply_video(video=video, caption=f"Videon hazır! \nMarka: @{brand}", reply_markup=reply_markup)
        else:
            await update.message.reply_text(f"Video üretildi: {final_path}", reply_markup=reply_markup)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        chat_id = update.effective_chat.id

        if data.startswith("dl_"):
            path = data.replace("dl_", "")
            if os.path.exists(path):
                with open(path, "rb") as f:
                    await context.bot.send_document(chat_id=chat_id, document=f, filename=os.path.basename(path))
            else:
                await context.bot.send_message(chat_id=chat_id, text="❌ Dosya bulunamadı.")

        elif data.startswith("rev_"):
            # Format: rev_path_brand
            parts = data.split("_")
            path = parts[1]
            brand = parts[2]
            self._user_state[chat_id] = "awaiting_revision"
            self._user_state[f"{chat_id}_brand"] = brand
            await context.bot.send_message(chat_id=chat_id, text=f"✍️ @{brand} için revize isteğini yaz:")

        elif data.startswith("pub_"):
            # Format: pub_{final_path}_{brand}_{platform}
            parts = data.split("_")
            platform_map = {"ig": "Instagram", "tt": "TikTok", "yt": "YouTube"}
            platform_code = parts[-1]
            platform = platform_map.get(platform_code, "Social Media")
            
            brand = parts[-2]
            path = "_".join(parts[1:-2]) # Handle path with underscores
            
            await context.bot.send_message(chat_id=chat_id, text=f"🚀 Videon internete yükleniyor ({platform})...")
            
            public_url = uploader.upload_file(path)
            
            if not public_url:
                await context.bot.send_message(chat_id=chat_id, text="❌ Yükleme hatası! Lütfen tekrar deneyin.")
                return

            await context.bot.send_message(chat_id=chat_id, text=f"✅ Yükleme başarılı!\n🚀 {platform}'a gönderiliyor...")
            
            webhook_url = os.getenv("MAKE_WEBHOOK_URL")
            if webhook_url:
                payload = {
                    "video_url": public_url, 
                    "brand": brand, 
                    "platform": platform,
                    "caption": f"Generated by Antigravity AI for @{brand} | Target: {platform}"
                }
                try:
                    requests.post(webhook_url, json=payload)
                    await context.bot.send_message(chat_id=chat_id, text=f"🚀 {platform} gönderimi başarıyla tetiklendi (@{brand})!")
                except Exception as e:
                    await context.bot.send_message(chat_id=chat_id, text=f"❌ Webhook hatası: {e}")
            else:
                await context.bot.send_message(chat_id=chat_id, text="❌ MAKE_WEBHOOK_URL eksik! Ayarları kontrol et.")

    async def _process_revision(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        revision_text = update.message.text
        brand = self._user_state.get(f"{chat_id}_brand", "glowup")
        
        if chat_id in self._user_state:
            del self._user_state[chat_id]
        
        await update.message.reply_text(f"🔄 @{brand} için revize isteği işleniyor: '{revision_text}'")
        
        # Send brand-tagged request to orchestrator
        msg = self.orchestrator.handle_request(f"@{brand} REVISE VIDEO: {revision_text}", agent="content", chat_id=chat_id)
        response = msg.content if hasattr(msg, 'content') else str(msg)
        
        if msg.data and msg.data.get("video_path"):
             await self._send_video_with_controls(update, context, msg.data.get("video_path"))
        elif ".mp4" in response.lower() or "outputs/" in response:
            await self._send_video_with_controls(update, context, response)
        else:
            await update.message.reply_text(response)

    async def handle_trigger(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manual trigger for content production - for testing the scheduler pipeline."""
        chat_id = update.effective_chat.id
        await update.message.reply_text(
            "🚀 *Manuel Tetikleme Başladı!*\n\n"
            "📹 @HolistiGlow için sabah wellness videosu üretiliyor...\n"
            "⏳ 1-2 dakika bekleyin.",
            parse_mode="Markdown"
        )
        topic = "@holistiglow Hollanda'da sabah wellness rutinleri ve bütünsel sağlık için ipuçları."
        threading.Thread(
            target=self._generate_video_sync,
            args=(chat_id, topic, "holisti", context),
            daemon=True
        ).start()

def start_telegram_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token: 
        logger.error("TELEGRAM_TOKEN not found!")
        return
    
    handler = TelegramHandler()
    application = Application.builder().token(token).build()
    
    health_monitor.start()
    
    # [SELF-HEALING] Resume pending tasks on startup
    pending = task_queue.get_pending_tasks()
    if pending:
        logger.info(f"🚀 Resuming {len(pending)} pending tasks from previous session...")
        for t in pending:
            asyncio.create_task(handler._process_task_async(t["id"], None)) # None context is handled

    print("Antigravity Agency OS Botu Hazir!")
    
    # Start the automated content scheduler
    try:
        default_chat = os.getenv("TELEGRAM_CHAT_ID", "812914122")
        logger.info(f"Initializing content scheduler for chat: {default_chat}")
        start_content_factory(default_chat, bot=application.bot)
        logger.info("✅ Content Scheduler started successfully in background thread.")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}", exc_info=True)

    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    start_telegram_bot()