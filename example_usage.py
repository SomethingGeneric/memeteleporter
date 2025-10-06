#!/usr/bin/env python3
"""
Example usage of memeteleporter components.

This demonstrates how to use the memeteleporter modules programmatically
instead of using the command-line interface.
"""

import os
from pathlib import Path
from config import Config
from immich_client import ImmichClient
from meme_detector import MemeDetector

# Example 1: Using ImmichClient directly
def example_immich_client():
    """Example of using ImmichClient to interact with Immich API."""
    print("Example 1: ImmichClient Usage")
    print("-" * 60)
    
    # Initialize client
    client = ImmichClient(
        api_url="http://your-immich-server:2283/api",
        api_key="your-api-key"
    )
    
    # Get all assets
    # assets = client.get_all_assets()
    # print(f"Total assets: {len(assets)}")
    
    # Get screenshots only
    # screenshots = client.get_screenshots()
    # print(f"Screenshots found: {len(screenshots)}")
    
    # Download an asset
    # success = client.download_asset(
    #     asset_id="some-asset-id",
    #     output_path=Path("./downloaded_image.jpg")
    # )
    
    # Delete an asset
    # success = client.delete_asset(asset_id="some-asset-id")
    
    print("ImmichClient methods available:")
    print("  - get_all_assets()")
    print("  - get_screenshots()")
    print("  - download_asset(asset_id, output_path)")
    print("  - delete_asset(asset_id)")
    print()


# Example 2: Using MemeDetector
def example_meme_detector():
    """Example of using MemeDetector for classification."""
    print("Example 2: MemeDetector Usage")
    print("-" * 60)
    
    # Initialize with OpenAI
    # detector = MemeDetector(
    #     approach='openai',
    #     openai_api_key='your-openai-key'
    # )
    
    # Or initialize with Tesseract
    # detector = MemeDetector(approach='tesseract')
    
    # Analyze an image
    # image_path = Path("./screenshot.jpg")
    # is_meme = detector.is_meme(image_path)
    # 
    # if is_meme:
    #     print(f"{image_path.name} is a MEME")
    # else:
    #     print(f"{image_path.name} is a GENUINE SCREENSHOT")
    
    print("MemeDetector methods available:")
    print("  - is_meme(image_path) -> bool")
    print()


# Example 3: Custom workflow
def example_custom_workflow():
    """Example of a custom workflow using the components."""
    print("Example 3: Custom Workflow")
    print("-" * 60)
    
    # This is a simplified version of what memeteleporter.py does
    
    # Step 1: Initialize components
    # Config.validate()  # This would fail without proper .env
    # client = ImmichClient(Config.IMMICH_API_URL, Config.IMMICH_API_KEY)
    # detector = MemeDetector(Config.OCR_APPROACH, Config.OPENAI_API_KEY)
    
    # Step 2: Get screenshots
    # screenshots = client.get_screenshots()
    
    # Step 3: Process each screenshot
    # for screenshot in screenshots:
    #     asset_id = screenshot['id']
    #     filename = screenshot['originalFileName']
    #     
    #     # Download
    #     temp_path = Path(f"/tmp/{filename}")
    #     if not client.download_asset(asset_id, temp_path):
    #         continue
    #     
    #     # Analyze
    #     is_meme = detector.is_meme(temp_path)
    #     
    #     # Take action
    #     if is_meme:
    #         # Cache locally
    #         cache_path = Config.MEME_CACHE_DIR / filename
    #         temp_path.rename(cache_path)
    #         
    #         # Delete from Immich
    #         client.delete_asset(asset_id)
    #     else:
    #         # Keep in Immich, remove temp file
    #         temp_path.unlink()
    
    print("Custom workflow steps:")
    print("  1. Initialize Config, ImmichClient, and MemeDetector")
    print("  2. Retrieve screenshots using client.get_screenshots()")
    print("  3. For each screenshot:")
    print("     a. Download using client.download_asset()")
    print("     b. Analyze using detector.is_meme()")
    print("     c. If meme: cache locally and delete from Immich")
    print("     d. If screenshot: keep in Immich")
    print()


# Example 4: Filtering screenshots by custom criteria
def example_custom_filtering():
    """Example of custom screenshot filtering."""
    print("Example 4: Custom Screenshot Filtering")
    print("-" * 60)
    
    # You can customize the screenshot detection logic
    # For example, add your own patterns or filters
    
    custom_patterns = [
        'screenshot',
        'screen_shot',
        'scrnshot',           # Custom pattern
        'capture',            # Custom pattern
        'snap',               # Custom pattern
    ]
    
    # Or filter by date
    # from datetime import datetime, timedelta
    # cutoff_date = datetime.now() - timedelta(days=30)
    # 
    # recent_screenshots = [
    #     asset for asset in screenshots
    #     if datetime.fromisoformat(asset['createdAt']) > cutoff_date
    # ]
    
    print("Custom filtering examples:")
    print("  - Add custom naming patterns")
    print("  - Filter by date range")
    print("  - Filter by file size")
    print("  - Filter by device type")
    print("  - Filter by album")
    print()


# Example 5: Batch processing with progress tracking
def example_batch_processing():
    """Example of batch processing with progress tracking."""
    print("Example 5: Batch Processing")
    print("-" * 60)
    
    # Process in batches to handle large libraries
    # batch_size = 10
    # 
    # screenshots = client.get_screenshots()
    # total = len(screenshots)
    # 
    # for i in range(0, total, batch_size):
    #     batch = screenshots[i:i+batch_size]
    #     print(f"Processing batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")
    #     
    #     for screenshot in batch:
    #         # Process screenshot
    #         pass
    #     
    #     # Optional: Add delay between batches to avoid rate limits
    #     time.sleep(1)
    
    print("Batch processing considerations:")
    print("  - Process in smaller batches for large libraries")
    print("  - Add delays to avoid API rate limits")
    print("  - Save progress periodically")
    print("  - Handle interruptions gracefully")
    print()


# Example 6: Error handling and retries
def example_error_handling():
    """Example of proper error handling."""
    print("Example 6: Error Handling")
    print("-" * 60)
    
    # import time
    # 
    # max_retries = 3
    # retry_delay = 5
    # 
    # for attempt in range(max_retries):
    #     try:
    #         # Try to download asset
    #         success = client.download_asset(asset_id, output_path)
    #         if success:
    #             break
    #     except Exception as e:
    #         print(f"Attempt {attempt + 1} failed: {e}")
    #         if attempt < max_retries - 1:
    #             time.sleep(retry_delay)
    #         else:
    #             print("Max retries reached, skipping asset")
    
    print("Error handling best practices:")
    print("  - Implement retry logic for network operations")
    print("  - Log errors with context")
    print("  - Continue processing other assets on failure")
    print("  - Track failed operations for later review")
    print()


def main():
    """Run all examples."""
    print("=" * 60)
    print("Memeteleporter Programmatic Usage Examples")
    print("=" * 60)
    print()
    
    example_immich_client()
    example_meme_detector()
    example_custom_workflow()
    example_custom_filtering()
    example_batch_processing()
    example_error_handling()
    
    print("=" * 60)
    print("For actual usage, set up your .env file and uncomment")
    print("the code in the examples above.")
    print("=" * 60)


if __name__ == '__main__':
    main()
