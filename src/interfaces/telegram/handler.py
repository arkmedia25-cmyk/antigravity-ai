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
        title = data.get("title", "")
        description = data.get("caption", "")
        tags = data.get("tags", "")

        from src.scheduler.content_scheduler import _send_telegram_message

        parts = ["✅ Video hazir!"]
        if title:
            parts.append(f"\nTITLE: {title}")
        if description:
            parts.append(f"\nDESCRIPTION:\n{description}")
        if tags:
            parts.append(f"\nTAGS:\n{tags}")

        caption = "\n".join(parts)
        if len(caption) > 1024: caption = caption[:1021] + "..."
        
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

    def _load_approvals(self) -> dict:
        f = os.path.join(_ROOT, ".social_approvals.json")
        try:
            return json.load(open(f)) if os.path.exists(f) else {}
        except Exception:
            return {}

    async def _publish_via_zapier(self, chat_id, vid_id: str, platforms: list[str], context):
        approvals = self._load_approvals()
        meta = approvals.get(vid_id)
        if not meta:
            await context.bot.send_message(chat_id=chat_id, text="❌ Goedkeuring niet gevonden.")
            return
        video_path = meta["path"]
        brand      = meta.get("brand", "")
        topic      = meta.get("topic", "")

        await context.bot.send_message(chat_id=chat_id, text="⏳ Video uploaden naar CDN...")
        public_url = uploader.upload_file(video_path)
        if not public_url:
            await context.bot.send_message(chat_id=chat_id,
                text="❌ Upload mislukt — video niet beschikbaar voor Zapier.")
            return

        handle_map = {"holistiglow": "@HolistiGlow", "glowup": "@GlowUpNL"}
        caption = (f"Via {handle_map.get(brand, brand)} | "
                   f"{topic.replace('_', ' ').title()}\n#wellness #health #nl")

        try:
            from src.skills.zapier_skill import post_via_zapier, post_to_all
        except ImportError:
            await context.bot.send_message(chat_id=chat_id, text="❌ zapier_skill niet geladen.")
            return

        if "all" in platforms:
            results = post_to_all(public_url, caption, brand, topic)
            lines = []
            for plat, (ok, msg) in results.items():
                icon = "✅" if ok else "❌"
                lines.append(f"{icon} {plat.upper()}: {msg}")
            await context.bot.send_message(chat_id=chat_id, text="\n".join(lines))
        else:
            for plat in platforms:
                ok, msg = post_via_zapier(plat, public_url, caption, brand, topic)
                icon = "✅" if ok else "❌"
                await context.bot.send_message(chat_id=chat_id,
                    text=f"{icon} {plat.upper()}: {msg}")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data  = query.data or ""
        chat_id = update.effective_chat.id

        # ── Download ─────────────────────────────────────────────────────────
        if data.startswith("dl_"):
            vid_id = data[3:]
            approvals = self._load_approvals()
            meta = approvals.get(vid_id)
            if meta and os.path.exists(meta["path"]):
                # Stuur als document → downloadbaar op PC én mobiel
                with open(meta["path"], "rb") as f:
                    await context.bot.send_document(
                        chat_id=chat_id,
                        document=f,
                        filename=os.path.basename(meta["path"]),
                        caption=f"⬇️ {meta.get('brand','')} — {meta.get('topic','').replace('_',' ')}",
                    )
            else:
                # Oud formaat fallback
                path = os.path.join(_ROOT, "outputs", os.path.basename(vid_id))
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        await context.bot.send_document(chat_id=chat_id, document=f,
                                                        filename=os.path.basename(path))
                else:
                    await context.bot.send_message(chat_id=chat_id, text="❌ Bestand niet gevonden.")

        # ── Aanpassen (revise) ────────────────────────────────────────────────
        elif data.startswith("rev_"):
            vid_id = data[4:]
            approvals = self._load_approvals()
            meta = approvals.get(vid_id, {})
            brand = meta.get("brand", "glowup")
            self._user_state[chat_id] = f"awaiting_revision_{vid_id}"
            self._user_state[f"{chat_id}_brand"] = brand
            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    "✏️ *Wat wil je aanpassen?*\n\n"
                    "Voorbeelden:\n"
                    "• `ander onderwerp: vitamine D`\n"
                    "• `andere stijl: sunset`\n"
                    "• `hook tekst: Slaapproblemen? Dit helpt!`\n"
                    "• `nieuwe video maken`"
                ),
                parse_mode="Markdown",
            )

        # ── Publiceren via Zapier ─────────────────────────────────────────────
        elif data.startswith("pub_"):
            # formaat: pub_ig_<id> | pub_tt_<id> | pub_yt_<id> | pub_all_<id>
            parts  = data.split("_", 2)   # ['pub', 'ig', '<id>']
            if len(parts) == 3:
                plat   = parts[1]          # 'ig' | 'tt' | 'yt' | 'all'
                vid_id = parts[2]
                platforms = list({"ig", "tt", "yt"}) if plat == "all" else [plat]
                await self._publish_via_zapier(chat_id, vid_id, platforms, context)
            else:
                # Oud formaat: pub_{filename}_{brand}_{platform}
                old_parts = data.split("_")
                path      = os.path.join(_ROOT, "outputs", old_parts[1])
                platform  = old_parts[-1]
                await context.bot.send_message(chat_id=chat_id, text="⏳ Video uploaden...")
                public_url = uploader.upload_file(path)
                if public_url:
                    await context.bot.send_message(chat_id=chat_id,
                        text=f"✅ Geüpload!\n🔗 {public_url}\n\nZapier webhook nog niet geconfigureerd voor oud formaat.")
                else:
                    await context.bot.send_message(chat_id=chat_id, text="❌ Upload mislukt!")

    async def _process_revision(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id  = update.effective_chat.id
        rev_text = update.message.text
        state    = self._user_state.get(chat_id, "")
        brand    = self._user_state.get(f"{chat_id}_brand", "glowup")

        # Extract vid_id from state 'awaiting_revision_<vid_id>'
        vid_id = state.replace("awaiting_revision_", "") if "_" in state else ""

        del self._user_state[chat_id]
        if f"{chat_id}_brand" in self._user_state:
            del self._user_state[f"{chat_id}_brand"]

        await update.message.reply_text("🔄 Opnieuw genereren...")

        rev_lower = rev_text.lower()
        if "ander onderwerp" in rev_lower or "ander topic" in rev_lower or "nieuwe video" in rev_lower:
            # Maak nieuwe reel met volgende topic
            try:
                sys.path.insert(0, os.path.join(_ROOT, "scripts"))
                from social_planner import run as plan_run
                plan_run(brand)
                await update.message.reply_text("✅ Nieuwe reel verstuurd ter goedkeuring!")
            except Exception as e:
                await update.message.reply_text(f"❌ Fout: {e}")
        elif "andere stijl" in rev_lower:
            style_name = rev_text.split(":")[-1].strip() if ":" in rev_text else None
            try:
                sys.path.insert(0, os.path.join(_ROOT, "scripts"))
                from social_planner import run as plan_run
                from amarenl_reel_maker import get_next_topic
                topic = get_next_topic(brand)
                import importlib, scripts.social_planner as sp
                sp.run(brand)
                await update.message.reply_text("✅ Nieuwe stijl verstuurd ter goedkeuring!")
            except Exception as e:
                await update.message.reply_text(f"❌ Fout: {e}")
        else:
            await update.message.reply_text(
                "📝 Notitie ontvangen. Stuur `/luna` of `/zen` voor een volledig nieuwe video."
            )

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