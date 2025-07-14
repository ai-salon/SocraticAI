"""Enhanced colored logging utilities for SocraticAI operations."""

import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text
from typing import Optional

# Global console instance
console = Console()

class ColoredLogger:
    """Enhanced logger with operation-specific colored output."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)
        
    def setup_rich_logging(self):
        """Setup rich logging handler if not already configured."""
        # Only add RichHandler if we don't already have one
        has_rich_handler = any(isinstance(h, RichHandler) for h in self.logger.handlers)
        if not has_rich_handler and console.is_terminal:
            rich_handler = RichHandler(
                console=console,
                show_time=False,
                show_path=False,
                markup=True
            )
            rich_handler.setLevel(logging.INFO)
            self.logger.addHandler(rich_handler)
            self.logger.setLevel(logging.INFO)
    
    # Audio/Transcription Operations
    def transcription_start(self, filename: str, service: str = "AssemblyAI"):
        """Log start of transcription process."""
        console.print(f"🎤 [bold cyan]TRANSCRIBING[/bold cyan] {filename} via {service}")
        
    def transcription_complete(self, filename: str, output_path: str, duration: Optional[float] = None):
        """Log successful transcription completion."""
        duration_str = f" ({duration:.1f}s)" if duration else ""
        console.print(f"✅ [bold green]TRANSCRIPTION COMPLETE[/bold green] → {output_path}{duration_str}")
        
    def transcription_found(self, filename: str, transcript_path: str):
        """Log when existing transcription is found."""
        console.print(f"📄 [bold yellow]TRANSCRIPT FOUND[/bold yellow] {filename} → {transcript_path}")
        
    # Anonymization Operations  
    def anonymization_start(self, filename: str):
        """Log start of anonymization process."""
        console.print(f"🔒 [bold magenta]ANONYMIZING[/bold magenta] {filename}")
        
    def anonymization_complete(self, filename: str, entities_found: int = 0):
        """Log successful anonymization completion."""
        entities_str = f" ({entities_found} entities masked)" if entities_found else ""
        console.print(f"✅ [bold green]ANONYMIZATION COMPLETE[/bold green]{entities_str}")
        
    def anonymization_skipped(self, reason: str = "disabled"):
        """Log when anonymization is skipped."""
        console.print(f"⏭️  [dim]ANONYMIZATION SKIPPED[/dim] ({reason})")
    
    # Analysis Operations
    def analysis_start(self, transcript_count: int, model: str):
        """Log start of transcript analysis."""
        count_str = f"{transcript_count} transcripts" if transcript_count > 1 else "transcript"
        console.print(f"🔍 [bold blue]ANALYZING[/bold blue] {count_str} with {model}")
        
    def analysis_complete(self, insights_count: int = 0, themes_count: int = 0, duration: Optional[float] = None):
        """Log successful analysis completion."""
        duration_str = f" ({duration:.1f}s)" if duration else ""
        stats = f"{insights_count} insights, {themes_count} themes" if insights_count else ""
        console.print(f"✅ [bold green]ANALYSIS COMPLETE[/bold green] {stats}{duration_str}")
    
    # Article Generation Operations
    def article_generation_start(self, source_type: str, model: str):
        """Log start of article generation."""
        console.print(f"✍️  [bold purple]GENERATING ARTICLE[/bold purple] from {source_type} using {model}")
        
    def article_generation_complete(self, word_count: int = 0, duration: Optional[float] = None):
        """Log successful article generation."""
        duration_str = f" ({duration:.1f}s)" if duration else ""
        word_str = f" ({word_count} words)" if word_count else ""
        console.print(f"✅ [bold green]ARTICLE GENERATED[/bold green]{word_str}{duration_str}")
    
    def article_refinement_start(self, model: str):
        """Log start of article refinement."""
        console.print(f"✨ [bold cyan]REFINING ARTICLE[/bold cyan] with {model}")
        
    def article_refinement_complete(self, duration: Optional[float] = None):
        """Log successful article refinement."""
        duration_str = f" ({duration:.1f}s)" if duration else ""
        console.print(f"✅ [bold green]REFINEMENT COMPLETE[/bold green]{duration_str}")
    
    # Multi-source Operations
    def combining_start(self, source_count: int, model: str):
        """Log start of combining multiple sources."""
        console.print(f"🔗 [bold orange1]COMBINING[/bold orange1] {source_count} sources with {model}")
        
    def combining_complete(self, final_word_count: int = 0, duration: Optional[float] = None):
        """Log successful combination."""
        duration_str = f" ({duration:.1f}s)" if duration else ""
        word_str = f" ({final_word_count} words)" if final_word_count else ""
        console.print(f"✅ [bold green]COMBINATION COMPLETE[/bold green]{word_str}{duration_str}")
    
    # Context and Token Management
    def context_grouping_start(self, transcript_count: int, model: str):
        """Log start of context-aware grouping."""
        console.print(f"📊 [bold yellow]CONTEXT ANALYSIS[/bold yellow] {transcript_count} transcripts for {model}")
        
    def context_grouping_complete(self, group_count: int, total_tokens: int):
        """Log context grouping results."""
        console.print(f"✅ [bold green]GROUPED INTO[/bold green] {group_count} context-aware groups (~{total_tokens:,} tokens)")
    
    def token_estimation(self, transcript_count: int, estimated_tokens: int, model: str):
        """Log token estimation results."""
        console.print(f"🧮 [dim]TOKEN ESTIMATE[/dim] {transcript_count} files: ~{estimated_tokens:,} tokens for {model}")
    
    # File Operations
    def file_save_start(self, filename: str, file_type: str = "article"):
        """Log start of file saving."""
        console.print(f"💾 [bold blue]SAVING[/bold blue] {file_type} → {filename}")
        
    def file_save_complete(self, filepath: str, size_kb: Optional[float] = None):
        """Log successful file save."""
        size_str = f" ({size_kb:.1f}KB)" if size_kb else ""
        console.print(f"✅ [bold green]SAVED[/bold green] {filepath}{size_str}")
        
    def file_exists_skip(self, filepath: str):
        """Log when file already exists and is skipped."""
        console.print(f"⏭️  [dim]FILE EXISTS[/dim] {filepath} (use --rerun to regenerate)")
    
    # Error Operations
    def error(self, operation: str, error_msg: str):
        """Log operation errors."""
        console.print(f"❌ [bold red]ERROR[/bold red] {operation}: {error_msg}")
        
    def warning(self, operation: str, warning_msg: str):
        """Log operation warnings."""
        console.print(f"⚠️  [bold yellow]WARNING[/bold yellow] {operation}: {warning_msg}")
    
    # Progress and Status
    def step_start(self, step_num: int, total_steps: int, description: str):
        """Log start of a processing step."""
        console.print(f"📋 [bold cyan]STEP {step_num}/{total_steps}[/bold cyan] {description}")
        
    def processing_summary(self, operation: str, success_count: int, total_count: int, duration: Optional[float] = None):
        """Log processing summary."""
        duration_str = f" in {duration:.1f}s" if duration else ""
        if success_count == total_count:
            console.print(f"🎉 [bold green]{operation} COMPLETE[/bold green] {success_count}/{total_count} successful{duration_str}")
        else:
            console.print(f"⚠️  [bold yellow]{operation} PARTIAL[/bold yellow] {success_count}/{total_count} successful{duration_str}")


def get_colored_logger(name: str) -> ColoredLogger:
    """Get a colored logger instance for the given name."""
    return ColoredLogger(name)