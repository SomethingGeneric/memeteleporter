"""Immich API client for interacting with Immich server."""
import requests
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ImmichClient:
    """Client for interacting with Immich API."""
    
    def __init__(self, api_url: str, api_key: str):
        """Initialize Immich client.
        
        Args:
            api_url: Base URL of Immich API
            api_key: API key for authentication
        """
        self.api_url = api_url.rstrip('/')
        self.headers = {
            'x-api-key': api_key,
            'Accept': 'application/json'
        }
    
    def get_all_assets(self) -> List[Dict]:
        """Retrieve all assets from Immich.
        
        Returns:
            List of asset dictionaries
        """
        try:
            response = requests.get(
                f"{self.api_url}/assets",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve assets: {e}")
            return []
    
    def get_screenshots(self) -> List[Dict]:
        """Filter and retrieve assets that are likely screenshots.
        
        Returns:
            List of screenshot asset dictionaries
        """
        all_assets = self.get_all_assets()
        screenshots = []
        
        for asset in all_assets:
            # Check if asset type is image
            if asset.get('type') != 'IMAGE':
                continue
            
            # Check various indicators that suggest a screenshot
            original_path = asset.get('originalPath', '').lower()
            original_filename = asset.get('originalFileName', '').lower()
            
            # Common screenshot patterns
            screenshot_patterns = [
                'screenshot',
                'screen_shot',
                'screen shot',
                'img_',
                'pxl_',
                'scr_'
            ]
            
            is_screenshot = any(
                pattern in original_path or pattern in original_filename
                for pattern in screenshot_patterns
            )
            
            if is_screenshot:
                screenshots.append(asset)
        
        logger.info(f"Found {len(screenshots)} potential screenshots out of {len(all_assets)} assets")
        return screenshots
    
    def download_asset(self, asset_id: str, output_path: Path) -> bool:
        """Download an asset from Immich.
        
        Args:
            asset_id: ID of the asset to download
            output_path: Path where to save the asset
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(
                f"{self.api_url}/assets/{asset_id}/original",
                headers=self.headers,
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded asset {asset_id} to {output_path}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download asset {asset_id}: {e}")
            return False
    
    def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset from Immich.
        
        Args:
            asset_id: ID of the asset to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.api_url}/assets",
                headers=self.headers,
                json={'ids': [asset_id]},
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"Deleted asset {asset_id} from Immich")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete asset {asset_id}: {e}")
            return False
