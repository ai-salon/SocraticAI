import logging
import os
import re
import uuid
from glob import glob
from typing import Dict, List

import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter

from SocraticAI.config import DATA_DIRECTORY


def get_data_directory(subdirectory):
    path = os.path.join(DATA_DIRECTORY, subdirectory)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_transcribed_path(file_path):
    basename = os.path.basename(file_path)
    if not basename.endswith("_transcript.txt"):
        basename = os.path.splitext(basename)[0] + "_transcript.txt"
    return os.path.join(get_data_directory("transcripts"), basename)


def get_processed_path(file_path):
    return (
        get_transcribed_path(file_path)
        .replace(".txt", "_processed.txt")
        .replace("transcripts", "processed")
    )


def get_anonymized_path(file_path):
    return get_processed_path(file_path).replace(".txt", "_anon.txt")


def get_output_path(file_path, postfix):
    basename = os.path.basename(file_path)
    basename = os.path.splitext(basename)[0] + "_" + postfix
    return os.path.join(get_data_directory("outputs"), basename)


def get_stats():
    audio_files = glob(os.path.join(DATA_DIRECTORY, "inputs", "*"))
    transcriptions = glob(os.path.join(DATA_DIRECTORY, "processed", "*transcript.txt"))
    processed_files = glob(os.path.join(DATA_DIRECTORY, "processed", "*_processed.txt"))
    anonymized_files = glob(os.path.join(DATA_DIRECTORY, "processed", "*_anon.txt"))
    takeaways = glob(os.path.join(DATA_DIRECTORY, "outputs", "*takeaways.md"))

    # log number of each
    logging.info(f"{len(audio_files)} audio files")
    logging.info(f"{len(transcriptions)} transcriptions")
    logging.info(f"{len(processed_files)} processed files")
    logging.info(f"{len(anonymized_files)} anonymized files")
    logging.info(f"{len(takeaways)} takeaways")


def chunk_text(text, chunk_size=5000, chunk_overlap=0):
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    docs = text_splitter.create_documents([text])
    chunks = [d.page_content for d in docs]
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
