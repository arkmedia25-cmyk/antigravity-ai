import sys
import os

# --- Path Fix for Server/Local Consistency ---
# Add the project root to sys.path so 'src' can be imported from anywhere
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _ROOT not in sys.path:
    sys.path.append(_ROOT)
# ---------------------------------------------

import time
import requests
import json
from collections import defaultdict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, ContextTypes, filters
from src.orchestrator import Orchestrator
from src.memory.memory_manager import MemoryManager
from src.skills.uploader_skill import uploader
from src.core.logging import get_logger

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
    "🎥 *KOMUTLAR:*\n"
    "/content @marka <konu> - Markaya özel video üretir.\n"
    "/build @marka <konu> - Markaya özel web sitesi üretir.\n"
    "/cmo <soru> - Stratejik danışmanlık verir.\n\n"
    "💡 *VİDEO YÖNETİMİ:*\n"
    "Video üretildiğinde altındaki butonlarla:\n"
    "📥 *Download:* Videoyu indir.\n"
    "✍️ *Revise:* Değişiklik iste.\n"
    "🚀 *Publish:* Instagram'a (Make) gönder."
)

class TelegramHandler:
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.memory = MemoryManager(namespace="telegram") # Fixing AttributeError: missing memory attribute
        self._user_state = {} 

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
            
        chat_id = update.effective_chat.id
        text = update.message.text
        
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

        for cmd, agent in {"/cmo": "cmo", "/content": "content", "/sales": "sales", "/canva": "canva"}.items():
            if text.startswith(cmd):
                task = text[len(cmd):].strip()
                await self._execute_task(update, context, agent, task)
                return

        await self._execute_task(update, context, "cmo", text)

    async def _execute_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE, agent: str, task: str):
        chat_id = update.effective_chat.id
        
        # Determine persona message based on brand mention
        persona_msg = "⏳ Luna mesajı aldı, çalışmaya başladı... ✍️"
        if "@holisti" in task.lower():
            persona_msg = "⏳ Zen mesajı aldı, çalışmaya başladı... 🌿"
        elif "@glow" in task.lower():
            persona_msg = "⏳ Luna mesajı aldı, çalışmaya başladı... ✍️"
            
        msg = await update.message.reply_text(persona_msg)
        
        response = self.orchestrator.handle_request(task, agent=agent, chat_id=chat_id)
        
        if ".mp4" in response.lower() or "outputs/" in response:
            await self._send_video_with_controls(update, context, response)
            await msg.delete() # 'Çalışıyor' mesajını sil
        else:
            await msg.edit_text(response)

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
            [InlineKeyboardButton(f"🚀 Publish to Instagram (@{brand})", callback_data=f"pub_{final_path}_{brand}")]
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
            # Format: pub_path_brand
            parts = data.split("_")
            path = "_".join(parts[1:-1]) # Handle path with underscores
            brand = parts[-1]
            
            await context.bot.send_message(chat_id=chat_id, text="🚀 Videon internete yükleniyor (Public URL)...")
            
            # Step 1: Upload to Cloud
            public_url = uploader.upload_file(path)
            
            if not public_url:
                await context.bot.send_message(chat_id=chat_id, text="❌ Yükleme hatası! Lütfen tekrar deneyin.")
                return

            await context.bot.send_message(chat_id=chat_id, text=f"✅ Yükleme başarılı: {public_url}\nInstagram'a gönderiliyor...")
            
            # Step 2: Trigger Make.com Webhook
            webhook_url = os.getenv("MAKE_WEBHOOK_URL")
            if webhook_url:
                payload = {
                    "video_url": public_url, 
                    "brand": brand, 
                    "caption": f"Generated by Antigravity AI for @{brand}"
                }
                try:
                    requests.post(webhook_url, json=payload)
                    await context.bot.send_message(chat_id=chat_id, text=f"🚀 Instagram gönderimi başarıyla tetiklendi (@{brand})!")
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
        response = self.orchestrator.handle_request(f"@{brand} REVISE VIDEO: {revision_text}", agent="content", chat_id=chat_id)
        
        if ".mp4" in response.lower() or "outputs/" in response:
            await self._send_video_with_controls(update, context, response)
        else:
            await update.message.reply_text(response)

def start_telegram_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token: 
        logger.error("TELEGRAM_TOKEN not found!")
        return
    
    handler = TelegramHandler()
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", handler.handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_message))
    application.add_handler(CallbackQueryHandler(handler.handle_callback))
    
    print("✅ Antigravity Agency OS Botu Hazır!")
    application.run_polling()

if __name__ == "__main__":
    start_telegram_bot()