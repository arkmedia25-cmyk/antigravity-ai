from src.agents.base_agent import BaseAgent
from src.core.protocol import SwarmMessage
from src.skills.video_skill import create_reel
from src.skills.uploader_skill import uploader
from src.skills.tts_skill import generate_dutch_audio
from src.skills.ai_client import ask_ai
import os
import time

class VideoProducerAgent(BaseAgent):
    """
    VideoProducerAgent: The autonomous editor of the Agency.
    Takes a script/idea and produces a short-form video (Reel).
    """
    def __init__(self):
        super().__init__(name="video_producer")

    def process(self, input_data: str, chat_id=None, brand: str = "glowup", context: dict = None) -> SwarmMessage:
        self.logger.info(f"[VideoProducer] Starting production: {input_data[:50]}...")

        try:
            # 1. Generate Metadata (Posting Kit)
            print(f"[VideoProducer] Generating Instagram metadata for {brand}...")
            meta_prompt = (
                f"Role: Expert Dutch Instagram Marketer. Brand: {brand}.\n"
                f"Topic: {input_data}\n"
                "Generate a professional Instagram Posting Kit in DUTCH.\n"
                "STRUCTURE:\n"
                "---TITLE---\n[Short Dutch title, max 40 chars]\n"
                "---CAPTION---\n[Dutch Instagram caption with hooks]\n"
                "---TAGS---\n[Relevant Dutch/Global hashtags]\n"
            )
            meta_resp = ask_ai(meta_prompt, use_mcp=False)
            
            title = meta_resp.split("---TITLE---")[-1].split("---CAPTION---")[0].strip() or "Wellness Tip"
            caption = meta_resp.split("---CAPTION---")[-1].split("---TAGS---")[0].strip()
            tags = meta_resp.split("---TAGS---")[-1].strip()

            # 2. Extract Reels Specific Text (to avoid reading the entire post/email in VO)
            import re
            # Much more flexible regex for extraction
            patterns = [
                r"(?s)(🎬\s*Reels-idee|Reels-idee|Video:)(.*?)(CTA:|📧|Email reeks|#|$)",
                r"(?s)(Inhoud:)(.*?)(CTA:|#|📧|$)"
            ]
            
            vo_text = ""
            for pattern in patterns:
                match = re.search(pattern, input_data, re.I)
                if match:
                    vo_text = match.group(2).strip()
                    self.logger.info(f"[VideoProducer] Extracted VO text via pattern: {pattern}")
                    break
            
            if not vo_text:
                # Fallback: if no specific block found, take the whole input but try to strip the Instagram caption part
                self.logger.warning("[VideoProducer] Specific marker not found in input, using fallback extraction.")
                vo_text = input_data.split("📸")[0].split("Instagram post")[0].strip() or input_data
            
            # Final VO cleanup: remove labels like "Hook:", "Inhoud:", "CTA:"
            vo_text = re.sub(r'(?i)(Hook|Inhoud|CTA|Scene|Beeld|Afsluiting|Intro|Hookzin):\s*', '', vo_text)
            vo_text = vo_text.strip()
            
            self.logger.info(f"[VideoProducer] Final VO Text (length {len(vo_text)}): {vo_text[:100]}...")
            
            # 3. Fetch Background Image from Pexels
            print(f"[VideoProducer] Searching for 100% relevant visual...")
            search_query_prompt = (
                f"Topic: {vo_text[:120]}\n"
                f"Brand: {brand}\n"
                "Action: Suggest a 3-word English search query for a HIGH-QUALITY Pinterest-style vertical photo. "
                "CRITICAL: Focus ONLY on wellness, healthy lifestyle, peaceful morning, or fitness. "
                "The image must feature a person or a serene nature scene (no machines, no industry).\n"
                "Return ONLY the 3 words."
            )
            raw_query = ask_ai(search_query_prompt, use_mcp=False).strip().replace("'", "").replace('"', '')
            
            # ✨ HARD-CODED ANCHORING (Pillar 25): Force wellness niche
            forbidden = ["wind", "turbine", "mill", "industry", "factory", "solar", "engine"]
            safe_query = raw_query.lower()
            for f in forbidden:
                safe_query = safe_query.replace(f, "wellness")
            
            # Combine with niche anchors
            final_search_query = f"wellness healthy lifestyle {safe_query}"
            
            image_path = None
            try:
                import requests
                pexels_key = os.getenv("PEXELS_API_KEY")
                if pexels_key:
                    headers = {"Authorization": pexels_key}
                    # Higher per_page to have variety if 1st one is bad? No, Pexels usually good.
                    params = {"query": final_search_query, "per_page": 1, "orientation": "portrait"}
                    p_resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=15)
                    if p_resp.status_code == 200:
                        p_data = p_resp.json()
                        if p_data.get("photos"):
                            img_url = p_data["photos"][0]["src"]["large2x"]
                            img_dest = os.path.join("outputs", f"bg_{int(time.time())}.jpg")
                            img_data = requests.get(img_url, timeout=15).content
                            with open(img_dest, "wb") as f:
                                f.write(img_data)
                            image_path = os.path.abspath(img_dest)
                            print(f"[VideoProducer] ✅ Relevant Image Found: {final_search_query}")
            except Exception as e:
                self.logger.warning(f"Pexels fetch failed: {e}")

            # 4. Generate Voiceover (TTS)
            filename = f"voice_{int(time.time())}.mp3"
            print(f"[VideoProducer] Generating voiceover...")
            voice_path = generate_dutch_audio(vo_text, filename)
            
            # 5. Get Word Timestamps & Generate ASS (Daktilo)
            from src.skills.alignment_skill import alignment_service
            # Append CTA to voiceover
            cta_text = " Vond je dit nuttig? Volg ons voor meer wellness tips, bewaar en deel deze video!"
            full_vo_text = vo_text + cta_text
            
            print(f"[VideoProducer] Creating absolute-center daktilo subtitles (.ass)...")
            word_timestamps = alignment_service.get_word_timestamps(voice_path)
            # Regenerate timestamps for full text if needed? 
            # Actually, I should generate speech for the combined text.
            
            # --- RE-RENDER SPEECH WITH CTA ---
            voice_path = generate_dutch_audio(full_vo_text, filename)
            word_timestamps = alignment_service.get_word_timestamps(voice_path)
            # ---
            
            srt_content = alignment_service.generate_ass_subtitles(word_timestamps)
            srt_path = os.path.join("outputs", f"subs_{int(time.time())}.ass")
            if srt_content:
                with open(srt_path, "w", encoding="utf-8") as f:
                    f.write(srt_content)
                print(f"[VideoProducer] ✅ ASS Subtitles Ready (Absolute Centering).")
            else:
                srt_path = None

            # 6. Compile Video
            print(f"[VideoProducer] Compiling premium video assets with CTA...")
            output_video_name = f"final_reel_{int(time.time())}.mp4"
            
            fragments = [{"sentence": full_vo_text, "audio": voice_path}]
            
            final_video_path = create_reel(
                fragments=fragments,
                image_path=image_path,
                srt_path=srt_path,
                brand=brand,
                output_filename=output_video_name
            )
            
            # 5. Secure Public Link
            print(f"[VideoProducer] Uploading to public server...")
            public_url = uploader.upload_file(final_video_path)
            
            # Final Rich Response with Metadata
            # Simplifed Response (Orchestrator will now join this with the original post text)
            combined_content = (
                f"🎥 *VIDEO HAZIR!* (@{brand})\n\n"
                f"🔗 *Video Linki:* {public_url or '⚠️ Upload hatası'}\n"
                f"💡 [Video Dosyası: {os.path.basename(final_video_path) if final_video_path else 'N/A'}]"
            )
            
            return SwarmMessage(
                sender=self.name,
                content=combined_content,
                data={
                    "video_path": final_video_path,
                    "public_url": public_url,
                    "brand": brand,
                    "title": title,
                    "caption": caption,
                    "tags": tags,
                    "status": "published"
                },
                status="success"
            )

        except Exception as e:
            self.logger.error(f"Video production failed: {e}")
            return SwarmMessage(
                sender=self.name,
                content=f"Video üretimi sırasında hata oluştu: {str(e)}",
                status="error"
            )
