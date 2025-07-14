import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from socraticai.core.llm import (
    LLMChain, 
    AnthropicLLMChain, 
    GeminiLLMChain,
    AnthropicLLMResponse,
    GeminiLLMResponse,
    get_all_models,
    get_provider_from_model,
    create_llm_chain,
    ANTHROPIC_MODELS,
    GEMINI_MODELS
)
from socraticai.config import TEST_GOOGLE_MODEL, TEST_ANTHROPIC_MODEL
from tenacity import RetryError

# Set up logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mark all tests in this file as unit tests
pytestmark = pytest.mark.unit

class TestModelDetection:
    """Test model provider detection functionality."""
    
    def test_get_all_models(self):
        """Test that get_all_models returns all supported models."""
        logger.info("Testing get_all_models function")
        models = get_all_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert TEST_GOOGLE_MODEL in models
        assert TEST_ANTHROPIC_MODEL in models
        logger.info(f"Found {len(models)} total models")
    
    def test_get_provider_from_model_anthropic(self):
        """Test provider detection for Anthropic models."""
        logger.info(f"Testing provider detection for Anthropic model: {TEST_ANTHROPIC_MODEL}")
        provider = get_provider_from_model(TEST_ANTHROPIC_MODEL)
        assert provider == "anthropic"
        logger.info("Anthropic model correctly identified")
    
    def test_get_provider_from_model_gemini(self):
        """Test provider detection for Gemini models."""
        logger.info(f"Testing provider detection for Gemini model: {TEST_GOOGLE_MODEL}")
        provider = get_provider_from_model(TEST_GOOGLE_MODEL)
        assert provider == "gemini"
        logger.info("Gemini model correctly identified")
    
    def test_get_provider_from_model_unknown(self):
        """Test provider detection for unknown models defaults to anthropic."""
        logger.info("Testing provider detection for unknown model")
        with patch('socraticai.core.llm.logger') as mock_logger:
            provider = get_provider_from_model("unknown-model")
            assert provider == "anthropic"
            mock_logger.warning.assert_called_once()
        logger.info("Unknown model correctly defaulted to anthropic")

class TestAnthropicLLMChain:
    """Test Anthropic LLM chain functionality."""
    
    @patch('socraticai.core.llm.Anthropic')
    @patch('socraticai.core.llm.ANTHROPIC_API_KEY', 'test-key')
    def test_anthropic_chain_creation(self, mock_anthropic_class):
        """Test creating an Anthropic LLM chain."""
        logger.info(f"Testing Anthropic chain creation with model: {TEST_ANTHROPIC_MODEL}")
        
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        chain = AnthropicLLMChain(model_name=TEST_ANTHROPIC_MODEL)
            
        assert chain.model_name == TEST_ANTHROPIC_MODEL
        assert chain.client == mock_client
        mock_anthropic_class.assert_called_once_with(api_key='test-key')
        logger.info("Anthropic chain created successfully")
    
    @patch('socraticai.core.llm.Anthropic')
    @patch('socraticai.core.llm.ANTHROPIC_API_KEY', 'test-key')
    def test_anthropic_generate_response(self, mock_anthropic_class):
        """Test generating a response with Anthropic chain."""
        logger.info("Testing Anthropic response generation")
        
        # Mock the API response
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response from Claude")]
        mock_response.model = TEST_ANTHROPIC_MODEL
        mock_response.usage = {"prompt_tokens": 10, "completion_tokens": 20}
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        chain = AnthropicLLMChain(model_name=TEST_ANTHROPIC_MODEL)
            
        response = chain.generate("Test prompt", system_prompt="Test system")
        
        assert isinstance(response, AnthropicLLMResponse)
        assert response.content == "Test response from Claude"
        assert response.metadata["model"] == TEST_ANTHROPIC_MODEL
        assert response.metadata["provider"] == "anthropic"
        logger.info("Anthropic response generated successfully")
    
    @patch('socraticai.core.llm.Anthropic')
    @patch('socraticai.core.llm.ANTHROPIC_API_KEY', 'test-key')
    def test_anthropic_generate_with_thinking(self, mock_anthropic_class):
        """Test generating a response with thinking tokens."""
        logger.info("Testing Anthropic response generation with thinking tokens")
        
        # Mock the API response with thinking
        mock_response = Mock()
        mock_response.content = [
            Mock(text="<thinking>Some thoughts</thinking>"),
            Mock(text="Final response")
        ]
        mock_response.model = TEST_ANTHROPIC_MODEL
        mock_response.usage = {"prompt_tokens": 10, "completion_tokens": 30}
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        chain = AnthropicLLMChain(model_name=TEST_ANTHROPIC_MODEL)
            
        response = chain.generate("Test prompt", thinking_tokens=1000)
        
        assert response.content == "Final response"
        # Verify thinking parameters were passed
        call_args = mock_client.messages.create.call_args
        assert "thinking" in call_args.kwargs
        assert call_args.kwargs["thinking"]["budget_tokens"] == 1000
        logger.info("Anthropic thinking response generated successfully")

