import os

import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.getenv("ANTHROPIC_KEY")
)

# models
# claude-3-haiku-20240307
# claude-3-sonnet-20240229
# claude-3-opus-20240229

message = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    temperature=0.0,
    system="Respond only in Yoda-speak.",
    messages=[{"role": "user", "content": "How are you today?"}],
)
