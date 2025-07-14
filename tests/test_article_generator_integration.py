"""Integration test for ArticleGenerator using real API calls.

This test script validates the complete article generation pipeline
using the test transcript and real LLM API calls.
"""

import pytest
import os
import logging
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from socraticai.content.article.article_generator import ArticleGenerator
from socraticai.config import TEST_MODEL, TEST_API_KEY
from socraticai import config

logger = logging.getLogger(__name__)
# Set logger level to debug for detailed test output
logger.setLevel(logging.DEBUG)

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration

class TestArticleGeneratorIntegration:
    """Integration tests for ArticleGenerator with real API calls.
    
    These tests:
    - Use real LLM API calls (costs money)
    - Test the complete article generation pipeline
    - Validate output quality and structure
    - Are skipped if API keys are not available
    """
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.original_get_output_path = None
        
        # Patch config.DATA_DIRECTORY to use our test directory
        config.DATA_DIRECTORY = self.test_dir
        
        # Get the test transcript path
        self.test_transcript_path = Path(__file__).parent / "test_transcript.txt"
        
        yield
        
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @pytest.mark.skipif(
        not TEST_API_KEY, 
        reason="TEST_API_KEY not set - skipping real API test"
    )
    def test_generate_article_from_transcript(self):
        """Test complete article generation from test transcript."""
        logger.info(f"Testing article generation with {TEST_MODEL} model")
        
        # Initialize generator with configured test model
        generator = ArticleGenerator(model=TEST_MODEL, refine=True)
        
        # Generate article from test transcript
        article_path, metadata_path = generator.generate(
            input_paths=str(self.test_transcript_path),
            rerun=True,
            anonymize=False  # Not needed for text input
        )
        
        # Verify files were created
        assert article_path.exists(), f"Article file not created: {article_path}"
        assert metadata_path.exists(), f"Metadata file not created: {metadata_path}"
        
        # Read and validate article content
        with open(article_path, 'r') as f:
            article_content = f.read()
        
        # Basic content validation
        assert len(article_content) > 1000, "Article content seems too short"
        assert "# Notes from the Conversation" in article_content
        assert "# Open Questions" in article_content
        assert "# Pull Quotes" in article_content
        assert "_Editors Note:" in article_content
        
        # Read and validate metadata
        import json
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Validate metadata structure
        assert metadata["type"] == "article"
        assert metadata["model_used"] == TEST_MODEL
        assert "generated_at" in metadata
        assert "transcript_length" in metadata
        assert "analysis_summary" in metadata
        assert "generation_times" in metadata
        assert metadata["transcript_length"] > 1000  # Test transcript should be substantial
        
        # Validate analysis sections were parsed
        assert "analysis_sections_raw" in metadata
        assert "parsed_analysis_sections" in metadata
        parsed_sections = metadata["parsed_analysis_sections"]
        assert "insights" in parsed_sections
        assert "questions" in parsed_sections
        assert "pull_quotes" in parsed_sections
        
        logger.info(f"Article generated successfully: {article_path}")
        logger.info(f"Article length: {len(article_content)} characters")
        logger.info(f"Generation times: {metadata['generation_times']}")
        
        return article_path, metadata_path
    
    @pytest.mark.skipif(
        not TEST_API_KEY, 
        reason="TEST_API_KEY not set - skipping real API test"
    )
    def test_rerun_behavior(self):
        """Test the rerun behavior - should not regenerate if files exist and rerun=False."""
        logger.info("Testing rerun behavior")
        
        generator = ArticleGenerator(model=TEST_MODEL, refine=True)
        
        # First generation
        article_path1, metadata_path1 = generator.generate(
            input_paths=str(self.test_transcript_path),
            rerun=True
        )
        
        # Get modification times
        article_mtime1 = article_path1.stat().st_mtime
        metadata_mtime1 = metadata_path1.stat().st_mtime
        
        # Second generation with rerun=False (should reuse existing files)
        article_path2, metadata_path2 = generator.generate(
            input_paths=str(self.test_transcript_path),
            rerun=False
        )
        
        # Should return same paths
        assert article_path1 == article_path2
        assert metadata_path1 == metadata_path2
        
        # Files should not have been modified
        article_mtime2 = article_path2.stat().st_mtime
        metadata_mtime2 = metadata_path2.stat().st_mtime
        
        assert article_mtime1 == article_mtime2, "Article file should not be regenerated when rerun=False"
        assert metadata_mtime1 == metadata_mtime2, "Metadata file should not be regenerated when rerun=False"
        
        # Third generation with rerun=True (should regenerate files)
        import time
        time.sleep(1)  # Ensure different modification times
        
        article_path3, metadata_path3 = generator.generate(
            input_paths=str(self.test_transcript_path),
            rerun=True
        )
        
        # Should return same paths
        assert article_path1 == article_path3
        assert metadata_path1 == metadata_path3
        
        # Files should have been modified
        article_mtime3 = article_path3.stat().st_mtime
        metadata_mtime3 = metadata_path3.stat().st_mtime
        
        assert article_mtime3 > article_mtime2, "Article file should be regenerated when rerun=True"
        assert metadata_mtime3 > metadata_mtime2, "Metadata file should be regenerated when rerun=True"
        
        logger.info("Rerun behavior test passed")

def run_integration_test():
    """Standalone function to run the integration test."""
    import sys
    
    # Check if API keys are available
    if not TEST_API_KEY:
        print("❌ No API key found. Set TEST_API_KEY to run integration tests.")
        sys.exit(1)
    
    print("🚀 Running ArticleGenerator integration test...")
    print(f"📄 Test transcript: {Path(__file__).parent / 'test_transcript.txt'}")
    print(f"🤖 Using model: {TEST_MODEL}")
    
    # Create test instance
    test_instance = TestArticleGeneratorIntegration()
    
    # Set up test environment manually
    test_instance.test_dir = tempfile.mkdtemp()
    test_instance.test_transcript_path = Path(__file__).parent / "test_transcript.txt"
    
    # Patch output path
    import socraticai.core.utils
    original_get_output_path = socraticai.core.utils.get_output_path
    socraticai.core.utils.get_output_path = lambda: test_instance.test_dir
    
    try:
        # Run the main test
        print("🤖 Testing article generation...")
        article_path, metadata_path = test_instance.test_generate_article_from_transcript()
        print(f"✅ Article generated: {article_path}")
        print(f"📊 Metadata saved: {metadata_path}")
        
        # Show some content
        with open(article_path, 'r') as f:
            content = f.read()
        print(f"\n📝 Article preview (first 500 chars):")
        print("-" * 50)
        print(content[:500] + "..." if len(content) > 500 else content)
        print("-" * 50)
        
        print("\n🎉 Integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        raise
    finally:
        # Cleanup
        socraticai.core.utils.get_output_path = original_get_output_path
        if os.path.exists(test_instance.test_dir):
            shutil.rmtree(test_instance.test_dir)

if __name__ == "__main__":
    run_integration_test() 