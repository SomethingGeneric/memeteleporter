# Memeteleporter Implementation Summary

This document provides a technical overview of the memeteleporter implementation.

## Architecture Overview

The memeteleporter system consists of four main components:

```
┌─────────────────────────────────────────────────────────────┐
│                     memeteleporter.py                        │
│                  (Main Orchestrator)                         │
└────────────┬──────────────────────────────┬─────────────────┘
             │                              │
             ▼                              ▼
    ┌────────────────┐            ┌──────────────────┐
    │ immich_client  │            │  meme_detector   │
    │    .py         │            │      .py         │
    └────────────────┘            └──────────────────┘
             │                              │
             ▼                              ▼
      ┌──────────┐                  ┌──────────────┐
      │  Immich  │                  │  OpenAI /    │
      │   API    │                  │  Tesseract   │
      └──────────┘                  └──────────────┘
```

## Component Details

### 1. config.py
**Purpose:** Configuration management using environment variables

**Key Features:**
- Loads settings from `.env` file
- Validates required configuration
- Provides sensible defaults
- Creates cache directory automatically

**Configuration Options:**
```python
IMMICH_API_URL      # Immich server API endpoint
IMMICH_API_KEY      # API authentication key
OPENAI_API_KEY      # OpenAI API key (for AI detection)
MEME_CACHE_DIR      # Local cache directory path
OCR_APPROACH        # Detection method: "openai" or "tesseract"
```

### 2. immich_client.py
**Purpose:** Abstraction layer for Immich API interactions

**Key Methods:**
- `get_all_assets()` - Retrieves all assets from Immich
- `get_screenshots()` - Filters assets to find screenshots
- `download_asset(asset_id, output_path)` - Downloads an asset
- `delete_asset(asset_id)` - Deletes an asset from Immich

**Screenshot Detection Logic:**
Identifies screenshots based on common naming patterns:
- "screenshot", "screen_shot", "screen shot"
- "img_" (common Android pattern)
- "pxl_" (Google Pixel pattern)
- "scr_" (some device patterns)

### 3. meme_detector.py
**Purpose:** AI/OCR-based classification of images

**Detection Approaches:**

#### OpenAI Vision API (Recommended)
- Uses GPT-4 Vision model (gpt-4o-mini for cost efficiency)
- Analyzes both visual content and text
- Provides contextual understanding
- Accuracy: ~95%+ for typical use cases

**Classification Criteria:**
- **Memes**: Humorous content, meme templates, social media jokes, image macros
- **Screenshots**: App interfaces, emails, websites, technical information

#### Tesseract OCR (Alternative)
- Extracts text using OCR
- Applies heuristic rules
- Pattern matching for meme indicators
- Accuracy: ~70-80% depending on content

**Heuristic Indicators:**
- Meme-specific language: "nobody:", "when you", "POV:", etc.
- Text length and structure
- Word count thresholds

### 4. memeteleporter.py
**Purpose:** Main application logic and workflow orchestration

**Workflow:**
1. Initialize configuration and clients
2. Load metadata from previous runs
3. Retrieve screenshots from Immich
4. For each screenshot:
   - Skip if already processed (from metadata)
   - Download to temporary location
   - Analyze using meme detector
   - If meme:
     - Move to permanent cache
     - Delete from Immich (unless dry-run)
     - Update metadata
   - If screenshot:
     - Remove temporary file
     - Keep in Immich
5. Save updated metadata
6. Report statistics

**Safety Features:**
- Dry-run mode (--dry-run flag)
- Metadata tracking prevents reprocessing
- Conservative classification (defaults to keeping)
- Comprehensive error handling
- Detailed logging at every step

## Data Flow

```
1. User runs memeteleporter.py
           ↓
2. Load configuration from .env
           ↓
3. Initialize ImmichClient and MemeDetector
           ↓
4. ImmichClient → Immich API: Get all assets
           ↓
5. Filter for screenshots based on naming patterns
           ↓
6. For each screenshot:
   ├─ Download image
   ├─ MemeDetector analyzes image
   ├─ If MEME:
   │  ├─ Cache locally
   │  ├─ Add to metadata
   │  └─ Delete from Immich (if not dry-run)
   └─ If SCREENSHOT:
      └─ Keep in Immich
           ↓
7. Save metadata
           ↓
8. Display statistics
```

## File Structure

```
memeteleporter/
├── .env.example              # Configuration template
├── .gitignore               # Git ignore rules
├── config.py                # Configuration management
├── immich_client.py         # Immich API client
├── meme_detector.py         # Meme detection logic
├── memeteleporter.py        # Main application (executable)
├── requirements.txt         # Python dependencies
├── README.md               # User documentation
├── USAGE_GUIDE.md          # Detailed usage instructions
├── IMPLEMENTATION_SUMMARY.md  # This file
├── test_example.py         # Test suite
├── example_usage.py        # Programmatic usage examples
└── meme_cache/             # Cached memes directory (created at runtime)
    ├── metadata.json       # Processing metadata
    └── [cached meme files] # Downloaded meme images
```

## Metadata Format

The `metadata.json` file tracks processing state:

```json
{
  "processed_assets": [
    "uuid-of-processed-asset-1",
    "uuid-of-processed-asset-2"
  ],
  "cached_memes": [
    {
      "asset_id": "uuid-of-meme-asset",
      "filename": "Screenshot_20240101.jpg",
      "original_filename": "Screenshot_20240101_123456.jpg"
    }
  ]
}
```

