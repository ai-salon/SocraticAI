import logging
import os
import time

import assemblyai as aai

from socraticai.transcribe.utils import anonymize_transcript
from socraticai.core.utils import (
    get_anonymized_path,
    get_transcribed_path,
)
from socraticai.config import ASSEMBLYAI_API_KEY

logger = logging.getLogger(__name__)

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

    if os.path.exists(output_file):
        logger.info(f"Transcription already done. Loading {output_file}...")
        with open(output_file, "r") as f:
            transcript = f.read()
    else:
        if aai.settings.api_key is None:
            raise ValueError("ASSEMBLYAI_KEY environment variable not set")
        print("Transcribing audio with assemblyai...")
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
        logger.info(f"Transcribed in {time.time() - start:.2f} seconds")
        with open(output_file, "w") as f:
            f.write(transcript_string)
    returned_file = output_file

    if anonymize:
        anon_file_path = get_anonymized_path(file_path)
        if not os.path.exists(anon_file_path):
            logger.info(f"Anonymizing {output_file}...")
            transcript = anonymize_transcript(output_file, anon_file_path)
        else:
            logger.info(f"Anonymized already. Loading {anon_file_path}...")
            with open(anon_file_path, "r") as f:
                transcript = f.read()
        returned_file = anon_file_path

    return returned_file, transcript
