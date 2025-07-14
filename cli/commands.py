"""CLI commands for SocraticAI."""

import click
from pathlib import Path
from typing import Optional, List
from glob import glob
import logging
import os
import time

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import print as rprint
from rich.prompt import Confirm

from socraticai.transcribe.service import transcribe
from socraticai.content.article.article_generator import (
    ArticleGenerator, 
    TranscriptTooShortError,
    UnsupportedFileTypeError
)
from socraticai.content.knowledge_graph.graph_generator import KnowledgeGraphGenerator
from socraticai.core.utils import get_stats, get_input_path
from socraticai.config import MODEL_CHOICES

logger = logging.getLogger(__name__)
console = Console()

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

def get_file_info(file_path: str) -> dict:
    """Get file information including size and modified time."""
    try:
        stat = os.stat(file_path)
        return {
            "size": stat.st_size,
            "modified": time.ctime(stat.st_mtime)
        }
    except:
        return {"size": 0, "modified": "Unknown"}

def get_file_list(path: Optional[str]) -> List[str]:
    """Get list of files to process based on path argument."""
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
            return []
        files = [path]
    
    # Filter out unwanted files
    files = [f for f in files if os.path.isfile(f) and not os.path.basename(f).startswith(".") and not os.path.basename(f) == "__init__.py"]
    return files

# Stats command
@click.command()
def stats():
    """Get comprehensive statistics about the data folder with rich formatting."""
    from socraticai.core.utils import get_data_directory
    
    console.print("\n[bold blue]📊 SocraticAI Data Directory Statistics[/bold blue]\n")
    
    # Get file counts and details
    audio_files = glob(os.path.join(get_data_directory("inputs"), "*"))
    audio_files = [f for f in audio_files if not f.endswith(".py") and os.path.isfile(f)]
    
    transcripts = glob(os.path.join(get_data_directory("transcripts"), "*_transcript.txt"))
    anonymized = glob(os.path.join(get_data_directory("processed"), "*_anon.txt"))
    articles = glob(os.path.join(get_data_directory("outputs"), "articles", "*.md"))
    
    # Calculate total sizes
    audio_size = sum(get_file_info(f)["size"] for f in audio_files)
    transcript_size = sum(get_file_info(f)["size"] for f in transcripts)
    article_size = sum(get_file_info(f)["size"] for f in articles)
    
    # Create summary table
    table = Table(title="Data Directory Overview")
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right", style="magenta")
    table.add_column("Total Size", justify="right", style="green")
    table.add_column("Directory", style="yellow")
    
    table.add_row(
        "🎵 Audio Files", 
        str(len(audio_files)), 
        format_file_size(audio_size),
        get_data_directory("inputs")
    )
    table.add_row(
        "📝 Transcripts", 
        str(len(transcripts)), 
        format_file_size(transcript_size),
        get_data_directory("transcripts")
    )
    table.add_row(
        "🔒 Anonymized", 
        str(len(anonymized)), 
        "—",
        get_data_directory("processed")
    )
    table.add_row(
        "📄 Articles", 
        str(len(articles)), 
        format_file_size(article_size),
        get_data_directory("outputs") + "/articles"
    )
    
    console.print(table)
    
    # Recent files summary
    if audio_files or transcripts or articles:
        console.print("\n[bold green]📋 Recent Activity[/bold green]")
        
        recent_table = Table()
        recent_table.add_column("Type", style="cyan")
        recent_table.add_column("File", style="white")
        recent_table.add_column("Modified", style="dim")
        
        # Get most recent files
        all_files = [(("Audio", f) for f in audio_files[-3:])] + \
                   [(("Transcript", f) for f in transcripts[-3:])] + \
                   [(("Article", f) for f in articles[-3:])]
        
        # Flatten and take most recent
        recent_files = []
        for file_group in all_files:
            for file_type, file_path in file_group:
                recent_files.append((file_type, file_path))
        
        # Sort by modification time and take last 6
        recent_files.sort(key=lambda x: os.path.getmtime(x[1]) if os.path.exists(x[1]) else 0)
        
        for file_type, file_path in recent_files[-6:]:
            info = get_file_info(file_path)
            recent_table.add_row(
                file_type,
                os.path.basename(file_path),
                info["modified"]
            )
        
        console.print(recent_table)
    
    console.print(f"\n[dim]Data directory: {get_data_directory('')}[/dim]")

