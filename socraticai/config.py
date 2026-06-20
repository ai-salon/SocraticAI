import os

BASE_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Update for a different data directory
DATA_DIRECTORY = os.path.join(BASE_DIRECTORY, "data")

# API Keys configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

# Default model configuration
DEFAULT_LLM_MODEL = "gemini-3-flash-preview"

# Default parallelism for batch processing
DEFAULT_MAX_WORKERS = 3

# Test configuration (used by test suite)
TEST_GOOGLE_MODEL = "gemini-2.5-flash-lite"
TEST_ANTHROPIC_MODEL = "claude-haiku-4-5"
TEST_MODEL = TEST_GOOGLE_MODEL
TEST_API_KEY = os.getenv("GOOGLE_API_KEY")
