![Alt text](https://github.com/ai-salon/SocraticAI/blob/main/static/logo.png?raw=true "AI Salon")

# SocraticAI

🤖 **Transform conversations into insights.** SocraticAI is an intelligent CLI tool that transcribes audio discussions and generates comprehensive, well-structured articles using advanced AI models like Claude and Gemini. Perfect for researchers, journalists, podcasters, and anyone who wants to extract meaningful content from recorded conversations.

✨ **What makes it special?** Smart multi-source synthesis, beautiful terminal interface, and context-aware processing that handles everything from quick meetings to lengthy multi-session discussions.

## Quick Start

### 1. Installation (5 minutes)

**Prerequisites:**
- Python 3.11+ (check with `python --version`)
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management

**Setup:**
```bash
# 1. Get the code
git clone https://github.com/ai-salon/SocraticAI.git
cd SocraticAI

# 2. Install everything
poetry install

# 3. Install language model for anonymization
poetry run python -m spacy download en_core_web_lg

# 4. Test installation
poetry run socraticai --help
```

### 2. API Keys Setup

Create a `.env` file in the project root:

```env
# Required for transcription
ASSEMBLYAI_API_KEY=your_assemblyai_key_here

# Choose one or both AI providers:
ANTHROPIC_API_KEY=your_anthropic_key_here  # For Claude models
GOOGLE_API_KEY=your_google_api_key_here    # For Gemini models
```

**Getting API Keys:**
- **AssemblyAI** (transcription): [Get free key](https://www.assemblyai.com/) - $0.37/hour of audio
- **Anthropic** (Claude): [Get key](https://console.anthropic.com/) - Advanced reasoning
- **Google** (Gemini): [Get key](https://makersuite.google.com/) - Large context windows

### 3. Create Your First Articles!

**Option A: Single File Article**
```bash
# Process one audio file or transcript
poetry run socraticai article your_meeting.mp3
# Creates: article_TIMESTAMP.md + metadata
```

**Option B: Multiple Files as Individual Articles**
```bash
# Drop multiple files in data/inputs/ then process each separately
poetry run socraticai article
# Creates: article_TIMESTAMP1.md, article_TIMESTAMP2.md, etc.
```

**Option C: Combined Multi-Source Article (🔥 Most Popular)**
```bash
# Combine multiple discussions into one comprehensive article
poetry run socraticai article session*.mp3 --multi-source
# Creates: combined_AI_Ethics_Debate_20240115_20240120.md
```

## ✨ Key Features

### 🔗 Smart Multi-Source Articles
Combine multiple recordings into a single, coherent article with automatically generated titles:
```bash
# Processes all files and creates: combined_AI_Ethics_Debate_20240115_20240120.md
socraticai article session*.mp3 --multi-source
```

### 🤖 Multiple AI Models
Choose the best model for your needs:
```bash
socraticai article --model sonnet    # Claude Sonnet-4 (best reasoning)
socraticai article --model pro       # Gemini 2.5 Pro (1M context)
socraticai article --model flash     # Gemini 2.5 Flash (fast, default)
```

### 🎯 Context-Aware Processing
- **Automatic Grouping**: Splits large multi-file projects to fit model limits
- **Smart Token Management**: Uses 75% of available context for reliability
- **Model-Specific Limits**: Claude (200k tokens), Gemini (1M tokens)

### 🎨 Beautiful Terminal Experience
- **Rich Progress Bars**: Visual feedback for long operations
- **Colored Output**: Success in green, warnings in yellow, errors in red
- **Interactive Prompts**: Confirmation for batch operations
- **Comprehensive Stats**: Beautiful overview of your data directory

## Command Reference

### 📄 Article Generation

```bash
socraticai article [path] [options]
```

**Examples:**
```bash
# Single file
socraticai article recording.mp3

# All files in input directory  
socraticai article

# Multiple files as one article (NEW!)
socraticai article "session*.mp3" --multi-source

# Choose specific model (sonnet/pro/flash)
socraticai article meeting.mp3 --model sonnet

# Force regeneration
socraticai article old_file.mp3 --rerun

# Skip anonymization (keeps names/emails)
socraticai article sensitive.mp3 --no-anonymize
```

**Options:**
- `--multi-source`: Combine multiple files into one comprehensive article
- `--model`: Choose AI model (`default`, `flash`, `sonnet`, `pro`)
- `--rerun`: Force regeneration even if article exists
- `--anonymize/--no-anonymize`: Control privacy (default: anonymize)

### 🎵 Transcription

```bash
socraticai transcribe [path] [options]
```

**Examples:**
```bash
# Single file
socraticai transcribe audio.mp3

# All files in input directory
socraticai transcribe

# Custom output name
socraticai transcribe audio.mp3 -o my_transcript.txt

# Skip anonymization
socraticai transcribe meeting.mp3 --no-anonymize
```

### 📊 Statistics

```bash
socraticai stats
```

Shows beautiful overview of your data directory with file counts, sizes, and recent activity.

## Supported Formats

**Audio:** mp3, wav, m4a, aac, flac  
**Text:** Any UTF-8 text file (treated as transcript)

## Output Structure

```
AiSalonContent/
├── inputs/          # Drop your files here
├── transcripts/     # Generated transcripts
├── processed/       # Anonymized versions
└── outputs/
    └── articles/    # Final articles + metadata
```

**Article Files:**
- `article_TIMESTAMP.md` - The article content
- `article_TIMESTAMP_meta.json` - Processing metadata
- `combined_TITLE_DATE1_DATE2.md` - Multi-source articles with generated titles

## Model Guide

| Model | Full Model Name | Best For | Context | Speed | Cost |
|-------|----------------|----------|---------|--------|------|
| **flash** (default) | gemini-2.5-flash | Most content, fast processing | 1M tokens | ⚡⚡⚡ | $ |
| **pro** | gemini-2.5-pro | Complex analysis, long discussions | 1M tokens | ⚡⚡ | $$ |
| **sonnet** | claude-sonnet-4-20250514 | Highest quality reasoning | 200k tokens | ⚡ | $$$ |

**Additional Models Available:**
- `claude-3-5-haiku-latest` - Fast, lightweight Claude model
- `gemini-2.5-flash-lite-preview-06-17` - Experimental lightweight Gemini

## Advanced Features

### Multi-Source Intelligence
When using `--multi-source`, SocraticAI:
- Analyzes themes across all sources
- Generates descriptive titles automatically
- Creates date-range filenames
- Synthesizes cross-cutting insights
- Maintains source attribution

### Smart Context Management
- Automatically groups files that exceed model context limits
- Uses safety margins to prevent token limit errors
- Estimates token usage before processing
- Provides detailed logging of context decisions

### Privacy & Anonymization
- Removes names, emails, phone numbers, addresses
- Replaces with generic placeholders (Person A, Person B)
- Maintains conversation flow and meaning
- Optional - can be disabled with `--no-anonymize`

## Troubleshooting

**"No API key found"**
- Check your `.env` file exists in the project root
- Verify API key format (no quotes needed)
- Restart terminal after adding keys

**"Transcript too short"**
- Minimum 1000 characters required
- Check audio quality and length
- Verify transcription completed successfully

**"Model returned empty response"**
- Try a different model with `--model`
- Check if you hit rate limits
- Verify API key has sufficient credits

**"File not found"**
- Use full paths for files outside the project
- Check file permissions
- Supported formats: mp3, wav, m4a, aac, flac, txt

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by the AI Salon community**