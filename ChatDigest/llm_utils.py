import json
import os
import re
import time
from collections import namedtuple

from anthropic import AI_PROMPT, HUMAN_PROMPT, Anthropic, InternalServerError
from tenacity import *

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))

MAX_TOKENS = 10000


@retry(
    retry=retry_if_exception_type([InternalServerError]),
    stop=stop_after_attempt(5),
    wait=wait_random_exponential(min=1, max=60),
    reraise=True,
)
def anthropic_completion(
    prompt, model="claude-instant-1", max_tokens_to_sample=MAX_TOKENS, **kwargs
):
    """
    Generates a chatbot response given a prompt using the specified model.

    Args:
        prompt (str): The prompt to generate a response for.
        model (str, optional): The name of the model to use. Defaults to "claude-instant-1".
        max_tokens_to_sample (int, optional): The maximum number of tokens to sample. Defaults to MAX_TOKENS.

    Returns:
        str: The generated chatbot response.
    """
    start = time.time()
    completion = anthropic.completions.create(
        model=model, max_tokens_to_sample=max_tokens_to_sample, prompt=prompt, **kwargs
    )
    print(f"Time taken: {time.time() - start:.2f} seconds with model {model}")
    return completion.completion


def chat(model="claude-instant-1", max_tokens_to_sample=MAX_TOKENS, **kwargs):
    """
    This function allows the user to chat with an AI model using the command line interface.

    Args:
    - model (str): the name of the AI model to use for the chat. Default is "claude-instant-1".
    - max_tokens_to_sample (int): the maximum number of tokens to sample from the model's output. Default is MAX_TOKENS.

    Returns:
    - None

    """
    history = ""
    while True:
        human_input = input("Human [q to exit]: ")
        if human_input == "q":
            break
        prompt = f"{history} {HUMAN_PROMPT} {human_input}{AI_PROMPT}"
        response = anthropic_completion(prompt, model, max_tokens_to_sample, **kwargs)
        history = f"{prompt} {response}"
        print(response)


def chat_completion(
    prompt, model="claude-instant-1", max_tokens_to_sample=MAX_TOKENS, **kwargs
):
    prompt = f"{HUMAN_PROMPT} {prompt}{AI_PROMPT}"
    return anthropic_completion(prompt, model, max_tokens_to_sample, **kwargs)


def chain_completion(
    prompts, model="claude-instant-1", max_tokens_to_sample=MAX_TOKENS
):
    """
    This function takes a list of prompts and generates a response for each prompt using the anthropic_completion function.
    It concatenates the prompts and responses to create a history, which is used as the prompt for the next response.
    The function returns a list of responses.

    Args:
    - prompts: a list of strings representing the prompts to generate responses for
    - model: a string representing the name of the GPT-3 model to use for generating responses (default: "claude-instant-1")
    - max_tokens_to_sample: an integer representing the maximum number of tokens to sample when generating a response (default: 1500)

    Returns:
    - a list of strings representing the responses generated for each prompt
    """

    history = ""
    responses = []
    for next_prompt in prompts:
        prompt = f"{history} {HUMAN_PROMPT} {next_prompt}{AI_PROMPT}"
        response = anthropic_completion(prompt, model, max_tokens_to_sample)
        history = f"{prompt} {response}"
        responses.append(response)
    return responses


def repair_json(json_str, error):
    repair_json_prompt = f"""
{json_str}

The JSON object is invalid for the following reason:
{error}

The following is a revised JSON object:\n;
"""
    response = chat_completion(repair_json_prompt, model="claude-2")
    return response


def extract_and_read_json(s, try_repair=True):
    # Look for the JSON substring by finding the substring that starts and ends with curly braces
    json_str = re.search(r"\{.*\}", s, re.DOTALL)
    if json_str:
        json_str = json_str.group()
        try:
            # Parse the JSON substring into a JSON object
            json_obj = json.loads(json_str)
            return json_obj
        except json.JSONDecodeError as e:
            error = e
            if try_repair:
                print("Trying to repair...")
                return extract_and_read_json(repair_json(json_str, error), False)
            else:
                print(e)
    else:
        raise ValueError("No JSON object found in the string")
