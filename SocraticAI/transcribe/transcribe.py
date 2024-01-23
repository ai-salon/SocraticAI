import logging
import os
import time

import assemblyai as aai

from SocraticAI.transcribe.process import anonymize_transcript, process_file
from SocraticAI.utils import get_data_directory

logger = logging.getLogger(__name__)

aai.settings.api_key = os.getenv("ASSEMBLYAI_KEY")


def transcribe(file_path, process=True, anonymize=True, output_file=None):
    """
    Transcribes an audio file using AssemblyAI's transcription service.

    Args:
        file_path (str): The path to the audio file to transcribe.
        output_file (str, optional): The path to save the transcript to. If not provided,
            a default path will be used.

    Returns:
        assemblyai.transcript.Transcript: The transcript object returned by AssemblyAI.
    """
    if output_file is None:
        basename = os.path.basename(file_path)
        basename = os.path.splitext(basename)[0] + "_transcript.txt"
        output_file = os.path.join(get_data_directory("processed"), basename)

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
        transcript = "\n".join(utterances)
        logger.info(f"Transcribed in {time.time() - start:.2f} seconds")
        with open(output_file, "w") as f:
            f.write(transcript)
    if process is True:
        transcript_file = output_file
        processed_file_path = transcript_file.replace(".txt", "_processed.txt")
        if not os.path.exists(processed_file_path):
            logger.info(f"Processing {transcript_file}...")
            transcript = process_file(transcript_file)
        else:
            logger.info(f"Processed already. Loading {processed_file_path}...")
            with open(processed_file_path, "r") as f:
                transcript = f.read()
        if anonymize_transcript:
            transcript = anonymize_transcript(processed_file_path, save_file=True)
    return output_file, transcript
