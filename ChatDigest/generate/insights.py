import logging
import re

from ChatDigest.generate.prompts import (
    basic_insight_prompt,
    insight_aggregator_prompt,
    insight_categorizer_prompt,
    insight_expand_prompt,
)
from ChatDigest.llm_utils import chat_completion, extract_and_read_json
from ChatDigest.utils import chunk_text

logger = logging.getLogger(__name__)


def generate_insights(text, model="claude-2"):
    logger.info(f"Generating insights from text using model: {model}")
    try:
        p = basic_insight_prompt(text=text)
        response = chat_completion(p, model=model)
        insights = re.findall(r"\* (.*?\.)\s*(?=\*|\Z)", response, re.S)
        logger.info(f"Generated {len(insights)} insights")
        return insights
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise


def generate_tree_insights(text, n=5, model="claude-2"):
    logger.info(
        f"Generating tree insights from text using model: {model}, iterations: {n}"
    )
    try:
        insights = [generate_insights(text, model=model) for _ in range(n)]
        insights = [item for sublist in insights for item in sublist]
        p = insight_aggregator_prompt(insight_list="\n\n".join(insights))
        response = chat_completion(p, model=model)
        final_insights = re.findall(r"\* (.*?\.)\s*(?=\*|\Z)", response, re.S)
        logger.info(f"Aggregated to {len(final_insights)} final insights")
        return insights, final_insights
    except Exception as e:
        logger.error(f"Error generating tree insights: {e}")
        raise


def generate_insights_from_chunks(
    text, chunk_size=10000, model="claude-2", tree_generator=False
):
    logger.info("Generating insights from text chunks")
    try:
        chunks = chunk_text(text, chunk_size)
        output = []
        for chunk in chunks:
            logger.info(f"Processing chunk of size: {len(chunk)}")
            if tree_generator:
                _, insights = generate_tree_insights(chunk, model=model)
            else:
                insights = generate_insights(chunk, model=model)
            output.append({"chunk": chunk, "insights": insights})
        logger.info("Completed generating insights from chunks")
        return output
    except Exception as e:
        logger.error(f"Error generating insights from chunks: {e}")
        raise


def classify_insights(insights, model="claude-2"):
    logger.info("Classifying insights")
    try:
        p = insight_categorizer_prompt(insight_list="\n\n".join(insights))
        classified_insights = chat_completion(p, model=model, temperature=0)
        try:
            extracted_json = extract_and_read_json(classified_insights)
            logger.info("Successfully classified and extracted insights")
            return extracted_json
        except:
            logger.warning("Could not extract JSON from classified insights")
            return classified_insights
    except Exception as e:
        logger.error(f"Error classifying insights: {e}")
        raise


def expand_insights(insights, model="claude-2"):
    logger.info("Expanding insights into blog posts")
    try:
        classified_insights = classify_insights(insights)
        expansions = {}
        for theme, insights in classified_insights.items():
            p = insight_expand_prompt(insight_list="\n\n".join(insights), theme=theme)
            response = chat_completion(p, model=model)
            expansions[theme] = {"blog": response, "insights": insights}
        logger.info("Expanded insights into blog posts")
        return expansions
    except Exception as e:
        logger.error(f"Error expanding insights: {e}")
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
        chunk_outputs = generate_insights_from_chunks(text, model=model)
        insights = [item["insights"] for item in chunk_outputs]
        # collapse list of lists
        insights = [item for sublist in insights for item in sublist]
        if expand:
            return expand_insights(insights, model=model)
        else:
            return classify_insights(insights, model=model)
    except Exception as e:
        logger.error(f"Error in running the full insight generation process: {e}")
        raise
