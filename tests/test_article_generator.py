import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import json
from pathlib import Path
import tempfile
import shutil
from datetime import datetime
import logging

from socraticai.content.article.article_generator import (
    ArticleGenerator,
    TranscriptTooShortError,
    UnsupportedFileTypeError,
    AnalysisParsingError
)
from socraticai.core.llm import LLMChain # Ensure this can be imported or mock its usage
from socraticai.config import TEST_GOOGLE_MODEL as TEST_LLM_MODEL

# Mock the LLMChain if it's complex to instantiate or has external dependencies
class MockLLMResponse:
    def __init__(self, content):
        self.content = content

class TestArticleGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up logging for the test class."""
        cls.logger = logging.getLogger(__name__)

    def setUp(self):
        """Set up test environment."""
        self.logger.info(f"Starting setUp for {self._testMethodName}")
        self.test_dir = tempfile.mkdtemp()
        self.output_path_patch = patch('socraticai.core.utils.get_output_path', return_value=self.test_dir)
        self.mock_output_path = self.output_path_patch.start()

        self.TEST_LLM_MODEL = TEST_LLM_MODEL # Use the imported model

        self.transcript_path = Path(__file__).parent / "test_transcript.txt"
        with open(self.transcript_path, 'r') as f:
            self.sample_transcript = f.read()

        # Use autospec=True for stricter mocking
        self.mock_llm_chain_patch = patch('socraticai.content.article.article_generator.LLMChain', autospec=True)
        self.MockLLMChain = self.mock_llm_chain_patch.start()
        self.mock_llm_instance = self.MockLLMChain.return_value
        # Default mock response; can be overridden per test using _mock_llm_generate
        self.mock_llm_instance.generate.return_value = MockLLMResponse("Default Mocked LLM content")

        # Initialize the ArticleGenerator after setting up the mock
        self.generator = ArticleGenerator(model=self.TEST_LLM_MODEL)
        self.generator.output_dir = Path(self.test_dir) / "articles" # Ensure output is within test_dir

        # Now mock the actual llm_chain instance that was created
        self.generator.llm_chain = self.mock_llm_instance

        self.min_transcript_length = ArticleGenerator.MIN_TRANSCRIPT_LENGTH
        self.logger.info(f"Finished setUp for {self._testMethodName}")

    def _mock_llm_generate(self, side_effects):
        """Helper to set up mock LLM responses."""
        if not isinstance(side_effects, list):
            side_effects = [side_effects]

        # Ensure each item in side_effects will produce a MockLLMResponse
        mock_responses = []
        for content in side_effects:
            if isinstance(content, Exception): # Allow mocking exceptions
                mock_responses.append(content)
            else:
                mock_responses.append(MockLLMResponse(str(content)))
        self.mock_llm_instance.generate.side_effect = mock_responses

    def tearDown(self):
        """Clean up test environment."""
        self.logger.info(f"Starting tearDown for {self._testMethodName}")
        self.output_path_patch.stop()
        self.mock_llm_chain_patch.stop()
        if os.path.exists(self.test_dir): # Ensure directory exists before trying to remove
            shutil.rmtree(self.test_dir)
        self.logger.info(f"Finished tearDown for {self._testMethodName}")

    def test_initialization(self):
        """Test ArticleGenerator initialization."""
        self.logger.info(f"Running test: {self._testMethodName}")
        self.assertEqual(self.generator.default_model, self.TEST_LLM_MODEL)
        self.assertTrue(self.generator.refine)  # Default is True, not False
        self.assertTrue(str(self.generator.output_dir).endswith("articles"))
        self.assertEqual(self.generator.default_model, self.TEST_LLM_MODEL)

    def test_get_base_filename(self):
        """Test _get_base_filename method."""
        self.logger.info(f"Running test: {self._testMethodName}")
        self.assertEqual(self.generator._get_base_filename("/path/to/2023-01-01-event.txt"), "2023-01-01-event")
        self.assertEqual(self.generator._get_base_filename("no_date_event.mp3"), "no_date_event")
        self.assertEqual(self.generator._get_base_filename("/a/b/c/2024_02_15_another_event.m4a", include_date=True), "2024_02_15_another_event")
        self.assertEqual(self.generator._get_base_filename("/a/b/c/2024_02_15_another_event.m4a", include_date=False), "another_event")
        self.assertEqual(self.generator._get_base_filename("only_date_2023-10-10.txt", include_date=False), "only_date_2023-10-10")
        self.assertEqual(self.generator._get_base_filename("2023-10-10-event-name.txt", include_date=False), "event-name")

    def test_is_audio_file(self):
        """Test _is_audio_file method."""
        self.logger.info(f"Running test: {self._testMethodName}")
        for ext in ArticleGenerator.SUPPORTED_AUDIO_EXTENSIONS:
            self.assertTrue(self.generator._is_audio_file(f"test{ext}"))
        self.assertFalse(self.generator._is_audio_file("test.txt"))
        self.assertFalse(self.generator._is_audio_file("test.md"))
        with patch('mimetypes.guess_type', return_value=('audio/ogg', None)):
            self.assertTrue(self.generator._is_audio_file("test.ogg"))
        with patch('mimetypes.guess_type', return_value=('application/json', None)):
            self.assertFalse(self.generator._is_audio_file("test.json_as_audio_ext"))

    def test_parse_analysis_sections(self):
        """Test _parse_analysis_sections method."""
        self.logger.info(f"Running test: {self._testMethodName}")
        analysis_text = """
