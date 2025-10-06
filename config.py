"""Configuration management for memeteleporter."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for memeteleporter."""
    
    # Immich API Configuration
    IMMICH_API_URL = os.getenv('IMMICH_API_URL', 'http://localhost:2283/api')
    IMMICH_API_KEY = os.getenv('IMMICH_API_KEY', '')
    
    # OpenAI API Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Local cache directory
    MEME_CACHE_DIR = Path(os.getenv('MEME_CACHE_DIR', './meme_cache'))
    
    # OCR approach: "tesseract" or "openai"
    OCR_APPROACH = os.getenv('OCR_APPROACH', 'openai')
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.IMMICH_API_KEY:
            raise ValueError("IMMICH_API_KEY is required")
        
        if cls.OCR_APPROACH == 'openai' and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI approach")
        
        # Create cache directory if it doesn't exist
        cls.MEME_CACHE_DIR.mkdir(parents=True, exist_ok=True)
