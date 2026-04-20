import time
import datetime
import threading
import os
import json
import requests
import pytz
from src.orchestrator import Orchestrator
from src.core.logging import get_logger
from src.skills.ai_client import ask_ai
from src.skills.dedup_service import dedup_service
from src.skills.research_tools import research_tools

# Initialize logger
logger = get_logger("scheduler.content_scheduler")

# Global flag to stop scheduler if needed
_STOP_SCHEDULER = False

# ── Topic theme banks — used to give AI variety context ──
_HOLISTI_THEMES = [
    "gut-brain connection and mental clarity",
    "adaptogens and stress relief (ashwagandha, rhodiola)",
    "circadian rhythm and sleep optimization",
    "magnesium deficiency and modern health",
    "anti-inflammatory foods and chronic inflammation",
    "the vagus nerve and emotional regulation",
    "intermittent fasting and cellular repair (autophagy)",
    "mineral deficiencies (zinc, selenium) in Dutch diet",
    "herbal medicine: valerian, chamomile, lemon balm",
    "breathwork and the nervous system",
    "omega-3 fatty acids and brain health",
    "hormonal balance and women over 30",
    "mindful eating and satiety hormones",
    "the lymphatic system and daily detox rituals",
    "probiotics vs prebiotics for gut microbiome",
    "Amare Happy Juice Pack and mood regulation",
    "sleep hygiene and melatonin production",
    "vitamin D deficiency in the Netherlands",
    "cortisol management and adrenal fatigue",
    "hydration science and electrolyte balance",
]

_GLOWUP_THEMES = [
    "collagen production and diet (vitamin C, amino acids)",
    "energy levels and mitochondrial health",
    "skin barrier repair with ceramides and niacinamide",
    "sugar impact on skin aging and acne",
    "exercise and longevity (zone 2 cardio)",
    "beauty sleep and skin cell regeneration",
    "hair growth and biotin, iron, zinc connection",
    "morning routines of high-energy Dutch women",
    "hormonal acne and gut microbiome link",
    "glow from within: antioxidants and free radicals",
    "cold showers and dopamine boost",
    "stress and cortisol effect on skin",
    "Amare HL5 Collagen and joint recovery",
    "sun damage repair and SPF importance",
    "body confidence and wellness mindset",
    "detox myths vs. real liver support foods",
    "why Dutch women are aging differently (lifestyle factors)",
    "metabolic flexibility and consistent energy",
    "fermented foods and radiant skin",
    "protein intake and muscle tone in women 25-45",
]


def _score_content(content: str) -> float:
    """
    Evaluates content quality using the content_scorer MCP logic (Pillar 18).
    Returns a score from 0-10. Anything below 7 is regenerated.
    """
    eval_prompt = (
        f"Rate the neuro-linguistic impact and viral potential of this Dutch wellness video topic out of 10.\n"
        f"Output ONLY a single number between 1 and 10.\n\n"
        f"Topic: {content}"
    )
    try:
        score_resp = ask_ai(eval_prompt).strip().replace(",", ".")
        # Extract first number found
        import re
        m = re.search(r'\d+(?:\.\d+)?', score_resp)
        return float(m.group()) if m else 5.0
    except Exception:
        return 5.0


def _route_model(task_description: str) -> str:
    """
    Model router (Pillar 1-2): Picks the right AI provider based on task.
    Video/complex = openai, simple/daily = openai-mini.
    """
    if any(kw in task_description.lower() for kw in ["video", "reel", "üret", "render", "compile"]):
        return "openai"     # will use gpt-4o in ask_ai
    return "openai"         # gpt-4.1-mini default (set in ai_client)


def _fetch_live_trends(niche: str) -> str:
    """
    Live trend scanner (Pillar 28 — trend_detector MCP logic).
    Queries Google/DuckDuckGo for current viral wellness trends in the Netherlands.
    """
    try:
        query = f"trending {niche} viral content Netherlands wellness social media {time.strftime('%Y-%m')}"
        results = research_tools.google_search(query, num_results=3)
        if results:
            snippets = [r.get("description") or r.get("title", "") for r in results if r]
            return " | ".join([s for s in snippets if s])[:600]
    except Exception as e:
        logger.warning(f"[Scheduler] Live trend fetch failed (non-critical): {e}")
    return ""