# Transcription command
@click.command()
@click.argument('path', type=str, required=False)
@click.option('--output-file', '-o', type=click.Path(), help='The name of the file to save the transcription to')
@click.option('--anonymize/--no-anonymize', default=True, help='Whether to anonymize the transcript (default: True)')
def transcribe_cmd(path=None, output_file=None, anonymize=True):
    """Transcribe audio files with progress tracking and rich output.
    
    If no path is provided, processes all files in the input directory.
    If a specific file path is provided, processes just that file.
    If a pattern with wildcards is provided, processes all matching files.
    """
    console.print("\n[bold blue]🎵 SocraticAI Transcription Service[/bold blue]\n")
    
    files = get_file_list(path)
    
    if not files:
        if path and not os.path.exists(path):
            console.print(f"[red]❌ Error: File not found: {path}[/red]")
        else:
            console.print(f"[yellow]⚠️  No files found to process[/yellow]")
        return
    
    # Show file summary
    if len(files) > 1:
        console.print(f"[green]📁 Found {len(files)} files to transcribe[/green]")
        if len(files) > 5:
            for f in files[:3]:
                console.print(f"  • {os.path.basename(f)}")
            console.print(f"  • ... and {len(files) - 3} more")
        else:
            for f in files:
                console.print(f"  • {os.path.basename(f)}")
        
        if not Confirm.ask(f"\n[yellow]Continue with transcription?[/yellow]"):
            console.print("[yellow]Operation cancelled[/yellow]")
            return
    
    # Process files with progress tracking
    success_count = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Transcribing files...", total=len(files))
        
        for i, file_path in enumerate(files):
            filename = os.path.basename(file_path)
            progress.update(task, description=f"[cyan]Transcribing {filename}...")
            
            try:
                output_path, _ = transcribe(
                    file_path, 
                    output_file=output_file if len(files) == 1 else None, 
                    anonymize=anonymize
                )
                success_count += 1
                progress.update(task, advance=1)
                console.print(f"  [green]✅ {filename} → {os.path.basename(output_path)}[/green]")
                
            except Exception as e:
                progress.update(task, advance=1)
                console.print(f"  [red]❌ {filename}: {str(e)}[/red]")
    
    # Summary
    if len(files) > 1:
        console.print(f"\n[bold green]🎉 Transcription Complete![/bold green]")
        console.print(f"Successfully transcribed {success_count} of {len(files)} files")
        if success_count < len(files):
            console.print(f"[yellow]{len(files) - success_count} files failed[/yellow]")
    elif success_count == 1:
        console.print(f"\n[bold green]🎉 Transcription successful![/bold green]")

