import logging
import os
import re
import uuid
from glob import glob
from typing import Dict, List

import tiktoken

from socraticai.config import DATA_DIRECTORY


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
