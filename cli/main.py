"""Main CLI entry point for SocraticAI."""

# Load environment variables first, before any other imports
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

import click
import logging
import os

from rich.console import Console
from rich import print as rprint

from cli.commands import transcribe_cmd, article, stats

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("SocraticAI")
console = Console()

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def cli():
    """🤖 SocraticAI - AI-powered audio transcription and content generation
    
    Transform your audio files into insightful articles and transcripts using advanced AI.
    
    \b
    Features:
    • 🎵 High-quality audio transcription with AssemblyAI
    • 📄 Intelligent article generation from transcripts
    • 🔗 Multi-source article combining for comprehensive content
    • 🔒 Optional transcript anonymization for privacy
    • 📊 Data directory statistics and management
    
    \b
    Examples:
      socraticai transcribe audio.mp3                    # Transcribe a single file
      socraticai article transcript.txt                  # Generate article from transcript
      socraticai article "*.mp3" --multi-source         # Combine multiple files into one article
      socraticai stats                                   # View data directory statistics
    """
    pass  # Environment variables already loaded at module level

# Add all commands
cli.add_command(stats)
cli.add_command(transcribe_cmd, name="transcribe")
cli.add_command(article)

if __name__ == '__main__':
    cli()
