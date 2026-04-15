import os
import requests
import urllib3
from src.core.logging import get_logger

# Disable insecure request warnings for local SSL bypass
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = get_logger("skills.uploader")

class UploaderSkill:
    """Uploads local files to a temporary public URL for third-party access (e.g. Make.com)."""
    
    def __init__(self):
        # Uguu.se is very stable for anonymous uploads
        self.uguu_endpoint = "https://uguu.se/upload.php"
        # Catbox as secondary
        self.catbox_endpoint = "https://catbox.moe/user/api.php"
        # Local fallback
        self.local_base_url = "https://arkmediaflow.com/outputs"

    def upload_file(self, file_path: str) -> str:
        """Provides a public URL for a file. Tries Uguu, then Catbox."""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None

        filename = os.path.basename(file_path)
        
        # Method 1: Uguu.se (Primary - Very stable)
        try:
            logger.info(f"[Uploader] Trying Uguu.se for {filename}...")
            # Note: We use verify=False to handle local SSL issues
            with open(file_path, 'rb') as f:
                response = requests.post(self.uguu_endpoint, files={'files[]': f}, timeout=60, verify=False)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        public_url = data['files'][0]['url']
                        logger.info(f"✅ Uguu Success: {public_url}")
                        return public_url
                    except:
                        if "http" in response.text:
                            public_url = response.text.strip()
                            logger.info(f"✅ Uguu Success (Raw): {public_url}")
                            return public_url
        except Exception as e:
            logger.warning(f"❌ Uguu error: {e}")

        # Method 2: Catbox.moe
        try:
            logger.info(f"[Uploader] Trying Catbox for {filename}...")
            with open(file_path, 'rb') as f:
                data = {'reqtype': 'fileupload'}
                files = {'fileToUpload': f}
                response = requests.post(self.catbox_endpoint, data=data, files=files, timeout=90, verify=False)
                if response.status_code == 200:
                    public_url = response.text.strip()
                    if public_url.startswith("http"):
                        logger.info(f"✅ Catbox Success: {public_url}")
                        return public_url
        except Exception as e:
            logger.warning(f"❌ Catbox error: {e}")

        # Final local fallback
        logger.warning(f"⚠️ All external uploaders failed. Returning local fallback.")
        return f"{self.local_base_url}/{filename}"

uploader = UploaderSkill()
