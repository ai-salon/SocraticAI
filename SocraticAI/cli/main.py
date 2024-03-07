import argparse
import os

from dotenv import find_dotenv, load_dotenv

from SocraticAI.cli.commands import (
    generate_multi,
    transcribe_generate,
    transcribe_multi,
)
from SocraticAI.generate.interpret import interpret_transcript
from SocraticAI.transcribe.transcribe import transcribe
from SocraticAI.utils import get_stats

# Initialize the argument parser
parser = argparse.ArgumentParser(description="SocraticAI CLI")
subparsers = parser.add_subparsers(title="commands", dest="command")

# Create the parser for stats
parser_generate = subparsers.add_parser("stats", help="Stats on repo")
parser_generate.set_defaults(func=get_stats)

# Create the parser for the transcribe_generate command
parser_generate = subparsers.add_parser(
    "full_run", help="Transcribe and generate_insights"
)
parser_generate.add_argument("file_path", help="the name of the audio file to use")
parser_generate.set_defaults(func=transcribe_generate)


# Create the parser for the 'generate' command
parser_generate = subparsers.add_parser(
    "generate", help="Generate insights from a transcript"
)
parser_generate.add_argument("file_path", help="the name of the transcription to use")
parser_generate.set_defaults(func=interpret_transcript)

# Create the parser for the 'generate_multi' command
parser_generate_multi = subparsers.add_parser(
    "generate_multi", help="Generate insights from multiple transcripts"
)
parser_generate_multi.add_argument(
    "path_pattern", help="the pattern of the transcripts to use for insights"
)
parser_generate_multi.set_defaults(func=generate_multi)

# Create the parser for the 'transcribe' command
parser_transcribe = subparsers.add_parser("transcribe", help="Transcribe a single file")
parser_transcribe.add_argument(
    "file_path", help="the name of the audio file to transcribe"
)
parser_transcribe.add_argument(
    "--output_file", help="the name of the file the transcription is saved to"
)
parser_transcribe.set_defaults(func=transcribe)

# Create the parser for the 'transcribe_multi' command
parser_transcribe_multi = subparsers.add_parser(
    "transcribe_multi", help="Transcribe multiple files"
)
parser_transcribe_multi.add_argument(
    "path_pattern", help="the pattern of the files to transcribe"
)
parser_transcribe_multi.set_defaults(func=transcribe_multi)


def main():
    # Parse the command line arguments
    dotenv_path = find_dotenv()
    print(f"Loading dotenv at {dotenv_path}", load_dotenv(dotenv_path))
    print(f'os.getenv("MODEL_TYPE") = {os.getenv("MODEL_TYPE")}')

    args = parser.parse_args()

    # Call the default function for the selected command
    if hasattr(args, "func"):
        args_dict = vars(args)
        # Remove the 'command' key
        args_dict.pop(
            "command", None
        )  # The `None` is there to prevent KeyError if 'command' is not in the dictionary
        func = args_dict.pop("func")
        # Call the function with the modified dictionary
        func(**args_dict)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
