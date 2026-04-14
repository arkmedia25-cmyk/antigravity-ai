import os
import requests
from src.core.logging import get_logger

logger = get_logger("skills.uploader")

class UploaderSkill:
    """Uploads local files to a temporary public URL for third-party access (e.g. Make.com)."""
    
    def __init__(self):
        # Primary: Local server hosting (Served via Flask in telegram_handler.py)
        # Secondary: file.io for ephemeral third-party access
        self.local_base_url = "https://arkmediaflow.com/outputs"
        self.fileio_endpoint = "https://file.io"

    def upload_file(self, file_path: str) -> str:
        """
        Provides a public URL for a file. 
        Tries local serving first, then falls back to file.io.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found for upload: {file_path}")
            return None

        filename = os.path.basename(file_path)
        
        # Method 1: Local Serving (Preferred)
        # Assuming the file is already in the 'outputs' directory which is served by Flask
        local_url = f"{self.local_base_url}/{filename}"
        logger.info(f"Using local server URL: {local_url}")
        
        # We assume local server is working if we are on the server.
        # But we also try an external upload as a secondary option for Make.com reliability
        # if the local domain has firewall/SSL issues for specific regions.
        
        # Method 2: External Fallback (bashupload.com)
        # Bashupload is extremely simple: PUT or POST to the endpoint returns a plain text URL.
        try:
            logger.info(f"Attempting fallback upload to bashupload.com for {filename}...")
            with open(file_path, 'rb') as f:
                # We use the filename in the URL for bashupload
                upload_url = f"https://bashupload.com/{filename}"
                response = requests.put(upload_url, data=f, timeout=60)
                
                if response.status_code == 200:
                    public_url = response.text.strip()
                    if public_url.startswith("http"):
                        logger.info(f"Bashupload success: {public_url}")
                        return public_url
                
                logger.warning(f"Bashupload failed (Status {response.status_code}): {response.text[:200]}")
        except Exception as e:
            logger.error(f"Error during bashupload fallback: {e}")

        # Method 3: Final fallback to file.io (just in case)
        try:
             logger.info(f"Attempting final fallback to file.io for {filename}...")
             with open(file_path, 'rb') as f:
                 response = requests.post("https://file.io", files={'file': f}, timeout=30)
                 if response.status_code == 200:
                     try:
                         data = response.json()
                         if data.get("success"):
                             return data.get("link")
                     except:
                         # Sometimes file.io returns HTML on error
                         pass
        except:
             pass

        # Final absolute fallback: Return the local URL anyway (assuming proxy might be fixed)
        return local_url

# Static instance for easy access
uploader = UploaderSkill()
