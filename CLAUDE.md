# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation and Setup
```bash
# Install dependencies
poetry install

# Install required spaCy model for anonymization
poetry run python -m spacy download en_core_web_lg

# Setup environment variables in .env file
ASSEMBLYAI_API_KEY=your_assemblyai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
```

### Main Commands
```bash
# Run the CLI
poetry run socraticai -h

# Generate article from audio/transcript
poetry run socraticai article [path]
poetry run socraticai article  # processes all files in data/inputs/

# Transcribe audio files
poetry run socraticai transcribe [path]
poetry run socraticai transcribe  # processes all files in data/inputs/

# Get repository statistics
poetry run socraticai stats
```

### Testing
```bash
# Run tests
poetry run pytest

# Run specific test types
poetry run pytest -m unit      # Unit tests only
poetry run pytest -m integration  # Integration tests only
poetry run pytest -m slow      # Slow tests only

# Run specific test file
poetry run pytest tests/test_article_generator.py
```

## Code Architecture

### High-Level Structure
- **CLI Layer** (`cli/`): Command-line interface and argument parsing
- **Core Layer** (`socraticai/core/`): Shared utilities and LLM abstraction
- **Content Generation** (`socraticai/content/`): Article generation and knowledge graph creation
- **Transcription** (`socraticai/transcribe/`): Audio-to-text conversion with anonymization
- **Data Management**: Structured data directories for inputs, outputs, and processing

### Key Components

#### LLM Abstraction (`socraticai/core/llm.py`)
- **Unified Interface**: `LLMChain` class provides single interface for multiple providers
- **Supported Providers**: Anthropic (Claude) and Google (Gemini)
- **Model Routing**: Automatically selects correct provider based on model name
- **Usage**: `LLMChain(model="claude-3-5-sonnet-20241022")` or `LLMChain(model="gemini-2.0-flash")`

#### Article Generation (`socraticai/content/article/`)
- **Multi-step Process**: Analysis → Initial article → Refinement (optional)
- **Input Flexibility**: Handles both audio files and text transcripts
- **Multi-input Support**: Can combine multiple inputs into single article
- **Thinking Tokens**: Uses Claude's thinking capability for complex reasoning

#### Data Flow
1. **Input Processing**: Audio → Transcription → Anonymization (optional)
2. **Analysis**: Transcript → Structured analysis (insights, questions, themes, quotes)
3. **Generation**: Analysis + Transcript → Article content
4. **Output**: Formatted markdown + metadata JSON

### Configuration

#### Models and API Keys (`socraticai/config.py`)
- **Default Model**: `DEFAULT_LLM_MODEL = "gemini-2.0-flash-lite"`
- **API Keys**: Environment variables for ANTHROPIC_API_KEY, GOOGLE_API_KEY, ASSEMBLYAI_API_KEY
- **Data Directory**: Configurable path for all data storage

#### Data Directory Structure
```
data/
├── inputs/         # Audio files or transcripts for processing
├── transcripts/    # Raw transcriptions
├── processed/      # Anonymized transcripts
└── outputs/
    └── articles/   # Generated articles (.md + _meta.json)
```

### Error Handling
- **Custom Exceptions**: `TranscriptTooShortError`, `UnsupportedFileTypeError`, etc.
- **Retry Logic**: Built-in retries for API calls with exponential backoff
- **Validation**: File type validation, transcript length checks
- **Logging**: Comprehensive logging throughout the pipeline

### Testing Architecture
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- **Test Structure**: Separate unit and integration tests
- **Mock Usage**: Mock external APIs for unit tests
- **Configuration**: Test-specific models and API keys in config

## Important Notes

### File Processing
- **Audio Support**: .mp3, .wav, .m4a, .aac, .flac
- **Minimum Transcript Length**: 1000 characters
- **Anonymization**: Uses spaCy for named entity recognition and replacement
- **Batch Processing**: Supports glob patterns and directory processing

### Model Selection
- **Provider Detection**: Automatic based on model name
- **Fallback**: Defaults to Anthropic for unknown models
- **Runtime Override**: Can specify different model per generation call

### Development Workflow
1. Place audio files or transcripts in `data/inputs/`
2. Run `socraticai article` to generate articles
3. Check `data/outputs/articles/` for results
4. Use `socraticai stats` to see repository statistics