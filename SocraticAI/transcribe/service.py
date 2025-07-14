import logging
import os
import time

import assemblyai as aai

from socraticai.transcribe.utils import anonymize_transcript
from socraticai.core.utils import (
    get_anonymized_path,
    get_transcribed_path,
)
from socraticai.core.colored_logging import get_colored_logger
from socraticai.config import ASSEMBLYAI_API_KEY

logger = logging.getLogger(__name__)
colored_logger = get_colored_logger(__name__)

aai.settings.api_key = ASSEMBLYAI_API_KEY


def transcribe(file_path, output_file=None, anonymize=True):
    """
    Transcribes an audio file using AssemblyAI's transcription service.

    Args:
        file_path (str): The path to the audio file to transcribe.
        output_file (str, optional): The path to save the transcript to. If not provided,
            a default path will be used.
        anonymize (bool, optional): Whether to anonymize the transcript. Defaults to True.

    Returns:
        tuple: A tuple containing the output file path and the transcript text.
    """
    if output_file is None:
        output_file = get_transcribed_path(file_path)

    filename = os.path.basename(file_path)
    colored_logger.setup_rich_logging()
    
    if os.path.exists(output_file):
        colored_logger.transcription_found(filename, output_file)
        with open(output_file, "r") as f:
            transcript = f.read()
    else:
        if aai.settings.api_key is None:
            raise ValueError("ASSEMBLYAI_KEY environment variable not set")
        
        colored_logger.transcription_start(filename, "AssemblyAI")
        start = time.time()
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(
            file_path, config=aai.TranscriptionConfig(speaker_labels=True)
        )
        utterances = [
            f"Speaker {utterance.speaker}: {utterance.text}"
            for utterance in transcript.utterances
        ]
        transcript_string = "\n".join(utterances)
        duration = time.time() - start
        colored_logger.transcription_complete(filename, os.path.basename(output_file), duration)
        
        with open(output_file, "w") as f:
            f.write(transcript_string)
        transcript = transcript_string
    returned_file = output_file

    if anonymize:
        anon_file_path = get_anonymized_path(file_path)
        if not os.path.exists(anon_file_path):
            colored_logger.anonymization_start(filename)
            start_time = time.time()
            transcript, entities_count = anonymize_transcript(output_file, anon_file_path)
            duration = time.time() - start_time
            colored_logger.anonymization_complete(filename, entities_count)
        else:
            with open(anon_file_path, "r") as f:
                transcript = f.read()
        returned_file = anon_file_path
    else:
        colored_logger.anonymization_skipped("disabled by user")

    return returned_file, transcript
