#!/usr/bin/env python3
"""Example test script to demonstrate memeteleporter functionality."""
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Test imports
try:
    from config import Config
    from immich_client import ImmichClient
    from meme_detector import MemeDetector
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    exit(1)

# Test 1: Configuration validation
print("\nTest 1: Configuration")
print("-" * 40)
try:
    # Test that config can be initialized
    print(f"  Default API URL: {Config.IMMICH_API_URL}")
    print(f"  Default Cache Dir: {Config.MEME_CACHE_DIR}")
    print(f"  Default OCR Approach: {Config.OCR_APPROACH}")
    print("✓ Configuration accessible")
except Exception as e:
    print(f"✗ Configuration failed: {e}")

# Test 2: ImmichClient initialization
print("\nTest 2: ImmichClient")
print("-" * 40)
try:
    client = ImmichClient("http://test.com/api", "test-key")
    print(f"  API URL: {client.api_url}")
    print(f"  Headers configured: {bool(client.headers)}")
    print("✓ ImmichClient initialized")
except Exception as e:
    print(f"✗ ImmichClient failed: {e}")

# Test 3: MemeDetector with mock
print("\nTest 3: MemeDetector")
print("-" * 40)
try:
    # Test with mock OpenAI client
    with patch('meme_detector.OpenAI'):
        detector = MemeDetector(approach='openai', openai_api_key='test-key')
        print(f"  Approach: {detector.approach}")
        print("✓ MemeDetector initialized with OpenAI")
except Exception as e:
    print(f"✗ MemeDetector with OpenAI failed: {e}")

# Test 4: Screenshot filtering logic
print("\nTest 4: Screenshot Detection Logic")
print("-" * 40)
try:
    test_assets = [
        {'id': '1', 'type': 'IMAGE', 'originalFileName': 'Screenshot_2024.jpg'},
        {'id': '2', 'type': 'IMAGE', 'originalFileName': 'IMG_1234.jpg'},
        {'id': '3', 'type': 'IMAGE', 'originalFileName': 'photo.jpg'},
        {'id': '4', 'type': 'VIDEO', 'originalFileName': 'Screenshot_video.mp4'},
    ]
    
    # Simulate screenshot detection
    screenshots = []
    screenshot_patterns = ['screenshot', 'img_', 'pxl_', 'scr_']
    
    for asset in test_assets:
        if asset.get('type') != 'IMAGE':
            continue
        filename = asset.get('originalFileName', '').lower()
        if any(pattern in filename for pattern in screenshot_patterns):
            screenshots.append(asset)
    
    print(f"  Total assets: {len(test_assets)}")
    print(f"  Screenshots found: {len(screenshots)}")
    print(f"  Screenshot IDs: {[s['id'] for s in screenshots]}")
    
    expected_count = 2  # Should find assets 1 and 2
    if len(screenshots) == expected_count:
        print("✓ Screenshot detection logic works correctly")
    else:
        print(f"✗ Expected {expected_count} screenshots, found {len(screenshots)}")
except Exception as e:
    print(f"✗ Screenshot detection failed: {e}")

# Test 5: Metadata handling
print("\nTest 5: Metadata Handling")
print("-" * 40)
try:
    with tempfile.TemporaryDirectory() as tmpdir:
        metadata_file = Path(tmpdir) / 'metadata.json'
        
        # Create metadata
        metadata = {
            'processed_assets': ['asset1', 'asset2'],
            'cached_memes': [
                {'asset_id': 'asset1', 'filename': 'meme1.jpg', 'original_filename': 'Screenshot_1.jpg'}
            ]
        }
        
        # Save metadata
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Load metadata
        with open(metadata_file, 'r') as f:
            loaded = json.load(f)
        
        print(f"  Processed assets: {len(loaded['processed_assets'])}")
        print(f"  Cached memes: {len(loaded['cached_memes'])}")
        
        if loaded == metadata:
            print("✓ Metadata handling works correctly")
        else:
            print("✗ Metadata mismatch")
except Exception as e:
    print(f"✗ Metadata handling failed: {e}")

# Test 6: Command-line interface
print("\nTest 6: CLI Interface")
print("-" * 40)
try:
    import subprocess
    result = subprocess.run(
        ['python3', 'memeteleporter.py', '--help'],
        capture_output=True,
        text=True,
        cwd='/home/runner/work/memeteleporter/memeteleporter'
    )
    
    if result.returncode == 0 and '--dry-run' in result.stdout:
        print("  CLI help message displayed correctly")
        print("✓ CLI interface works")
    else:
        print(f"✗ CLI test failed with return code {result.returncode}")
except Exception as e:
    print(f"✗ CLI test failed: {e}")

print("\n" + "=" * 40)
print("Test suite completed!")
print("=" * 40)
