from ChatDigest.interpret.prompts import COPY_EDIT
from ChatDigest.llm_utils import chat_completion
from ChatDigest.utils import chunk_text


def process_file(file_path, save_file=True, process_prompt=COPY_EDIT):
    """
    Process a text file by chunking its contents, running each chunk through a chat completion model,
    and concatenating the processed chunks into a single string. Optionally saves the processed text
    to a new file.

    Args:
        file_path (str): The path to the input file.
        save_file (bool, optional): Whether to save the processed text to a new file. Defaults to True.
        process_prompt (function, optional): A function that takes a conversation string as input and returns a
            modified version of the conversation string to be used as input to the chat completion model.
            Defaults to COPY_EDIT. Must be a PROMPT that takes a single
            argument: text

    Returns:
        str: The processed text as a single string.
    """
    # Read the file
    with open(file_path, "r") as f:
        text = f.read()
    text_chunks = chunk_text(text)
    processed_chunks = []
    for i, chunk in enumerate(text_chunks):
        print(f"Processing chunk {i+1}/{len(text_chunks)}")
        processed = chat_completion(process_prompt(text=chunk), "claude-2", 10000)
        # remove text at beginning of string
        to_remove = (
            "Here is an edited version of the conversation with filler content removed:"
        )
        processed = processed.replace(to_remove, "")
        processed_chunks.append(processed)
    processed_text = "\n".join(processed_chunks)
    if save_file:
        output_file = file_path.replace(".txt", "_processed.txt")
        with open(output_file, "w") as f:
            f.write(processed_text)
    return processed_text
