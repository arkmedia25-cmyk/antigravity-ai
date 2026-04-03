import os
import requests
from src.core.logging import get_logger

logger = get_logger("skills.uploader")

class UploaderSkill:
    """Uploads local files to a temporary public URL for third-party access (e.g. Make.com)."""
    
    def __init__(self):
        # We'll use catbox.moe for temporary hosting (Reliable and easy API)
        self.endpoint = "https://catbox.moe/user/api.php"

    def upload_file(self, file_path: str) -> str:
        """Uploads a file and returns its public URL. Supports .mp4, .png, .jpg."""
        if not os.path.exists(file_path):
            logger.error(f"File not found for upload: {file_path}")
            return None

        logger.info(f"Uploading file: {file_path} to public host...")
        
        try:
            with open(file_path, 'rb') as f:
                # Catbox API requires 'reqtype' and 'fileToUpload'
                files = {'fileToUpload': (os.path.basename(file_path), f)}
                data = {'reqtype': 'fileupload'}
                
                response = requests.post(self.endpoint, data=data, files=files, timeout=60)
                
                if response.status_code == 200:
                    public_url = response.text.strip()
                    logger.info(f"File successfully uploaded: {public_url}")
                    return public_url
                else:
                    logger.error(f"Upload failed (Status {response.status_code}): {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Critical error during file upload: {e}")
            return None

# Static instance for easy access
uploader = UploaderSkill()
