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
            meta_resp = ask_ai(meta_prompt)
            
            title = meta_resp.split("---TITLE---")[-1].split("---CAPTION---")[0].strip() or "Wellness Tip"
            caption = meta_resp.split("---CAPTION---")[-1].split("---TAGS---")[0].strip()
            tags = meta_resp.split("---TAGS---")[-1].strip()

            # 2. Generate Voiceover (using existing TTS skill)
            filename = f"voice_{int(time.time())}.mp3"
            print(f"[VideoProducer] Generating voiceover...")
            voice_path = generate_dutch_audio(input_data, filename)
            
            # 3. Compile Video (using existing video skill)
            print(f"[VideoProducer] Compiling video assets...")
            output_video_name = f"final_reel_{int(time.time())}.mp4"
            final_video_path = create_reel(
                text=input_data,
                audio_path=voice_path,
                brand=brand,
                output_filename=output_video_name
            )
            
            # 4. Secure Public Link
            print(f"[VideoProducer] Uploading to public server...")
            public_url = uploader.upload_file(final_video_path)
            
            return SwarmMessage(
                sender=self.name,
                content=f"🚀 *Video üretimi tamamlandı!* @{brand}\n\n📝 *{title.upper()}*\n\n{caption}\n\n{tags}\n\n📥 İzle: {public_url}",
                data={
                    "video_path": final_video_path,
                    "public_url": public_url,
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
