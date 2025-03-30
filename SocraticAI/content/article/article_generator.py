"""Module for generating article posts from transcripts."""

import os
import mimetypes
import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime
import time

from socraticai.core.llm import LLMChain, LLMResponse
from socraticai.content.article.prompts import transcript_analysis_prompt, article_writing_prompt, article_refinement_prompt
from socraticai.transcribe.service import transcribe
from socraticai.core.utils import get_output_path

logger = logging.getLogger(__name__)

class articleGenerationError(Exception):
    """Base exception for article generation errors."""
    pass

class TranscriptTooShortError(articleGenerationError):
    """Exception raised when transcript is too short."""
    pass

class UnsupportedFileTypeError(articleGenerationError):
    """Exception raised when file type is not supported."""
    pass

class AnalysisParsingError(articleGenerationError):
    """Exception raised when analysis sections cannot be parsed."""
    pass

class ArticleGenerator:
    # Supported audio file extensions
    SUPPORTED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.aac', '.flac'}
    # Minimum transcript length (in characters)
    MIN_TRANSCRIPT_LENGTH = 1000
    
    def __init__(self, llm_chain: Optional[LLMChain] = None):
        self.llm_chain = llm_chain or LLMChain()
        self.output_dir = Path(get_output_path()) / "articles"
        logger.info(f"Initialized ArticleGenerator with output directory: {self.output_dir}")
    
    def generate(self,
                input_path: str,
                rerun: bool = False) -> Tuple[Path, Path]:
        """
        Generate and save a article post from either an audio file or transcript.
        
        Args:
            input_path: Path to either an audio file or transcript text file
            rerun: Whether to rerun the generation even if the article already exists
        Returns:
            Tuple of (article_path, metadata_path) where the files were saved
            
        Raises:
            UnsupportedFileTypeError: If the file type is not supported
            TranscriptTooShortError: If the transcript is too short
            FileNotFoundError: If the input file doesn't exist
        """
        logger.info(f"Starting article generation from input: {input_path}")
        output_base_path = self.output_dir / self._get_base_filename(input_path)
        if os.path.exists(output_base_path.with_suffix('.md')) and not rerun:
            logger.info(f"article already exists. Skipping generation. Set rerun=True to regenerate: {output_base_path.with_suffix('.md')}")
            return output_base_path.with_suffix('.md'), output_base_path.with_suffix('.meta.json')

        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        # Detect file type
        is_audio = self._is_audio_file(input_path)
        logger.info(f"Input detected as {'audio' if is_audio else 'text'} file")
        
        if is_audio:
            logger.info("Processing audio file for article generation")
            result = self.generate_article_from_audiofile(
                audio_file=input_path,
            )
        else:
            # Try to read as text file
            try:
                logger.info("Reading transcript file")
                with open(input_path, 'r') as f:
                    transcript = f.read()
                result = self.generate_article_from_transcript(
                    transcript=transcript,
                    source_file=input_path
                )
            except UnicodeDecodeError:
                error_msg = f"File {input_path} is neither a supported audio file ({', '.join(self.SUPPORTED_AUDIO_EXTENSIONS)}) nor a valid text file."
                logger.error(error_msg)
                raise UnsupportedFileTypeError(error_msg)
                
        # Save the generated article and metadata
        logger.info("Saving generated article and metadata")
        article_path, metadata_path = self._save_article(result, output_base_path)
        logger.info(f"article saved to: {article_path}")
        logger.info(f"Metadata saved to: {metadata_path}")
        return article_path, metadata_path
        
    def generate_article_from_transcript(self, 
                                    transcript: str,
                                    source_file: str) -> Dict[str, Any]:
        """
        Generate a article post from a transcript.
        
        Args:
            transcript: The input transcript text
            source_file: Optional path to the source transcript file
        Returns:
            Dictionary containing the generated content and metadata
            
        Raises:
            TranscriptTooShortError: If the transcript is too short
            AnalysisParsingError: If analysis sections cannot be parsed
        """
        # Validate transcript length
        transcript_length = len(transcript)
        logger.info(f"Processing transcript of length: {transcript_length} characters")
        
        if transcript_length < self.MIN_TRANSCRIPT_LENGTH:
            error_msg = f"Transcript is too short ({transcript_length} chars). Minimum length is {self.MIN_TRANSCRIPT_LENGTH} chars."
            logger.error(error_msg)
            raise TranscriptTooShortError(error_msg)
            
        # Track timing for each step
        step_times = {}
        
        # Step 1: Analyze the transcript
        logger.info("Step 1: Analyzing transcript for insights and themes")
        start_time = time.time()
        analysis_prompt = transcript_analysis_prompt(text=transcript)
        analysis_response = self.llm_chain.generate(
            prompt=analysis_prompt,
            thinking_tokens=4096
        )
        analysis = analysis_response.content
        step_times['analysis'] = time.time() - start_time
        logger.info(f"Transcript analysis completed in {step_times['analysis']:.2f} seconds")
        
        # Parse the analysis sections
        analysis_sections = self._parse_analysis_sections(analysis)
        
        # Step 2: Generate initial article post
        logger.info("Step 2: Writing initial article post based on analysis")
        start_time = time.time()
        article_prompt = article_writing_prompt(
            text=transcript,
            analysis=analysis
        )
        article_response = self.llm_chain.generate(
            prompt=article_prompt,
            thinking_tokens=8096
        )
        initial_article = article_response.content
        step_times['initial_article'] = time.time() - start_time
        logger.info(f"Initial article content generated in {step_times['initial_article']:.2f} seconds")
        final_article = initial_article

        # Step 3: reformat article
        # Format the final article content
        formatted_content = self._format_article_content(source_file, final_article, analysis_sections)
        
        # Calculate total time
        total_time = sum(step_times.values())
        logger.info(f"Total article generation completed in {total_time:.2f} seconds")
        
        # Process and structure the output
        output = {
            "content": formatted_content,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "type": "article",
                "transcript_length": transcript_length,
                "analysis": {
                    "insights": analysis_sections["insights"],
                    "questions": analysis_sections["questions"],
                    "themes": analysis_sections["themes"],
                    "pull_quotes": analysis_sections["pull_quotes"]
                },
                "generation_times": {
                    "analysis_time": step_times['analysis'],
                    "initial_article_time": step_times['initial_article'],
                    "total_time": total_time
                }
            }
        }
        
        # Add source file if provided
        if source_file:
            logger.info(f"Adding source file to metadata: {source_file}")
            output["metadata"]["source_transcript"] = source_file
            
        return output

    def generate_article_from_audiofile(self,
                                   audio_file: str) -> Dict[str, Any]:
        """
        Transcribe an audio file and generate a article post from it.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Dictionary containing the generated content and metadata
            
        Raises:
            UnsupportedFileTypeError: If the file is not a supported audio file
        """
        # Validate audio file type
        if not self._is_audio_file(audio_file):
            error_msg = f"File {audio_file} is not a supported audio file. Supported extensions: {', '.join(self.SUPPORTED_AUDIO_EXTENSIONS)}"
            logger.error(error_msg)
            raise UnsupportedFileTypeError(error_msg)
            
        # First transcribe the audio file
        logger.info(f"Starting transcription of audio file: {audio_file}")
        transcript_file, transcript = transcribe(
            audio_file, 
        )
        logger.info(f"Audio transcription completed. Transcript saved to: {transcript_file}")
        
        # Generate article from the transcript
        logger.info("Generating article from transcription")
        output = self.generate_article_from_transcript(
            transcript=transcript,
            source_file=transcript_file
        )
        
        # Add audio source metadata
        logger.info("Adding audio source metadata")
        output["metadata"].update({
            "source_audio": audio_file,
            "transcript_file": transcript_file
        })
        
        return output

    def _is_audio_file(self, file_path: str) -> bool:
        """Check if a file is a supported audio file."""
        ext = os.path.splitext(file_path)[1].lower()
        mime_type = mimetypes.guess_type(file_path)[0]
        
        is_audio = (ext in self.SUPPORTED_AUDIO_EXTENSIONS or 
                   (mime_type and mime_type.startswith('audio/')))
        logger.debug(f"File {file_path} audio check: {is_audio} (ext: {ext}, mime: {mime_type})")
        return is_audio

    def _format_article_content(self, input_path: str, article_content: str, analysis_sections: Dict[str, Any]) -> str:
        """Format the article content with the analysis sections in the correct places."""
        logger.debug("Formatting final article content")
        
        try:
            
            # Construct the final article with proper sections
            sections = [
                f"{self._get_header(input_path)}\n\n",
                article_content,
                "\n\n# Notes from the Conversation",
                analysis_sections["insights"],
                "\n\n# Open Questions",
                analysis_sections["questions"],
                "\n\n# Pull Quotes",
                analysis_sections["pull_quotes"]
            ]
            
            formatted_content = "\n".join(sections)
            logger.debug("Successfully formatted article content")
            return formatted_content
            
        except Exception as e:
            error_msg = f"Error formatting article content: {str(e)}"
            logger.error(error_msg)
            raise AnalysisParsingError(error_msg)

    def _get_header(self, input_path: str) -> str:
        """Get the header for the article post."""
        header = """_Editors Note: This article article is an AI-supported distillation of an in-person event held in [CITY] on [DATE] facilitated by [HOST]- it is meant to capture the conversations at the event. Quotes are paraphrased from the original conversation and all names have been changed._

👉 [Jump](https://aisalon.substack.com/i/FILLIN/notes-from-the-conversation) to a longer list of takeaways and open questions"""
        # Try to extract date from filename format "YYYY-MM-DD *"
        try:
            filename = Path(input_path).stem
            date_str = filename[:10]
            date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")
            header = header.replace("[DATE]", date)
        except (ValueError, IndexError):
            # If date parsing fails, leave as placeholder
            logger.debug("Could not parse date from filename")
            date = None
        if date:
            header = header.replace("[DATE]", date)
        return header
    
    def _get_base_filename(self, input_path: str) -> str:
        """Generate a base filename from the input path."""
        # Get the stem of the input file (name without extension)
        stem = Path(input_path).stem
        

        base_name = f"{stem}"
        logger.debug(f"Generated base filename: {base_name} from input: {input_path}")
        return base_name
    
    def _parse_analysis_sections(self, analysis: str) -> Dict[str, Any]:
        """Parse the analysis text into its component sections."""
        logger.debug("Parsing analysis sections")
        
        try:
            # Extract sections using regex
            insights_match = re.search(r'# Key Insights\n(.*?)(?=\n#)', analysis, re.DOTALL)
            questions_match = re.search(r'# Open Questions\n(.*?)(?=\n#)', analysis, re.DOTALL)
            themes_match = re.search(r'# Main Themes\n(.*?)$', analysis, re.DOTALL)
            pull_quotes_match = re.search(r'# Pull Quotes\n(.*?)$', analysis, re.DOTALL)
            
            if not all([insights_match, questions_match, themes_match]):
                raise AnalysisParsingError("Could not find all required sections in analysis")
            
            # Clean up the sections
            insights = insights_match.group(1).strip()
            questions = questions_match.group(1).strip()
            themes = themes_match.group(1).strip()
            pull_quotes = pull_quotes_match.group(1).strip() if pull_quotes_match else None
            logger.debug("Successfully parsed analysis sections")
            return {
                "insights": insights,
                "questions": questions,
                "themes": themes,
                "pull_quotes": pull_quotes
            }
        except Exception as e:
            error_msg = f"Error parsing analysis sections: {str(e)}"
            logger.error(error_msg)
            raise AnalysisParsingError(error_msg)
        
    def _save_article(self, article_info: Dict[str, Any], output_base_path: str) -> Tuple[Path, Path]:
        """
        Save the article content and metadata as separate files.
        
        Args:
            article_info: Dictionary containing article content and metadata
            output_base_path: Base path to save the article and metadata
            
        Returns:
            Tuple of (article_path, metadata_path)
        """
        # Generate base filename from input
        logger.info(f"Preparing to save files with output path: {output_base_path}")
        
        # Create directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save article content as markdown
        article_path = output_base_path.with_suffix('.md')
        logger.info(f"Saving article content to: {article_path}")
        with open(article_path, 'w') as f:
            f.write(article_info["content"])
            
        # Save metadata as JSON
        stem = Path(output_base_path).stem
        metadata_path = output_base_path.with_name(f'{stem}_meta.json')
        logger.info(f"Saving metadata to: {metadata_path}")
        with open(metadata_path, 'w') as f:
            import json
            json.dump(article_info["metadata"], f, indent=2)
            
        return article_path, metadata_path
