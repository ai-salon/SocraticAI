![Alt text](https://github.com/ai-salon/SocraticAI/blob/main/static/logo.png?raw=true "AI Salon")


# SocraticAI

A powerful tool for transcribing conversations and generating blog posts from transcripts or audio files.

## Quickstart

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SocraticAI.git
cd SocraticAI
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Install spaCy model:
```bash
poetry run python -m spacy download en_core_web_lg
```

### Environment Setup

Create a `.env` file in the root directory with the following variables:

```env
# Required for transcription
ASSEMBLYAI_API_KEY=your_assemblyai_key

# Required for blog generation
ANTHROPIC_API_KEY=your_anthropic_key

# Optional settings
MODEL_TYPE=claude-3-sonnet  # Default model for generation
```

### Basic Usage

Generate a blog post from an audio file or transcript:
```bash
# From audio file
socraticai substack generate recording.mp3

# From transcript
socraticai substack generate transcript.txt
```

Transcribe audio files:
```bash
# Single file
socraticai transcribe single audio.mp3

# Multiple files
socraticai transcribe batch "audio/*.mp3"
```

## Detailed CLI Guide

The CLI provides several command groups for different functionalities:

### Transcription Commands

```bash
# Transcribe a single audio file
socraticai transcribe single <file_path> [options]

Options:
  -o, --output-file TEXT    The name of the file to save the transcription to

# Transcribe multiple audio files
socraticai transcribe batch <path_pattern>
```

### Blog Generation Commands

```bash
# Generate a blog post from audio or transcript
socraticai substack generate <input_file>
```

The `generate` command automatically detects whether the input is an audio file or transcript and processes it accordingly. Supported audio formats: mp3, wav, m4a, aac, flac.

Blog posts and metadata are automatically saved in the `outputs/articles` directory:
- The blog content is saved as a markdown file (`.md`)
- Associated metadata is saved in a separate JSON file (`.meta.json`)

### Other Commands

```bash
# Get repository statistics
socraticai stats
```

## Output Format

For each generated blog post, two files are created in the `outputs/articles` directory:

1. Blog Content (`article_TIMESTAMP.md`):
```markdown
# Generated blog content in markdown format
```

2. Metadata (`article_TIMESTAMP.meta.json`):
```json
{
  "generated_at": "ISO timestamp",
  "type": "article",
  "transcript_length": 1234,
  "model": "claude-3-sonnet",
  "source_audio": "path/to/audio.mp3",  // If generated from audio
  "transcript_file": "path/to/transcript.txt"  // If generated from audio
}
```

## Requirements

- Python 3.11 or higher
- Poetry for dependency management
- AssemblyAI API key for transcription
- Anthropic API key for blog generation
- spaCy's en_core_web_lg model

## Error Handling

The tool includes various error checks:
- Validates input file types (audio/text)
- Ensures transcripts are long enough (minimum 1000 characters)
- Provides helpful error messages for common issues

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
