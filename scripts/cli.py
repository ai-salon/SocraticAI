import argparse
import logging
from glob import glob

from ChatDigest.generate.interpret import interpret_transcript
from ChatDigest.generate.multi_convo_insights import \
    compare_conversation_insights
from ChatDigest.transcribe import transcribe

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Initialize the logger
logger = logging.getLogger("ChatDigestCLI")



def transcribe_generate(file_path, expand=False):
    output_file, transcription = transcribe(file_path)
    insight_string = interpret_transcript(output_file, expand)
    return insight_string

def generate_multi(path_pattern, expand, multi_convo_path):
    insight_strings = []
    for file_path in glob(path_pattern):
        s = interpret_transcript(file_path, expand)
        insight_strings.append(s)
    if multi_convo_path:
        out = compare_conversation_insights(insight_strings)
        with open(multi_convo_path, "w") as f:
            f.write(out)



def transcribe_multi(path_pattern):
    for file_path in glob(path_pattern):
        logger.info(f"Transcribing {file_path}...")
        output_file, transcription = transcribe(file_path)
        logger.info(f"Transcribed {file_path} to {output_file}")


# Initialize the argument parser
parser = argparse.ArgumentParser(description="ChatDigest CLI")
subparsers = parser.add_subparsers(title="commands", dest="command")

# Create the parser for the transcribe_generate command
parser_generate = subparsers.add_parser("full_run", help="Trabnscribe and generate_insights")
parser_generate.add_argument("file_path", help="the name of the audio file to use")
parser_generate.add_argument("--expand", action="store_true", help="expand the transcript into insights")


# Create the parser for the 'generate' command
parser_generate = subparsers.add_parser("generate", help="Generate insights from a transcript")
parser_generate.add_argument("file_path", help="the name of the transcription to use")
parser_generate.add_argument("--expand", action="store_true", help="expand the transcript into insights")
parser_generate.set_defaults(func=interpret_transcript)

# Create the parser for the 'generate_multi' command
parser_generate_multi = subparsers.add_parser("generate_multi", help="Generate insights from multiple transcripts")
parser_generate_multi.add_argument("path_pattern", help="the pattern of the transcripts to use for insights")
parser_generate_multi.add_argument("--expand", action="store_true", help="expand the insights into blogs")
parser_generate_multi.add_argument("--multi_convo_path", default=None, help="the path to write the multi-convo insights to")

parser_generate_multi.set_defaults(func=generate_multi)

# Create the parser for the 'transcribe' command
parser_transcribe = subparsers.add_parser("transcribe", help="Transcribe a single file")
parser_transcribe.add_argument("file_path", help="the name of the audio file to transcribe")
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
    args = parser.parse_args()

    # Call the default function for the selected command
    if hasattr(args, "func"):
        args_dict = vars(args)
        # Remove the 'command' key
        args_dict.pop('command', None)  # The `None` is there to prevent KeyError if 'command' is not in the dictionary
        func = args_dict.pop('func')
        # Call the function with the modified dictionary
        func(**args_dict)
    else:
        parser.print_help()

# Ensure this is at the bottom of the cli.py file
if __name__ == '__main__':
    main()
