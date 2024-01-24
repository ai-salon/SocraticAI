import logging
from glob import glob

from SocraticAI.generate.interpret import interpret_transcript
from SocraticAI.transcribe.transcribe import transcribe

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Initialize the logger
logger = logging.getLogger("SocraticAICLI")


def transcribe_generate(file_path, expand=False):
    """
    Transcribes the given file and generates a takeaway string.

    Args:
        file_path (str): The path to the file to be transcribed.
        expand (bool, optional): Whether to expand the takeaway string. Defaults to False.

    Returns:
        str: The generated takeaway string.
    """
    output_file, _ = transcribe(file_path)
    takeaway_string = interpret_transcript(output_file, expand)
    return takeaway_string


def generate_multi(path_pattern, expand):
    """
    Generate multiple takeaway strings from files matching the given path pattern.

    Args:
        path_pattern (str): The pattern to match the file paths.
        expand (bool): Flag indicating whether to expand the takeaway strings.

    Returns:
        list: A list of takeaway strings generated from the matching files.
    """
    takeaway_strings = []
    for file_path in glob(path_pattern):
        s = interpret_transcript(file_path, expand)
        takeaway_strings.append(s)


def transcribe_multi(path_pattern):
    """
    Transcribes multiple files based on the given path pattern.

    Args:
        path_pattern (str): The pattern to match the file paths.

    Returns:
        None
    """
    for file_path in glob(path_pattern):
        logger.info(f"Transcribing {file_path}...")
        output_file, _ = transcribe(file_path)
        logger.info(f"Transcribed {file_path} to {output_file}")