# Article command
@click.command()
@click.argument('path', type=str, required=False)
@click.option('--rerun', is_flag=True, help='Force regeneration even if article already exists')
@click.option('--anonymize/--no-anonymize', default=True, help='Whether to anonymize the transcript (default: True)')
@click.option('--multi-source', is_flag=True, help='Process multiple files as a single combined article')
@click.option('--model', type=click.Choice(['default', 'flash', 'sonnet', 'pro']), help='Choose model: 1) default (gemini-2.5-flash), 2) flash (gemini-2.5-flash), 3) sonnet (claude-sonnet-4), 4) pro (gemini-2.5-pro)')
def article(path=None, rerun=False, anonymize=True, multi_source=False, model=None):
    """Generate articles from audio or transcript files with enhanced UX.
    
    If no path is provided, processes all files in the input directory.
    If a specific file path is provided, processes just that file.
    If a pattern with wildcards is provided, processes all matching files.
    Use --multi-source to combine multiple files into a single article.
    
    Model choices:
    1) default - gemini-2.5-flash (default)
    2) flash - gemini-2.5-flash  
    3) sonnet - claude-sonnet-4-20250514
    4) pro - gemini-2.5-pro
    """
    console.print("\n[bold blue]📄 SocraticAI Article Generator[/bold blue]\n")
    
    # Show model selection if specified
    if model:
        selected_model = MODEL_CHOICES.get(model, MODEL_CHOICES["default"])
        console.print(f"[cyan]🤖 Using model: {model} ({selected_model})[/cyan]\n")
    
    files = get_file_list(path)
    
    if not files:
        if path and not os.path.exists(path):
            console.print(f"[red]❌ Error: File not found: {path}[/red]")
        else:
            console.print(f"[yellow]⚠️  No files found to process[/yellow]")
        return
    
    # Handle multi-source mode
    if multi_source and len(files) > 1:
        console.print(f"[green]🔗 Multi-source mode: Combining {len(files)} files into one article[/green]")
        for f in files:
            console.print(f"  • {os.path.basename(f)}")
        
        if not Confirm.ask(f"\n[yellow]Generate combined article from these files?[/yellow]"):
            console.print("[yellow]Operation cancelled[/yellow]")
            return
        
        # Process as single multi-input
        generator_kwargs = {}
        if model:
            generator_kwargs['model'] = MODEL_CHOICES.get(model, MODEL_CHOICES["default"])
        generator = ArticleGenerator(**generator_kwargs)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Generating combined article...", total=None)
            
            try:
                article_path, metadata_path = generator.generate(
                    input_paths=files, 
                    rerun=rerun, 
                    anonymize=anonymize
                )
                progress.stop()
                
                console.print("\n[bold green]🎉 Combined article generated successfully![/bold green]")
                console.print(f"[green]📄 Article: {os.path.basename(article_path)}[/green]")
                console.print(f"[dim]📁 Location: {article_path}[/dim]")
                
            except TranscriptTooShortError:
                progress.stop()
                console.print(f"[red]❌ Error: One or more transcripts are too short[/red]")
            except UnsupportedFileTypeError:
                progress.stop()
                console.print(f"[red]❌ Error: Unsupported file type detected[/red]")
            except RuntimeError as e:
                progress.stop()
                if "returned empty response" in str(e):
                    console.print(f"[red]❌ Error: Model returned no response (try a different model with --model)[/red]")
                else:
                    console.print(f"[red]❌ Error: {str(e)}[/red]")
            except Exception as e:
                progress.stop()
                console.print(f"[red]❌ Error: {str(e)}[/red]")
        return
    
    # Show file summary for individual processing
    if len(files) > 1:
        console.print(f"[green]📁 Found {len(files)} files to process individually[/green]")
        if len(files) > 5:
            for f in files[:3]:
                console.print(f"  • {os.path.basename(f)}")
            console.print(f"  • ... and {len(files) - 3} more")
        else:
            for f in files:
                console.print(f"  • {os.path.basename(f)}")
        
        console.print(f"\n[dim]💡 Tip: Use --multi-source to combine multiple files into one article[/dim]")
        
        if not Confirm.ask(f"\n[yellow]Continue with individual article generation?[/yellow]"):
            console.print("[yellow]Operation cancelled[/yellow]")
            return
    
    # Process files individually with progress tracking
    generator_kwargs = {}
    if model:
        generator_kwargs['model'] = MODEL_CHOICES.get(model, MODEL_CHOICES["default"])
    generator = ArticleGenerator(**generator_kwargs)
    success_count = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Generating articles...", total=len(files))
        
        for i, file_path in enumerate(files):
            filename = os.path.basename(file_path)
            progress.update(task, description=f"[cyan]Processing {filename}...")
            
            try:
                article_path, metadata_path = generator.generate(
                    input_paths=file_path, 
                    rerun=rerun, 
                    anonymize=anonymize
                )
                success_count += 1
                progress.update(task, advance=1)
                console.print(f"  [green]✅ {filename} → {os.path.basename(article_path)}[/green]")
                
            except TranscriptTooShortError:
                progress.update(task, advance=1)
                console.print(f"  [red]❌ {filename}: Transcript too short[/red]")
            except UnsupportedFileTypeError:
                progress.update(task, advance=1)
                console.print(f"  [red]❌ {filename}: Unsupported file type[/red]")
            except RuntimeError as e:
                progress.update(task, advance=1)
                if "returned empty response" in str(e):
                    console.print(f"  [red]❌ {filename}: Model returned no response (try a different model)[/red]")
                else:
                    console.print(f"  [red]❌ {filename}: {str(e)}[/red]")
            except Exception as e:
                progress.update(task, advance=1)
                console.print(f"  [red]❌ {filename}: {str(e)}[/red]")
    
    # Summary
    if len(files) > 1:
        console.print(f"\n[bold green]🎉 Article Generation Complete![/bold green]")
        console.print(f"Successfully generated {success_count} of {len(files)} articles")
        if success_count < len(files):
            console.print(f"[yellow]{len(files) - success_count} files failed[/yellow]")
    elif success_count == 1:
        console.print(f"\n[bold green]🎉 Article generated successfully![/bold green]")