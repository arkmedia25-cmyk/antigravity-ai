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

# Per-brand in-memory topic history
_handler_used_topics: dict = {"glow": [], "holisti": [], "wellness": []}

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

class TelegramHandler:
    def __init__(self):
        self.orchestrator = Orchestrator()
        try:
            self.memory = MemoryManager(namespace="telegram")
            logger.info("TelegramHandler: MemoryManager initialized.")
        except Exception as e:
            logger.error(f"TelegramHandler: MemoryManager init failed: {e}")
            self.memory = None 
        self._user_state = {} 

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
            
        chat_id = update.effective_chat.id
        text = update.message.text
        logger.info(f"📥 [Telegram] New message from {chat_id}: {text}")
        
        if _is_rate_limited(chat_id):
            await update.message.reply_text("Sakin ol şampiyon! Çok hızlı gidiyorsun. 🛑")
            return

        if chat_id in self._user_state and self._user_state[chat_id] == "awaiting_revision":
            await self._process_revision(update, context)
            return

        if text.startswith("/start"):
            await update.message.reply_text(_START_MESSAGE, parse_mode="Markdown")
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
                f"🧠 *Orchestrator:* Aktif (Agentic Swarm)\n"
                f"🎥 *Video Pipeline:* Unified Agency Routing\n"
            )
            await update.message.reply_text(status_msg, parse_mode="Markdown")
            return

        # --- Enhanced Parsing (Pillar 26) ---
        if text.startswith("/luna"):
            # Strip command and any legacy formatting
            user_topic = text.replace("/luna", "").replace("_video_", "").strip()
            brand = "glow"
            if not user_topic:
                user_topic = _generate_dynamic_topic(brand, "user request", _handler_used_topics[brand])
            
            task_id = task_queue.add_task(chat_id, user_topic, brand)
            dedup_service.register_content(user_topic, "topic", metadata={"brand": brand, "source": "manual"})
            _handler_used_topics[brand].append(user_topic)
            await update.message.reply_text(f"🔥 Luna @GlowUpNL için çalışıyor...\n📌 Görev: {task_id}\n📌 Konu: {user_topic}")
            asyncio.create_task(self._process_task_async(task_id, context))
            return

        if text.startswith("/zen"):
            user_topic = text.replace("/zen", "").replace("_video_", "").strip()
            brand = "holisti"
            if not user_topic:
                user_topic = _generate_dynamic_topic(brand, "user request", _handler_used_topics[brand])
            
            task_id = task_queue.add_task(chat_id, user_topic, brand)
            dedup_service.register_content(user_topic, "topic", metadata={"brand": brand, "source": "manual"})
            _handler_used_topics[brand].append(user_topic)
            await update.message.reply_text(f"🌿 Zen @HolistiGlow için çalışıyor...\n📌 Görev: {task_id}\n📌 Konu: {user_topic}")
            asyncio.create_task(self._process_task_async(task_id, context))
            return

        if text.startswith("/priya"):
            user_topic = text.replace("/priya", "").strip()
            brand = "wellness" 
            if not user_topic:
                user_topic = "Bütünsel sağlık ve zihin-beden dengesi"
            
            task_id = task_queue.add_task(chat_id, user_topic, brand, metadata={"type": "heygen"})
            await update.message.reply_text(f"👤 Dr. Priya @Wellness için hazırlanıyor...\n📌 Görev: {task_id}\n📌 Konu: {user_topic}")
            asyncio.create_task(self._process_task_async(task_id, context))
            return

        for cmd, agent in {"/cmo": "cmo", "/content": "content", "/sales": "sales", "/research": "research"}.items():
            if text.startswith(cmd):
                task = text[len(cmd):].strip()
                await self._execute_task(update, context, agent, task)
                return

        await self._execute_task(update, context, "cmo", text)

    async def _execute_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE, agent: str, task: str):
        chat_id = update.effective_chat.id
        msg_status = await update.message.reply_text("⏳ Ajan yanıtı hazırlanıyor...")
        
        try:
            swarm_msg = self.orchestrator.handle_request(task, agent=agent, chat_id=chat_id)
            response = swarm_msg.content if hasattr(swarm_msg, 'content') else str(swarm_msg)
            
            if swarm_msg.data and swarm_msg.data.get("video_path"):
                await self._send_video_message(chat_id, response, swarm_msg.data, context)
                await msg_status.delete() 
            else:
                await msg_status.edit_text(response, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            await msg_status.edit_text(f"❌ İşlem sırasında hata oluştu: {str(e)[:100]}")

    async def _process_task_async(self, task_id, context):
        """Unified Task Processor using the Agent Orchestrator."""
        task = task_queue.tasks.get(task_id)
        if not task: return

        chat_id = task["chat_id"]
        brand = task["brand"]
        topic = task["topic"]
        
        task_queue.update_status(task_id, "in_progress")
        
        try:
            brand_tag = "@holistiglow" if brand == "holisti" else "@glowup"
            # Include "reel" keyword so ContentAgent triggers delegation to VideoProducer
            full_prompt = f"{brand_tag} maak een reel over: {topic}"

            # Use to_thread for agent processing
            message = await asyncio.to_thread(self.orchestrator.handle_request, full_prompt, agent="content", chat_id=chat_id)
            
            response_text = message.content if hasattr(message, 'content') else str(message)
            video_data = message.data if hasattr(message, 'data') else {}
            
            if video_data.get("video_path"):
                # Send content kit (Instagram post + email sequence) as a separate message first
                content_kit = video_data.get("content_kit", "")
                if content_kit:
                    await context.bot.send_message(chat_id, content_kit[:4000])
                await self._send_video_message(chat_id, response_text, video_data, context, task_id=task_id)
            else:
                await context.bot.send_message(chat_id, f"✅ Görev tamamlandı!\n\n{response_text[:3500]}")
            
            task_queue.update_status(task_id, "completed")

        except Exception as e:
            logger.error(f"❌ _process_task_async failed: {e}", exc_info=True)
            task_queue.update_status(task_id, "failed", error=str(e))
            if context and context.bot:
                await context.bot.send_message(chat_id, f"❌ Görev #{task_id} hatası: {str(e)[:100]}")

    async def _send_video_message(self, chat_id, text, data, context, task_id=None):
        video_path = data.get("video_path")
        public_url = data.get("public_url")
        brand = data.get("brand", "glowup")
        
        from src.scheduler.content_scheduler import _send_telegram_message
        
        caption = f"✅ Görev {'#'+str(task_id) if task_id else ''} Hazır!\n\n{text}"
        if len(caption) > 1000: caption = caption[:997] + "..."
        
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "📥 İndir", "url": public_url or "#"},
                    {"text": "✍️ Revise", "callback_data": f"rev_{task_id or '99'}_{brand}"}
                ],
                [
                    {"text": "📸 Instagram", "callback_data": f"pub_{os.path.basename(video_path)}_{brand}_ig"},
                    {"text": "📱 TikTok", "callback_data": f"pub_{os.path.basename(video_path)}_{brand}_tt"}
                ]
            ]
        }
        
        _send_telegram_message(chat_id, caption, video_path=video_path, reply_markup=reply_markup)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        chat_id = update.effective_chat.id

        if data.startswith("dl_"):
            path = data.replace("dl_", "")
            path = os.path.join("outputs", os.path.basename(path))
            if os.path.exists(path):
                with open(path, "rb") as f:
                    await context.bot.send_document(chat_id=chat_id, document=f, filename=os.path.basename(path))
            else:
                await context.bot.send_message(chat_id=chat_id, text="❌ Dosya bulunamadı.")

        elif data.startswith("rev_"):
            parts = data.split("_")
            self._user_state[chat_id] = "awaiting_revision"
            self._user_state[f"{chat_id}_brand"] = parts[2] if len(parts) > 2 else "glowup"
            await context.bot.send_message(chat_id=chat_id, text=f"✍️ Revize isteğini yaz:")

        elif data.startswith("pub_"):
            parts = data.split("_")
            brand = parts[-2]
            path = os.path.join("outputs", parts[1])
            platform = parts[-1]
            
            await context.bot.send_message(chat_id=chat_id, text=f"🚀 Videon internete yükleniyor...")
            public_url = uploader.upload_file(path)
            
            if public_url:
                await context.bot.send_message(chat_id=chat_id, text=f"✅ Yükleme başarılı!\n🔗 {public_url}")
            else:
                await context.bot.send_message(chat_id=chat_id, text="❌ Yükleme hatası!")

    async def _process_revision(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        rev_text = update.message.text
        brand = self._user_state.get(f"{chat_id}_brand", "glowup")
        del self._user_state[chat_id]
        
        await update.message.reply_text(f"🔄 Revize işleniyor...")
        msg = self.orchestrator.handle_request(f"@{brand} REVISE: {rev_text}", agent="content", chat_id=chat_id)
        await update.message.reply_text(msg.content)

def start_telegram_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token: return
    
    handler = TelegramHandler()
    application = Application.builder().token(token).build()
    
    # Register message handlers
    application.add_handler(MessageHandler(filters.ALL, handler.handle_message))
    application.add_handler(CallbackQueryHandler(handler.handle_callback))
    
    # Start scheduler
    default_chat = os.getenv("TELEGRAM_CHAT_ID", "812914122")
    start_content_factory(default_chat, bot=application.bot)

    print("Antigravity Agency OS Botu Hazir!")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    start_telegram_bot()