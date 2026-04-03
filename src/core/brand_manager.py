import os
import json
from src.core.logging import get_logger

logger = get_logger("core.brand_manager")

class BrandManager:
    """Manages brand identities and configurations."""
    
    def __init__(self, brands_dir="brands"):
        self.brands_dir = brands_dir
        self.brands = {}
        self.load_all_brands()

    def load_all_brands(self):
        """Loads all brand identity.json files from the brands directory."""
        if not os.path.exists(self.brands_dir):
            os.makedirs(self.brands_dir)
            return

        for brand_name in os.listdir(self.brands_dir):
            brand_path = os.path.join(self.brands_dir, brand_name)
            if os.path.isdir(brand_path):
                identity_file = os.path.join(brand_path, "identity.json")
                if os.path.exists(identity_file):
                    try:
                        with open(identity_file, "r", encoding="utf-8") as f:
                            self.brands[brand_name] = json.load(f)
                            logger.info(f"Loaded brand: {brand_name}")
                    except Exception as e:
                        logger.error(f"Failed to load brand {brand_name}: {e}")

    def get_brand(self, brand_name):
        """Returns the identity configuration for a specific brand."""
        # Clean '@' prefix if present
        name = brand_name.lower().replace("@", "")
        return self.brands.get(name)

    def list_brands(self):
        """Returns a list of all loaded brand names."""
        return list(self.brands.keys())

    def get_theme_for_video(self, brand_name):
        """Converts brand identity into a theme format used by video_skill."""
        brand_config = self.get_brand(brand_name)
        if not brand_config:
            return None
        
        vis = brand_config.get("visuals", {})
        colors = vis.get("colors", {})
        
        # Convert hex to RGB tuples for PIL
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        return {
            "bg": hex_to_rgb(colors.get("background", "#FFFFFF")),
            "accent": hex_to_rgb(colors.get("primary", "#000000")),
            "accent2": hex_to_rgb(colors.get("secondary", "#CCCCCC")),
            "text": hex_to_rgb(colors.get("text", "#000000")),
            "glass": (255, 255, 255, 215), # Standard premium glass
            "font_title": vis.get("fonts", {}).get("title", "title"),
            "font_body": vis.get("fonts", {}).get("body", "body"),
            "brand_name": brand_config.get("brand_name", brand_name),
            "watermark": vis.get("watermark", "✨")
        }
