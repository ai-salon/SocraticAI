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
        # Configure logging to show INFO level messages for tests
        # You can adjust level and format as needed
        # To see logs during `python -m unittest` add the --buffer flag or use a test runner that captures logs
        #logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s')
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
        # The regex for sections looks for known titles. "#Bad Title" is not one of them.
        # The content under "#Bad Title" would be part of "Insight A" if it's not followed by another known title.
        # Let's re-evaluate the expected behavior of _parse_analysis_sections based on its implementation.
        # The pattern is: rf"""#\s*{re.escape(title)}\s*(.*?)(?=\s*\n(?:#\s*(?:{all_known_titles_regex}|END_OF_ANALYSIS_MARKER)|$))"""
        # This means it captures everything until the next known title or end marker.
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
        self.assertIn("an in-person event held in [CITY] on October 20, 2023 facilitated by [HOST]", header)

    def test_get_header_single_file_no_date_in_filename(self):
        """Test _get_header for a single file without a parseable date."""
        self.logger.info(f"Running test: {self._testMethodName}")
        header = self.generator._get_header("/path/to/myevent.txt")
        self.assertIn("[DATE]", header)
        self.assertIn("an in-person event held in [CITY] on [DATE] facilitated by [HOST]", header)

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

    def test_generate_article_components_from_transcript_too_short(self):
        """Test error for transcript too short."""
        self.logger.info(f"Running test: {self._testMethodName}")
        short_transcript = "a" * (self.min_transcript_length - 1)
        with self.assertRaises(TranscriptTooShortError):
            self.generator._generate_article_components_from_transcript(short_transcript, "source.txt", self.TEST_LLM_MODEL)

    def test_generate_article_components_from_transcript_success(self):
        """Test successful generation of article components from transcript (no refinement)."""
        self.logger.info(f"Running test: {self._testMethodName}")
        self._mock_llm_generate(side_effects=[
            "# Key Insights\nMocked Analysis From LLM",
            "Mocked Initial Article From LLM"
        ])
        
        self.generator.refine = False
        components = self.generator._generate_article_components_from_transcript(
            self.sample_transcript, "source.txt", model=self.TEST_LLM_MODEL
        )

        self.assertEqual(components["final_article_content"], "Mocked Initial Article From LLM")
        self.assertEqual(components["raw_article_content"], "Mocked Initial Article From LLM")
        self.assertIn("Mocked Analysis From LLM", components["analysis_sections"]["insights"])
        self.assertEqual(components["analysis_raw_text"], "# Key Insights\nMocked Analysis From LLM")
        self.assertEqual(components["metadata"]["source_transcript"], "source.txt")
        self.assertEqual(components["metadata"]["transcript_length"], len(self.sample_transcript))
        self.assertIn("analysis", components["metadata"]["generation_times"])
        self.assertIn("initial_article", components["metadata"]["generation_times"])
        self.assertNotIn("refinement", components["metadata"]["generation_times"])
        
        # Check that LLMChain().generate was called with the correct model
        self.mock_llm_instance.generate.assert_any_call(prompt=unittest.mock.ANY, thinking_tokens=unittest.mock.ANY, model=self.TEST_LLM_MODEL)
        self.assertEqual(self.mock_llm_instance.generate.call_count, 2)

    def test_generate_article_components_from_transcript_with_refinement(self):
        """Test successful generation with refinement."""
        self.logger.info(f"Running test: {self._testMethodName}")
        self._mock_llm_generate(side_effects=[
            "# Key Insights\nAnalysis for refinement LLM",
            "Initial Article for refinement LLM",
            "Refined Article From LLM"
        ])

        self.generator.refine = True
        components = self.generator._generate_article_components_from_transcript(
            self.sample_transcript, "source_ref.txt", model=self.TEST_LLM_MODEL
        )
        self.generator.refine = False # Reset for other tests

        self.assertEqual(components["final_article_content"], "Refined Article From LLM")
        self.assertEqual(components["raw_article_content"], "Refined Article From LLM")
        self.assertIn("Analysis for refinement LLM", components["analysis_sections"]["insights"])
        self.assertIn("refinement", components["metadata"]["generation_times"])
        self.mock_llm_instance.generate.assert_any_call(prompt=unittest.mock.ANY, thinking_tokens=unittest.mock.ANY, model=self.TEST_LLM_MODEL)
        self.assertEqual(self.mock_llm_instance.generate.call_count, 3)

    @patch('socraticai.content.article.article_generator.transcribe')
    def test_generate_article_components_from_audiofile(self, mock_transcribe):
        """Test generating components from a (mocked) audio file."""
        self.logger.info(f"Running test: {self._testMethodName}")
        # Fix: Make the mocked transcript long enough
        long_enough_mock_transcript = "This is a sufficiently long mock transcript. " * (self.min_transcript_length // 40 + 1)
        mock_transcribe.return_value=("mock_transcript.txt", long_enough_mock_transcript)

        self._mock_llm_generate(side_effects=[
            "# Key Insights\nAudio Analysis LLM", 
            "Audio Article LLM"
        ])
        self.generator.refine = False
        
        with patch.object(self.generator, '_is_audio_file', return_value=True) as mock_is_audio:
            components = self.generator._generate_article_components_from_audiofile(
                "test.mp3", anonymize=True, model=self.TEST_LLM_MODEL
            )
        
        mock_transcribe.assert_called_once_with("test.mp3", anonymize=True)
        mock_is_audio.assert_called_once_with("test.mp3")

        self.assertEqual(components["final_article_content"], "Audio Article LLM")
        self.assertIn("Audio Analysis LLM", components["analysis_sections"]["insights"])
        self.assertEqual(components["metadata"]["source_audio"], "test.mp3")
        self.assertEqual(components["metadata"]["source_transcript"], "mock_transcript.txt")
        self.assertTrue(components["metadata"]["anonymized"])
        self.mock_llm_instance.generate.assert_any_call(prompt=unittest.mock.ANY, thinking_tokens=unittest.mock.ANY, model=self.TEST_LLM_MODEL)

    def test_generate_article_components_from_audiofile_unsupported_type(self):
        """Test error for unsupported audio file type when _is_audio_file is false."""
        self.logger.info(f"Running test: {self._testMethodName}")
        with patch.object(self.generator, '_is_audio_file', return_value=False):
            with self.assertRaises(UnsupportedFileTypeError):
                self.generator._generate_article_components_from_audiofile("test.docx", True, self.TEST_LLM_MODEL)

    def test_process_single_input_transcript_success(self):
        """Test _process_single_input with a transcript, successful generation and saving."""
        self.logger.info(f"Running test: {self._testMethodName}")
        temp_transcript_path = self.generator.output_dir.parent / "temp_transcript_for_process.txt"
        with open(temp_transcript_path, "w") as f:
            f.write(self.sample_transcript)

        self._mock_llm_generate(side_effects=[
            "# Key Insights\nProcessed Analysis LLM", 
            "Processed Article LLM"
        ])
        self.generator.refine = False
        output_base_name = "processed_article_single"
        output_base = self.generator.output_dir / output_base_name

        article_data, raw_llm_output = self.generator._process_single_input(
            str(temp_transcript_path), rerun=True, anonymize=False, model=self.TEST_LLM_MODEL,
            output_base_path_for_sub_article=output_base
        )

        self.assertEqual(raw_llm_output, "Processed Article LLM")
        self.assertIn("Processed Article LLM", article_data["content"])
        self.assertIn("Processed Analysis LLM", article_data["metadata"]["analysis_summary"]["insights"])
        self.assertEqual(article_data["metadata"]["model_used"], self.TEST_LLM_MODEL)
        self.assertEqual(article_data["metadata"]["source_transcript"], str(temp_transcript_path))
        self.assertEqual(article_data["metadata"]["raw_llm_article_content"], "Processed Article LLM")
        
        expected_md_path = output_base.with_suffix(".md")
        # Corrected path construction for metadata file, consistent with the fix in article_generator.py
        expected_meta_path = output_base.with_name(output_base.name + "_meta.json")
        self.assertTrue(expected_md_path.exists())
        self.assertTrue(expected_meta_path.exists())
        
        with open(expected_md_path, 'r') as f_md, open(expected_meta_path, 'r') as f_meta:
            saved_md = f_md.read()
            saved_meta = json.load(f_meta)
        self.assertIn("Processed Article LLM", saved_md)
        self.assertEqual(saved_meta["raw_llm_article_content"], "Processed Article LLM")
        self.assertEqual(saved_meta["model_used"], self.TEST_LLM_MODEL)
        
        os.remove(temp_transcript_path)
        self.mock_llm_instance.generate.assert_any_call(prompt=unittest.mock.ANY, thinking_tokens=unittest.mock.ANY, model=self.TEST_LLM_MODEL)

    def test_process_single_input_file_not_found(self):
        """Test _process_single_input with a non-existent input file."""
        self.logger.info(f"Running test: {self._testMethodName}")
        output_base = self.generator.output_dir / "non_existent_test"
        with self.assertRaises(FileNotFoundError):
            self.generator._process_single_input("non_existent_file.txt", rerun=True, anonymize=False, model=self.TEST_LLM_MODEL, output_base_path_for_sub_article=output_base)

    def test_process_single_input_unsupported_file_type_as_transcript(self):
        """Test _process_single_input with an unsupported file type (e.g. binary) treated as transcript."""
        self.logger.info(f"Running test: {self._testMethodName}")
        unsupported_file_path = self.generator.output_dir.parent / "unsupported.dat"
        with open(unsupported_file_path, "wb") as f:
            f.write(os.urandom(10)) 
        
        output_base = self.generator.output_dir / "unsupported_test"
        with patch.object(self.generator, '_is_audio_file', return_value=False):
            with self.assertRaises(UnsupportedFileTypeError): 
                self.generator._process_single_input(
                    str(unsupported_file_path), 
                    rerun=True, anonymize=False, model=self.TEST_LLM_MODEL, 
                    output_base_path_for_sub_article=output_base
                )
        os.remove(unsupported_file_path)

    def test_process_single_input_transcript_no_rerun_files_exist_with_raw_llm(self):
        """Test _process_single_input: no rerun, files exist, metadata has raw_llm_content."""
        self.logger.info(f"Running test: {self._testMethodName}")
        output_base_name = "existing_article_no_rerun"
        output_base = self.generator.output_dir / output_base_name
        os.makedirs(self.generator.output_dir, exist_ok=True)
        
        mock_metadata = {
            "raw_llm_article_content": "Existing LLM Output from Meta",
            "model_used": "old_model_in_meta", # This should be preserved
            "source_transcript": "dummy_transcript.txt"
        }
        md_path = output_base.with_suffix(".md")
        meta_path = output_base.with_name(output_base.name + "_meta.json")

        with open(md_path, "w") as f_md: f_md.write("Existing MD Content")
        with open(meta_path, "w") as f_meta: json.dump(mock_metadata, f_meta)

        dummy_input_path = "dummy_transcript.txt" 

        article_data, raw_llm_output = self.generator._process_single_input(
            dummy_input_path, rerun=False, anonymize=False, model=self.TEST_LLM_MODEL, # New model shouldn't be used
            output_base_path_for_sub_article=output_base
        )
        self.assertEqual(raw_llm_output, "Existing LLM Output from Meta")
        self.assertEqual(article_data["content"], "Existing MD Content")
        self.assertEqual(article_data["metadata"]["model_used"], "old_model_in_meta") # Verify old model is kept
        self.mock_llm_instance.generate.assert_not_called()

    def test_process_single_input_transcript_no_rerun_files_exist_no_raw_llm(self):
        """Test _process_single_input: no rerun, files exist, but metadata missing raw_llm_content (should regenerate)."""
        self.logger.info(f"Running test: {self._testMethodName}")
        temp_transcript_path = self.generator.output_dir.parent / "temp_regen_transcript_no_raw.txt"
        with open(temp_transcript_path, "w") as f:
            f.write(self.sample_transcript)

        output_base_name = "existing_article_regen_no_raw"
        output_base = self.generator.output_dir / output_base_name
        os.makedirs(self.generator.output_dir, exist_ok=True)
        
        mock_metadata_no_raw = {
            "model_used": "old_model_no_raw",
            "source_transcript": str(temp_transcript_path)
        }
        md_path = output_base.with_suffix(".md")
        meta_path = output_base.with_name(output_base.name + "_meta.json")
        with open(md_path, "w") as f_md: f_md.write("Old MD Content, will be overwritten")
        with open(meta_path, "w") as f_meta: json.dump(mock_metadata_no_raw, f_meta)

        self._mock_llm_generate(side_effects=[
            "# Key Insights\nRegenerated Analysis Due to No Raw LLM", 
            "Regenerated Article Due to No Raw LLM"
        ])
        self.generator.refine = False

        article_data, raw_llm_output = self.generator._process_single_input(
            str(temp_transcript_path), rerun=False, anonymize=False, model=self.TEST_LLM_MODEL,
            output_base_path_for_sub_article=output_base, is_sub_article=True 
        )

        self.assertEqual(raw_llm_output, "Regenerated Article Due to No Raw LLM")
        self.assertIn("Regenerated Article Due to No Raw LLM", article_data["content"])
        self.assertEqual(article_data["metadata"]["model_used"], self.TEST_LLM_MODEL) # Should use new model
        self.mock_llm_instance.generate.assert_called() 
        self.assertTrue(md_path.exists())
        self.assertTrue(meta_path.exists())
        with open(meta_path, 'r') as f_meta_new:
            new_meta = json.load(f_meta_new)
        self.assertEqual(new_meta["raw_llm_article_content"], "Regenerated Article Due to No Raw LLM")
        self.mock_llm_instance.generate.assert_any_call(prompt=unittest.mock.ANY, thinking_tokens=unittest.mock.ANY, model=self.TEST_LLM_MODEL)
        os.remove(temp_transcript_path)

    def test_generate_single_transcript_input(self):
        """Test main generate method with a single transcript file (rerun=True)."""
        self.logger.info(f"Running test: {self._testMethodName}")
        temp_transcript_path = self.generator.output_dir.parent / "main_gen_single_transcript.txt"
        with open(temp_transcript_path, "w") as f:
            f.write(self.sample_transcript)

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
        self.mock_llm_instance.generate.assert_any_call(prompt=unittest.mock.ANY, thinking_tokens=unittest.mock.ANY, model=self.TEST_LLM_MODEL)
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

    def test_combine_articles_content(self):
        """Test _combine_articles_content method."""
        self.logger.info(f"Running test: {self._testMethodName}")
        self._mock_llm_generate("Combined Article Output LLM")
        raw_texts = ["Article 1 text content.", "Article 2 text content."]
        source_ids = ["source_id_1", "source_id_2"]
        
        combined_content = self.generator._combine_articles_content(raw_texts, source_ids, model=self.TEST_LLM_MODEL)
        self.assertEqual(combined_content, "Combined Article Output LLM")
        
        self.mock_llm_instance.generate.assert_called_once()
        args, kwargs = self.mock_llm_instance.generate.call_args_list[0] # Get the first (and only) call
        called_prompt = kwargs['prompt']
        self.assertIn("--- Source Article 1: source_id_1 ---", called_prompt)
        self.assertIn("Article 1 text content.", called_prompt)
        self.assertIn("--- Source Article 2: source_id_2 ---", called_prompt)
        self.assertIn("Article 2 text content.", called_prompt)
        self.assertEqual(kwargs['model'], self.TEST_LLM_MODEL)

    def test_synthesize_combined_analysis_sections(self):
        """Test _synthesize_combined_analysis_sections method."""
        self.logger.info(f"Running test: {self._testMethodName}")
        self._mock_llm_generate("# Key Insights\nSynthesized Insights From LLM")
        collected_sections = [
            {"identifier": "src_analysis_1", "sections": "# Key Insights\nInsight From Source 1"},
            {"identifier": "src_analysis_2", "sections": "# Open Questions\nQuestion From Source 2"}
        ]
        synthesized_output = self.generator._synthesize_combined_analysis_sections(collected_sections, model=self.TEST_LLM_MODEL)
        self.assertEqual(synthesized_output, "# Key Insights\nSynthesized Insights From LLM")
        self.mock_llm_instance.generate.assert_called_once()
        args, kwargs = self.mock_llm_instance.generate.call_args_list[0] # Get the first (and only) call
        called_prompt = kwargs['prompt']
        self.assertIn("--- Source: src_analysis_1 ---", called_prompt)
        self.assertIn("# Key Insights\nInsight From Source 1", called_prompt)
        self.assertIn("--- Source: src_analysis_2 ---", called_prompt)
        self.assertIn("# Open Questions\nQuestion From Source 2", called_prompt)
        self.assertEqual(kwargs['model'], self.TEST_LLM_MODEL)

    def test_synthesize_combined_analysis_sections_no_valid_sections(self):
        """Test synthesis with no valid (string) sections provided."""
        self.logger.info(f"Running test: {self._testMethodName}")
        output_empty = self.generator._synthesize_combined_analysis_sections([], model=self.TEST_LLM_MODEL)
        self.assertIn("[No insights synthesized due to missing source data.]", output_empty)
        self.mock_llm_instance.generate.assert_not_called()
        
        output_invalid_type = self.generator._synthesize_combined_analysis_sections(
            [{"identifier": "s1", "sections": {"key": "value"}}], model=self.TEST_LLM_MODEL
        )
        self.assertIn("[No insights synthesized due to missing source data.]", output_invalid_type)
        self.mock_llm_instance.generate.assert_not_called()

    def test_generate_multiple_transcript_inputs(self):
        """Test main generate method with multiple transcript files for combined article."""
        self.logger.info(f"Running test: {self._testMethodName}")
        temp_transcript1_path = self.generator.output_dir.parent / "multi_transcript1_for_main_gen.txt"
        temp_transcript2_path = self.generator.output_dir.parent / "multi_transcript2_for_main_gen.txt"
        
        # Write transcripts that are long enough to pass the minimum length requirement
        long_transcript1 = "Transcript 1 content for multi-gen. This is a longer transcript to meet the minimum length requirement." * 20
        long_transcript2 = "Transcript 2 content for multi-gen. This is a longer transcript to meet the minimum length requirement." * 20
        
        with open(temp_transcript1_path, "w") as f: f.write(long_transcript1)
        with open(temp_transcript2_path, "w") as f: f.write(long_transcript2)

        # Mock the LLM responses for the new multi-source flow
        self._mock_llm_generate(side_effects=[
            "# Key Insights\nMulti-source Analysis From LLM",  # Analysis response
            "Combined Multi-Source Article Content From LLM"    # Article response
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
        # The metadata filename for combined uses a timestamp, so we only check suffix
        self.assertTrue(meta_path.name.endswith("_meta.json")) 

        # Verify that the LLM was called for analysis and article generation
        self.assertEqual(self.mock_llm_instance.generate.call_count, 2)

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

if __name__ == '__main__':
    unittest.main() 