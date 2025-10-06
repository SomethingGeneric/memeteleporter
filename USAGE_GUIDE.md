# Memeteleporter Usage Guide

This guide provides detailed instructions on how to use memeteleporter to organize your Immich photo library.

## Quick Start

### 1. Initial Setup

```bash
# Clone the repository
git clone https://github.com/SomethingGeneric/memeteleporter.git
cd memeteleporter

# Install dependencies
pip install -r requirements.txt

# Copy configuration template
cp .env.example .env

# Edit configuration with your credentials
nano .env  # or use your preferred editor
```

### 2. Configure Your API Keys

Edit `.env` and add:

```bash
# Required: Your Immich server URL and API key
IMMICH_API_URL=http://your-immich-server.com:2283/api
IMMICH_API_KEY=your-immich-api-key

# Required if using OpenAI (recommended)
OPENAI_API_KEY=sk-your-openai-key

# Optional: Change cache directory
MEME_CACHE_DIR=./meme_cache

# Optional: Change detection method
OCR_APPROACH=openai  # or "tesseract"
```

### 3. Test Run (Dry Run)

**Always start with a dry run** to see what would happen without making any changes:

```bash
python memeteleporter.py --dry-run
```

This will:
- Connect to your Immich server
- Find all screenshots
- Analyze each one
- Cache detected memes locally
- Show what would be deleted (but won't actually delete)

### 4. Review Results

Check the `meme_cache` directory to see what was classified as memes:

```bash
ls -lh meme_cache/
cat meme_cache/metadata.json
```

### 5. Run for Real

Once you're satisfied with the dry run results:

```bash
python memeteleporter.py
```

This will:
- Process all screenshots
- Cache memes locally
- **Delete memes from Immich**

## Detection Approaches

### OpenAI Vision (Recommended)

**Best for:** Accurate detection, varied content

**Pros:**
- High accuracy understanding visual context
- Distinguishes subtle differences
- Handles various meme formats

**Cons:**
- Requires API key and credits (~$0.001 per image with gpt-4o-mini)
- Needs internet connection

**Configuration:**
```bash
OCR_APPROACH=openai
OPENAI_API_KEY=sk-your-key
```

### Tesseract OCR

**Best for:** Privacy, offline use, budget constraints

**Pros:**
- Free and open source
- Works offline
- No API required

**Cons:**
- Lower accuracy
- Text-based heuristics only
- May miss visual-only memes

**Configuration:**
```bash
OCR_APPROACH=tesseract
```

**Installation:**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

## Understanding the Output

### During Execution

```
2024-10-06 10:30:15 - __main__ - INFO - ============================================================
2024-10-06 10:30:15 - __main__ - INFO - Meme Teleporter Starting
2024-10-06 10:30:15 - __main__ - INFO - Cache directory: meme_cache
2024-10-06 10:30:15 - __main__ - INFO - Detection approach: openai
2024-10-06 10:30:15 - __main__ - INFO - Dry run mode: True
2024-10-06 10:30:15 - __main__ - INFO - ============================================================
2024-10-06 10:30:16 - immich_client - INFO - Found 45 potential screenshots out of 1523 assets
2024-10-06 10:30:16 - __main__ - INFO - Processing 45 screenshots...
2024-10-06 10:30:17 - [1/45] Processing Screenshot_20240101_123456.jpg...
2024-10-06 10:30:18 - meme_detector - INFO - OpenAI analysis: MEME -> MEME
2024-10-06 10:30:18 - __main__ - INFO - ✓ Detected as MEME: Screenshot_20240101_123456.jpg
2024-10-06 10:30:18 - __main__ - INFO -   [DRY RUN] Would delete from Immich: asset-123
```

### Final Statistics

```
============================================================
Meme Teleporter Complete
Total screenshots processed: 45
Memes found: 23
Memes cached: 23
Memes deleted from Immich: 0  (dry run)
Genuine screenshots kept: 22
Errors: 0
============================================================
```

## File Organization

### Cache Directory Structure

```
meme_cache/
├── metadata.json                    # Tracking data
├── Screenshot_20240101_123456.jpg   # Cached meme
├── Screenshot_20240105_234567.jpg   # Cached meme
└── IMG_20240110_345678.jpg         # Cached meme
```

### Metadata File

```json
{
  "processed_assets": [
    "asset-id-1",
    "asset-id-2",
    "asset-id-3"
  ],
  "cached_memes": [
    {
      "asset_id": "asset-id-1",
      "filename": "Screenshot_20240101_123456.jpg",
      "original_filename": "Screenshot_20240101_123456.jpg"
    }
  ]
}
```

## Advanced Usage

### Processing Specific Batches

Since the script tracks processed assets, you can run it multiple times safely:

```bash
# First run - processes all screenshots
python memeteleporter.py --dry-run

# Second run - only processes new screenshots
python memeteleporter.py --dry-run
```

### Reprocessing Everything

To reprocess all assets (ignoring metadata):

```bash
# Delete metadata file
rm meme_cache/metadata.json

# Run again
python memeteleporter.py --dry-run
```

### Migrating Cached Memes

After caching memes, you can move them elsewhere:

```bash
# Copy to external storage
cp -r meme_cache /mnt/external/memes/

# Or upload to cloud
rclone copy meme_cache remote:memes/

# Or move to another Immich album (manual process via Immich UI)
```

## Troubleshooting

### No Screenshots Found

If the script reports 0 screenshots:

1. Check your screenshot naming patterns
2. Modify `immich_client.py` to match your pattern:

```python
screenshot_patterns = [
    'screenshot',
    'screen_shot',
    'scrnshot',  # Add custom patterns
    'your_pattern',
]
```

### False Positives/Negatives

If classifications are incorrect:

**For OpenAI approach:**
- The model is generally accurate but not perfect
- Review the `meme_cache` directory after dry run
- Consider tweaking the prompt in `meme_detector.py`

**For Tesseract approach:**
- Add more patterns to improve detection
- Adjust word count thresholds
- Consider switching to OpenAI for better accuracy

### API Rate Limits

If you hit OpenAI rate limits:

```bash
# Process in smaller batches by temporarily moving assets
# Or add delays in the code
```

### Connection Issues

If you can't connect to Immich:

1. Verify server is running: `curl http://your-server:2283/api/server-info`
2. Check API key is valid
3. Ensure firewall allows connections
4. Try accessing Immich web UI to confirm server status

## Best Practices

### 1. Always Start with Dry Run
```bash
python memeteleporter.py --dry-run
```

### 2. Review Before Deleting
```bash
# Check what was found
ls -lh meme_cache/
cat meme_cache/metadata.json | jq '.cached_memes | length'
```

### 3. Backup First
```bash
# Back up your Immich database before first real run
# Follow Immich backup procedures
```

### 4. Process in Stages
```bash
# Test on a small set first
# Then process your full library
```

### 5. Keep Metadata
```bash
# Don't delete metadata.json
# It prevents reprocessing and tracks what was done
```

## Integration Ideas

### Automatic Scheduled Runs

Create a cron job to run daily:

```bash
# Edit crontab
crontab -e

# Add line to run at 2 AM daily
0 2 * * * cd /path/to/memeteleporter && /usr/bin/python3 memeteleporter.py >> /var/log/memeteleporter.log 2>&1
```

### Notification on Completion

Add notification to your script:

```bash
#!/bin/bash
cd /path/to/memeteleporter
python3 memeteleporter.py
if [ $? -eq 0 ]; then
    notify-send "Memeteleporter" "Processing complete!"
    # Or send email, Slack message, etc.
fi
```

### Cloud Sync

Automatically sync cached memes to cloud:

```bash
#!/bin/bash
cd /path/to/memeteleporter
python3 memeteleporter.py

# Sync to cloud after processing
rclone sync meme_cache remote:memes/
```

## FAQ

**Q: Will this delete my genuine screenshots?**
A: The detection is designed to be conservative. When uncertain, images are kept as screenshots. Always use --dry-run first.

**Q: Can I undo deletions?**
A: Immich has a trash feature. Check your Immich trash bin if you need to recover something.

**Q: How much does OpenAI cost?**
A: With gpt-4o-mini, it's approximately $0.001 per image. 1000 images ≈ $1.

**Q: Can I use local AI models?**
A: Not yet, but this is planned for future versions. You can use Tesseract for now.

**Q: Does this work with other photo managers?**
A: Currently only Immich is supported. Other platforms could be added.

**Q: What if I want to review each decision?**
A: Use --dry-run, review the cache, and manually curate. Future versions may add interactive mode.

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section above

## Next Steps

After successfully running memeteleporter:

1. Review your cached memes
2. Decide on permanent storage location
3. Set up automatic scheduling if desired
4. Customize detection patterns for your needs
5. Share feedback to improve the tool
