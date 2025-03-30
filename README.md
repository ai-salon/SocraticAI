![Alt text](https://github.com/ai-salon/SocraticAI/blob/main/static/logo.png?raw=true "AI Salon")


# SocraticAI

A tool for transcribing conversations and generating distillations (summaries, articles) from transcripts or audio files.

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

3. Install spaCy model (used for transcript anonymization)
```bash
poetry run python -m spacy download en_core_web_lg
```

4. Run Socratic AI
```bash
poetry run socraticai -h
```

### Environment Setup

Create a `.env` file in the root directory with the following variables:

```env
# Required for transcription
ASSEMBLYAI_API_KEY=your_assemblyai_key

# Required for article generation
ANTHROPIC_API_KEY=your_anthropic_key

# Optional settings
MODEL_TYPE=claude-3-sonnet  # Default model for generation
```

### Data Directory Setup

SocraticAI uses a structured data directory for all inputs and outputs. By default it will use the data directory in the repo. You can change that directory in the `socraticai/config.py`. 

Place any audio files or transcripts you want to process in the `data/inputs` directory.

### Basic Usage

Generate an article (which will also transcribe)
```bash
# Process all files in the input directory
socraticai article

# From a specific file (doesn't have to be in the input directory)
socraticai article recording.mp3

# From multiple files using a wildcard pattern
socraticai article "recordings/*.mp3"


# Generate article without anonymization
socraticai article recording.mp3 --no-anonymize
```

Transcribe audio files with content creation:
```bash
# A specific file
socraticai transcribe audio.mp3

# Multiple files using a wildcard pattern
socraticai transcribe "audio/*.mp3"

# Process all files in the input directory
socraticai transcribe

# Transcribe without anonymization
socraticai transcribe audio.mp3 --no-anonymize
```

## Detailed CLI Guide

The CLI provides several main commands with adaptive behavior:

### Transcription Command

```bash
socraticai transcribe [path] [options]
```

The `transcribe` command adapts to the argument provided:
- No path: Processes all files in the input directory
- Specific file: Processes just that file
- Path with wildcards: Processes all matching files

Options:
```
-o, --output-file TEXT                The name of the file to save the transcription to (only works when processing a single file)
--anonymize/--no-anonymize            Whether to anonymize the transcript (default: True)
```

### Article Generation Command

```bash
socraticai article [path] [options]
```

The `article` command adapts to the argument provided:
- No path: Processes all files in the input directory
- Specific file: Processes just that file
- Path with wildcards: Processes all matching files

Options:
```
--rerun                              Force regeneration even if article already exists
--anonymize/--no-anonymize           Whether to anonymize the transcript (default: True)
```

The article command automatically detects whether the input is an audio file or transcript and processes it accordingly. Supported audio formats: mp3, wav, m4a, aac, flac.

Articles and metadata are automatically saved in the `outputs/articles` directory:
- The article content is saved as a markdown file (`.md`)
- Associated metadata is saved in a separate JSON file (`.meta.json`)

### Other Commands

```bash
# Get repository statistics
socraticai stats
```

## Custom Data Directory

By default, SocraticAI uses a `data` directory in the project root for all input and output files. You can customize this location by modifying the `socraticai/config.py` file:

```python
# Update this path to use a different data directory
DATA_DIRECTORY = os.path.join(BASE_DIRECTORY, "data")
```

The data directory structure is as follows:
- `data/inputs/` - Place your audio files or transcripts here for batch processing
- `data/transcripts/` - Generated transcripts are stored here
- `data/processed/` - Processed and anonymized transcripts
- `data/outputs/` - Generated outputs (articles, etc.)

These folders will be automatically created by running SocraticAI.

## Output Format

For each generated article post, two files are created in the `outputs/articles` directory:

1. Article Content (`article_TIMESTAMP.md`):
```markdown
# Generated article content in markdown format
```

2. Metadata (`article_TIMESTAMP.meta.json`):
```json
{
  "generated_at": "ISO timestamp",
  "type": "article",
  "transcript_length": 1234,
  "model": "claude-3-sonnet",
  "source_audio": "path/to/audio.mp3",  // If generated from audio
  "transcript_file": "path/to/transcript.txt",  // If generated from audio
  "anonymized": true  // Whether the transcript was anonymized
}
```

## Requirements

- Python 3.11 or higher
- Poetry for dependency management
- AssemblyAI API key for transcription
- Anthropic API key for article generation
- spaCy's en_core_web_lg model

## Error Handling

The tool includes various error checks:
- Validates input file types (audio/text)
- Ensures transcripts are long enough (minimum 1000 characters)
- Provides helpful error messages for common issues

## Developer Guide

### Adding New Output Types

SocraticAI is designed to be modular, allowing for easy addition of new output types beyond articles. To create a new output type:

1. Create a new submodule in the `socraticai/content/` directory:
```
socraticai/content/your_output_type/
```

2. Create a generator class following the pattern of `ArticleGenerator`:
```python
# socraticai/content/your_output_type/output_generator.py

class YourOutputTypeGenerator:
    def __init__(self):
        # Setup necessary resources
        pass
        
    def generate(self, input_path, anonymize=True):
        # Handle both audio files and transcript files
        # Use the transcribe service with the anonymize option
        # Generate your output
        # Return paths to output files
        pass
```

3. Add prompts for your generator (if using LLMs):
```python
# socraticai/content/your_output_type/prompts.py

def your_prompt_template(text, **kwargs):
    return f"""
    Your prompt instructions here...
    
    {text}
    """
```

4. Add a new command to the CLI:
```python
# cli/commands.py

@click.command()
@click.argument('path', type=str, required=False)
@click.option('--anonymize/--no-anonymize', default=True, help='Whether to anonymize the transcript (default: True)')
def your_output_type(path=None, anonymize=True):
    """Generate your output type from audio or transcript files."""
    # Implementation similar to the article command
    pass
    
# Register in cli/__init__.py
```

5. Update tests to cover your new functionality.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
