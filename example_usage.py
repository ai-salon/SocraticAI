#!/usr/bin/env python3
"""
Example usage of the abstracted LLM system supporting both Anthropic and Gemini models.
"""

from socraticai.core.llm import create_llm_chain, LLMChain
from socraticai.config import TEST_GOOGLE_MODEL, TEST_ANTHROPIC_MODEL

def main():
    # Example 1: Using the unified LLMChain with model parameter (Recommended)
    print("=== Example 1: Unified LLMChain with model parameter ===")
    
    # Use Anthropic Claude
    claude_chain = LLMChain(model=TEST_ANTHROPIC_MODEL)
    print(f"Created: {claude_chain}")
    response1 = claude_chain.generate(
        prompt="What is the capital of France?",
        system_prompt="You are a helpful geography assistant."
    )
    print(f"Claude Response: {response1.content}")
    print(f"Provider: {response1.metadata.get('provider')}")
    print()
    
    # Use Google Gemini (if available)
    try:
        gemini_chain = LLMChain(model=TEST_GOOGLE_MODEL)
        print(f"Created: {gemini_chain}")
        response2 = gemini_chain.generate(
            prompt="What is the capital of France?",
            system_prompt="You are a helpful geography assistant."
        )
        print(f"Gemini Response: {response2.content}")
        print(f"Provider: {response2.metadata.get('provider')}")
    except ImportError as e:
        print(f"Gemini not available: {e}")
    except Exception as e:
        print(f"Error with Gemini: {e}")
    print()
    
    # Example 2: Temporary model override in generate method
    print("=== Example 2: Temporary model override ===")
    
    # Create a Claude chain but temporarily use Gemini for one generation
    main_chain = LLMChain(model=TEST_ANTHROPIC_MODEL)
    print(f"Main chain: {main_chain}")
    
    # Use the main model
    response3 = main_chain.generate("What is 2+2?")
    print(f"Main model response: {response3.content}")
    print(f"Provider: {response3.metadata.get('provider')}")
    
    # Temporarily override to use Gemini for this specific generation
    try:
        response4 = main_chain.generate(
            "What is 2+2?", 
            model=TEST_GOOGLE_MODEL
        )
        print(f"Temporary override response: {response4.content}")
        print(f"Provider: {response4.metadata.get('provider')}")
    except Exception as e:
        print(f"Temporary override failed: {e}")
    
    # Back to main model for next generation
    response5 = main_chain.generate("What is 3+3?")
    print(f"Back to main model: {response5.content}")
    print(f"Provider: {response5.metadata.get('provider')}")
    print()
    
    # Example 3: Using factory function for direct access
    print("=== Example 3: Factory function (Alternative approach) ===")
    
    # This will automatically use AnthropicLLMChain
    anthropic_chain = create_llm_chain(TEST_ANTHROPIC_MODEL)
    response6 = anthropic_chain.generate(
        prompt="What is AI?",
        system_prompt="You are a tech expert."
    )
    print(f"Factory Response: {response6.content}")
    print(f"Provider: {response6.metadata.get('provider')}")
    print()
    
    # Example 4: Default model usage
    print("=== Example 4: Default model usage ===")
    
    # Uses the DEFAULT_LLM_MODEL from config
    default_chain = LLMChain()
    print(f"Created: {default_chain}")
    response7 = default_chain.generate(
        prompt="Explain quantum computing in simple terms.",
        temperature=0.5
    )
    print(f"Default Response: {response7.content[:100]}...")
    print(f"Provider: {response7.metadata.get('provider')}")
    print()
    
    # Example 5: Using process_chain with unified interface
    print("=== Example 5: Process chain with unified interface ===")
    
    def summarizer(text, **kwargs):
        chain = LLMChain(model=TEST_ANTHROPIC_MODEL)
        return chain.generate(f"Summarize this in one sentence: {text}")
    
    def translator(text, **kwargs):
        # You can even use different models in the chain!
        try:
            chain = LLMChain(model=TEST_GOOGLE_MODEL)
        except:
            chain = LLMChain(model=TEST_ANTHROPIC_MODEL)
        return chain.generate(f"Translate this to Spanish: {text}")
    
    processors = [summarizer, translator]
    processing_chain = LLMChain(model=TEST_ANTHROPIC_MODEL)
    results = processing_chain.process_chain(
        "Artificial intelligence is a branch of computer science that aims to create machines that mimic human intelligence. It involves developing algorithms and systems that can perform tasks typically requiring human intelligence, such as learning, reasoning, perception, and decision-making.",
        processors
    )
    
    for i, result in enumerate(results):
        print(f"Step {i+1}: {result.content}")
    print()
    
    # Example 6: Dynamic model switching and comparison
    print("=== Example 6: Dynamic model switching and comparison ===")
    
    models_to_try = ["claude-3-5-sonnet-20241022", "gemini-1.5-pro"]
    prompt = "What's the meaning of life?"
    
    # Method 1: Create separate chains
    for model in models_to_try:
        try:
            chain = LLMChain(model=model)
            response = chain.generate(prompt, temperature=0.8)
            print(f"{model}: {response.content[:80]}...")
        except Exception as e:
            print(f"{model}: Error - {e}")
    
    print()
    
    # Method 2: Use temporary model override (more efficient)
    base_chain = LLMChain(model=TEST_ANTHROPIC_MODEL)
    for model in models_to_try:
        try:
            response = base_chain.generate(prompt, model=model, temperature=0.8)
            print(f"{model} (override): {response.content[:80]}...")
        except Exception as e:
            print(f"{model} (override): Error - {e}")

if __name__ == "__main__":
    main() 