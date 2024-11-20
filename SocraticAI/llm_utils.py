import json
import logging
import os
import re
import time
from collections import namedtuple

from anthropic import AI_PROMPT, HUMAN_PROMPT, Anthropic, InternalServerError
from openai import OpenAI

logger = logging.getLogger(__name__)

MAX_TOKENS = 2000


def chat(
    modelType="claude-3-sonnet-20240229", max_tokens_to_sample=MAX_TOKENS, **kwargs
):
    """
    This function allows the user to chat with an AI model using the command line interface.

    Args:
    - model (str): the name of the AI model to use for the chat. Default is "claude-instant-1".
    - max_tokens_to_sample (int): the maximum number of tokens to sample from the model's output. Default is MAX_TOKENS.

    Returns:
    - None

    """
    model = Model.get_instance()
    history = ""
    while True:
        human_input = input("Human [q to exit]: ")
        if human_input == "q":
            break
        prompt = f"{history} {HUMAN_PROMPT} {human_input}{AI_PROMPT}"
        response = model.chat_completion(
            prompt, modelType, max_tokens_to_sample, **kwargs
        )
        history = f"{prompt} {response}"
        logger.info(response)


def chain_completion(
    prompts, modelType="claude-instant-1", max_tokens_to_sample=MAX_TOKENS
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
    model = Model.get_instance()
    history = ""
    responses = []
    for next_prompt in prompts:
        prompt = f"{history} {HUMAN_PROMPT} {next_prompt}{AI_PROMPT}"
        response = model.chat_completion(prompt, modelType, max_tokens_to_sample)
        history = f"{prompt} {response}"
        responses.append(response)
    return responses


def repair_json(json_str, error):
    model = Model.get_instance()

    repair_json_prompt = f"""
{json_str}

The JSON object is invalid for the following reason:
{error}

The following is a revised JSON object:\n;
"""
    response = model.chat_completion(repair_json_prompt, "simple")
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
                logger.info(f"Trying to repair error {error}")
                return extract_and_read_json(repair_json(json_str, error), False)
            else:
                logger.error(e)
    else:
        raise ValueError("No JSON object found in the string")


class OpenAiClient:
    def __init__(self, api_key):
        self.low_level_client = OpenAI(api_key=api_key)

    def __call__(self, prompt, modelType="gpt-3.5-turbo", max_tokens_to_sample=MAX_TOKENS, **kwargs):
        start = time.time()
        formattedPrompt = self._format_prompt(prompt)
        # Remove @retry decorator - built-in retries will handle it
        completion = self.low_level_client.chat.completions.create(
            model=modelType, 
            messages=formattedPrompt, 
            **kwargs
        )
        logger.info(f"Time taken: {time.time() - start:.2f} seconds with model {modelType}")
        return completion.choices[0].message.content


    def _format_prompt(self, prompt):
        return [{"role": "user", "content": prompt}]


class AnthropicClient:
    def __init__(self, api_key):
        self.low_level_client = Anthropic(api_key=api_key)

    def __call__(self, prompt, modelType="claude-instant-1", max_tokens_to_sample=MAX_TOKENS, **kwargs):
        start = time.time()
        formattedPrompt = self._format_prompt(prompt)
        # Remove @retry decorator - built-in retries will handle it
        completion = self.low_level_client.completions.create(
            model=modelType,
            max_tokens_to_sample=max_tokens_to_sample,
            prompt=formattedPrompt,
            **kwargs
        )
        logger.info(f"Time taken: {time.time() - start:.2f} seconds with model {modelType}")
        return completion.completion

    def _format_prompt(self, prompt):
        return f"{HUMAN_PROMPT} {prompt}{AI_PROMPT}"


class Model:
    """
    A class representing a model.

    Attributes:
    -----------
    template : str
        The string template for the prompt, with variables to be filled in using the `format` method.
    """

    _instance: "Model" = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """
        Initializes a new Model object.

        By default, the model is backed by Anthropic's "claude-instant-1".
        """
        self.type = os.getenv("MODEL_TYPE") or "anthropic"
        if self.type == "openai":
            self.client = OpenAiClient(api_key=os.getenv("OPENAI_KEY"))
            self.name_dict = {
                "simple": "gpt-3.5-turbo",
                "complex": "gpt-4-turbo-preview",
            }
        else:
            self.client = AnthropicClient(api_key=os.getenv("ANTHROPIC_KEY"))
            self.name_dict = {"simple": "claude-instant-1", "complex": "claude-2"}

    def __str__(self):
        """Return information about the current model."""
        return f"Model(type={self.type})"

    def chat_completion(
        self, prompt, modelType="simple", max_tokens_to_sample=MAX_TOKENS, **kwargs
    ):
        print("Using model type:", self.name_dict[modelType])
        return self.client(
            prompt, self.name_dict[modelType], max_tokens_to_sample, **kwargs
        )