class TestGeminiLLMChain:
    """Test Gemini LLM chain functionality."""
    
    @patch('socraticai.core.llm.GENAI_AVAILABLE', True)
    @patch('socraticai.core.llm.genai')
    def test_gemini_chain_creation(self, mock_genai):
        """Test creating a Gemini LLM chain."""
        logger.info(f"Testing Gemini chain creation with model: {TEST_GOOGLE_MODEL}")
        
        mock_client = Mock()
        mock_genai.Client.return_value = mock_client
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
            chain = GeminiLLMChain(model_name=TEST_GOOGLE_MODEL)
            
        assert chain.model_name == TEST_GOOGLE_MODEL
        assert chain.client == mock_client
        mock_genai.Client.assert_called_once_with(api_key='test-key')
        logger.info("Gemini chain created successfully")
    
    @patch('socraticai.core.llm.GENAI_AVAILABLE', True)
    @patch('socraticai.core.llm.genai')
    def test_gemini_generate_response(self, mock_genai):
        """Test generating a response with Gemini chain."""
        logger.info("Testing Gemini response generation")
        
        # Mock the API response
        mock_response = Mock()
        mock_response.text = "Test response from Gemini"
        mock_response.usage_metadata = Mock()
        mock_response.usage_metadata.prompt_token_count = 10
        mock_response.usage_metadata.candidates_token_count = 25
        
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client
        mock_genai.types.GenerationConfig = Mock()
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
            chain = GeminiLLMChain(model_name=TEST_GOOGLE_MODEL)
            
        response = chain.generate("Test prompt", system_prompt="Test system")
        
        assert isinstance(response, GeminiLLMResponse)
        assert response.content == "Test response from Gemini"
        assert response.metadata["model"] == TEST_GOOGLE_MODEL
        assert response.metadata["provider"] == "gemini"
        logger.info("Gemini response generated successfully")
    
    @patch('socraticai.core.llm.GENAI_AVAILABLE', False)
    def test_gemini_unavailable_error(self):
        """Test error when Gemini dependencies are not available."""
        logger.info("Testing Gemini unavailable error")
        
        with pytest.raises(ImportError, match="google-generativeai package is required"):
            GeminiLLMChain(model_name=TEST_GOOGLE_MODEL)
        logger.info("Gemini unavailable error handled correctly")

class TestUnifiedLLMChain:
    """Test the unified LLM chain that routes to appropriate providers."""
    
    @patch('socraticai.core.llm.AnthropicLLMChain')
    def test_unified_chain_anthropic_routing(self, mock_anthropic_chain_class):
        """Test that unified chain routes to Anthropic for Anthropic models."""
        logger.info(f"Testing unified chain routing for Anthropic model: {TEST_ANTHROPIC_MODEL}")
        
        mock_chain = Mock()
        mock_anthropic_chain_class.return_value = mock_chain
        
        chain = LLMChain(model=TEST_ANTHROPIC_MODEL, api_key="test-key")
        
        assert chain.provider == "anthropic"
        mock_anthropic_chain_class.assert_called_once_with(
            model_name=TEST_ANTHROPIC_MODEL, 
            api_key="test-key"
        )
        logger.info("Unified chain correctly routed to Anthropic")
    
    @patch('socraticai.core.llm.GENAI_AVAILABLE', True)
    @patch('socraticai.core.llm.GeminiLLMChain')
    def test_unified_chain_gemini_routing(self, mock_gemini_chain_class):
        """Test that unified chain routes to Gemini for Gemini models."""
        logger.info(f"Testing unified chain routing for Gemini model: {TEST_GOOGLE_MODEL}")
        
        mock_chain = Mock()
        mock_gemini_chain_class.return_value = mock_chain
        
        chain = LLMChain(model=TEST_GOOGLE_MODEL, api_key="test-key")
        
        assert chain.provider == "gemini"
        mock_gemini_chain_class.assert_called_once_with(
            model_name=TEST_GOOGLE_MODEL, 
            api_key="test-key"
        )
        logger.info("Unified chain correctly routed to Gemini")
    
    @patch('socraticai.core.llm.AnthropicLLMChain')
    def test_unified_chain_generate(self, mock_anthropic_chain_class):
        """Test generating response through unified chain."""
        logger.info("Testing unified chain generate method")
        
        mock_response = AnthropicLLMResponse("Test response", {"model": TEST_ANTHROPIC_MODEL})
        mock_chain = Mock()
        mock_chain.generate.return_value = mock_response
        mock_anthropic_chain_class.return_value = mock_chain
        
        chain = LLMChain(model=TEST_ANTHROPIC_MODEL)
        response = chain.generate("Test prompt")
        
        assert response == mock_response
        mock_chain.generate.assert_called_once()
        logger.info("Unified chain generate method works correctly")
    
    @patch('socraticai.core.llm.AnthropicLLMChain')
    @patch('socraticai.core.llm.GENAI_AVAILABLE', True)
    @patch('socraticai.core.llm.GeminiLLMChain')
    def test_unified_chain_model_override(self, mock_gemini_chain_class, mock_anthropic_chain_class):
        """Test overriding model for specific generation."""
        logger.info("Testing unified chain model override")
        
        # Setup mocks
        mock_anthropic_chain = Mock()
        mock_gemini_chain = Mock()
        mock_anthropic_response = AnthropicLLMResponse("Anthropic response", {})
        mock_gemini_response = GeminiLLMResponse("Gemini response", {})
        
        mock_anthropic_chain.generate.return_value = mock_anthropic_response
        mock_gemini_chain.generate.return_value = mock_gemini_response
        mock_anthropic_chain_class.return_value = mock_anthropic_chain
        mock_gemini_chain_class.return_value = mock_gemini_chain
        
        # Create chain with Anthropic model
        chain = LLMChain(model=TEST_ANTHROPIC_MODEL)
        
        # Generate with different model
        response = chain.generate("Test prompt", model=TEST_GOOGLE_MODEL)
        
        # Should create temporary Gemini chain and use it
        mock_gemini_chain_class.assert_called_with(model_name=TEST_GOOGLE_MODEL, api_key=None)
        assert response == mock_gemini_response
        logger.info("Unified chain model override works correctly")

