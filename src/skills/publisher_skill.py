import os
import time
import requests
from src.config.settings import settings

class PublisherSkill:
    """
    Handles autonomous publishing of media to social platforms.
    Current focus: Instagram Reels (via Meta Graph API).
    """

    @staticmethod
    def publish_to_instagram(video_url: str, caption: str) -> dict:
        """
        Publishes a Video to Instagram Reels.
        Note: video_url must be a public URL (Dropbox/S3).
        """
        biz_id = settings.INSTAGRAM_BUSINESS_ID
        token = settings.INSTAGRAM_ACCESS_TOKEN

        if not biz_id or not token:
            return {"success": False, "error": "Instagram Credentials missing in .env"}

        try:
            # 1. Create Media Container
            url = f"https://graph.facebook.com/v19.0/{biz_id}/media"
            payload = {
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "access_token": token
            }
            res = requests.post(url, data=payload).json()
            
            if "id" not in res:
                return {"success": False, "error": f"Container Creation Failed: {res}"}
            
            container_id = res["id"]
            print(f"[Publisher] Container Created: {container_id}. Waiting for processing...")

            # 2. Poll for status (Wait max 2 mins)
            status_url = f"https://graph.facebook.com/v19.0/{container_id}"
            params = {"fields": "status_code", "access_token": token}
            
            for _ in range(12): # 12 * 10s = 120s
                time.sleep(10)
                status_res = requests.get(status_url, params=params).json()
                status = status_res.get("status_code")
                print(f"[Publisher] Processing Status: {status}")
                if status == "FINISHED":
                    break
                if status == "ERROR":
                    return {"success": False, "error": "Meta Processing Error"}
            else:
                return {"success": False, "error": "Timeout waiting for Meta to process video"}

            # 3. Publish Container
            publish_url = f"https://graph.facebook.com/v19.0/{biz_id}/media_publish"
            publish_payload = {
                "creation_id": container_id,
                "access_token": token
            }
            final_res = requests.post(publish_url, data=publish_payload).json()

            if "id" in final_res:
                return {"success": True, "id": final_res["id"]}
            return {"success": False, "error": f"Publishing Failed: {final_res}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def publish_to_tiktok(video_url: str, caption: str) -> dict:
        """
        Placeholder for TikTok Content Posting API.
        Requires TikTok for Developers App approval.
        """
        return {"success": False, "error": "TikTok Integration is under development."}

publisher_skill = PublisherSkill()
