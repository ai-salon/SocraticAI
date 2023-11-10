import logging
import os

from ChatDigest.generate.process import process_file
from ChatDigest.generate.takeaways import run_insight_generation
from ChatDigest.generate.utils import (
    dict_to_markdown,
    expansion_to_string,
    get_data_directory,
)

logger = logging.getLogger(__name__)


def interpret_transcript(file_path, expand=False):
    processed_file_path = file_path.replace(".txt", "_processed.txt")
    if not os.path.exists(processed_file_path):
        logger.info(f"Processing {file_path}...")
        text = process_file(file_path)
    else:
        logger.info(f"Loading {processed_file_path}...")
        with open(processed_file_path, "r") as f:
            text = f.read()

    # create insights if they don't exist
    basename = os.path.basename(file_path)
    output_path = os.path.join(
        get_data_directory("outputs"), basename.replace("transcript.txt", "insights.md")
    )

    if not os.path.exists(output_path):
        # generate insights and "blogs"
        logger.info("Generating insights...")
        try:
            insights = run_insight_generation(text, model="claude-2", expand=expand)
        except Exception as e:
            logger.error(e)
            logger.error(f"Failed to generate insights for {file_path}")

        # save expansions to file in output folder
        logger.info("Saving insights...")
        if expand:
            insight_string = expansion_to_string(insights)
        else:
            insight_string = dict_to_markdown(insights)

        with open(output_path, "w") as f:
            f.write(insight_string)
    else:
        logger.info(f"Loading {output_path}...")
        with open(output_path, "r") as f:
            insight_string = f.read()
    return insight_string
