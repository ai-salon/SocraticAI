"""CLI commands for SocraticAI."""

import click
from pathlib import Path
from typing import Optional
from glob import glob
import logging

from socraticai.transcribe.service import transcribe
from socraticai.content.article.article_generator import (
    ArticleGenerator, 
    articleGenerationError,
    TranscriptTooShortError,
    UnsupportedFileTypeError
)
from socraticai.content.knowledge_graph.graph_generator import KnowledgeGraphGenerator
from socraticai.core.utils import get_stats

logger = logging.getLogger(__name__)

# Stats command
@click.command()
def stats():
    """Get statistics about the repository."""
    get_stats()

# Transcription commands
@click.group()
def transcribe_group():
    """Commands for audio transcription."""
    pass

@transcribe_group.command(name="single")
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output-file', '-o',
              type=click.Path(),
              help='The name of the file the transcription is saved to')
def transcribe_single(file_path: str, output_file: Optional[str] = None):
    """Transcribe a single audio file."""
    try:
        output_file, _ = transcribe(file_path, output_file=output_file)
        click.echo(f"Successfully transcribed {file_path} to {output_file}")
    except Exception as e:
        click.echo(f"Error transcribing file: {str(e)}", err=True)

@transcribe_group.command(name="batch")
@click.argument('path_pattern', type=str)
def transcribe_multi(path_pattern: str):
    """Transcribe multiple files matching a pattern."""
    files = glob(path_pattern)
    if not files:
        click.echo(f"No files found matching pattern: {path_pattern}", err=True)
        return
    
    for file_path in files:
        try:
            output_file, _ = transcribe(file_path)
            click.echo(f"Successfully transcribed {file_path} to {output_file}")
        except Exception as e:
            click.echo(f"Error transcribing {file_path}: {str(e)}", err=True)

# Substack commands
@click.group()
def substack():
    """Commands for managing Substack article content."""
    pass

@substack.command()
@click.argument('input_file', type=click.Path(exists=True))
def generate(input_file: str, rerun: bool = False):
    """Generate a article post from either an audio file or transcript.
    
    The command automatically detects whether the input is an audio file
    or a transcript and processes it accordingly.
    """
    # Initialize the article generator
    generator = ArticleGenerator()
    
    try:
        # Generate article and get file paths
        article_path, metadata_path = generator.generate(
            input_path=input_file,
            rerun=rerun
        )
        
        # Show success message
        click.echo(f"article post generated successfully!")
        click.echo(f"article saved to: {article_path}")
        click.echo(f"Metadata saved to: {metadata_path}")
            
    except TranscriptTooShortError as e:
        click.echo(f"Error: {str(e)}", err=True)
        click.echo("The transcript needs to be longer to generate a meaningful article post.", err=True)
    except UnsupportedFileTypeError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except FileNotFoundError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Error generating article post: {str(e)}", err=True)

@substack.command(name="generate-multi")
@click.argument('path_pattern', type=str)
def generate_multi(path_pattern: str, rerun: bool = False):
    """Generate article posts from multiple files matching a pattern.
    
    This command will process all audio files or transcripts that match
    the provided glob pattern and generate a article post for each one.
    """
    files = glob(path_pattern)
    if not files:
        click.echo(f"No files found matching pattern: {path_pattern}", err=True)
        return
    
    generator = ArticleGenerator()
    success_count = 0
    
    for file_path in files:
        try:
            article_path, metadata_path = generator.generate(input_path=file_path, rerun=rerun)
            click.echo(f"Successfully generated article from {file_path}")
            click.echo(f"  article: {article_path}")
            click.echo(f"  Metadata: {metadata_path}")
            success_count += 1
        except TranscriptTooShortError as e:
            click.echo(f"Error processing {file_path}: Transcript too short", err=True)
        except UnsupportedFileTypeError as e:
            click.echo(f"Error processing {file_path}: Unsupported file type", err=True)
        except Exception as e:
            click.echo(f"Error processing {file_path}: {str(e)}", err=True)
    
    click.echo(f"\nSummary: Successfully generated {success_count} of {len(files)} article posts")


# Knowledge Graph commands
@click.group()
def knowledge_graph():
    """Commands for managing knowledge graph content."""
    pass

@knowledge_graph.command()
@click.argument('article_path', type=click.Path(exists=True))
def process_article(article_path: str):
    """Process an article and generate knowledge graph nodes.
    
    This command will:
    1. Extract entities from the article
    2. Generate or update nodes for each entity
    3. Update related nodes to maintain consistency
    """
    generator = KnowledgeGraphGenerator()
    
    try:
        # Read the article
        with open(article_path, 'r') as f:
            content = f.read()
            
        # Process the article
        source_id = Path(article_path).stem
        updated_nodes = generator.process_article(content, source_id)
        
        # Show success message
        click.echo(f"Successfully processed article!")
        click.echo(f"Generated/updated {len(updated_nodes)} nodes:")
        for node_path in updated_nodes:
            click.echo(f"  - {node_path}")
            
    except Exception as e:
        click.echo(f"Error processing article: {str(e)}", err=True)

@knowledge_graph.command()
@click.argument('source_id', type=str)
@click.argument('target_id', type=str)
def merge_entities(source_id: str, target_id: str):
    """Merge two entities in the knowledge graph.
    
    This will:
    1. Merge the source entity into the target
    2. Update all relationships
    3. Delete the source node
    4. Update the target node
    """
    generator = KnowledgeGraphGenerator()
    
    try:
        # Merge entities
        updated_node = generator.merge_entities(source_id, target_id)
        
        if updated_node:
            click.echo(f"Successfully merged entities!")
            click.echo(f"Updated node: {updated_node}")
        else:
            click.echo("Failed to merge entities - check entity IDs", err=True)
            
    except Exception as e:
        click.echo(f"Error merging entities: {str(e)}", err=True)