# Key Insights
- Insight 1
- Insight 2

# Open Questions
- Question 1?

# Main Themes
- Theme A
- Theme B

# Pull Quotes
"This is a quote." - Speaker
        """
        expected_sections = {
            "insights": "- Insight 1\n- Insight 2",
            "questions": "- Question 1?",
            "themes": "- Theme A\n- Theme B",
            "pull_quotes": '"This is a quote." - Speaker'
        }
        sections = self.generator._parse_analysis_sections(analysis_text)
        self.assertEqual(sections, expected_sections)

    def test_parse_analysis_sections_missing_sections(self):
        """Test _parse_analysis_sections with some sections missing."""
        self.logger.info(f"Running test: {self._testMethodName}")
        analysis_text = """
# Key Insights
- Only insight.

# Pull Quotes
"Just a quote."
        """
        sections = self.generator._parse_analysis_sections(analysis_text)
        self.assertEqual(sections["insights"], "- Only insight.")
        self.assertEqual(sections["pull_quotes"], '"Just a quote."')
        self.assertEqual(sections["questions"], "[Open Questions not found in analysis]")
        self.assertEqual(sections["themes"], "[Main Themes not found in analysis]")

    def test_parse_analysis_sections_empty_input(self):
        """Test _parse_analysis_sections with empty input."""
        self.logger.info(f"Running test: {self._testMethodName}")
        sections = self.generator._parse_analysis_sections("")
        self.assertEqual(sections["insights"], "[Key Insights not found in analysis]")
        self.assertEqual(sections["questions"], "[Open Questions not found in analysis]")
        self.assertEqual(sections["themes"], "[Main Themes not found in analysis]")
        self.assertEqual(sections["pull_quotes"], "[Pull Quotes not found in analysis]")

    def test_parse_analysis_sections_malformed(self):
        """Test _parse_analysis_sections with malformed section titles."""
        self.logger.info(f"Running test: {self._testMethodName}")
        analysis_text = "# Key Insights\nInsight A\n#Bad Title\nContent"
        sections = self.generator._parse_analysis_sections(analysis_text)
        self.assertEqual(sections["insights"], "Insight A\n#Bad Title\nContent") # Corrected expected output
        self.assertEqual(sections["questions"], "[Open Questions not found in analysis]")
        self.assertEqual(sections["themes"], "[Main Themes not found in analysis]")
        self.assertEqual(sections["pull_quotes"], "[Pull Quotes not found in analysis]")

    def test_get_header_single_file(self):
        """Test _get_header for a single file with a date."""
        self.logger.info(f"Running test: {self._testMethodName}")
        header = self.generator._get_header("/path/to/2023-10-20-event.txt")
        self.assertIn("October 20, 2023", header)
        self.assertIn("an in-person [Ai Salon](https://aisalon.xyz/) event held in [CITY] on October 20, 2023 facilitated by [HOST]", header)

    def test_get_header_single_file_no_date_in_filename(self):
        """Test _get_header for a single file without a parseable date."""
        self.logger.info(f"Running test: {self._testMethodName}")
        header = self.generator._get_header("/path/to/myevent.txt")
        self.assertIn("[DATE]", header)
        self.assertIn("an in-person [Ai Salon](https://aisalon.xyz/) event held in [CITY] on [DATE] facilitated by [HOST]", header)

    def test_get_header_combined(self):
        """Test _get_header for a combined article."""
        self.logger.info(f"Running test: {self._testMethodName}")
        header = self.generator._get_header(["file1.txt", "file2.txt"], is_combined=True, num_sources=2)
        self.assertIn("2 discussions/events held in [CITY] around [DATE] facilitated by [HOST]", header)

    def test_get_header_combined_with_num_sources(self):
        """Test _get_header for a combined article explicitly providing num_sources."""
        self.logger.info(f"Running test: {self._testMethodName}")
        header = self.generator._get_header(["f1.txt", "f2.txt", "f3.txt"], is_combined=True, num_sources=3)
        self.assertIn("3 discussions/events", header)

    def test_format_article_content(self):
        """Test _format_article_content method."""
        self.logger.info(f"Running test: {self._testMethodName}")
        mock_analysis = {
            "insights": "Test insights.",
            "questions": "Test questions?",
            "pull_quotes": "Test quote."
        }
        formatted_content = self.generator._format_article_content(
            "test_input", "Main article body.", mock_analysis
        )
        self.assertIn("Main article body.", formatted_content)
        self.assertIn("# Notes from the Conversation\nTest insights.", formatted_content)
        self.assertIn("# Open Questions\nTest questions?", formatted_content)
        self.assertIn("# Pull Quotes\nTest quote.", formatted_content)
        self.assertIn("_Editors Note:", formatted_content)

    def test_format_article_content_with_header_override(self):
        """Test _format_article_content with a header override."""
        self.logger.info(f"Running test: {self._testMethodName}")
        mock_analysis = {"insights": "i", "questions": "q", "pull_quotes": "pq"}
        custom_header = "MY CUSTOM HEADER"
        formatted_content = self.generator._format_article_content(
            "test_input", "Body", mock_analysis, header_override=custom_header
        )
        self.assertTrue(formatted_content.startswith(custom_header))
        self.assertIn("\n\nBody", formatted_content)
        self.assertIn("\n\n# Notes from the Conversation\ni", formatted_content)

    # --- Tests for _process_single_transcript (replaces old _generate_article_components_from_transcript) ---

    def test_process_single_transcript_success(self):
        """Test successful _process_single_transcript (no refinement)."""
        self.logger.info(f"Running test: {self._testMethodName}")
        self._mock_llm_generate(side_effects=[
            "# Key Insights\nMocked Analysis From LLM",
            "Mocked Initial Article From LLM"
        ])

        self.generator.refine = False
        transcript_data = {
            'content': self.sample_transcript,
            'source': 'source.txt',
            'original_input': 'source.txt',
            'is_audio': False,
            'anonymized': False
        }
        result = self.generator._process_single_transcript(transcript_data, model=self.TEST_LLM_MODEL)

        self.assertEqual(result["article_content"], "Mocked Initial Article From LLM")
        self.assertIn("Mocked Analysis From LLM", result["analysis_sections"]["insights"])
        self.assertEqual(result["metadata"]["analysis_sections_raw"], "# Key Insights\nMocked Analysis From LLM")
        self.assertEqual(result["metadata"]["source_transcript"], "source.txt")
        self.assertEqual(result["metadata"]["transcript_length"], len(self.sample_transcript))
        self.assertIn("analysis", result["metadata"]["generation_times"])
        self.assertIn("article", result["metadata"]["generation_times"])
        self.assertNotIn("refinement", result["metadata"]["generation_times"])

        self.assertEqual(self.mock_llm_instance.generate.call_count, 2)
        for call in self.mock_llm_instance.generate.call_args_list:
            self.assertEqual(call.kwargs['model'], self.TEST_LLM_MODEL)

    def test_process_single_transcript_with_refinement(self):
        """Test _process_single_transcript with refinement."""
        self.logger.info(f"Running test: {self._testMethodName}")
        self._mock_llm_generate(side_effects=[
            "# Key Insights\nAnalysis for refinement LLM",
            "Initial Article for refinement LLM",
            "# Refined Article From LLM"
        ])

        self.generator.refine = True
        transcript_data = {
            'content': self.sample_transcript,
            'source': 'source_ref.txt',
            'original_input': 'source_ref.txt',
            'is_audio': False,
            'anonymized': False
        }
        result = self.generator._process_single_transcript(transcript_data, model=self.TEST_LLM_MODEL)
        self.generator.refine = False # Reset for other tests

        self.assertEqual(result["article_content"], "# Refined Article From LLM")
        self.assertIn("Analysis for refinement LLM", result["analysis_sections"]["insights"])
        self.assertIn("refinement", result["metadata"]["generation_times"])
        self.assertEqual(self.mock_llm_instance.generate.call_count, 3)
        for call in self.mock_llm_instance.generate.call_args_list:
            self.assertEqual(call.kwargs['model'], self.TEST_LLM_MODEL)

    def test_process_single_transcript_audio_metadata(self):
        """Test that _process_single_transcript includes audio metadata when is_audio is True."""
        self.logger.info(f"Running test: {self._testMethodName}")
        self._mock_llm_generate(side_effects=[
            "# Key Insights\nAudio Analysis LLM",
            "Audio Article LLM"
        ])
        self.generator.refine = False

        transcript_data = {
            'content': self.sample_transcript,
            'source': 'mock_transcript.txt',
            'original_input': 'test.mp3',
            'is_audio': True,
            'anonymized': True
        }
        result = self.generator._process_single_transcript(transcript_data, model=self.TEST_LLM_MODEL)

        self.assertEqual(result["article_content"], "Audio Article LLM")
        self.assertIn("Audio Analysis LLM", result["analysis_sections"]["insights"])
        self.assertEqual(result["metadata"]["source_audio"], "test.mp3")
        self.assertEqual(result["metadata"]["source_transcript"], "mock_transcript.txt")
        self.assertTrue(result["metadata"]["anonymized"])

    # --- Tests for _transcribe_all_inputs ---

    def test_transcribe_all_inputs_transcript_too_short(self):
        """Test error for transcript too short via _transcribe_all_inputs."""
        self.logger.info(f"Running test: {self._testMethodName}")
        short_file = Path(self.test_dir) / "short.txt"
        short_content = "a" * (self.min_transcript_length - 1)
        with open(short_file, "w") as f:
            f.write(short_content)

        with self.assertRaises(TranscriptTooShortError):
            self.generator._transcribe_all_inputs([str(short_file)], anonymize=False, model=self.TEST_LLM_MODEL)

    @patch('socraticai.content.article.article_generator.transcribe')
    @patch('socraticai.content.article.article_generator.estimate_transcript_tokens', return_value=100)
    def test_transcribe_all_inputs_audio_file(self, mock_tokens, mock_transcribe):
        """Test _transcribe_all_inputs with an audio file."""
        self.logger.info(f"Running test: {self._testMethodName}")
        long_enough_transcript = "This is a sufficiently long mock transcript. " * (self.min_transcript_length // 40 + 1)
        mock_transcribe.return_value = ("mock_transcript.txt", long_enough_transcript)

        # Create a dummy audio file path (doesn't need to exist since transcribe is mocked)
        audio_path = Path(self.test_dir) / "test.mp3"
        audio_path.touch()

        transcripts = self.generator._transcribe_all_inputs(
            [str(audio_path)], anonymize=True, model=self.TEST_LLM_MODEL
        )

        mock_transcribe.assert_called_once_with(str(audio_path), anonymize=True)
        self.assertEqual(len(transcripts), 1)
        self.assertEqual(transcripts[0]['source'], "mock_transcript.txt")
        self.assertEqual(transcripts[0]['original_input'], str(audio_path))
        self.assertTrue(transcripts[0]['is_audio'])
        self.assertTrue(transcripts[0]['anonymized'])

    def test_transcribe_all_inputs_file_not_found(self):
        """Test _transcribe_all_inputs with a non-existent file."""
        self.logger.info(f"Running test: {self._testMethodName}")
        with self.assertRaises(FileNotFoundError):
            self.generator._transcribe_all_inputs(
                ["non_existent_file.txt"], anonymize=False, model=self.TEST_LLM_MODEL
            )

    @patch('socraticai.content.article.article_generator.estimate_transcript_tokens', return_value=100)
    def test_transcribe_all_inputs_unsupported_binary_file(self, mock_tokens):
        """Test _transcribe_all_inputs with a binary file treated as transcript."""
        self.logger.info(f"Running test: {self._testMethodName}")
        unsupported_file_path = Path(self.test_dir) / "unsupported.dat"
        with open(unsupported_file_path, "wb") as f:
            f.write(os.urandom(10))

        with patch.object(self.generator, '_is_audio_file', return_value=False):
            with self.assertRaises(UnsupportedFileTypeError):
                self.generator._transcribe_all_inputs(
                    [str(unsupported_file_path)], anonymize=False, model=self.TEST_LLM_MODEL
                )

    # --- Tests for generate (end-to-end) ---

    @patch('socraticai.content.article.article_generator.group_transcripts_by_context')
    @patch('socraticai.content.article.article_generator.estimate_transcript_tokens', return_value=100)
    def test_generate_single_transcript_input(self, mock_tokens, mock_grouping):
        """Test main generate method with a single transcript file (rerun=True)."""
        self.logger.info(f"Running test: {self._testMethodName}")
        temp_transcript_path = self.generator.output_dir.parent / "main_gen_single_transcript.txt"
        with open(temp_transcript_path, "w") as f:
            f.write(self.sample_transcript)

        # Mock grouping to return a single group with one transcript
        def group_side_effect(transcripts, model):
            return [transcripts]
        mock_grouping.side_effect = group_side_effect

        self._mock_llm_generate(side_effects=[
            "# Key Insights\nMain Gen Single Analysis LLM",
            "Main Gen Single Article LLM"
        ])
        self.generator.refine = False

        article_path, meta_path = self.generator.generate(
            str(temp_transcript_path), rerun=True, model=self.TEST_LLM_MODEL
        )

        self.assertTrue(article_path.exists())
        self.assertTrue(meta_path.exists())
        expected_base_name = self.generator._get_base_filename(str(temp_transcript_path))
        self.assertEqual(article_path.name, f"{expected_base_name}.md")
        self.assertEqual(meta_path.name, f"{expected_base_name}_meta.json")

        with open(article_path, 'r') as f_art, open(meta_path, 'r') as f_meta:
            article_content = f_art.read()
            metadata_content = json.load(f_meta)

        self.assertIn("Main Gen Single Article LLM", article_content)
        self.assertIn("Main Gen Single Analysis LLM", metadata_content["analysis_summary"]["insights"])
        self.assertEqual(metadata_content["model_used"], self.TEST_LLM_MODEL)
        self.assertEqual(metadata_content["raw_llm_article_content"], "Main Gen Single Article LLM")
        self.assertEqual(metadata_content["source_transcript"], str(temp_transcript_path))
        # Verify LLM was called with the correct model (analysis + article = 2 calls)
        self.assertEqual(self.mock_llm_instance.generate.call_count, 2)
        for call in self.mock_llm_instance.generate.call_args_list:
            self.assertEqual(call.kwargs['model'], self.TEST_LLM_MODEL)
        os.remove(temp_transcript_path)

    def test_generate_single_transcript_input_no_rerun_exists(self):
        """Test main generate, single transcript, no rerun, files already exist."""
        self.logger.info(f"Running test: {self._testMethodName}")
        temp_transcript_path = self.generator.output_dir.parent / "main_gen_exists_transcript.txt"
        base_name = self.generator._get_base_filename(str(temp_transcript_path))
        output_base = self.generator.output_dir / base_name
        os.makedirs(self.generator.output_dir, exist_ok=True)

        md_path = output_base.with_suffix(".md")
        meta_path = output_base.with_name(output_base.name + "_meta.json")

        # Include raw_llm_article_content in metadata to prevent regeneration
        metadata_with_raw = {
            "info": "meta_already_here",
            "raw_llm_article_content": "Existing Raw LLM Content"
        }

        with open(md_path, "w") as f_md: f_md.write("Already Here MD Content")
        with open(meta_path, "w") as f_meta: json.dump(metadata_with_raw, f_meta)
        with open(temp_transcript_path, "w") as f_ts: f_ts.write(self.sample_transcript)

        article_path_res, meta_path_res = self.generator.generate(
            str(temp_transcript_path), rerun=False, model=self.TEST_LLM_MODEL
        )

        self.assertEqual(article_path_res, md_path)
        self.assertEqual(meta_path_res, meta_path)
        with open(article_path_res, 'r') as f_art:
            self.assertEqual(f_art.read(), "Already Here MD Content")
        with open(meta_path_res, 'r') as f_m:
            metadata_loaded = json.load(f_m)
            self.assertEqual(metadata_loaded["info"], "meta_already_here")
            self.assertEqual(metadata_loaded["raw_llm_article_content"], "Existing Raw LLM Content")
        self.mock_llm_instance.generate.assert_not_called()
        os.remove(temp_transcript_path)

    def test_generate_no_input_paths(self):
        """Test generate with an empty list of input paths."""
        self.logger.info(f"Running test: {self._testMethodName}")
        with self.assertRaisesRegex(ValueError, "No input paths provided."):
            self.generator.generate([])

    def test_combine_group_results(self):
        """Test _combine_group_results method."""
        self.logger.info(f"Running test: {self._testMethodName}")
        # Two LLM calls: article combination + analysis synthesis
        self._mock_llm_generate([
            "Combined Article Output LLM",
            "# Key Insights\nSynthesized insights"
        ])
        group_results = [
            {
                "article_content": "Article 1 text content.",
                "metadata": {
                    "analysis_sections_raw": "# Key Insights\nInsight from group 1",
                    "source_transcripts": ["transcript_1.txt"],
                    "original_inputs": ["input_1.mp3"],
                    "total_transcript_length": 5000
                }
            },
            {
                "article_content": "Article 2 text content.",
                "metadata": {
                    "analysis_sections_raw": "# Key Insights\nInsight from group 2",
                    "source_transcripts": ["transcript_2.txt"],
                    "original_inputs": ["input_2.mp3"],
                    "total_transcript_length": 6000
                }
            }
        ]

        result = self.generator._combine_group_results(group_results, model=self.TEST_LLM_MODEL)
        self.assertEqual(result["article_content"], "Combined Article Output LLM")

        self.assertEqual(self.mock_llm_instance.generate.call_count, 2)
        # Check the article combination call
        args, kwargs = self.mock_llm_instance.generate.call_args_list[0]
        called_prompt = kwargs['prompt']
        self.assertIn("--- Group 1 ---", called_prompt)
        self.assertIn("Article 1 text content.", called_prompt)
        self.assertIn("--- Group 2 ---", called_prompt)
        self.assertIn("Article 2 text content.", called_prompt)
        self.assertEqual(kwargs['model'], self.TEST_LLM_MODEL)

    @patch('socraticai.content.article.article_generator.group_transcripts_by_context')
    @patch('socraticai.content.article.article_generator.estimate_transcript_tokens', return_value=100)
    def test_generate_multiple_transcript_inputs(self, mock_tokens, mock_grouping):
        """Test main generate method with multiple transcript files for combined article."""
        self.logger.info(f"Running test: {self._testMethodName}")
        temp_transcript1_path = self.generator.output_dir.parent / "multi_transcript1_for_main_gen.txt"
        temp_transcript2_path = self.generator.output_dir.parent / "multi_transcript2_for_main_gen.txt"

        # Write transcripts that are long enough to pass the minimum length requirement
        long_transcript1 = "Transcript 1 content for multi-gen. This is a longer transcript to meet the minimum length requirement." * 20
        long_transcript2 = "Transcript 2 content for multi-gen. This is a longer transcript to meet the minimum length requirement." * 20

        with open(temp_transcript1_path, "w") as f: f.write(long_transcript1)
        with open(temp_transcript2_path, "w") as f: f.write(long_transcript2)

        # Mock grouping to put both transcripts in a single group
        def group_side_effect(transcripts, model):
            return [transcripts]
        mock_grouping.side_effect = group_side_effect

        # Mock the LLM responses for the new multi-source flow
        self._mock_llm_generate(side_effects=[
            "# Key Insights\nMulti-source Analysis From LLM",  # Analysis response
            "Combined Multi-Source Article Content From LLM",   # Article response
            "AI_and_Discussion"                                 # Title generation response
        ])

        self.generator.refine = False

        input_paths_list = [str(temp_transcript1_path), str(temp_transcript2_path)]
        article_path, meta_path = self.generator.generate(
            input_paths_list,
            rerun=True,
            model=self.TEST_LLM_MODEL
        )

        self.assertTrue(article_path.exists())
        self.assertTrue(meta_path.exists())
        self.assertTrue(article_path.name.startswith("combined_"))
        self.assertTrue(meta_path.name.startswith("combined_"))
        self.assertTrue(meta_path.name.endswith("_meta.json"))

        with open(article_path, 'r') as f_art, open(meta_path, 'r') as f_meta:
            article_content = f_art.read()
            metadata_content = json.load(f_meta)

        self.assertIn("Combined Multi-Source Article Content From LLM", article_content)
        self.assertIn("# Notes from the Conversation\nMulti-source Analysis From LLM", article_content)
        self.assertEqual(metadata_content["type"], "multi_source_article")
        self.assertEqual(metadata_content["model_used"], self.TEST_LLM_MODEL)
        self.assertEqual(metadata_content["source_count"], 2)
        self.assertIn(str(temp_transcript1_path), metadata_content["source_transcripts"])
        self.assertIn(str(temp_transcript2_path), metadata_content["source_transcripts"])
        self.assertIn("Multi-source Analysis From LLM", metadata_content["analysis_sections_raw"])

        os.remove(temp_transcript1_path)
        os.remove(temp_transcript2_path)

    def test_extract_date_from_filename_yyyymmdd(self):
        """Test date extraction from various YYYY-MM-DD format filenames."""
        self.logger.info(f"Running test: {self._testMethodName}")
        # YYYY-MM-DD
        self.assertEqual(self.generator._extract_date_from_filename("2023-10-20-event.txt"), "20231020")
        # YYYYMMDD
        self.assertEqual(self.generator._extract_date_from_filename("20231020_event.txt"), "20231020")
        # YYYY_MM_DD
        self.assertEqual(self.generator._extract_date_from_filename("2023_10_20_event.txt"), "20231020")

    def test_extract_date_from_filename_no_date(self):
        """Test that filenames with no date return None."""
        self.logger.info(f"Running test: {self._testMethodName}")
        self.assertIsNone(self.generator._extract_date_from_filename("myevent.txt"))
        self.assertIsNone(self.generator._extract_date_from_filename("notes.md"))

    def test_extract_date_uses_numeric_comparison(self):
        """Verify numeric comparison is used for year validation (not string)."""
        self.logger.info(f"Running test: {self._testMethodName}")
        # Year 2023 should work
        self.assertEqual(self.generator._extract_date_from_filename("20230115_event.txt"), "20230115")
        # Year 1899 should not be valid (< 1900)
        self.assertIsNone(self.generator._extract_date_from_filename("18990115_event.txt"))

if __name__ == '__main__':
    unittest.main()
