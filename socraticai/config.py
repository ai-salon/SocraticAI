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
