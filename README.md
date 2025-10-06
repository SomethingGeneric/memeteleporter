# memeteleporter
Pull apart your actual photos from all the screenshots of memes

## Overview

Memeteleporter is a Python script that automatically identifies and separates memes from genuine screenshots in your Immich photo library. It uses OCR and AI analysis to distinguish between:

- **Memes**: Humorous images, social media posts, meme templates with text overlays
- **Genuine Screenshots**: App interfaces, emails, website content, error messages, productivity tools

Once identified, memes are cached locally and optionally deleted from Immich to keep your photo library clean and organized.

## Documentation

- 📖 **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- 📚 **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Comprehensive usage instructions
- 🔧 **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical documentation
- 💻 **[example_usage.py](example_usage.py)** - Programmatic API examples

## Features

- 🔍 Automatically detects screenshots in Immich
- 🤖 AI-powered meme detection using OpenAI Vision API or Tesseract OCR
- 💾 Local caching of detected memes
- 🗑️ Optional deletion from Immich
- 📊 Detailed processing statistics
- 🔄 Metadata tracking to avoid reprocessing
- 🧪 Dry-run mode for testing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SomethingGeneric/memeteleporter.git
cd memeteleporter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. If using Tesseract OCR, install Tesseract:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your settings:
```bash
# Immich API Configuration
IMMICH_API_URL=http://your-immich-server:2283/api
IMMICH_API_KEY=your-api-key-here

# OpenAI API Configuration (for AI-based detection)
OPENAI_API_KEY=your-openai-api-key-here

# Local cache directory for memes
MEME_CACHE_DIR=./meme_cache

# OCR approach: "tesseract" or "openai"
OCR_APPROACH=openai
```

### Getting API Keys

**Immich API Key:**
1. Log into your Immich web interface
2. Go to Account Settings → API Keys
3. Create a new API key
4. Copy the key to your `.env` file

**OpenAI API Key:**
1. Sign up at https://platform.openai.com/
2. Navigate to API Keys section
3. Create a new secret key
4. Copy the key to your `.env` file

## Usage

### Basic Usage

Run the script in dry-run mode first to see what would be processed:
```bash
python memeteleporter.py --dry-run
```

Once you're satisfied with the results, run without dry-run to actually delete from Immich:
```bash
python memeteleporter.py
```

### Command Line Options

- `--dry-run`: Process and cache memes without deleting from Immich

## How It Works

1. **Screenshot Detection**: Connects to Immich API and identifies assets that match screenshot naming patterns (e.g., "Screenshot_", "IMG_", "PXL_")

2. **Meme Analysis**: Downloads each screenshot and analyzes it using either:
   - **OpenAI Vision API** (recommended): Uses GPT-4 Vision to understand image content and context
   - **Tesseract OCR**: Extracts text and uses heuristics to identify meme-like patterns

3. **Classification**: Determines if the image is:
   - **Meme**: Contains humor, meme formats, social media jokes, image macros
   - **Screenshot**: Shows app interfaces, emails, websites, technical info

4. **Action**: 
   - Memes are saved to the local cache directory
   - Metadata is recorded to prevent reprocessing
   - If not in dry-run mode, memes are deleted from Immich

## Detection Approaches

### OpenAI Vision API (Recommended)

- **Pros**: More accurate, understands context and visual content
- **Cons**: Requires API key, costs per image (very low cost with gpt-4o-mini)
- **Best for**: Most use cases, especially with varied content

Set `OCR_APPROACH=openai` in `.env`

### Tesseract OCR

- **Pros**: Free, runs locally, no API required
- **Cons**: Less accurate, relies on text patterns only
- **Best for**: Privacy-conscious users, offline use, budget constraints

Set `OCR_APPROACH=tesseract` in `.env`

## Output

The script creates:

- **meme_cache/**: Directory containing all detected memes
- **meme_cache/metadata.json**: Tracking file with processed assets and cached memes

### Metadata Structure

```json
{
  "processed_assets": ["asset-id-1", "asset-id-2", ...],
  "cached_memes": [
    {
      "asset_id": "asset-id-1",
      "filename": "cached_filename.jpg",
      "original_filename": "Screenshot_20240101.jpg"
    }
  ]
}
```

## Safety Features

- **Dry-run mode**: Test without making changes
- **Metadata tracking**: Prevents reprocessing the same images
- **Error handling**: Failed operations are logged and don't stop the process
- **Conservative defaults**: When uncertain, images are kept as screenshots

## Troubleshooting

### "IMMICH_API_KEY is required"
Make sure you've created a `.env` file with your Immich API key.

### "Failed to retrieve assets"
- Check that your `IMMICH_API_URL` is correct
- Verify your Immich server is running and accessible
- Confirm your API key is valid

### "OpenAI API error"
- Verify your OpenAI API key is correct
- Check you have sufficient API credits
- Consider switching to `OCR_APPROACH=tesseract`

### "Tesseract not found"
Install Tesseract OCR following the installation instructions above.

## Future Enhancements

- Support for additional AI providers (Anthropic Claude, local models)
- Configurable destination for memes (cloud storage, different Immich albums)
- Web UI for reviewing classifications
- Batch processing optimizations
- Custom classification rules

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see LICENSE file for details
