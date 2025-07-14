import logging
import os
import re
import uuid
from glob import glob
from typing import Dict, List

import tiktoken

from socraticai.config import DATA_DIRECTORY
from socraticai.core.llm import ANTHROPIC_MODELS, GEMINI_MODELS


def ensure_data_directories():
    """Ensure all required data directories exist."""
    subdirs = ['inputs', 'transcripts', 'processed', 'outputs']
    for subdir in subdirs:
        path = os.path.join(DATA_DIRECTORY, subdir)
        if not os.path.exists(path):
            os.makedirs(path)
            logging.info(f"Created directory: {path}")


def get_data_directory(subdirectory):
    """Get the path to a data subdirectory, creating it if it doesn't exist."""
    path = os.path.join(DATA_DIRECTORY, subdirectory)
    if not os.path.exists(path):
        os.makedirs(path)
        logging.info(f"Created directory: {path}")
    return path


def get_transcribed_path(file_path):
    """Get the path where a transcription should be saved."""
    basename = os.path.basename(file_path)
    if not basename.endswith("_transcript.txt"):
        basename = os.path.splitext(basename)[0] + "_transcript.txt"
    return os.path.join(get_data_directory("transcripts"), basename)


def get_anonymized_path(file_path):
    """Get the path where an anonymized transcription should be saved."""
    return (
        get_transcribed_path(file_path)
        .replace(".txt", "_anon.txt")
        .replace("transcripts", "processed")
    )

def get_input_path():
    """Get the path where input files should be saved."""
    return get_data_directory("inputs")

def get_output_path():
    """Get the path where output files should be saved."""
    return get_data_directory("outputs")


def get_stats():
    """Get statistics about the files in the data directory."""
    ensure_data_directories()
    
    audio_files = glob(os.path.join(DATA_DIRECTORY, "inputs", "*"))
    audio_files = [file for file in audio_files if not file.endswith(".py")]
    transcriptions = glob(os.path.join(DATA_DIRECTORY, "transcripts", "*_transcript.txt"))
    anonymized_files = glob(os.path.join(DATA_DIRECTORY, "processed", "*_anon.txt"))
    articles = glob(os.path.join(DATA_DIRECTORY, "outputs", "articles","*.md"))

    print("\nSocraticAI Data Directory Statistics:")
    print("-" * 35)
    print(f"Audio files: {len(audio_files)}")
    print(f"Transcriptions: {len(transcriptions)}")
    print(f"Anonymized files: {len(anonymized_files)}")
    print(f"Articles: {len(articles)}")
    print(f"\nData directory: {DATA_DIRECTORY}")


def split_text(text, chunk_size=1000, overlap=200):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    chunks = []
    
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(encoding.decode(chunk_tokens))
        start += (chunk_size - overlap)
    
    return chunks


def chunk_text(text, chunk_size=5000, chunk_overlap=0):
    chunks = split_text(text, chunk_size, chunk_overlap)
    return chunks


