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
    output_file, _ = transcribe(file_path)
    takeaway_string = interpret_transcript(output_file, expand)
    return takeaway_string


def generate_multi(path_pattern, expand):
    takeaway_strings = []
    for file_path in glob(path_pattern):
        s = interpret_transcript(file_path, expand)
        takeaway_strings.append(s)


def transcribe_multi(path_pattern):
    for file_path in glob(path_pattern):
        logger.info(f"Transcribing {file_path}...")
        output_file, _ = transcribe(file_path)
        logger.info(f"Transcribed {file_path} to {output_file}")