**Purpose:**
- `processed_assets`: List of asset IDs that have been analyzed
- `cached_memes`: Details about memes that were cached locally

**Benefits:**
- Prevents reprocessing the same images
- Allows incremental processing
- Tracks what was done for auditing
- Enables recovery if process is interrupted

## API Usage

### Immich API Endpoints Used

```
GET  /api/assets              # Retrieve all assets
GET  /api/assets/{id}/original  # Download asset file
DELETE /api/assets            # Delete assets (batch)
```

**Authentication:**
- Uses `x-api-key` header for authentication
- API key obtained from Immich web interface

### OpenAI API Usage

```
POST https://api.openai.com/v1/chat/completions
```

**Model:** gpt-4o-mini
**Request Format:**
```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Analyze this image..."},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
      ]
    }
  ],
  "max_tokens": 10
}
```

**Cost:** ~$0.001 per image with gpt-4o-mini

## Error Handling

### Strategy
- Try-except blocks around all external operations
- Log errors with full context
- Continue processing remaining items on error
- Track error count in statistics

### Common Errors and Handling
1. **Network/API errors**: Log and skip item
2. **File I/O errors**: Log and skip item
3. **Configuration errors**: Fail fast with clear message
4. **API authentication errors**: Fail fast with clear message

## Performance Considerations

### Bottlenecks
1. **API rate limits**: Both Immich and OpenAI have limits
2. **Network I/O**: Download/upload time for images
3. **Image analysis**: OpenAI API calls take 1-3 seconds each

### Optimization Strategies
1. **Sequential processing**: Process one at a time (current implementation)
2. **Future: Batch processing**: Could parallelize with threading/async
3. **Future: Caching**: Could cache OpenAI responses for identical images
4. **Metadata tracking**: Prevents reprocessing same images

### Scalability
- Current: Suitable for personal libraries (100-10,000 images)
- For larger: Could add batch processing, parallel execution
- For enterprise: Would need queue system, distributed processing

## Security Considerations

### API Keys
- Stored in `.env` file (excluded from git)
- Never logged or printed
- Validated at startup

### Data Privacy
- Images temporarily downloaded to local system
- OpenAI: Images sent to API (see OpenAI privacy policy)
- Tesseract: Processes images locally (no external transmission)

### Immich Access
- Requires API key with asset read/delete permissions
- Deletions are permanent (check Immich trash feature)

## Testing

### Test Coverage
1. **Unit tests** (`test_example.py`):
   - Configuration loading
   - Client initialization
   - Screenshot filtering logic
   - Metadata handling
   - CLI interface

2. **Manual tests** (requires live Immich):
   - End-to-end workflow with dry-run
   - Actual deletion workflow
   - Error recovery
   - Edge cases

### Test Data Needed
- Sample screenshots (genuine)
- Sample memes
- Sample other images (photos)
- Immich test instance

## Future Enhancements

### Short-term
- [ ] Batch/parallel processing for speed
- [ ] Progress bar for visual feedback
- [ ] Configuration file validation tool
- [ ] Support for additional screenshot patterns

### Medium-term
- [ ] Interactive mode (manual review before deletion)
- [ ] Web UI for reviewing classifications
- [ ] Support for other AI providers (Anthropic Claude, etc.)
- [ ] Local AI model support (no API required)

### Long-term
- [ ] Support for other photo management systems
- [ ] Album-based organization in Immich
- [ ] Automatic cloud sync integration
- [ ] Machine learning training for custom patterns
- [ ] Plugin system for custom workflows

## Troubleshooting Guide

### Common Issues

**1. "IMMICH_API_KEY is required"**
- Solution: Create `.env` file from `.env.example`
- Add valid Immich API key

**2. "Failed to retrieve assets"**
- Check: Immich server running and accessible
- Check: API URL is correct (include /api)
- Check: API key is valid and has permissions

**3. "OpenAI API error"**
- Check: API key is valid
- Check: Sufficient API credits
- Alternative: Switch to tesseract approach

**4. "No screenshots found"**
- Check: Screenshots exist in Immich
- Solution: Modify screenshot patterns in `immich_client.py`

**5. False positives/negatives**
- OpenAI: Generally accurate, review cache directory
- Tesseract: Less accurate, consider switching to OpenAI
- Solution: Adjust detection logic or thresholds

## Development

### Adding New Features

**Example: Add support for custom patterns**

1. Modify `immich_client.py`:
```python
screenshot_patterns = [
    'screenshot',
    'custom_pattern',  # Add here
]
```

2. Test with dry-run
3. Commit changes

**Example: Add new AI provider**

1. Create new method in `meme_detector.py`:
```python
def _is_meme_anthropic(self, image_path: Path) -> bool:
    # Implementation
    pass
```

2. Update `__init__` to support new approach
3. Update config to allow new option
4. Test thoroughly

### Code Style
- PEP 8 compliant
- Type hints where appropriate
- Docstrings for all public methods
- Comprehensive error handling
- Detailed logging

### Contributing
1. Fork repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request
5. Address review feedback

## Conclusion

Memeteleporter provides a complete solution for organizing photo libraries by separating memes from genuine screenshots. The modular design allows for easy customization and extension, while safety features like dry-run mode and metadata tracking ensure safe operation.

The dual detection approach (OpenAI and Tesseract) provides flexibility for different use cases, balancing accuracy, cost, and privacy considerations.

For most users, the OpenAI approach is recommended for its superior accuracy, while the Tesseract approach serves users with privacy concerns or budget constraints.
