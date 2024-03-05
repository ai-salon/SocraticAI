import json
import logging
import os

from SocraticAI.generate.takeaways import run_takeaway_generation
from SocraticAI.utils import get_anonymized_path, get_output_path

logger = logging.getLogger(__name__)


def interpret_transcript(file_path):
    """
    Interprets a transcript file and generates takeaways.

    Args:
        file_path (str): The path to the transcript file.
        expand (bool, optional): Whether to expand the takeaways or not. Defaults to False.

    Returns:
        str: The generated takeaways as a string.
    """
    processed_file_path = get_anonymized_path(file_path)
    if not os.path.exists(processed_file_path):
        logger.info(
            f"No anonymous processed file found. First transcribe and process file before continuing. Exiting..."
        )
        return
    else:
        logger.info(f"Processed already. Loading {processed_file_path}...")
        with open(processed_file_path, "r") as f:
            text = f.read()

    takeaways_path = get_output_path(file_path, postfix="takeaways.json")
    if os.path.exists(takeaways_path):
        logger.info(f"Takeaways already exist at {takeaways_path}. Loading...")
        with open(takeaways_path, "r") as f:
            takeaways = json.load(f)
        save_takeaways(takeaways, file_path)
        return takeaways
    else:
        logger.info(f"No takeaways found at {takeaways_path}. Generating...")
        takeaways = run_takeaway_generation(text)
        save_takeaways(takeaways, file_path)
        return takeaways


def save_takeaways(takeaways, file_path):
    """
    Write takeaways to file.

    Combine insights, questions and disagreements into one markdownfile.
    Save the full article into another.
    Save the entire takeaways dictionary into a json file.
    """
    # write takeaways to file
    output_path = get_output_path(file_path, postfix="takeaways.md")
    if not os.path.exists(output_path):
        logger.info("Writing takeaways to file...")
        try:

            preamble = f"These are the takeaways from the conversation: {os.path.basename(file_path)}"
            with open(output_path, "w") as f:
                f.write(f"{preamble}\n\n")
                f.write("# Insights\n")
                f.writelines([f"- {item}\n\n" for item in takeaways["insights"]])
                f.write("\n\n# Questions\n")
                f.writelines([f"- {item}\n\n" for item in takeaways["questions"]])
                f.write("\n\n# Disagreements\n")
                f.writelines([f"- {item}\n\n" for item in takeaways["disagreements"]])
            logger.info(f"Saved takeaways to {output_path}")

        except Exception as e:
            logger.error(f"Error writing takeaways to file: {e}")
            raise
    else:
        logger.info(f"Takeaways already exist at {output_path}. Skipping...")

    # write article to file
    output_path = get_output_path(file_path, postfix="article.md")
    if not os.path.exists(output_path):
        logger.info("Writing article to file...")
        try:
            with open(output_path, "w") as f:
                f.write(takeaways["article"])
            logger.info(f"Saved article to {output_path}")
        except Exception as e:
            logger.error(f"Error writing article to file: {e}")
            raise
    else:
        logger.info(f"Article already exists at {output_path}. Skipping...")

    # writing takeaways to json
    output_path = get_output_path(file_path, postfix="takeaways.json")
    if not os.path.exists(output_path):
        logger.info("Writing takeaways to json...")
        try:
            with open(output_path, "w") as f:
                f.write(json.dumps(takeaways))
            logger.info(f"Saved takeaways to {output_path}")
        except Exception as e:
            logger.error(f"Error writing takeaways to json: {e}")
            raise
    else:
        logger.info(f"Takeaway JSON already exist at {output_path}. Skipping...")
