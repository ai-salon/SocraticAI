import os
import time

import assemblyai as aai

aai.settings.api_key = os.getenv("ASSEMBLYAI_KEY")


def transcribe(file_path, output_file=None):
    """
    Transcribes an audio file using AssemblyAI's transcription service.

    Args:
        file_path (str): The path to the audio file to transcribe.
        output_file (str, optional): The path to save the transcript to. If not provided,
            a default path will be used.

    Returns:
        assemblyai.transcript.Transcript: The transcript object returned by AssemblyAI.
    """
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
    transcript_text = "\n".join(utterances)
    print(f"Transcribed in {time.time() - start:.2f} seconds")
    if output_file is None:
        output_file = os.path.splitext(file_path)[0] + "_transcript.txt"
    with open(output_file, "w") as f:
        f.write(transcript_text)
    return transcript
