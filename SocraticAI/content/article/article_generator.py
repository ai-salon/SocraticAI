"""Module for generating article posts from transcripts."""

import os
import mimetypes
import logging
import re
import json
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List, Union
from datetime import datetime
import time

from socraticai.core.llm import LLMChain
from socraticai.core.colored_logging import get_colored_logger
from socraticai.content.article.prompts import (
    transcript_analysis_prompt, 
    article_writing_prompt, 
    article_refinement_prompt, 
    combine_articles_prompt,
    synthesize_analysis_sections_prompt,
    multi_source_transcript_analysis_prompt,
    multi_source_article_writing_prompt,
    combined_title_prompt
)
from socraticai.transcribe.service import transcribe
from socraticai.core.utils import (
    get_output_path,
    get_model_context_limit,
    estimate_transcript_tokens,
    group_transcripts_by_context
)
from socraticai.config import DEFAULT_LLM_MODEL

logger = logging.getLogger(__name__)
colored_logger = get_colored_logger(__name__)

class ArticleGenerationError(Exception):
    """Base exception for article generation errors."""
    pass

class TranscriptTooShortError(ArticleGenerationError):
    """Exception raised when transcript is too short."""
    pass

class UnsupportedFileTypeError(ArticleGenerationError):
    """Exception raised when file type is not supported."""
    pass

class AnalysisParsingError(ArticleGenerationError):
    """Exception raised when analysis sections cannot be parsed."""
    pass

