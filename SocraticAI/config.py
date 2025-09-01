import os

BASE_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Update for a different data directory
DATA_DIRECTORY = os.path.join(BASE_DIRECTORY, "data")

# API Keys configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

# Default model configuration (pick a valid Anthropic model by default so only ANTHROPIC_API_KEY is required)
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "claude-sonnet-4-20250514")

# Test model shortcuts used by examples/tests
TEST_ANTHROPIC_MODEL = os.getenv("TEST_ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
TEST_GOOGLE_MODEL = os.getenv("TEST_GOOGLE_MODEL", "gemini-2.5-pro")

# CLI model choices mapping
MODEL_CHOICES = {
    "default": os.getenv("DEFAULT_CLI_MODEL", "gemini-2.5-flash"),
    "flash": "gemini-2.5-flash",
    "sonnet": "claude-sonnet-4-20250514",
    "pro": "gemini-2.5-pro",
}
