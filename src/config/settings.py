import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    MEMORY_DB_PATH: str = os.getenv("MEMORY_DB_PATH", "")
    CANVA_CLIENT_ID: str = os.getenv("CANVA_CLIENT_ID", "")
    CANVA_CLIENT_SECRET: str = os.getenv("CANVA_CLIENT_SECRET", "")
    CANVA_REDIRECT_URI: str = os.getenv("CANVA_REDIRECT_URI", "")
    CANVA_TEMPLATE_INSTAGRAM: str = os.getenv("CANVA_TEMPLATE_INSTAGRAM", "EAF9zZ6X6kM")
    
    # Social Media Publisher Credentials
    INSTAGRAM_BUSINESS_ID: str = os.getenv("INSTAGRAM_BUSINESS_ID", "")
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    TIKTOK_ACCESS_TOKEN: str = os.getenv("TIKTOK_ACCESS_TOKEN", "")
    TIKTOK_OPEN_ID: str = os.getenv("TIKTOK_OPEN_ID", "")

    @classmethod
    def validate(cls) -> None:
        """Raise ValueError if any required env var is missing."""
        required = ["ANTHROPIC_API_KEY", "TELEGRAM_TOKEN"]
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Set them in .env or Railway environment settings."
            )


settings = Settings()