def count_message_tokens(
    messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo-0301"
) -> int:
    """
    Returns the number of tokens used by a list of messages.

    Args:
    messages (list): A list of messages, each of which is a dictionary containing the role and content of the message.
    model (str): The name of the model to use for tokenization. Defaults to "gpt-3.5-turbo-0301".

    Returns:
    int: The number of tokens used by the list of messages.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logging.warn("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        # !Node: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return count_message_tokens(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        # !Note: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return count_message_tokens(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def count_string_tokens(string: str, model_name: str = "gpt-3.5-turbo-0301") -> int:
    """
    Returns the number of tokens in a text string.

    Args:
    string (str): The text string.
    model_name (str): The name of the encoding to use. (e.g., "gpt-3.5-turbo")

    Returns:
    int: The number of tokens in the text string.
    """
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def get_model_context_limit(model_name: str) -> int:
    """
    Get the context window limit for a specific model.
    
    Args:
        model_name: The name of the model
        
    Returns:
        int: The context window limit in tokens
    """
    # Claude models context limits
    if model_name in ANTHROPIC_MODELS:
        # Claude 3.5 Sonnet and newer models have 200k context
        if "claude-3-5-sonnet" in model_name or "claude-3-7-sonnet" in model_name:
            return 200000
        # Claude 3.5 Haiku has 200k context
        elif "claude-3-5-haiku" in model_name:
            return 200000
        # Claude 3 Opus has 200k context
        elif "claude-3-opus" in model_name:
            return 200000
        # Claude 3 Sonnet has 200k context
        elif "claude-3-sonnet" in model_name:
            return 200000
        # Claude 3 Haiku has 200k context
        elif "claude-3-haiku" in model_name:
            return 200000
        else:
            # Conservative default for unknown Claude models
            return 200000
    
    # Gemini models context limits
    elif model_name in GEMINI_MODELS:
        # Gemini 2.5 Pro has 1M context
        if "gemini-2.5-pro" in model_name:
            return 1000000
        # Gemini 2.5 Flash has 1M context
        elif "gemini-2.5-flash" in model_name:
            return 1000000
        else:
            # Conservative default for unknown Gemini models
            return 1000000
    
    else:
        # Conservative default for unknown models
        logging.warning(f"Unknown model '{model_name}', using conservative 200k token limit")
        return 200000


def estimate_transcript_tokens(transcript: str, model_name: str = "gpt-3.5-turbo") -> int:
    """
    Estimate the number of tokens in a transcript for a given model.
    
    Args:
        transcript: The transcript text
        model_name: The model name (for encoding selection)
        
    Returns:
        int: Estimated number of tokens
    """
    try:
        # Use appropriate encoding based on model
        if model_name in ANTHROPIC_MODELS:
            # Claude uses cl100k_base encoding
            encoding = tiktoken.get_encoding("cl100k_base")
        elif model_name in GEMINI_MODELS:
            # Gemini also uses cl100k_base encoding approximately
            encoding = tiktoken.get_encoding("cl100k_base")
        else:
            # Default to cl100k_base for unknown models
            encoding = tiktoken.get_encoding("cl100k_base")
        
        return len(encoding.encode(transcript))
    except Exception as e:
        logging.error(f"Error estimating tokens for transcript: {e}")
        # Fallback: rough estimate of 4 characters per token
        return len(transcript) // 4


def group_transcripts_by_context(transcripts: List[Dict[str, str]], model_name: str, 
                                 safety_margin: float = 0.75) -> List[List[Dict[str, str]]]:
    """
    Group transcripts into batches that fit within the model's context window.
    
    Args:
        transcripts: List of transcript dictionaries with 'content' and 'source' keys
        model_name: The model name to determine context limits
        safety_margin: Percentage of context to use (default 0.75 = 75%)
        
    Returns:
        List of transcript groups, where each group fits within context limits
    """
    context_limit = get_model_context_limit(model_name)
    usable_tokens = int(context_limit * safety_margin)
    
    logging.info(f"Grouping transcripts for model {model_name} with {usable_tokens} usable tokens "
                f"(safety margin: {safety_margin:.1%})")
    
    groups = []
    current_group = []
    current_tokens = 0
    
    # Reserve tokens for prompts and overhead (rough estimate)
    prompt_overhead = 2000
    
    for transcript in transcripts:
        transcript_tokens = estimate_transcript_tokens(transcript['content'], model_name)
        
        # Check if single transcript exceeds limit
        if transcript_tokens > (usable_tokens - prompt_overhead):
            logging.warning(f"Single transcript from {transcript['source']} ({transcript_tokens} tokens) "
                          f"exceeds context limit. May need truncation.")
            
            # If we have a current group, save it
            if current_group:
                groups.append(current_group)
                current_group = []
                current_tokens = 0
            
            # Add oversized transcript as its own group
            groups.append([transcript])
            continue
        
        # Check if adding this transcript would exceed the limit
        if current_tokens + transcript_tokens + prompt_overhead > usable_tokens:
            # Start a new group
            if current_group:
                groups.append(current_group)
            current_group = [transcript]
            current_tokens = transcript_tokens
        else:
            # Add to current group
            current_group.append(transcript)
            current_tokens += transcript_tokens
    
    # Add any remaining group
    if current_group:
        groups.append(current_group)
    
    logging.info(f"Created {len(groups)} transcript groups from {len(transcripts)} transcripts")
    for i, group in enumerate(groups):
        total_tokens = sum(estimate_transcript_tokens(t['content'], model_name) for t in group)
        logging.info(f"Group {i+1}: {len(group)} transcripts, ~{total_tokens} tokens")
    
    return groups


class Prompt:
    """
    A class representing a prompt with variables to be filled in.

    Attributes:
    -----------
    template : str
        The string template for the prompt, with variables to be filled in using the `format` method.
    """

    def __init__(self, name, template):
        """
        Initializes a new Prompt object.

        Parameters:
        -----------
        template : str
            The string template for the prompt, with variables to be filled in using the `format` method.
        """
        # generate random id
        self.id = f"prompt_{uuid.uuid4()}"
        self.template = template

    def __call__(self, **kwargs):
        """
        Formats the prompt string with the given keyword arguments.

        Parameters:
        -----------
        **kwargs : dict
            The keyword arguments to be used to fill in the variables in the prompt string.

        Returns:
        --------
        str
            The formatted prompt string.
        """
        return self.template.format(**kwargs)

    def required_variables(self):
        """
        Returns a list of the variable names that are required to fill in the prompt string.

        Returns:
        --------
        list of str
            The list of variable names that are required to fill in the prompt string.
        """
        pattern = r"\{(\w+)\}"
        variable_names = re.findall(pattern, self.template)
        return variable_names

    def __str__(self):
        """Return the current state of the template."""
        return self.template
