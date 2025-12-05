# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

Book Sort is an intelligent book categorization system that uses AI (DeepSeek API) to automatically sort book files into appropriate category directories. The system scans source directories for book files, classifies them using AI, and organizes them into categorized folders in the target directory.

## Architecture

The system follows a modular architecture with dependency injection pattern:

```
book_sort/
├── config/                      # Configuration layer
│   └── config_manager.py       # Configuration management (API keys, paths, batch size)
├── database/                     # Data persistence
│   ├── models.py                # ORM models: BookInfo, ClassificationTask
│   └── database_manager.py      # Database operations & session management
├── services/                     # Business logic
│   ├── ai_categorization_service.py   # DeepSeek API integration
│   └── file_manager.py          # File operations (move, create directories)
├── scanners/                     # File system operations
│   └── file_scanner.py          # Directory scanning & permission checks
├── utils/                        # Utilities
│   └── task_manager.py          # Classification task progress tracking
└── book_sort.py                 # Main entry point & BookSortController
```

## Key Commands

### Environment Setup
```bash
# Activate the required conda environment (required before any operations)
conda activate fastapi-env
```
Note: This project requires the `fastapi-env` conda environment to be activated before running any commands.

### Running the System
```bash
# Basic usage with default paths
python book_sort.py

# Specify custom source and target directories
python book_sort.py --src_dir /path/to/source --target_dir /path/to/target
```

### Running Tests
```bash
python test_refactored.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Development Commands
```bash
# Run individual component tests
python -c "import sys; sys.path.insert(0, '.'); from test_refactored import *; test_config_manager()"

# Quick configuration check
python -c "import sys; sys.path.insert(0, '.'); from config.config_manager import ConfigManager; print(ConfigManager().get_all_config())"
```

## Core Components

### BookSortController (book_sort.py:23-225)
Main orchestrator that coordinates all components through dependency injection. Key method: `run(src_dir, target_dir)` executes the full categorization workflow.

### AICategorizationService (services/ai_categorization_service.py:12-218)
Handles AI API communication with DeepSeek. Features:
- Async batch processing with configurable batch size (default: 16)
- Retry logic (3 attempts with exponential backoff)
- Error handling for API failures, timeouts, rate limits
- JSON response parsing with fallback regex extraction

### FileManager (services/file_manager.py)
Manages file operations safely. Key operations:
- Creates category directories in target location
- Moves files to appropriate categories
- Handles "uncategorized" folder for unmatched books

### FileScanner (scanners/file_scanner.py)
- Scans source directories for supported file types (pdf, epub, mobi, djvu, txt)
- Checks directory access permissions before processing
- Detects existing categories in target directory to preserve user structure

### DatabaseManager (database/database_manager.py)
SQLAlchemy wrapper providing:
- Database initialization in target directory
- Book metadata storage and retrieval
- Task progress persistence
- Session management

### TaskManager (utils/task_manager.py)
Tracks classification progress with ClassificationTask model.
Enables resuming interrupted operations by persisting task state.

### ConfigManager (config/config_manager.py)
Unified configuration management loading from:
- `config.yaml` file (primary source)
- Environment variables (fallback for API keys)
- Default values (hard-coded as last resort)

## Configuration

The system uses `config.yaml` with these key settings:
- `deepseek_api_url`: API endpoint (default: https://api.deepseek.com/v1/chat/completions)
- `deepseek_api_key`: API key (should be moved to environment variable DEEPSEEK_API_KEY for security)
- `batch_max_size`: Batch size for AI processing (default: 16, max 50)
- `book_exts`: Supported file extensions
- `default_paths`: Source and target directories
- `uncat`: Uncategorized folder name (default: "其他")

## API Integration Details

The system calls DeepSeek API with:
- **Model**: deepseek-chat
- **Timeout**: 60 seconds total, 10 seconds connect
- **Rate Limiting**: 3 retries with 2-second delay, increased for payload errors
- **Prompt**: System + user prompt asking AI to categorize books from existing categories or create new ones
- **Response Format**: JSON object mapping filenames to categories
- **Error Handling**: Multiple exception types handled (TimeoutError, ClientPayloadError, network errors)

## Database Schema

### BookInfo Table
- Primary key: id (auto-increment)
- filename: Unique, indexed
- file_path: Full file path
- file_size, file_ext: File metadata
- category_tag: AI-assigned category
- Timestamps: created_at, updated_at

### ClassificationTask Table
- task_id: Unique identifier (task_YYYYMMDD_HHMMSS)
- total_files, processed_files: Progress counters
- completed_files, pending_files: JSON arrays of file paths
- is_completed: Boolean status flag
- Timestamps for tracking

## Testing Considerations

When modifying components:
- Run `python test_refactored.py` to verify all components work correctly
- Test individual components using import statements from test_refactored.py
- Verify API mocking works correctly for offline testing scenarios
- Check database operations work with both existing and new databases

## Important Notes

1. **API Key Security**: The config.yaml currently stores API key in plaintext. This should be moved to DEEPSEEK_API_KEY environment variable.

2. **Async Processing**: The system uses asyncio and aiohttp for concurrent API calls. Ensure async/await patterns are maintained when modifying AI service.

3. **Batch Size**: Currently set to 16 to avoid API payload errors. Can be tuned between 4-50 based on network conditions and file naming complexity.

4. **Default Directories**: Source: ~/Downloads, Target: ~/Documents/Books (defined in config.yaml)

5. **Error Recovery**: Failed API calls are retried 3 times. Individual file processing errors are logged but don't stop the entire batch.

6. **Session Management**: DatabaseManager.get_session() must be properly closed after use (using try/finally or context manager pattern)

7. **File Path Handling**: All paths should be absolute paths. The system uses os.path operations for cross-platform compatibility.