class TestErrorHandling:
    """Test error handling in LLM chains."""
    
    @patch('socraticai.core.llm.ANTHROPIC_API_KEY', None)
    def test_anthropic_missing_api_key(self):
        """Test error when Anthropic API key is missing."""
        logger.info("Testing Anthropic missing API key error")
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Anthropic API key must be provided"):
                AnthropicLLMChain(model_name=TEST_ANTHROPIC_MODEL)
        logger.info("Anthropic missing API key error handled correctly")
    
    @patch('socraticai.core.llm.GENAI_AVAILABLE', True)
    def test_gemini_missing_api_key(self):
        """Test error when Gemini API key is missing."""
        logger.info("Testing Gemini missing API key error")
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Google API key must be provided"):
                GeminiLLMChain(model_name=TEST_GOOGLE_MODEL)
        logger.info("Gemini missing API key error handled correctly")
    
    @patch('socraticai.core.llm.Anthropic')
    @patch('socraticai.core.llm.ANTHROPIC_API_KEY', 'test-key')
    def test_anthropic_generation_error(self, mock_anthropic_class):
        """Test error handling during Anthropic response generation."""
        logger.info("Testing Anthropic generation error handling")
        
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic_class.return_value = mock_client
        
        chain = AnthropicLLMChain(model_name=TEST_ANTHROPIC_MODEL)
            
        # The retry decorator will wrap the original exception in a RetryError
        # Suppress error logging during this test to reduce noise
        with patch('socraticai.core.llm.logger') as mock_logger:
            with pytest.raises(RetryError):
                chain.generate("Test prompt")
        logger.info("Anthropic generation error handled correctly")

class TestBackwardsCompatibility:
    """Test backwards compatibility functions."""
    
    @patch('socraticai.core.llm.AnthropicLLMChain')
    def test_create_llm_chain_function(self, mock_anthropic_chain_class):
        """Test the backwards compatibility create_llm_chain function."""
        logger.info("Testing backwards compatibility create_llm_chain function")
        
        mock_chain = Mock()
        mock_anthropic_chain_class.return_value = mock_chain
        
        result = create_llm_chain(TEST_ANTHROPIC_MODEL, api_key="test-key")
        
        mock_anthropic_chain_class.assert_called_once_with(
            model_name=TEST_ANTHROPIC_MODEL, 
            api_key="test-key"
        )
        assert result == mock_chain
        logger.info("Backwards compatibility function works correctly")

class TestResponseClasses:
    """Test LLM response classes."""
    
    def test_anthropic_response_creation(self):
        """Test creating an Anthropic LLM response."""
        logger.info("Testing Anthropic response creation")
        
        content = "Test response content"
        metadata = {"model": TEST_ANTHROPIC_MODEL, "tokens": 100}
        
        response = AnthropicLLMResponse(content, metadata)
        
        assert response.content == content
        assert response.metadata == metadata
        logger.info("Anthropic response created successfully")
    
    def test_gemini_response_creation(self):
        """Test creating a Gemini LLM response."""
        logger.info("Testing Gemini response creation")
        
        content = "Test response content"
        metadata = {"model": TEST_GOOGLE_MODEL, "tokens": 150}
        
        response = GeminiLLMResponse(content, metadata)
        
        assert response.content == content
        assert response.metadata == metadata
        logger.info("Gemini response created successfully")
    
    def test_response_default_metadata(self):
        """Test response creation with default metadata."""
        logger.info("Testing response creation with default metadata")
        
        response = AnthropicLLMResponse("Test content")
        
        assert response.content == "Test content"
        assert response.metadata == {}
        logger.info("Response with default metadata created successfully")

if __name__ == "__main__":
    logger.info("Running LLM tests...")
    pytest.main([__file__, "-v"])
