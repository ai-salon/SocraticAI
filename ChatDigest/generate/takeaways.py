import logging
import re

from ChatDigest.generate.prompts import (
    aggregator_prompt,
    article_prompt,
    basic_prompts,
    categorizer_prompt,
    expand_prompt,
)
from ChatDigest.llm_utils import chat_completion, extract_and_read_json
from ChatDigest.utils import chunk_text

logger = logging.getLogger(__name__)

DEFAULT_TAKEAWAY = "insights"


def generate_takeaways(text, takeaway_type=DEFAULT_TAKEAWAY, model="claude-2"):
    logger.info(
        f"Generating takeaways ({takeaway_type}) from text using model: {model}"
    )
    try:
        p = basic_prompts[takeaway_type](text=text)
        response = chat_completion(p, model=model)
        takeaways = re.findall(r"\* (.*?[.!?])\s*(?=\*|\Z)", response, re.S)
        logger.info(f"Generated {len(takeaways)} {takeaway_type}")
        return takeaways
    except Exception as e:
        logger.error(f"Error generating takeaways: {e}")
        raise


def generate_tree_takeaways(
    text, takeaway_type=DEFAULT_TAKEAWAY, n=5, model="claude-2"
):
    logger.info(
        f"Generating tree insights from text using model: {model}, iterations: {n}"
    )
    try:
        takeaways = [
            generate_takeaways(text, takeaway_type, model=model) for _ in range(n)
        ]
        takeaways = [item for sublist in takeaways for item in sublist]
        p = aggregator_prompt(output_list="\n\n".join(takeaways), output_type="insight")
        response = chat_completion(p, model=model)
        final_takeaways = re.findall(r"\* (.*?\.)\s*(?=\*|\Z)", response, re.S)
        logger.info(f"Aggregated to {len(final_takeaways)} final {takeaway_type}")
        return takeaways, final_takeaways
    except Exception as e:
        logger.error(f"Error generating tree takeaways: {e}")
        raise


def generate_takeaways_from_chunks(
    text,
    takeaway_type=DEFAULT_TAKEAWAY,
    chunk_size=10000,
    model="claude-2",
    tree_generator=False,
):
    logger.info("Generating takeaways from text chunks")
    try:
        chunks = chunk_text(text, chunk_size)
        output = []
        for chunk in chunks:
            logger.info(f"Processing chunk of size: {len(chunk)}")
            if tree_generator:
                _, takeaways = generate_tree_takeaways(
                    chunk, takeaway_type, model=model
                )
            else:
                takeaways = generate_takeaways(chunk, takeaway_type, model=model)
            output.append({"chunk": chunk, "takeaways": takeaways})
        logger.info("Completed generating takeaways from chunks")
        return output
    except Exception as e:
        logger.error(f"Error generating takeaways from chunks: {e}")
        raise


def generate_all_takeaways(text, model="claude-2"):
    takeaways = {
        t: generate_takeaways_from_chunks(text, t) for t in basic_prompts.keys()
    }
    return takeaways


def collapse_takeaways(takeaways):
    # takeaways must be a dictionary of different takeaway types
    if isinstance(takeaways, dict):
        takeaway_list = []
        for takeaway_type, chunks in takeaways.items():
            for chunk in chunks:
                tmp_takeaways = [f"{takeaway_type}: {i}" for i in chunk["takeaways"]]
                takeaway_list += tmp_takeaways
    else:
        takeaway_list = [item for sublist in takeaways for item in sublist["takeaways"]]
    return takeaway_list


def classify_takeaways(takeaways, model="claude-2"):
    logger.info("Classifying takeaways")
    try:
        p = categorizer_prompt(takeaway_list="\n\n".join(takeaways))
        classified_takeaways = chat_completion(p, model=model, temperature=0)
        try:
            extracted_json = extract_and_read_json(classified_takeaways)
            logger.info("Successfully classified and extracted takeaways")
            return extracted_json
        except:
            logger.error("Could not extract JSON from classified takeaways")
            return classified_takeaways
    except Exception as e:
        logger.error(f"Error classifying takeaways: {e}")
        raise


def expand_insights(classified_insights, model="claude-2"):
    logger.info("Expanding insights into blog posts")
    try:
        expansions = {}
        for theme, insights in classified_insights.items():
            p = expand_prompt(takeaway_list="\n\n".join(insights), theme=theme)
            response = chat_completion(p, model=model)
            expansions[theme] = {"blog": response, "insights": insights}
        logger.info("Expanded insights into blog posts")
        return expansions
    except Exception as e:
        logger.error(f"Error expanding insights: {e}")
        raise


def write_article(expansions, questions, disagreements, length=1000, model="claude-2"):
    logger.info("Writing an article...")
    try:
        expansion_string = "\n\n".join([e["blog"] for e in expansions.values()])
        questions = "\n\n".join(collapse_takeaways(questions))
        disagreements = "\n\n".join(collapse_takeaways(disagreements))
        p = article_prompt(
            blogs=expansion_string,
            open_questions=questions,
            disagreements=disagreements,
            length=length,
        )
        response = chat_completion(p, model=model)
        logger.info("wrote article")
        return response
    except Exception as e:
        logger.error(f"Error writing article: {e}")
        raise


def run_insight_generation(text, model="claude-2", expand=False):
    """
    Generates insights from the given text using the specified model.

    Args:
        text (str): The text to generate insights from.
        model (str, optional): The name of the model to use for generating insights. Defaults to "claude-2".
        expand (bool, optional): Whether to expand the insights into blog posts. Defaults to True.

    Returns:
        tuple: A tuple containing two lists. The first list contains the expanded insights as blog posts, and the second list contains the raw insights.
    """
    logger.info("Running the full insight generation process")
    try:
        chunk_outputs = generate_takeaways_from_chunks(text, model=model)
        takeaways = [item["takeaways"] for item in chunk_outputs]
        # collapse list of lists
        takeaways = [item for sublist in takeaways for item in sublist]
        if expand:
            return expand_takeaways(takeaways, model=model)
        else:
            return classify_takeaways(takeaways, model=model)
    except Exception as e:
        logger.error(f"Error in running the full insight generation process: {e}")
        raise
