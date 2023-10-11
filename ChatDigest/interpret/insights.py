import re

from ChatDigest.interpret.prompts import (
    basic_insight_prompt,
    insight_aggregator_prompt,
    insight_categorizer_prompt,
    insight_expand_prompt,
)
from ChatDigest.llm_utils import chat_completion, extract_and_read_json
from ChatDigest.utils import chunk_text


def generate_insights(text, model="claude-2"):
    """
    Generates insights from a given text using the specified model.

    Args:
        text (str): The text to generate insights from.
        model (str, optional): The name of the model to use for generating insights. Defaults to "claude-2".

    Returns:
        List[str]: A list of insights generated from the given text.
    """
    p = basic_insight_prompt(text=text)
    response = chat_completion(p, model=model)
    insights = re.findall(r"\* (.*?\.)\s*(?=\*|\Z)", response, re.S)
    return insights


def generate_tree_insights(text, n=5, model="claude-2"):
    """
    Generates insights for a given text using the specified language model.

    Args:
        text (str): The text to generate insights for.
        n (int, optional): The number of times to generate insights. Defaults to 5.
        model (str, optional): The name of the language model to use. Defaults to "claude-2".

    Returns:
        tuple: A tuple containing two lists. The first list contains all generated insights, and the second list
        contains the final insights after being processed by the chatbot.
    """
    insights = [generate_insights(text, model=model) for _ in range(n)]
    insights = [item for sublist in insights for item in sublist]
    p = insight_aggregator_prompt(insight_list="\n\n".join(insights))
    response = chat_completion(p, model=model)
    final_insights = re.findall(r"\* (.*?\.)\s*(?=\*|\Z)", response, re.S)
    return insights, final_insights


def generate_insights_from_chunks(
    text, chunk_size=10000, model="claude-2", tree_generator=False
):
    """
    Generate insights from text by chunking it into smaller pieces and running
    the insights generation algorithm on each chunk.

    Args:
        text (str): The text to generate insights from.
        chunk_size (int, optional): The size of each chunk. Defaults to 5000.
        model (str, optional): The name of the insights generation model to use.
            Defaults to "claude-2".
        tree_generator (bool, optional): Whether to use the tree-based insights
            generation algorithm. Defaults to False.

    Returns:
        list: A list of dictionaries, where each dictionary contains a chunk of
        the original text and the insights generated from that chunk.
    """
    chunks = chunk_text(text, chunk_size)
    output = []
    for chunk in chunks:
        if tree_generator:
            _, insights = generate_tree_insights(chunk, model=model)
        else:
            insights = generate_insights(chunk, model=model)
        output.append({"chunk": chunk, "insights": insights})
    return output


def classify_insights(insights, model="claude-2"):
    """
    Classifies a list of insights using the specified model.

    Args:
        insights (list): A list of insights to classify.
        model (str): The name of the model to use for classification. Defaults to "claude-2".

    Returns:
        str: The response from the chat_completion function.
    """
    p = insight_categorizer_prompt(insight_list="\n\n".join(insights))
    response = chat_completion(p, model=model, temperature=0)
    return response


def expand_insights(insights, model="claude-2"):
    """
    Given a list of insights, this function classifies them into themes and expands each theme into a blog post using a
    language model.

    Args:
        insights (list): A list of insights to be expanded into blog posts.
        model (str): The name of the language model to use for expanding the insights. Defaults to "claude-2".

    Returns:
        dict: A dictionary where the keys are the themes of the insights and the values are the expanded blog posts.
    """
    classified_insights = classify_insights(insights)
    try:
        extracted_json = extract_and_read_json(classified_insights)
    except:
        pass
    expansions = {}
    for theme, insights in extracted_json.items():
        p = insight_expand_prompt(insight_list="\n\n".join(insights), theme=theme)
        response = chat_completion(p, model=model)
        expansions[theme] = {"blog": response, "insights": insights}
    return expansions


def run_insight_generation(text, model="claude-2"):
    """
    Generates insights from the given text using the specified model.

    Args:
        text (str): The text to generate insights from.
        model (str, optional): The name of the model to use for generating insights. Defaults to "claude-2".

    Returns:
        tuple: A tuple containing two lists. The first list contains the expanded insights as blog posts, and the second list contains the raw insights.
    """
    chunk_outputs = generate_insights_from_chunks(text, model=model)
    insights = [item["insights"] for item in chunk_outputs]
    # collapse list of lists
    insights = [item for sublist in insights for item in sublist]
    # create blog posts
    expanded_insights = expand_insights(insights, model=model)
    return expanded_insights
