#!/usr/bin/env python3
"""Main script for memeteleporter - separates memes from genuine screenshots."""
import logging
import sys
from pathlib import Path
from typing import List, Dict
import json

from config import Config
from immich_client import ImmichClient
from meme_detector import MemeDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MemeTeleporter:
    """Main class for the memeteleporter application."""
    
    def __init__(self):
        """Initialize the memeteleporter."""
        # Validate configuration
        Config.validate()
        
        # Initialize clients
        self.immich_client = ImmichClient(Config.IMMICH_API_URL, Config.IMMICH_API_KEY)
        self.meme_detector = MemeDetector(
            approach=Config.OCR_APPROACH,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        # Create cache directory
        self.cache_dir = Config.MEME_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create metadata file path
        self.metadata_file = self.cache_dir / 'metadata.json'
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load metadata from cache directory.
        
        Returns:
            Metadata dictionary
        """
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}")
        return {'processed_assets': [], 'cached_memes': []}
    
    def _save_metadata(self):
        """Save metadata to cache directory."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def process_screenshots(self, dry_run: bool = False) -> Dict[str, int]:
        """Process all screenshots from Immich.
        
        Args:
            dry_run: If True, don't delete from Immich, just report what would be done
            
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_screenshots': 0,
            'memes_found': 0,
            'memes_cached': 0,
            'memes_deleted': 0,
            'genuine_screenshots': 0,
            'errors': 0
        }
        
        logger.info("Retrieving screenshots from Immich...")
        screenshots = self.immich_client.get_screenshots()
        stats['total_screenshots'] = len(screenshots)
        
        if not screenshots:
            logger.info("No screenshots found.")
            return stats
        
        logger.info(f"Processing {len(screenshots)} screenshots...")
        
        for i, asset in enumerate(screenshots, 1):
            asset_id = asset.get('id')
            filename = asset.get('originalFileName', f'asset_{asset_id}')
            
            # Skip if already processed
            if asset_id in self.metadata['processed_assets']:
                logger.debug(f"Skipping already processed asset: {asset_id}")
                continue
            
            logger.info(f"[{i}/{len(screenshots)}] Processing {filename}...")
            
            # Download asset temporarily
            temp_path = self.cache_dir / f'temp_{filename}'
            
            try:
                if not self.immich_client.download_asset(asset_id, temp_path):
                    logger.error(f"Failed to download asset {asset_id}")
                    stats['errors'] += 1
                    continue
                
                # Detect if it's a meme
                is_meme = self.meme_detector.is_meme(temp_path)
                
                if is_meme:
                    stats['memes_found'] += 1
                    logger.info(f"✓ Detected as MEME: {filename}")
                    
                    # Move to permanent cache location
                    cache_path = self.cache_dir / filename
                    counter = 1
                    while cache_path.exists():
                        stem = Path(filename).stem
                        suffix = Path(filename).suffix
                        cache_path = self.cache_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    temp_path.rename(cache_path)
                    stats['memes_cached'] += 1
                    
                    # Add to metadata
                    self.metadata['cached_memes'].append({
                        'asset_id': asset_id,
                        'filename': cache_path.name,
                        'original_filename': filename
                    })
                    
                    # Delete from Immich
                    if not dry_run:
                        if self.immich_client.delete_asset(asset_id):
                            stats['memes_deleted'] += 1
                            logger.info(f"  Deleted from Immich: {asset_id}")
                        else:
                            logger.error(f"  Failed to delete from Immich: {asset_id}")
                            stats['errors'] += 1
                    else:
                        logger.info(f"  [DRY RUN] Would delete from Immich: {asset_id}")
                else:
                    stats['genuine_screenshots'] += 1
                    logger.info(f"✓ Detected as GENUINE SCREENSHOT: {filename}")
                    # Remove temporary file
                    if temp_path.exists():
                        temp_path.unlink()
                
                # Mark as processed
                self.metadata['processed_assets'].append(asset_id)
                self._save_metadata()
                
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
                stats['errors'] += 1
                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()
        
        return stats
    
    def run(self, dry_run: bool = False):
        """Run the memeteleporter.
        
        Args:
            dry_run: If True, don't delete from Immich
        """
        logger.info("=" * 60)
        logger.info("Meme Teleporter Starting")
        logger.info(f"Cache directory: {self.cache_dir}")
        logger.info(f"Detection approach: {Config.OCR_APPROACH}")
        logger.info(f"Dry run mode: {dry_run}")
        logger.info("=" * 60)
        
        stats = self.process_screenshots(dry_run=dry_run)
        
        logger.info("=" * 60)
        logger.info("Meme Teleporter Complete")
        logger.info(f"Total screenshots processed: {stats['total_screenshots']}")
        logger.info(f"Memes found: {stats['memes_found']}")
        logger.info(f"Memes cached: {stats['memes_cached']}")
        logger.info(f"Memes deleted from Immich: {stats['memes_deleted']}")
        logger.info(f"Genuine screenshots kept: {stats['genuine_screenshots']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info("=" * 60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Meme Teleporter - Separate memes from genuine screenshots in Immich'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without deleting from Immich (just cache locally)'
    )
    
    args = parser.parse_args()
    
    try:
        teleporter = MemeTeleporter()
        teleporter.run(dry_run=args.dry_run)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