class ArticleGenerator:
    SUPPORTED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.aac', '.flac'}
    MIN_TRANSCRIPT_LENGTH = 1000
    def __init__(self, model: Optional[str] = None, refine: bool = True):
        """Initialize the ArticleGenerator.
        
        Args:
            model: Optional model to use for generation. Defaults to DEFAULT_LLM_MODEL.
            refine: Whether to refine the generated article with an additional pass.
                   Defaults to True.
        """
        self.default_model = model or DEFAULT_LLM_MODEL
        self.llm_chain = LLMChain(model=self.default_model) # Initialize with default, can be overridden in generate
        self.output_dir = Path(get_output_path()) / "articles"
        self.refine = refine
        colored_logger.setup_rich_logging()
        logger.info(f"Initialized ArticleGenerator with default model: {self.default_model}, output directory: {self.output_dir}")
    
    def generate(
        self,
        input_paths: Union[str, List[str]],
        rerun: bool = False,
        anonymize: bool = True,
        model: Optional[str] = None
    ) -> Tuple[Path, Path]:
        """
        Generate and save an article post from one or more audio files or transcripts.
        
        New Context-Aware Flow:
        1. Transcribe one or more files
        2. Estimate total length using model-specific context limits
        3. Break into transcript groups if necessary to fit context
        4. Process each group to get insights, questions, quotes, and article
        5. Combine articles and analysis sections together
        
        Args:
            input_paths: Path to a single audio/transcript file or a list of paths.
            rerun: Whether to rerun generation even if articles exist.
            anonymize: Whether to anonymize transcripts (for audio inputs). Defaults to True.
            model: Optional LLM model to use for this generation, overrides instance default.
        Returns:
            Tuple of (article_path, metadata_path) for the final (potentially combined) article.
        Raises:
            Various ArticleGenerationError subclasses for specific failures.
        """
        current_model = model or self.default_model
        start_time = time.time()
        
        if isinstance(input_paths, str):
            input_paths = [input_paths]

        if not input_paths:
            raise ValueError("No input paths provided.")

        # Step 0: Check if we should skip generation entirely
        if len(input_paths) == 1:
            output_base_path = self.output_dir / self._get_base_filename(input_paths[0])
        else:
            # For multi-source, we'll generate a temporary path first
            # The final path will be determined after we generate the title
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_names = "_&_".join([self._get_base_filename(p, include_date=False) for p in input_paths])
            temp_combined_filename_stem = f"combined_{base_names[:50]}_{timestamp}"
            output_base_path = self.output_dir / temp_combined_filename_stem
        
        # Check if we should skip generation
        if not rerun and output_base_path.with_suffix('.md').exists():
            colored_logger.file_exists_skip(str(output_base_path.with_suffix('.md')))
            return output_base_path.with_suffix('.md'), output_base_path.with_name(output_base_path.name + '_meta.json')

        # Step 1: Transcribe all files and get transcripts
        colored_logger.step_start(1, 5, "Transcribing input files")
        transcripts = self._transcribe_all_inputs(input_paths, anonymize, current_model)
        
        # Step 2: Estimate total length and determine processing strategy
        colored_logger.step_start(2, 5, "Context analysis and grouping")
        transcript_groups = self._group_transcripts_by_context(transcripts, current_model)
        
        # Step 3: Process each group
        colored_logger.step_start(3, 5, f"Processing {len(transcript_groups)} transcript groups")
        group_results = []
        for i, group in enumerate(transcript_groups):
            group_result = self._process_transcript_group(group, current_model)
            group_results.append(group_result)
        
        # Step 4: Combine results if multiple groups
        if len(group_results) == 1:
            colored_logger.step_start(4, 5, "Formatting final article")
            final_result = group_results[0]
        else:
            colored_logger.step_start(4, 5, f"Combining {len(group_results)} group results")
            final_result = self._combine_group_results(group_results, current_model)
        
        # Step 5: Save final article
        colored_logger.step_start(5, 5, "Saving final article")
        
        # For multi-source articles, generate a proper filename with title and date range
        if len(input_paths) > 1:
            generated_title = self._generate_combined_title(final_result["article_content"], current_model)
            first_date, last_date = self._get_date_range_from_inputs(input_paths)
            
            if first_date == last_date:
                date_range = first_date
            else:
                date_range = f"{first_date}_{last_date}"
                
            final_filename = f"combined_{generated_title}_{date_range}"
            output_base_path = self.output_dir / final_filename
        
        # Format and save the final article
        formatted_content = self._format_article_content(
            str(output_base_path),
            final_result["article_content"],
            final_result["analysis_sections"],
            is_combined_article=len(input_paths) > 1,
            header_override=final_result.get("header")
        )
        
        article_data = {
            "content": formatted_content,
            "metadata": final_result["metadata"]
        }
        
        return self._save_article(article_data, output_base_path)

    def _transcribe_all_inputs(self, input_paths: List[str], anonymize: bool, model: str) -> List[Dict[str, str]]:
        """
        Transcribe all input files and return transcript data.
        
        Args:
            input_paths: List of paths to audio or transcript files
            anonymize: Whether to anonymize transcripts
            model: Model name for context estimation
            
        Returns:
            List of transcript dictionaries with 'content' and 'source' keys
        """
        transcripts = []
        
        for input_path in input_paths:
            if not os.path.exists(input_path):
                colored_logger.error("File processing", f"Input file not found: {input_path}")
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            is_audio = self._is_audio_file(input_path)
            filename = os.path.basename(input_path)
            
            if is_audio:
                # Transcribe audio file
                start_time = time.time()
                transcript_file, transcript_content = transcribe(input_path, anonymize=anonymize)
                duration = time.time() - start_time
                source_file = transcript_file
                colored_logger.transcription_complete(filename, os.path.basename(transcript_file), duration)
            else:
                # Read transcript file
                colored_logger.transcription_found(filename, input_path)
                try:
                    with open(input_path, 'r', encoding='utf-8') as f:
                        transcript_content = f.read()
                    source_file = input_path
                except UnicodeDecodeError:
                    error_msg = f"File {input_path} is neither a supported audio file nor a valid text file."
                    colored_logger.error("File reading", error_msg)
                    raise UnsupportedFileTypeError(error_msg)
            
            # Validate transcript length
            if len(transcript_content) < self.MIN_TRANSCRIPT_LENGTH:
                raise TranscriptTooShortError(
                    f"Transcript from {input_path} is too short ({len(transcript_content)} chars). "
                    f"Minimum is {self.MIN_TRANSCRIPT_LENGTH}."
                )
            
            transcripts.append({
                'content': transcript_content,
                'source': source_file,
                'original_input': input_path,
                'is_audio': is_audio,
                'anonymized': anonymize if is_audio else False
            })
        
        # Token estimation for context planning
        total_tokens = sum(estimate_transcript_tokens(t['content'], model) for t in transcripts)
        colored_logger.token_estimation(len(transcripts), total_tokens, model)
        
        return transcripts

    def _group_transcripts_by_context(self, transcripts: List[Dict[str, str]], model: str) -> List[List[Dict[str, str]]]:
        """
        Group transcripts by context window limits.
        
        Args:
            transcripts: List of transcript dictionaries
            model: Model name to determine context limits
            
        Returns:
            List of transcript groups that fit within context limits
        """
        colored_logger.context_grouping_start(len(transcripts), model)
        groups = group_transcripts_by_context(transcripts, model)
        total_tokens = sum(estimate_transcript_tokens(t['content'], model) for group in groups for t in group)
        colored_logger.context_grouping_complete(len(groups), total_tokens)
        return groups

    def _process_transcript_group(self, transcript_group: List[Dict[str, str]], model: str) -> Dict[str, Any]:
        """
        Process a group of transcripts to generate analysis and article content.
        
        Args:
            transcript_group: List of transcript dictionaries
            model: Model to use for generation
            
        Returns:
            Dictionary containing article content, analysis sections, and metadata
        """
        logger.info(f"Processing transcript group with {len(transcript_group)} transcripts")
        
        if len(transcript_group) == 1:
            # Single transcript - use existing single-transcript flow
            return self._process_single_transcript(transcript_group[0], model)
        else:
            # Multiple transcripts - use new multi-source flow
            return self._process_multi_source_transcripts(transcript_group, model)

    def _process_single_transcript(self, transcript_data: Dict[str, str], model: str) -> Dict[str, Any]:
        """
        Process a single transcript using the original flow.
        
        Args:
            transcript_data: Transcript dictionary with content and metadata
            model: Model to use for generation
            
        Returns:
            Dictionary containing article content, analysis sections, and metadata
        """
        transcript_content = transcript_data['content']
        source_file = transcript_data['source']
        
        step_times = {}
        
        # Step 1: Analyze transcript
        colored_logger.analysis_start(1, model)
        start_time = time.time()
        analysis_prompt_text = transcript_analysis_prompt(text=transcript_content)
        analysis_response = self.llm_chain.generate(
            prompt=analysis_prompt_text, 
            max_tokens=16384,
            thinking_tokens=8192, 
            model=model
        )
        
        if analysis_response is None or analysis_response.content is None:
            colored_logger.error("Analysis generation", f"LLM returned no response for transcript analysis using {model}")
            raise ArticleGenerationError(f"Failed to generate analysis - LLM returned no response using {model}")
        
        analysis_raw = analysis_response.content
        step_times['analysis'] = time.time() - start_time
        
        # Parse analysis sections
        analysis_sections = self._parse_analysis_sections(analysis_raw)
        insights_count = len(analysis_sections.get('insights', "").split("\n"))
        themes_count = len(analysis_sections.get('themes', "").split("##"))
        colored_logger.analysis_complete(insights_count, themes_count, step_times['analysis'])
        
        # Step 2: Generate initial article
        colored_logger.article_generation_start("single transcript", model)
        start_time = time.time()
        article_prompt_text = article_writing_prompt(text=transcript_content, analysis=analysis_raw)
        article_response = self.llm_chain.generate(
            prompt=article_prompt_text, 
            max_tokens=8192,
            thinking_tokens=8192, 
            model=model
        )
        
        if article_response is None or article_response.content is None:
            colored_logger.error("Article generation", f"LLM returned no response for article generation using {model}")
            raise ArticleGenerationError(f"Failed to generate article - LLM returned no response using {model}")
        
        article_content = article_response.content
        step_times['article'] = time.time() - start_time
        word_count = len(article_content.split())
        colored_logger.article_generation_complete(word_count, step_times['article'])
        
        # Step 3: Refine article (optional)
        if self.refine:
            colored_logger.article_refinement_start(model)
            start_time = time.time()
            refinement_prompt_text = article_refinement_prompt(
                analysis=analysis_raw, 
                article=article_content
            )
            refinement_response = self.llm_chain.generate(
                prompt=refinement_prompt_text, 
                max_tokens=8192,
                thinking_tokens=8192, 
                model=model
            )
            article_content = refinement_response.content
            step_times['refinement'] = time.time() - start_time
            colored_logger.article_refinement_complete(step_times['refinement'])
            logger.info(f"Article refinement completed in {step_times['refinement']:.2f}s")
        
        # Build metadata
        total_time = sum(step_times.values())
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "type": "article",
            "model_used": model,
            "transcript_length": len(transcript_content),
            "analysis_summary": {k: v[:200] + '...' if isinstance(v, str) and len(v) > 200 else v for k,v in analysis_sections.items()},
            "generation_times": {**step_times, "total_time": total_time},
            "source_transcript": source_file,
            "analysis_sections_raw": analysis_raw,
            "parsed_analysis_sections": analysis_sections,
            "raw_llm_article_content": article_content
        }
        
        # Add audio-specific metadata if applicable
        if transcript_data.get('is_audio'):
            metadata.update({
                "source_audio": transcript_data['original_input'],
                "anonymized": transcript_data.get('anonymized', False)
            })
        
        return {
            "article_content": article_content,
            "analysis_sections": analysis_sections,
            "metadata": metadata
        }

    def _process_multi_source_transcripts(self, transcript_group: List[Dict[str, str]], model: str) -> Dict[str, Any]:
        """
        Process multiple transcripts together using the new multi-source flow.
        
        Args:
            transcript_group: List of transcript dictionaries
            model: Model to use for generation
            
        Returns:
            Dictionary containing article content, analysis sections, and metadata
        """
        
        # Prepare combined transcript text with source delineation
        combined_transcript_parts = []
        source_files = []
        original_inputs = []
        
        for i, transcript_data in enumerate(transcript_group):
            source_label = f"Source {i+1}"
            combined_transcript_parts.append(
                f"--- {source_label}: {Path(transcript_data['source']).name} ---\n"
                f"{transcript_data['content']}\n"
                f"--- End of {source_label} ---"
            )
            source_files.append(transcript_data['source'])
            original_inputs.append(transcript_data['original_input'])
        
        combined_transcript = "\n\n".join(combined_transcript_parts)
        
        step_times = {}
        
        # Step 1: Analyze combined transcripts
        colored_logger.analysis_start(len(transcript_group), model)
        start_time = time.time()
        analysis_prompt_text = multi_source_transcript_analysis_prompt(transcripts_text=combined_transcript)
        analysis_response = self.llm_chain.generate(
            prompt=analysis_prompt_text, 
            max_tokens=16384,
            thinking_tokens=8192, 
            model=model
        )
        
        if analysis_response is None or analysis_response.content is None:
            colored_logger.error("Multi-source analysis", f"LLM returned no response for multi-source analysis using {model}")
            raise ArticleGenerationError(f"Failed to generate multi-source analysis - LLM returned no response using {model}")
        
        analysis_raw = analysis_response.content
        step_times['analysis'] = time.time() - start_time
        
        # Parse analysis sections
        analysis_sections = self._parse_analysis_sections(analysis_raw)
        insights_count = len(analysis_sections.get('insights', []))
        themes_count = len(analysis_sections.get('themes', []))
        colored_logger.analysis_complete(insights_count, themes_count, step_times['analysis'])
        
        # Step 2: Generate article from combined content
        colored_logger.article_generation_start(f"{len(transcript_group)} transcripts", model)
        start_time = time.time()
        article_prompt_text = multi_source_article_writing_prompt(
            transcripts_text=combined_transcript, 
            analysis=analysis_raw
        )
        article_response = self.llm_chain.generate(
            prompt=article_prompt_text, 
            max_tokens=8192,
            thinking_tokens=16384, 
            model=model
        )
        
        if article_response is None or article_response.content is None:
            colored_logger.error("Multi-source article generation", f"LLM returned no response for multi-source article generation using {model}")
            raise ArticleGenerationError(f"Failed to generate multi-source article - LLM returned no response using {model}")
        
        article_content = article_response.content
        step_times['article'] = time.time() - start_time
        word_count = len(article_content.split())
        colored_logger.article_generation_complete(word_count, step_times['article'])
        
        # Step 3: Refine article (optional)
        if self.refine:
            colored_logger.article_refinement_start(model)
            start_time = time.time()
            refinement_prompt_text = article_refinement_prompt(
                analysis=analysis_raw, 
                article=article_content
            )
            refinement_response = self.llm_chain.generate(
                prompt=refinement_prompt_text, 
                max_tokens=8192,
                thinking_tokens=8192, 
                model=model
            )
            article_content = refinement_response.content
            step_times['refinement'] = time.time() - start_time
            colored_logger.article_refinement_complete(step_times['refinement'])
        
        # Build metadata
        total_time = sum(step_times.values())
        total_transcript_length = sum(len(t['content']) for t in transcript_group)
        
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "type": "multi_source_article",
            "model_used": model,
            "source_count": len(transcript_group),
            "total_transcript_length": total_transcript_length,
            "generation_times": {**step_times, "total_time": total_time},
            "source_transcripts": source_files,
            "original_inputs": original_inputs,
            "analysis_sections_raw": analysis_raw,
            "parsed_analysis_sections": analysis_sections
        }
        
        # Add audio-specific metadata if applicable
        audio_sources = [t['original_input'] for t in transcript_group if t.get('is_audio')]
        if audio_sources:
            metadata["source_audio_files"] = audio_sources
            metadata["anonymized"] = any(t.get('anonymized', False) for t in transcript_group)
        
        # Generate header for multi-source article
        header = self._get_header(original_inputs, is_combined=True, num_sources=len(transcript_group))
        
        return {
            "article_content": article_content,
            "analysis_sections": analysis_sections,
            "metadata": metadata,
            "header": header
        }

    def _combine_group_results(self, group_results: List[Dict[str, Any]], model: str) -> Dict[str, Any]:
        """
        Combine results from multiple transcript groups.
        
        Args:
            group_results: List of group result dictionaries
            model: Model to use for combination
            
        Returns:
            Combined result dictionary
        """
        colored_logger.combining_start(len(group_results), model)
        start_time = time.time()
        
        # Combine article content
        article_texts = []
        for i, result in enumerate(group_results):
            article_texts.append(
                f"--- Group {i+1} ---\n{result['article_content']}\n--- End of Group {i+1} ---"
            )
        
        combined_article_text = "\n\n".join(article_texts)
        combination_prompt_text = combine_articles_prompt(article_texts=combined_article_text)
        
        # Estimate thinking tokens
        thinking_budget = min(16384, len(combination_prompt_text.split()) + len(combined_article_text.split()))
        
        combination_response = self.llm_chain.generate(
            prompt=combination_prompt_text,
            thinking_tokens=thinking_budget,
            model=model,
            max_tokens=16384
        )
        final_article_content = combination_response.content
        combination_duration = time.time() - start_time
        final_word_count = len(final_article_content.split())
        colored_logger.combining_complete(final_word_count, combination_duration)
        
        # Combine analysis sections
        analysis_sections_for_synthesis = []
        for i, result in enumerate(group_results):
            analysis_sections_for_synthesis.append({
                "identifier": f"Group {i+1}",
                "sections": result["metadata"]["analysis_sections_raw"]
            })
        
        combined_analysis_input = "\n\n".join([
            f"--- {item['identifier']} ---\n{item['sections']}\n--- End of {item['identifier']} ---"
            for item in analysis_sections_for_synthesis
        ])
        
        synthesis_prompt_text = synthesize_analysis_sections_prompt(
            analysis_sections_texts=combined_analysis_input
        )
        
        synthesis_response = self.llm_chain.generate(
            prompt=synthesis_prompt_text,
            max_tokens=16384,
            thinking_tokens=16384,
            model=model
        )
        
        combined_analysis_sections = self._parse_analysis_sections(synthesis_response.content)
        
        # Combine metadata
        all_source_files = []
        all_original_inputs = []
        total_transcript_length = 0
        
        for result in group_results:
            metadata = result["metadata"]
            if "source_transcripts" in metadata:
                all_source_files.extend(metadata["source_transcripts"])
            elif "source_transcript" in metadata:
                all_source_files.append(metadata["source_transcript"])
            
            if "original_inputs" in metadata:
                all_original_inputs.extend(metadata["original_inputs"])
            
            total_transcript_length += metadata.get("total_transcript_length", 
                                                   metadata.get("transcript_length", 0))
        
        combined_metadata = {
            "generated_at": datetime.now().isoformat(),
            "type": "combined_multi_group_article",
            "model_used": model,
            "group_count": len(group_results),
            "total_transcript_length": total_transcript_length,
            "source_transcripts": all_source_files,
            "original_inputs": all_original_inputs,
            "analysis_sections_raw": synthesis_response.content,
            "parsed_analysis_sections": combined_analysis_sections
        }
        
        # Generate header for combined article
        header = self._get_header(all_original_inputs, is_combined=True, num_sources=len(all_source_files))
        
        return {
            "article_content": final_article_content,
            "analysis_sections": combined_analysis_sections,
            "metadata": combined_metadata,
            "header": header
        }



    def _is_audio_file(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        mime_type = mimetypes.guess_type(file_path)[0]
        is_audio = (ext in self.SUPPORTED_AUDIO_EXTENSIONS or (mime_type and mime_type.startswith('audio/')))
        logger.debug(f"File {file_path} audio check: {is_audio} (ext: {ext}, mime: {mime_type})")
        return is_audio

    def _format_article_content(self, 
                                input_path_or_stem: str, 
                                article_content: str, 
                                analysis_sections: Dict[str, Any],
                                is_combined_article: bool = False,
                                header_override: Optional[str] = None) -> str:
        logger.debug("Formatting final article content")
        try:
            if header_override:
                header = header_override
            else:
                header = self._get_header(input_path_or_stem, is_combined=is_combined_article)
            
            sections_to_append = [
                f"{header}\n\n",
                article_content,
                "\n\n# Notes from the Conversation",
                analysis_sections.get("insights", "Insights not available."),
                "\n\n# Open Questions",
                analysis_sections.get("questions", "Open questions not available."),
                "\n\n# Pull Quotes",
                analysis_sections.get("pull_quotes", "Pull quotes not available.")
            ]
            formatted_content = "\n".join(sections_to_append)
            logger.debug("Successfully formatted article content")
            return formatted_content
        except Exception as e:
            logger.error(f"Error formatting article content: {str(e)}", exc_info=True)
            raise AnalysisParsingError(f"Error formatting article content: {str(e)}")

    def _get_header(self, input_path_or_paths: Union[str, List[str]], is_combined: bool = False, num_sources: Optional[int] = None) -> str:
        base_header = """_Editors Note: This article is an AI-supported distillation of {source_description} - it is meant to capture the conversations at the event. Transcripts are fed into our custom tool, [SocraticAI](https://github.com/ai-salon/SocraticAI), to create these blogs, followed by human editing. Quotes are paraphrased from the original conversation and all names have been changed._

👉 [Jump](https://aisalon.substack.com/i/FILLIN/notes-from-the-conversation) to a longer list of takeaways and open questions"""

        date_str_for_header = "[DATE]"
        city_str = "[CITY]"
        host_str = "[HOST]"

        if is_combined and isinstance(input_path_or_paths, list):
            source_description = f"{num_sources or len(input_path_or_paths)} discussions/events held in {city_str} around {date_str_for_header} facilitated by {host_str}"
        elif isinstance(input_path_or_paths, str):
            input_path = input_path_or_paths
            try:
                filename = Path(input_path).stem
                date_match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
                if date_match:
                    extracted_date = datetime.strptime(date_match.group(1), "%Y-%m-%d").strftime("%B %d, %Y")
                    date_str_for_header = extracted_date
                else:
                    logger.debug(f"Could not parse date from filename: {filename} for header.")
            except (ValueError, IndexError):
                logger.debug(f"Error parsing date from filename: {filename} for header.")
            source_description = f"an in-person event held in {city_str} on {date_str_for_header} facilitated by {host_str}"
        else:
            source_description = f"a discussion held in {city_str} on {date_str_for_header} facilitated by {host_str}"
        
        header = base_header.format(source_description=source_description)
        return header
    
    def _get_base_filename(self, input_path: str, include_date: bool = True) -> str:
        stem = Path(input_path).stem
        if include_date:
            return stem
        else:
            name_part = re.sub(r"^(\d{4}[-_]?\d{2}[-_]?\d{2}[-_]?)+", '', stem).lstrip('-_ ')
            return name_part if name_part else stem
    
    def _generate_combined_title(self, article_content: str, model: str) -> str:
        """
        Generate a concise title for a combined article using LLM.
        
        Args:
            article_content: The generated article content to analyze
            model: Model to use for title generation
            
        Returns:
            A short, descriptive title suitable for filename
        """
        colored_logger.info("Generating combined article title")
        
        # Use first 2000 characters for title generation to keep prompt size reasonable
        content_sample = article_content[:2000]
        if len(article_content) > 2000:
            content_sample += "..."
            
        title_prompt_text = combined_title_prompt(article_content=content_sample)
        
        try:
            response = self.llm_chain.generate(
                prompt=title_prompt_text,
                max_tokens=50,  # Very small since we only want a few words
                temperature=0.3,  # Lower temperature for more consistent results
                model=model
            )
            
            # Clean up the response to ensure it's filename-safe
            title = response.content.strip().strip('"\'')
            title = re.sub(r'[^a-zA-Z0-9_-]', '_', title)
            title = re.sub(r'_+', '_', title).strip('_')
            
            if not title or len(title) < 2:
                title = "Combined_Discussion"
                
            colored_logger.success(f"Generated title: {title}")
            return title
            
        except Exception as e:
            logger.warning(f"Failed to generate title: {e}. Using fallback.")
            return "Combined_Discussion"
    
    def _extract_date_from_filename(self, filename: str) -> Optional[str]:
        """
        Extract date from filename in various formats.
        
        Returns date in YYYYMMDD format or None if not found.
        """
        stem = Path(filename).stem
        
        # Common date patterns
        patterns = [
            r'(\d{4}[-_]?\d{2}[-_]?\d{2})',  # YYYY-MM-DD, YYYY_MM_DD, YYYYMMDD
            r'(\d{2}[-_]?\d{2}[-_]?\d{4})',  # MM-DD-YYYY, MM_DD_YYYY, MMDDYYYY
            r'(\d{4}[-_]?\d{1,2}[-_]?\d{1,2})',  # YYYY-M-D variants
        ]
        
        for pattern in patterns:
            match = re.search(pattern, stem)
            if match:
                date_str = match.group(1)
                # Normalize to YYYYMMDD format
                date_str = re.sub(r'[-_]', '', date_str)
                
                # Handle different formats
                if len(date_str) == 8:  # YYYYMMDD or MMDDYYYY
                    if date_str[:4] > '1900' and date_str[:4] < '2100':  # Likely YYYYMMDD
                        return date_str
                    elif date_str[4:] > '1900' and date_str[4:] < '2100':  # Likely MMDDYYYY
                        return date_str[4:] + date_str[:4]
                
                # Add more date parsing as needed
                break
                
        return None
    
    def _get_date_range_from_inputs(self, input_paths: List[str]) -> Tuple[str, str]:
        """
        Extract date range from input filenames.
        
        Returns:
            Tuple of (first_date, last_date) in YYYYMMDD format, or current date if no dates found
        """
        dates = []
        current_date = datetime.now().strftime("%Y%m%d")
        
        for path in input_paths:
            filename = os.path.basename(path)
            date_str = self._extract_date_from_filename(filename)
            if date_str:
                dates.append(date_str)
        
        if not dates:
            # No dates found, use current date
            return current_date, current_date
            
        dates.sort()
        return dates[0], dates[-1]
    
    def _parse_analysis_sections(self, analysis: str) -> Dict[str, Any]:
        logger.debug("Parsing analysis sections")
        sections = {}
        analysis_with_marker = analysis.strip() + "\n\n#END_OF_ANALYSIS_MARKER\n"

        section_titles = {
            "insights": "Key Insights",
            "questions": "Open Questions",
            "themes": "Main Themes",
            "pull_quotes": "Pull Quotes"
        }
        
        all_known_titles_regex = "|".join([re.escape(t) for t in section_titles.values()])

        for key, title in section_titles.items():
            pattern = rf"""#\s*{re.escape(title)}\s*
(.*?)(?=\s*\n(?:#\s*(?:{all_known_titles_regex}|END_OF_ANALYSIS_MARKER)|$))"""
            match = re.search(pattern, analysis_with_marker, re.DOTALL | re.IGNORECASE)
            
            if match:
                sections[key] = match.group(1).strip()
            else:
                logger.warning(f"Could not find section '{title}' in analysis. It will be empty.")
                sections[key] = f"[{title} not found in analysis]"
        
        if not any(sections[key] != f"[{section_titles[key]} not found in analysis]" for key in sections):
             logger.error(f"Could not parse any substantive sections from analysis. Analysis (first 500 chars):\n{analysis[:500]}...")

        return sections
        
    def _save_article(self, article_info: Dict[str, Any], output_base_path: Path) -> Tuple[Path, Path]:
        os.makedirs(self.output_dir, exist_ok=True)

        article_path = output_base_path.with_suffix('.md')
        colored_logger.file_save_start(os.path.basename(article_path), "article")
        with open(article_path, 'w') as f:
            f.write(article_info["content"])
        article_size_kb = os.path.getsize(article_path) / 1024
        colored_logger.file_save_complete(str(article_path), article_size_kb)
            
        metadata_path = output_base_path.with_name(output_base_path.name + '_meta.json')
        colored_logger.file_save_start(os.path.basename(metadata_path), "metadata")
        with open(metadata_path, 'w') as f:
            json.dump(article_info["metadata"], f, indent=2)
        metadata_size_kb = os.path.getsize(metadata_path) / 1024
        colored_logger.file_save_complete(str(metadata_path), metadata_size_kb)
            
        return article_path, metadata_path

