import os
import logging
import videodb
from typing import Optional, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class VideoService:
    """Implementaion of the VideoDB skill for Agency Swarm OS."""
    
    def __init__(self):
        # Load .env to ensure VIDEO_DB_API_KEY is available
        load_dotenv()
        self.api_key = os.getenv("VIDEO_DB_API_KEY")
        self._conn = None
        self._coll = None

    def _get_connection(self):
        if not self.api_key:
            logger.error("VIDEO_DB_API_KEY is missing! VideoDB functions will fail.")
            raise ValueError("VIDEO_DB_API_KEY is missing from .env")
            
        if self._conn is None:
            try:
                self._conn = videodb.connect()
                self._coll = self._conn.get_collection()
                logger.info("Successfully connected to VideoDB.")
            except Exception as e:
                logger.error(f"Failed to connect to VideoDB: {e}")
                raise
        return self._conn, self._coll

    def upload_video(self, file_path: str) -> Optional[Any]:
        """Uploads a local file to VideoDB."""
        _, coll = self._get_connection()
        try:
            video = coll.upload(file_path=file_path)
            logger.info(f"Video uploaded successfully. ID: {video.id}")
            return video
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return None

    def reframe_to_vertical(self, video_id: str, start: int = 0, end: int = 60) -> Optional[str]:
        """Uses VideoDB Smart Reframe to convert video to 9:16 for Reels."""
        _, coll = self._get_connection()
        try:
            video = coll.get_video(video_id)
            # Smart reframe is a high-level AI operation
            reframed_video = video.reframe(
                start=start, 
                end=end, 
                target="vertical"
            )
            # Returns a stream URL
            return reframed_video.stream_url
        except Exception as e:
            logger.error(f"Reframe failed: {e}")
            return None

    def add_subtitles(self, video_id: str) -> Optional[str]:
        """Automated transcription and subtitle burning via VideoDB."""
        _, coll = self._get_connection()
        try:
            video = coll.get_video(video_id)
            video.index_spoken_words(force=True)
            stream_url = video.add_subtitle()
            return stream_url
        except Exception as e:
            logger.error(f"Subtitle generation failed: {e}")
            return None

# Global instance
video_service = VideoService()
