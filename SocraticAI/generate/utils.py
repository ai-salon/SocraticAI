import re


def create_block_quote(text):
    # Split the input text into lines
    lines = text.split("\n")

    # Add the ">" symbol and a space to the beginning of each line
    block_quote_lines = [f"> {line}" for line in lines]

    # Join the lines back together with newline characters
    block_quote = "\n".join(block_quote_lines)

    return block_quote


def strip_preamble(text):
    # Claude sometimes starts by explaining what it's about to do. We don't want that
    result = re.sub(r".*?:\n\n", "", text, flags=re.DOTALL)
    return result
