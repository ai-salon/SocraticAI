import logging
import os

from SocraticAI.generate.takeaways import run_takeaway_generation
from SocraticAI.generate.utils import dict_to_markdown, expansion_to_string
from SocraticAI.transcribe.process import process_file
from SocraticAI.utils import get_data_directory

logger = logging.getLogger(__name__)


def interpret_transcript(file_path, expand=False):
    processed_file_path = file_path.replace(".txt", "_processed_anon.txt")
    if not os.path.exists(processed_file_path):
        logger.info(
            f"No anonymous processed file found. First transcribe and process file before continuing. Exiting..."
        )
        return
    else:
        logger.info(f"Processed already. Loading {processed_file_path}...")
        with open(processed_file_path, "r") as f:
            text = f.read()

    # create takeaways if they don't exist
    basename = os.path.basename(file_path)
    output_path = os.path.join(
        get_data_directory("outputs"),
        basename.replace("transcript.txt", "takeaways.md"),
    )

    if not os.path.exists(output_path):
        # generate takeaways and "blogs"
        logger.info("Generating takeaways...")
        try:
            takeaways = run_takeaway_generation(text, model="claude-2", expand=expand)
        except Exception as e:
            logger.error(e)
            logger.error(f"Failed to generate insights for {file_path}")

        # save expansions to file in output folder
        logger.info("Saving insights...")
        if expand:
            takeaway_string = expansion_to_string(takeaways)
        else:
            takeaway_string = dict_to_markdown(takeaways)

        with open(output_path, "w") as f:
            f.write(takeaway_string)
    else:
        logger.info(f"Loading {output_path}...")
        with open(output_path, "r") as f:
            takeaway_string = f.read()
    return takeaway_string
