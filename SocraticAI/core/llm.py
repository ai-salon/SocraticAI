import logging
import os
from collections import namedtuple
from typing import Optional, Dict, Any, List, Union
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from socraticai.config import ANTHROPIC_API_KEY, DEFAULT_LLM_MODEL

logger = logging.getLogger(__name__)
MODEL = DEFAULT_LLM_MODEL

class LLMResponse:
    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.metadata = metadata or {}

class LLMChain:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("Anthropic API key must be provided or set in ANTHROPIC_API_KEY environment variable")
        self.client = Anthropic(api_key=self.api_key)
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate(self, 
                prompt: str, 
                system_prompt: Optional[str] = '',
                temperature: float = 0.7,
                max_tokens: int = 4096,
                thinking_tokens: int = 0) -> LLMResponse:
        """
        Generate a response using Anthropic's Claude model.
        
        Args:
            prompt: The main prompt to send to the model
            system_prompt: Optional system prompt to set context
            temperature: Controls randomness in the output (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            thinking_tokens: Maximum number of tokens to use for thinking

        Returns:
            LLMResponse object containing the generated content and metadata
        """
        max_tokens = max(max_tokens, thinking_tokens+1)
        try:
            messages = []
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            kwargs = {
                "model": MODEL,
                "max_tokens": max_tokens,
                "messages": messages,
                "temperature": temperature
            }
            if system_prompt:
                kwargs["system"] = system_prompt
            if thinking_tokens > 0:
                kwargs['temperature'] = 1
                kwargs["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": thinking_tokens
                }

            response = self.client.messages.create(**kwargs)
            
            if thinking_tokens > 0:
                content = response.content[1].text
            else:
                content = response.content[0].text
            
            return LLMResponse(
                content=content,
                metadata={
                    "model": response.model,
                    "usage": response.usage
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    def process_chain(self, 
                     initial_input: str,
                     processors: List[callable],
                     **kwargs) -> List[LLMResponse]:
        """
        Process a chain of operations on the input text.
        
        Args:
            initial_input: The starting text to process
            processors: List of processing functions to apply sequentially
            **kwargs: Additional arguments to pass to processors
            
        Returns:
            List of LLMResponse objects from each processing step
        """
        results = []
        current_input = initial_input
        
        for processor in processors:
            result = processor(current_input, **kwargs)
            results.append(result)
            current_input = result.content
            
        return results
