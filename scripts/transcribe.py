import argparse

from ChatDigest.transcribe import transcribe

parser = argparse.ArgumentParser()
parser.add_argument("file_path", help="the name of the file to transcribe")
parser.add_argument(
    "output_file",
    help="the name of the transcribed file. Defaults to the same name as the input with a _transcript suffix.",
    default=None,
    nargs="?",
)


args = parser.parse_args()

transcription = transcribe(args.file_path, args.output_file)
print(transcription)
