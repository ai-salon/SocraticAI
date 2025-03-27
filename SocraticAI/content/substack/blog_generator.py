"""Module for generating blog posts from transcripts."""

import os
import mimetypes
import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime
import time

from socraticai.core.llm import LLMChain, LLMResponse
from socraticai.content.substack.prompts import transcript_analysis_prompt, blog_writing_prompt, blog_refinement_prompt
from socraticai.transcribe.service import transcribe
from socraticai.core.utils import get_output_path

logger = logging.getLogger(__name__)

class BlogGenerationError(Exception):
    """Base exception for blog generation errors."""
    pass

class TranscriptTooShortError(BlogGenerationError):
    """Exception raised when transcript is too short."""
    pass

class UnsupportedFileTypeError(BlogGenerationError):
    """Exception raised when file type is not supported."""
    pass

class AnalysisParsingError(BlogGenerationError):
    """Exception raised when analysis sections cannot be parsed."""
    pass

class BlogGenerator:
    # Supported audio file extensions
    SUPPORTED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.aac', '.flac'}
    # Minimum transcript length (in characters)
    MIN_TRANSCRIPT_LENGTH = 1000
    
    def __init__(self, llm_chain: Optional[LLMChain] = None):
        self.llm_chain = llm_chain or LLMChain()
        self.output_dir = Path(get_output_path()) / "articles"
        logger.info(f"Initialized BlogGenerator with output directory: {self.output_dir}")
    
    def generate(self,
                input_path: str,
                rerun: bool = False) -> Tuple[Path, Path]:
        """
        Generate and save a blog post from either an audio file or transcript.
        
        Args:
            input_path: Path to either an audio file or transcript text file
            rerun: Whether to rerun the generation even if the blog already exists
        Returns:
            Tuple of (blog_path, metadata_path) where the files were saved
            
        Raises:
            UnsupportedFileTypeError: If the file type is not supported
            TranscriptTooShortError: If the transcript is too short
            FileNotFoundError: If the input file doesn't exist
        """
        logger.info(f"Starting blog generation from input: {input_path}")
        output_base_path = self.output_dir / self._get_base_filename(input_path)
        if os.path.exists(output_base_path.with_suffix('.md')) and not rerun:
            logger.info(f"Blog already exists. Skipping generation. Set rerun=True to regenerate: {output_base_path.with_suffix('.md')}")
            return output_base_path.with_suffix('.md'), output_base_path.with_suffix('.meta.json')

        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        # Detect file type
        is_audio = self._is_audio_file(input_path)
        logger.info(f"Input detected as {'audio' if is_audio else 'text'} file")
        
        if is_audio:
            logger.info("Processing audio file for blog generation")
            result = self.generate_blog_from_audiofile(
                audio_file=input_path,
            )
        else:
            # Try to read as text file
            try:
                logger.info("Reading transcript file")
                with open(input_path, 'r') as f:
                    transcript = f.read()
                result = self.generate_blog_from_transcript(
                    transcript=transcript,
                    source_file=input_path
                )
            except UnicodeDecodeError:
                error_msg = f"File {input_path} is neither a supported audio file ({', '.join(self.SUPPORTED_AUDIO_EXTENSIONS)}) nor a valid text file."
                logger.error(error_msg)
                raise UnsupportedFileTypeError(error_msg)
                
        # Save the generated blog and metadata
        logger.info("Saving generated blog and metadata")
        blog_path, metadata_path = self._save_blog(result, output_base_path)
        logger.info(f"Blog saved to: {blog_path}")
        logger.info(f"Metadata saved to: {metadata_path}")
        return blog_path, metadata_path
        
    def generate_blog_from_transcript(self, 
                                    transcript: str,
                                    source_file: str) -> Dict[str, Any]:
        """
        Generate a blog post from a transcript.
        
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
        
        # Step 2: Generate initial blog post
        logger.info("Step 2: Writing initial blog post based on analysis")
        start_time = time.time()
        blog_prompt = blog_writing_prompt(
            text=transcript,
            analysis=analysis
        )
        blog_response = self.llm_chain.generate(
            prompt=blog_prompt,
            thinking_tokens=8096
        )
        initial_blog = blog_response.content
        step_times['initial_blog'] = time.time() - start_time
        logger.info(f"Initial blog content generated in {step_times['initial_blog']:.2f} seconds")
        final_blog = initial_blog

        # Step 3: reformat blog
        # Format the final blog content
        formatted_content = self._format_blog_content(source_file, final_blog, analysis_sections)
        
        # Calculate total time
        total_time = sum(step_times.values())
        logger.info(f"Total blog generation completed in {total_time:.2f} seconds")
        
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
                    "initial_blog_time": step_times['initial_blog'],
                    "total_time": total_time
                }
            }
        }
        
        # Add source file if provided
        if source_file:
            logger.info(f"Adding source file to metadata: {source_file}")
            output["metadata"]["source_transcript"] = source_file
            
        return output

    def generate_blog_from_audiofile(self,
                                   audio_file: str) -> Dict[str, Any]:
        """
        Transcribe an audio file and generate a blog post from it.
        
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
        
        # Generate blog from the transcript
        logger.info("Generating blog from transcription")
        output = self.generate_blog_from_transcript(
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

    def _format_blog_content(self, input_path: str, blog_content: str, analysis_sections: Dict[str, Any]) -> str:
        """Format the blog content with the analysis sections in the correct places."""
        logger.debug("Formatting final blog content")
        
        try:
            
            # Construct the final blog with proper sections
            sections = [
                f"{self._get_header(input_path)}\n\n",
                blog_content,
                "\n\n# Notes from the Conversation",
                analysis_sections["insights"],
                "\n\n# Open Questions",
                analysis_sections["questions"],
                "\n\n# Pull Quotes",
                analysis_sections["pull_quotes"]
            ]
            
            formatted_content = "\n".join(sections)
            logger.debug("Successfully formatted blog content")
            return formatted_content
            
        except Exception as e:
            error_msg = f"Error formatting blog content: {str(e)}"
            logger.error(error_msg)
            raise AnalysisParsingError(error_msg)

    def _get_header(self, input_path: str) -> str:
        """Get the header for the blog post."""
        header = """_Editors Note: This blog article is an AI-supported distillation of an in-person event held in [CITY] on [DATE] facilitated by [HOST]- it is meant to capture the conversations at the event. Quotes are paraphrased from the original conversation and all names have been changed._

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
        
    def _save_blog(self, blog_info: Dict[str, Any], output_base_path: str) -> Tuple[Path, Path]:
        """
        Save the blog content and metadata as separate files.
        
        Args:
            blog_info: Dictionary containing blog content and metadata
            output_base_path: Base path to save the blog and metadata
            
        Returns:
            Tuple of (blog_path, metadata_path)
        """
        # Generate base filename from input
        logger.info(f"Preparing to save files with output path: {output_base_path}")
        
        # Create directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save blog content as markdown
        blog_path = output_base_path.with_suffix('.md')
        logger.info(f"Saving blog content to: {blog_path}")
        with open(blog_path, 'w') as f:
            f.write(blog_info["content"])
            
        # Save metadata as JSON
        stem = Path(output_base_path).stem
        metadata_path = output_base_path.with_name(f'{stem}_meta.json')
        logger.info(f"Saving metadata to: {metadata_path}")
        with open(metadata_path, 'w') as f:
            import json
            json.dump(blog_info["metadata"], f, indent=2)
            
        return blog_path, metadata_path
