import argparse
import os
import time

import whisper
from pyannote.audio import Pipeline

from transcription_utils import convert_m4a_to_wav, diarize_text, write_to_txt

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
HF_TOKEN = os.environ.get("HF_TOKEN")


def diarize_audio(audiofile):
    print("Diarizing audio...")
    start = time.time()
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization", use_auth_token=HF_TOKEN
    )
    pipeline.to("mps")
    diarization = pipeline(audiofile)
    print(f"Diarized in {time.time() - start:.2f} seconds")
    return diarization


def transcribe_audio(file_path):
    print("Transcribing audio...")
    start = time.time()
    # Use the Recognizer class
    model = whisper.load_model("base")
    text = model.transcribe(file_path)
    print(f"Transcribed in {time.time() - start:.2f} seconds")
    return text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transcribe an audio file and save the transcription to a file."
    )
    parser.add_argument(
        "input", type=str, help="The path to the audio file to transcribe."
    )
    parser.add_argument(
        "output_dir", type=str, help="The path to the directory for audiofiles."
    )

    args = parser.parse_args()
    audiofile = convert_m4a_to_wav(args.input)

    # Transcribe the audio
    transcription = transcribe_audio(audiofile)
    try:
        diarization_result = diarize_audio(audiofile)
    except NotImplementedError:
        print("diarization failed")
        diarization_result = None
    final_result = diarize_text(transcription, diarization_result)

    transcription_location = os.path.basename(audiofile).replace(
        ".wav", "_transcribed.txt"
    )
    transcription_location = os.path.join(args.output_dir, transcription_location)
    # save the transcription
    write_to_txt(final_result, transcription_location)
