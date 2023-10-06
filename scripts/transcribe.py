import argparse

from ChatDigest.transcribe import transcribe

parser = argparse.ArgumentParser()
parser.add_argument("file_path", help="the name of the file to transcribe")
parser.add_argument(
    "output_file",
    help="the name of the file to transcribe",
    default=None,
    optional=True,
)


args = parser.parse_args()

transcription = transcribe(args.filename, args.output_file)
print(transcription)
