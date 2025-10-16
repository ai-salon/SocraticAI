import os

BASE_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Update for a different data directory
DATA_DIRECTORY = os.path.join(BASE_DIRECTORY, "data")

# API Keys configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

# Default model configuration
DEFAULT_LLM_MODEL = "claude-3-7-sonnet-20250219"

# Model choices for CLI
MODEL_CHOICES = {
    "default": "gemini-2.5-flash",
    "flash": "gemini-2.5-flash",
    "sonnet": "claude-sonnet-4-20250514",
    "pro": "gemini-2.5-pro"
}
