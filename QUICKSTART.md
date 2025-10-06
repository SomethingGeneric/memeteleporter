# Memeteleporter Quick Start

Get started with memeteleporter in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Immich server with API access
- OpenAI API key (recommended) OR Tesseract OCR installed

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/SomethingGeneric/memeteleporter.git
cd memeteleporter

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Install Tesseract if not using OpenAI
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract
```

## Configuration

```bash
# 1. Copy the example configuration
cp .env.example .env

# 2. Edit .env with your settings
nano .env
```

**Minimum required settings:**
```bash
IMMICH_API_URL=http://your-immich-server:2283/api
IMMICH_API_KEY=your-immich-api-key-here
OPENAI_API_KEY=your-openai-key-here  # If using OpenAI
```

### Getting Your API Keys

**Immich API Key:**
1. Open your Immich web interface
2. Click your profile → Account Settings
3. Navigate to "API Keys"
4. Click "New API Key"
5. Copy the key to your `.env` file

**OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key to your `.env` file

## Usage

### First Run (Dry-Run Mode)

**Always test first without making changes:**

```bash
python memeteleporter.py --dry-run
```

This will:
- ✅ Connect to Immich
- ✅ Find screenshots
- ✅ Analyze each one
- ✅ Cache memes locally
- ✅ Show what would be deleted
- ❌ NOT delete anything from Immich

### Review Results

```bash
# Check what was classified as memes
ls -lh meme_cache/

# View metadata
cat meme_cache/metadata.json
```

### Run For Real

Once you're satisfied with the dry-run:

```bash
python memeteleporter.py
```

This will cache memes and delete them from Immich.

## What It Does

```
1. Finds screenshots in Immich
   └─ Looks for: Screenshot_*, IMG_*, PXL_*, etc.

2. Downloads each screenshot

3. Analyzes with AI/OCR
   ├─ MEME → Cache locally & delete from Immich
   └─ SCREENSHOT → Keep in Immich

4. Reports statistics
```

## Output Example

```
============================================================
Meme Teleporter Starting
Cache directory: meme_cache
Detection approach: openai
Dry run mode: True
============================================================
Found 45 potential screenshots out of 1523 assets
Processing 45 screenshots...
[1/45] Processing Screenshot_20240101.jpg...
✓ Detected as MEME: Screenshot_20240101.jpg
  [DRY RUN] Would delete from Immich: asset-123
[2/45] Processing Screenshot_20240102.jpg...
✓ Detected as GENUINE SCREENSHOT: Screenshot_20240102.jpg
...
============================================================
Meme Teleporter Complete
Total screenshots processed: 45
Memes found: 23
Memes cached: 23
Memes deleted from Immich: 0
Genuine screenshots kept: 22
Errors: 0
============================================================
```

## Configuration Options

### Use OpenAI (Recommended)

```bash
OCR_APPROACH=openai
OPENAI_API_KEY=sk-your-key
```

**Pros:** More accurate, understands context
**Cons:** Small cost (~$0.001 per image)

### Use Tesseract (Free)

```bash
OCR_APPROACH=tesseract
```

**Pros:** Free, runs locally, privacy-focused
**Cons:** Less accurate, text-only analysis

### Change Cache Directory

```bash
MEME_CACHE_DIR=/path/to/your/meme/folder
```

## Troubleshooting

### "IMMICH_API_KEY is required"
➜ Create `.env` file from `.env.example` and add your API key

### "Failed to retrieve assets"
➜ Check your Immich server URL and API key
➜ Make sure server is running: `curl http://your-server:2283/api/server-info`

### "OpenAI API error"
➜ Verify your API key is correct
➜ Check you have API credits
➜ Or switch to Tesseract: `OCR_APPROACH=tesseract`

### No screenshots found
➜ Check if you have screenshots in Immich
➜ They should be named like: Screenshot_*, IMG_*, PXL_*

## Next Steps

- 📖 Read [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed instructions
- 🔧 Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for technical details
- 💻 Check [example_usage.py](example_usage.py) for programmatic usage
- ✅ Run [test_example.py](test_example.py) to verify installation

## Safety Tips

✅ **Always start with --dry-run**
✅ **Review the meme_cache directory before deleting**
✅ **Back up your Immich database** (optional but recommended)
✅ **Check Immich trash** if you need to recover something

## Quick Reference

```bash
# Test without changes
python memeteleporter.py --dry-run

# Run for real
python memeteleporter.py

# Get help
python memeteleporter.py --help

# Run tests
python test_example.py

# View examples
python example_usage.py
```

## Support

Found a bug or need help?
- 🐛 Open an issue on GitHub
- 📖 Check the documentation files
- 💬 Review troubleshooting sections

---

**That's it! You're ready to start teleporting memes! 🚀**
