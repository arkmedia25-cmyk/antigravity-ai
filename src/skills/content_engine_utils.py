import logging

logger = logging.getLogger(__name__)

class ContentEngine:
    """Implementaion of platform-native content rules from Content Engine skill."""
    
    PLATFORM_GUIDANCE = {
        "tiktok": """
### TikTok / Short Video Rules:
- The first 3 seconds must interrupt attention (STRONG HOOK).
- Script around visuals, not just narration.
- One demo, one claim, one CTA.
- Tone: Energetic, direct, and immersive.""",
        
        "instagram": """
### Instagram Reels Rules:
- Strong hook in the first 4 seconds.
- High-quality visual storytelling.
- Use specifics over slogans.
- CTA: Clear and small (e.g., 'Save this for tonight').""",
        
        "linkedin": """
### LinkedIn Rules:
- Strong first line.
- Short paragraphs.
- Explicit framing around lessons, results, and takeaways."""
    }

    @staticmethod
    def get_platform_prompt(platform: str) -> str:
        """Returns the platform-specific guidance prompt."""
        return ContentEngine.PLATFORM_GUIDANCE.get(platform.lower(), "")

    @staticmethod
    def inject_rules(prompt: str, platform: str) -> str:
        """Injects platform-native rules into a content generation prompt."""
        rules = ContentEngine.get_platform_prompt(platform)
        if not rules:
            return prompt
            
        return f"{prompt}\n\n{rules}\n\nCRITICAL: Follow these platform rules strictly."

# Global instance
content_engine = ContentEngine()
