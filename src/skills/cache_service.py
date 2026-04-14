import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass(frozen=True, slots=True)
class CacheEntry:
    key_hash: str
    content: Any
    metadata: dict

class CacheService:
    """Implementaion of the Content-Hash File Cache Pattern."""
    
    def __init__(self, cache_dir: str = ".cache"):
        # Use a path relative to the project root
        self.project_root = Path(__file__).parent.parent.parent
        self.cache_base = self.project_root / cache_dir
        self.cache_base.mkdir(parents=True, exist_ok=True)

    def _compute_hash(self, content: str) -> str:
        """Computes SHA-256 hash of the content string."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def get(self, key_source: str) -> Optional[Any]:
        """Lookup cache by the hash of the key_source."""
        h = self._compute_hash(key_source)
        cache_file = self.cache_base / f"{h}.json"
        
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Cache hit for hash: {h[:12]}")
                return data.get("content")
        except Exception as e:
            logger.warning(f"Cache read error for {h}: {e}")
            return None

    def set(self, key_source: str, content: Any, metadata: dict = None):
        """Save content to cache using the hash of key_source."""
        h = self._compute_hash(key_source)
        cache_file = self.cache_base / f"{h}.json"
        
        entry = {
            "key_hash": h,
            "content": content,
            "metadata": metadata or {}
        }
        
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(entry, f, ensure_ascii=False, indent=2)
            logger.info(f"Cache write successful: {h[:12]}")
        except Exception as e:
            logger.error(f"Cache write error: {e}")

# Global instance
cache_service = CacheService()
