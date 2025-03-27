"""Main CLI entry point for SocraticAI."""

import click
import logging
from dotenv import find_dotenv, load_dotenv
import os

from cli.commands import substack, transcribe_group, stats

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("SocraticAI")

@click.group()
def cli():
    """SocraticAI CLI tool."""
    # Load environment variables
    dotenv_path = find_dotenv()
    if dotenv_path:
        logger.info(f"Loading environment from {dotenv_path}")
        load_dotenv(dotenv_path)
        logger.info(f'Model type: {os.getenv("MODEL_TYPE")}')

# Add all command groups
cli.add_command(stats)
cli.add_command(transcribe_group, name="transcribe")
cli.add_command(substack)

if __name__ == '__main__':
    cli()
