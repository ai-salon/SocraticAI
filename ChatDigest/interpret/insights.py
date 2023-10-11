import re

from ChatDigest.interpret.prompts import basic_insight_prompt, insight_aggregator_prompt
from ChatDigest.llm_utils import chat_completion
from ChatDigest.utils import chunk_text


def generate_insights(text, model="claude-2"):
    p = basic_insight_prompt(text=text)
    response = chat_completion(p, model=model)
    insights = re.findall(r"\* (.*?\.)\s*(?=\*|\Z)", response, re.S)
    return insights


def generate_tree_insights(text, n=5, model="claude-2"):
    insights = [generate_insights(text, model=model) for _ in range(n)]
    insights = [item for sublist in insights for item in sublist]
    p = insight_aggregator_prompt(insight_list="\n\n".join(insights))
    response = chat_completion(p, model=model)
    return insights, response


def generate_insights_from_chunks(text, n=5, model="claude-2", tree_generator=False):
    if tree_generator:
        fun = generate_tree_insights
    else:
        fun = generate_insights
    chunks = chunk_text(text, n=n)
    insights = []
    for chunk in chunks:
        insights += fun(chunk, model=model)
    return insights
