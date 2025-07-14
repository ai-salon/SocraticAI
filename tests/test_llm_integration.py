import pytest
import os
import logging
from socraticai.core.llm import LLMChain, AnthropicLLMChain, GeminiLLMChain
from socraticai.config import TEST_GOOGLE_MODEL, TEST_ANTHROPIC_MODEL

logger = logging.getLogger(__name__)

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration

class TestRealAPIIntegration:
    """Integration tests that make real API calls.
    
    These tests are:
    - Marked with @pytest.mark.integration
    - Skipped if API keys are not available
    - Run separately from unit tests
    - Expected to be slower and cost money
    """
    
    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"), 
        reason="ANTHROPIC_API_KEY not set - skipping real API test"
    )
    def test_real_anthropic_api_call(self):
        """Test actual Anthropic API integration."""
        logger.info("Testing real Anthropic API call")
        
        chain = AnthropicLLMChain(model_name=TEST_ANTHROPIC_MODEL)
        response = chain.generate(
            prompt="Say 'Hello from Anthropic' and nothing else.",
            max_tokens=50
        )
        
        # Verify we got a real response
        assert response.content
        assert len(response.content) > 0
        assert "anthropic" in response.content.lower()
        
        # Verify metadata structure
        assert response.metadata["provider"] == "anthropic"
        assert response.metadata["model"] == TEST_ANTHROPIC_MODEL
        assert "usage" in response.metadata
        
        logger.info(f"Real Anthropic response: {response.content[:50]}...")
    
    @pytest.mark.skipif(
        not os.getenv("GOOGLE_API_KEY"), 
        reason="GOOGLE_API_KEY not set - skipping real API test"
    )
    def test_real_gemini_api_call(self):
        """Test actual Gemini API integration."""
        logger.info("Testing real Gemini API call")
        
        chain = GeminiLLMChain(model_name=TEST_GOOGLE_MODEL)
        response = chain.generate(
            prompt="Say 'Hello from Gemini' and nothing else.",
            max_tokens=50
        )
        
        # Verify we got a real response
        assert response.content
        assert len(response.content) > 0
        assert "gemini" in response.content.lower()
        
        # Verify metadata structure
        assert response.metadata["provider"] == "gemini"
        assert response.metadata["model"] == TEST_GOOGLE_MODEL
        
        logger.info(f"Real Gemini response: {response.content[:50]}...")
    
    @pytest.mark.skipif(
        not (os.getenv("ANTHROPIC_API_KEY") and os.getenv("GOOGLE_API_KEY")), 
        reason="Both API keys needed for unified chain test"
    )
    def test_real_unified_chain_model_switching(self):
        """Test real API calls with model switching."""
        logger.info("Testing real unified chain with model switching")
        
        # Start with Anthropic
        chain = LLMChain(model=TEST_ANTHROPIC_MODEL)
        
        # Test Anthropic
        anthropic_response = chain.generate("Say 'Anthropic test' briefly.")
        assert anthropic_response.content
        assert anthropic_response.metadata["provider"] == "anthropic"
        
        # Switch to Gemini for one call
        gemini_response = chain.generate(
            "Say 'Gemini test' briefly.", 
            model=TEST_GOOGLE_MODEL
        )
        assert gemini_response.content
        assert gemini_response.metadata["provider"] == "gemini"
        
        logger.info("Real model switching test completed")
    
    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"), 
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_real_anthropic_api_call(self):
        """Test real Anthropic API call."""
        logger.info("Testing real Anthropic API call")
        
        chain = AnthropicLLMChain(model_name=TEST_ANTHROPIC_MODEL)
        response = chain.generate(
            prompt="Think about why the sky is blue, then explain it simply.",
            max_tokens=50
        )
        
        # Should get a response (thinking content is internal)
        assert response.content
        assert len(response.content) > 10
        assert response.metadata["provider"] == "anthropic"
        
        logger.info("Real thinking tokens test completed")
    

# Configuration for running integration tests
class TestIntegrationConfig:
    """Configuration and utilities for integration tests."""
    
    @staticmethod
    def check_api_keys():
        """Check which API keys are available."""
        anthropic_available = bool(os.getenv("ANTHROPIC_API_KEY"))
        google_available = bool(os.getenv("GOOGLE_API_KEY"))
        
        return {
            "anthropic": anthropic_available,
            "google": google_available,
            "both": anthropic_available and google_available
        }
    
    def test_api_key_availability(self):
        """Report which API keys are available for testing."""
        keys = self.check_api_keys()
        logger.info(f"API Key availability: {keys}")
        
        if not any(keys.values()):
            pytest.skip("No API keys available - all integration tests will be skipped")

if __name__ == "__main__":
    # Run only integration tests
    pytest.main([__file__, "-v", "-m", "integration"]) 