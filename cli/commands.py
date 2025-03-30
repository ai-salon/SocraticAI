"""CLI commands for SocraticAI."""

import click
from pathlib import Path
from typing import Optional
from glob import glob
import logging
import os

from socraticai.transcribe.service import transcribe
from socraticai.content.article.article_generator import (
    ArticleGenerator, 
    TranscriptTooShortError,
    UnsupportedFileTypeError
)
from socraticai.content.knowledge_graph.graph_generator import KnowledgeGraphGenerator
from socraticai.core.utils import get_stats, get_input_path

logger = logging.getLogger(__name__)

# Stats command
@click.command()
def stats():
    """Get statistics about the data folder."""
    get_stats()

# Transcription command
@click.command()
@click.argument('path', type=str, required=False)
@click.option('--output-file', '-o', type=click.Path(), help='The name of the file to save the transcription to')
@click.option('--anonymize/--no-anonymize', default=True, help='Whether to anonymize the transcript (default: True)')
def transcribe(path=None, output_file=None, anonymize=True):
    """Transcribe audio files.
    
    If no path is provided, processes all files in the input directory.
    If a specific file path is provided, processes just that file.
    If a pattern with wildcards is provided, processes all matching files.
    """
    if path is None:
        # Process all files in the input directory
        input_path = get_input_path()
        files = glob(os.path.join(input_path, "*"))
    elif '*' in path or '?' in path:
        # Process files matching the pattern
        files = glob(path)
    else:
        # Process a single file
        if not os.path.exists(path):
            click.echo(f"Error: File not found: {path}", err=True)
            return
        files = [path]
        
    # Filter out __init__.py files
    files = [f for f in files if not os.path.basename(f) == "__init__.py"]
        
    if not files:
        click.echo(f"No files found to process", err=True)
        return
    
    for file_path in files:
        try:
            output_path, _ = transcribe(file_path, output_file=output_file if len(files) == 1 else None, anonymize=anonymize)
            click.echo(f"Successfully transcribed {file_path} to {output_path}")
        except Exception as e:
            click.echo(f"Error transcribing {file_path}: {str(e)}", err=True)

# Article command
@click.command()
@click.argument('path', type=str, required=False)
@click.option('--rerun', is_flag=True, help='Force regeneration even if article already exists')
@click.option('--anonymize/--no-anonymize', default=True, help='Whether to anonymize the transcript (default: True)')
def article(path=None, rerun=False, anonymize=True):
    """Generate articles from audio or transcript files.
    
    If no path is provided, processes all files in the input directory.
    If a specific file path is provided, processes just that file.
    If a pattern with wildcards is provided, processes all matching files.
    """
    if path is None:
        # Process all files in the input directory
        input_path = get_input_path()
        files = glob(os.path.join(input_path, "*"))
    elif '*' in path or '?' in path:
        # Process files matching the pattern
        files = glob(path)
    else:
        # Process a single file
        if not os.path.exists(path):
            click.echo(f"Error: File not found: {path}", err=True)
            return
        files = [path]
    
    # Filter out __init__.py files
    files = [f for f in files if not os.path.basename(f) == "__init__.py"]
    
    if not files:
        click.echo(f"No files found to process", err=True)
        return
    
    generator = ArticleGenerator()
    success_count = 0
    
    for file_path in files:
        try:
            article_path, metadata_path = generator.generate(input_path=file_path, rerun=rerun, anonymize=anonymize)
            click.echo(f"Successfully generated article from {file_path}")
            click.echo(f"  Article: {article_path}")
            click.echo(f"  Metadata: {metadata_path}")
            success_count += 1
        except TranscriptTooShortError as e:
            click.echo(f"Error processing {file_path}: Transcript too short", err=True)
        except UnsupportedFileTypeError as e:
            click.echo(f"Error processing {file_path}: Unsupported file type", err=True)
        except Exception as e:
            click.echo(f"Error processing {file_path}: {str(e)}", err=True)
    
    if len(files) > 1:
        click.echo(f"\nSummary: Successfully generated {success_count} of {len(files)} articles")

