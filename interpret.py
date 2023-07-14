import os

from anthropic import AI_PROMPT, HUMAN_PROMPT, Anthropic
from interpret_prompts impor t*

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))
import time
from collections import namedtuple


def chat_completion(prompt, model="claude-instant-1", max_tokens_to_sample=1500):
    """
    Generate a chat completion using the Claude model.

    Args:
        prompt (str): The prompt to use for the completion.
        model (str): The model to use for the completion. Options, see here: https://docs.anthropic.com/claude/reference/selecting-a-model

    """
    start = time.time()
    completion = anthropic.completions.create(
        model=model,
        max_tokens_to_sample=max_tokens_to_sample,
        prompt=prompt,
    )
    print(f"Time taken: {time.time() - start:.2f} seconds with model {model}")
    return completion.completion


def chat(model="claude-2", max_tokens_to_sample=1500):
    history = ""
    while True:
        human_input = input("Human [q to exit]: ")
        if human_input == "q":
            break
        prompt = f"{history} {HUMAN_PROMPT} {human_input}{AI_PROMPT}"
        response = chat_completion(prompt, model, max_tokens_to_sample)
        history = f"{prompt} {response}"
        print(response)


def chain_completion(prompts, model="claude-instant-1", max_tokens_to_sample=1500):
    history = ""
    responses = []
    for next_prompt in prompts:
        prompt = f"{history} {HUMAN_PROMPT} {next_prompt}{AI_PROMPT}"
        response = chat_completion(prompt, model, max_tokens_to_sample)
        history = f"{prompt} {response}"
        responses.append(response)
    return responses


def chat_chain(prompts, model="claude-instant-1"):
    for prompt in prompts:
        response = chat_completion(prompt, model=model, return_conversation=True)


if __name__ == "__main__":

    file_path = # fill in 
    # Read the file
    with open(file_path, "r") as f:
        text = f.read()

    PII_prompts = [remove_PII_template(text=text), "continue", "continue", "continue"]
    PII_removed = chain_completion(PII_prompts, "claude-2", len(text))

    chat_completion(remove_PII_template(text=text), "claude-2", len(text))

    templates = [archetype_template, distill_template, twitter_template]
    outputs = {}
    for template in templates:
        prompt = template(text=text)
        outputs[template.name] = chat_completion(prompt, "claude-2")
