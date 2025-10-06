"""Meme detection using OCR and AI analysis."""
import logging
from pathlib import Path
from typing import Optional
import base64

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class MemeDetector:
    """Detector to distinguish memes from genuine screenshots."""
    
    def __init__(self, approach: str = 'openai', openai_api_key: Optional[str] = None):
        """Initialize meme detector.
        
        Args:
            approach: Detection approach ('tesseract' or 'openai')
            openai_api_key: OpenAI API key (required if approach is 'openai')
        """
        self.approach = approach.lower()
        
        if self.approach == 'openai':
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI library not available. Install with: pip install openai")
            if not openai_api_key:
                raise ValueError("OpenAI API key is required for 'openai' approach")
            self.openai_client = OpenAI(api_key=openai_api_key)
        elif self.approach == 'tesseract':
            if not TESSERACT_AVAILABLE:
                raise ImportError("Tesseract not available. Install with: pip install pytesseract Pillow")
        else:
            raise ValueError(f"Unknown approach: {approach}. Use 'tesseract' or 'openai'")
    
    def is_meme(self, image_path: Path) -> bool:
        """Determine if an image is a meme or a genuine screenshot.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if the image is a meme, False if it's a genuine screenshot
        """
        if self.approach == 'openai':
            return self._is_meme_openai(image_path)
        elif self.approach == 'tesseract':
            return self._is_meme_tesseract(image_path)
        return False
    
    def _is_meme_openai(self, image_path: Path) -> bool:
        """Use OpenAI Vision API to detect memes.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if the image is a meme, False otherwise
        """
        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Determine image type
            suffix = image_path.suffix.lower()
            mime_type = 'image/jpeg' if suffix in ['.jpg', '.jpeg'] else f'image/{suffix[1:]}'
            
            # Create vision API request
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this image and determine if it's a meme or a genuine screenshot of an app/email/website.

A MEME typically has:
- Humorous or ironic text overlays
- Popular meme formats or templates
- Social media posts with jokes or commentary
- Funny or satirical content meant to be shared
- Image macros with text at top and bottom

A GENUINE SCREENSHOT typically shows:
- App interfaces (settings, conversations, forms)
- Email clients with actual correspondence
- Website content for reference
- Error messages or technical information
- Banking, shopping, or productivity apps

Respond with ONLY "MEME" or "SCREENSHOT" (one word)."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().upper()
            is_meme = 'MEME' in result
            
            logger.info(f"OpenAI analysis for {image_path.name}: {result} -> {'MEME' if is_meme else 'SCREENSHOT'}")
            return is_meme
            
        except Exception as e:
            logger.error(f"Failed to analyze image with OpenAI: {e}")
            # Default to not deleting if we can't determine
            return False
    
    def _is_meme_tesseract(self, image_path: Path) -> bool:
        """Use Tesseract OCR to detect memes based on text patterns.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if the image is a meme, False otherwise
        """
        try:
            # Open image and extract text
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image).lower()
            
            # Heuristics for meme detection
            # Memes often have short, punchy text with meme-specific language
            meme_indicators = [
                'nobody:',
                'me:',
                'when you',
                'pov:',
                'imagine',
                'be like',
                'tfw',
                'mfw',
                'literally',
                'y tho',
                'smh',
                'bruh'
            ]
            
            # Check for meme indicators
            has_meme_language = any(indicator in text for indicator in meme_indicators)
            
            # Memes tend to have less structured text than app screenshots
            # Count lines and words
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            word_count = len(text.split())
            
            # Heuristic: Memes usually have fewer, shorter text blocks
            # App screenshots have more structured, longer text
            is_short_text = word_count < 100 and len(lines) < 10
            
            is_meme = has_meme_language or (is_short_text and word_count > 5)
            
            logger.info(f"Tesseract analysis for {image_path.name}: words={word_count}, lines={len(lines)}, meme_lang={has_meme_language} -> {'MEME' if is_meme else 'SCREENSHOT'}")
            return is_meme
            
        except Exception as e:
            logger.error(f"Failed to analyze image with Tesseract: {e}")
            # Default to not deleting if we can't determine
            return False
