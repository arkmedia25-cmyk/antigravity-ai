import sys
import os

# --- Path Fix for Server/Local Consistency ---
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _ROOT not in sys.path:
    sys.path.append(_ROOT)
# ---------------------------------------------

# --- Single Instance Lock ---
import fcntl
_LOCK_FILE = "/tmp/antigravity_bot.lock"
_lock_fh = open(_LOCK_FILE, "w")
try:
    fcntl.flock(_lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    print("[LOCK] Another instance is already running. Exiting.")
    sys.exit(0)
# ----------------------------

import time
import threading
import requests
import json
from collections import defaultdict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, ContextTypes, filters
from src.orchestrator import Orchestrator
from src.memory.memory_manager import MemoryManager
from src.skills.uploader_skill import uploader
from src.core.logging import get_logger

# Video pipeline
try:
    from src.skills.tts_skill import generate_dutch_audio
    from src.skills.video_skill import create_reel
    from src.skills.ai_client import ask_ai
    _video_ok = True
except Exception as _ve:
    _video_ok = False
    print(f"[Video] Pipeline niet beschikbaar: {_ve}")

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
    "/zen <konu> - @HolistiGlow için video üretir (sakin)\n\n"
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

        if text.startswith("/luna"):
            topic = text[5:].strip() or "Energie en gezondheid"
            await update.message.reply_text(f"🔥 Luna @GlowUpNL için çalışıyor...\nKonu: {topic}")
            threading.Thread(target=self._generate_video_sync, args=(chat_id, topic, "glow", context), daemon=True).start()
            return

        if text.startswith("/zen"):
            topic = text[4:].strip() or "Holistische wellness"
            await update.message.reply_text(f"🌿 Zen @HolistiGlow için çalışıyor...\nKonu: {topic}")
            threading.Thread(target=self._generate_video_sync, args=(chat_id, topic, "holisti", context), daemon=True).start()
            return

        for cmd, agent in {"/cmo": "cmo", "/content": "content", "/sales": "sales", "/canva": "canva"}.items():
            if text.startswith(cmd):
                task = text[len(cmd):].strip()
                await self._execute_task(update, context, agent, task)
                return

        await self._execute_task(update, context, "cmo", text)

    def _generate_video_sync(self, chat_id, topic, brand, context):
        """Video üretim pipeline — thread içinde çalışır."""
        import datetime, re, os
        if not _video_ok:
            context.bot.send_message(chat_id=chat_id, text="❌ Video pipeline yüklenemedi.")
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
                "---SCRIPT---\n[Dutch voiceover, 3-4 sentences]\n"
                "---CAPTION---\n[Dutch Instagram caption]\n"
                "---TAGS---\n[Hashtags]\n"
            )
            response = ask_ai(prompt)

            title = response.split("---TITLE---")[-1].split("---SCRIPT---")[0].strip() or topic
            script = response.split("---SCRIPT---")[-1].split("---CAPTION---")[0].strip()
            caption = response.split("---CAPTION---")[-1].split("---TAGS---")[0].strip()
            tags = response.split("---TAGS---")[-1].strip()

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

            output_filename = f"reel_{brand}_{ts}.mp4"
            video_path = create_reel(
                fragments=fragment_data,
                image_path=None,
                brand=brand,
                output_filename=output_filename,
            )

            keyboard = [
                [InlineKeyboardButton("📥 Download", callback_data=f"dl_{video_path}"),
                 InlineKeyboardButton("✍️ Revise", callback_data=f"rev_{video_path}_{brand}")],
                [InlineKeyboardButton(f"🚀 Instagram (@{brand_label})", callback_data=f"pub_{video_path}_{brand}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            pkg = f"📝 {title.upper()}\n\n{caption}\n\n{tags}"

            if os.path.exists(video_path):
                with open(video_path, "rb") as vf:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(context.bot.send_video(
                        chat_id=chat_id, video=vf,
                        caption=f"{brand_label} — Video Hazır!",
                        reply_markup=reply_markup
                    ))
                    loop.run_until_complete(context.bot.send_message(chat_id=chat_id, text=pkg))
                    loop.close()
            else:
                import asyncio
                loop = asyncio.new_event_loop()
                loop.run_until_complete(context.bot.send_message(chat_id=chat_id, text=f"❌ Video dosyası bulunamadı: {video_path}"))
                loop.close()

        except Exception as e:
            import asyncio
            loop = asyncio.new_event_loop()
            loop.run_until_complete(context.bot.send_message(chat_id=chat_id, text=f"❌ Video hatası: {e}"))
            loop.close()

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
    application.add_handler(CommandHandler("luna", handler.handle_message))
    application.add_handler(CommandHandler("zen", handler.handle_message))
    application.add_handler(CommandHandler("content", handler.handle_message))
    application.add_handler(CommandHandler("cmo", handler.handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_message))
    application.add_handler(CallbackQueryHandler(handler.handle_callback))
    
    print("✅ Antigravity Agency OS Botu Hazır!")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    start_telegram_bot()