def _generate_dynamic_topic(brand: str, time_of_day: str, used_topics: list) -> str:
    """
    Uses AI + live trend data to generate a fresh, unique, high-scoring topic.
    Integrates: trend_detector (Pillar 28) + content_scorer (Pillar 18).
    Avoids previously used topics by passing them as context.
    """
    theme_bank = _HOLISTI_THEMES if "holisti" in brand else _GLOWUP_THEMES
    brand_label = "@HolistiGlow" if "holisti" in brand else "@GlowUpNL"
    brand_desc = (
        "wise, calm, educational wellness mentor for Dutch health-conscious women. "
        "Focus: holistic health, mind-body connection, herbal science, trustworthy advice."
    ) if "holisti" in brand else (
        "energetic, empowering beauty & wellness coach for Dutch women 25-45. "
        "Focus: glow, energy, skin health, confidence, and modern wellness."
    )

    niche = "holistic wellness herbs mindfulness" if "holisti" in brand else "beauty skin glow energy wellness"

    # 1. Live trend scan (Pillar 28)
    live_trends = _fetch_live_trends(niche)
    live_trend_block = f"\nCURRENT VIRAL TRENDS (use as inspiration):\n{live_trends}" if live_trends else ""

    # Rotate through static themes as anchor ideas
    available_themes = [t for t in theme_bank if t not in used_topics[-len(theme_bank)//2:]]
    if not available_themes:
        available_themes = theme_bank

    recent_used_str = "\n".join([f"- {t}" for t in used_topics[-10:]]) if used_topics else "None yet"

    prompt = (
        f"You are a creative director for {brand_label}, a Dutch wellness brand.\n"
        f"Brand personality: {brand_desc}\n\n"
        f"LANGUAGE: STRICTLY DUTCH (NEDERLANDS).\n"
        f"Time of post: {time_of_day}\n"
        f"Anchor topic ideas: {', '.join(available_themes[:6])}\n"
        f"{live_trend_block}\n\n"
        f"RECENT TOPICS (DO NOT REPEAT): {recent_used_str}\n\n"
        "Generate ONE unique, viral Dutch wellness video topic.\n"
        "Return ONLY the topic in Dutch. No hashtags, no English."
    )

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            topic = ask_ai(prompt, use_mcp=(attempt == 0)).strip().strip('"').strip("'")
            
            # Dutch language sanity check (if it looks like English, retry)
            english_indicators = [" the ", " is ", " for ", " and ", " with ", " how to "]
            if any(ind in topic.lower() for ind in english_indicators) and not any(ind in topic.lower() for ind in [" de ", " het ", " een "]):
                logger.warning(f"[Scheduler] 🚩 English detected in topic: '{topic}'. Retrying in Dutch...")
                continue

            logger.info(f"[Scheduler] 🧠 AI topic [{brand_label}]: {topic}")
            score = _score_content(topic)
            if score >= 6.5:
                return topic
            else:
                logger.warning(f"[Scheduler] ⚠️ Low score ({score}), retrying...")
                used_topics = used_topics + [topic]
        except Exception as e:
            logger.warning(f"[Scheduler] Topic attempt {attempt+1} failed: {e}")

    # Final fallback: random from static bank
    import random
    return random.choice(available_themes)


def _send_telegram_message(chat_id: str, text: str, reply_markup=None, video_path=None, caption=None):
    """Send a message (text or video) via Telegram HTTP API with markup support."""
    token = os.getenv("TELEGRAM_TOKEN", "")
    if not token:
        logger.error("[Scheduler] TELEGRAM_TOKEN not set.")
        return

    try:
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
    Each slot generates a UNIQUE AI-chosen topic — no repetition.

    Peak Hours (Amsterdam Time):
    - 08:00  → @holistiglow (Sabah Wellness)
    - 12:30  → @glowup     (Öğle Enerjisi)
    - 20:15  → @glowup     (Akşam Rutini)
    - 22:00  → @holistiglow (Gece Ritüelleri)
    """

    # Static schedule: defines BRAND + LABEL + TIME_OF_DAY context only.
    # The actual TOPIC is generated dynamically by AI.
    SCHEDULE = {
        "08:00": ("holisti", "🌅 Sabah Paylaşımı (HolistiGlow)", "early morning, sunrise, start of day"),
        "12:30": ("glow",    "☀️ Öğle Paylaşımı (GlowUp)",       "midday, lunch break, energy boost"),
        "20:15": ("glow",    "🌆 Akşam Paylaşımı (GlowUp)",       "evening, end of work day, wind-down"),
        "22:00": ("holisti", "🌙 Gece Paylaşımı (HolistiGlow)",   "night, bedtime, relaxation, sleep"),
    }

    # In-memory topic history per brand (persisted across scheduler ticks in this process)
    _used_topics = {"holisti": [], "glow": []}

    def run_scheduler():
        logger.info(f"[Scheduler] ✅ Dynamic Content Factory started. Chat: {chat_id}")

        orchestrator = Orchestrator()
        amsterdam_tz = pytz.timezone("Europe/Amsterdam")
        heartbeat_timestamp = time.time()

        while not _STOP_SCHEDULER:
            try:
                now = datetime.datetime.now(amsterdam_tz)
                current_time = now.strftime("%H:%M")

                # Heartbeat every 10 minutes
                if time.time() - heartbeat_timestamp >= 600:
                    logger.info(f"[Scheduler ♥] Active. Amsterdam Time: {current_time}")
                    heartbeat_timestamp = time.time()

                if current_time in SCHEDULE:
                    brand, label, time_of_day = SCHEDULE[current_time]
                    logger.info(f"[Scheduler] 🚀 TRIGGERED: {label} at {current_time}")

                    def execute_production(b=brand, lbl=label, tod=time_of_day):
                        try:
                            # 1. Generate a fresh, unique topic via AI
                            topic = _generate_dynamic_topic(b, tod, _used_topics[b])

                            # 2. Dedup check — skip if identical content was produced before
                            if dedup_service.is_duplicate(topic):
                                logger.warning(f"[Scheduler] ⚠️ Duplicate topic detected, regenerating: {topic}")
                                # Try once more with stronger instruction
                                topic = _generate_dynamic_topic(b, tod, _used_topics[b] + [topic])

                            # 3. Register this topic so it won't be repeated
                            dedup_service.register_content(topic, content_type="topic", metadata={"brand": b, "slot": tod})
                            _used_topics[b].append(topic)
                            # Keep in-memory history to last 30 entries
                            if len(_used_topics[b]) > 30:
                                _used_topics[b] = _used_topics[b][-30:]

                            brand_tag = "@holistiglow" if b == "holisti" else "@glowup"
                            full_prompt = f"{brand_tag} {topic}"

                            _send_telegram_message(
                                chat_id,
                                f"🤖 *{lbl} başladı...*\n📌 Konu: _{topic}_\n⏳ Üretim devam ediyor, lütfen bekleyin."
                            )

                            msg = orchestrator.handle_request(full_prompt, agent="content", chat_id=chat_id)
                            response_text = msg.content if hasattr(msg, "content") else str(msg)

                            reply_markup = None
                            video_path = None

                            if hasattr(msg, "data") and msg.data and msg.data.get("video_path"):
                                video_path = msg.data.get("video_path")
                                public_url = msg.data.get("public_url", "#")
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
                                _send_telegram_message(
                                    chat_id,
                                    f"✅ *{lbl} tamamlandı!*",
                                    video_path=video_path,
                                    reply_markup=reply_markup,
                                    caption=f"✅ *{lbl} hazır!*\n\n{response_text}"
                                )
                            else:
                                _send_telegram_message(
                                    chat_id,
                                    f"✅ *{lbl} tamamlandı!*\n\n{response_text}",
                                    reply_markup=reply_markup
                                )

                        except Exception as e:
                            logger.error(f"[Scheduler] Production error: {e}", exc_info=True)
                            _send_telegram_message(chat_id, f"❌ *{lbl} hatası:* {e}")

                    threading.Thread(target=execute_production, daemon=True).start()

                    logger.debug("[Scheduler] Sleeping 65s to prevent double trigger.")
                    time.sleep(65)

                time.sleep(30)

            except Exception as e:
                logger.error(f"[Scheduler Loop Error] {e}", exc_info=True)
                time.sleep(60)

    thread = threading.Thread(target=run_scheduler, name="ContentSchedulerThread", daemon=True)
    thread.start()
    return thread
