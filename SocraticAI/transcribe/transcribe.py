import logging
import os
import time

import assemblyai as aai

from SocraticAI.transcribe.process import anonymize_transcript, process_file
from SocraticAI.utils import (
    get_anonymized_path,
    get_processed_path,
    get_transcribed_path,
)

logger = logging.getLogger(__name__)

aai.settings.api_key = os.getenv("ASSEMBLYAI_KEY")


def transcribe(file_path, process=True, output_file=None):
    """
    Transcribes an audio file using AssemblyAI's transcription service.

    Args:
        file_path (str): The path to the audio file to transcribe.
        process (bool, optional): Whether to process the transcript after transcription.
            Defaults to True.
        anonymize_transcript (bool, optional): Whether to anonymize the transcript.
            Defaults to True.
        output_file (str, optional): The path to save the transcript to. If not provided,
            a default path will be used.

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
    if process is True:
        transcript_file = output_file
        processed_file_path = get_processed_path(file_path)
        if not os.path.exists(processed_file_path):
            logger.info(f"Processing {transcript_file}...")
            transcript = process_file(transcript_file)
        else:
            logger.info(f"Processed already. Loading {processed_file_path}...")
            with open(processed_file_path, "r") as f:
                transcript = f.read()
        anon_file_path = get_anonymized_path(file_path)
        if not os.path.exists(anon_file_path):
            logger.info(f"Anonymizing {processed_file_path}...")
            transcript = anonymize_transcript(processed_file_path, anon_file_path)
        else:
            logger.info(f"Anonymized already. Loading {anon_file_path}...")
            with open(anon_file_path, "r") as f:
                transcript = f.read()
    return output_file, transcript
