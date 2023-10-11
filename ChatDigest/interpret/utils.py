def create_block_quote(text):
    # Split the input text into lines
    lines = text.split("\n")

    # Add the ">" symbol and a space to the beginning of each line
    block_quote_lines = [f"> {line}" for line in lines]

    # Join the lines back together with newline characters
    block_quote = "\n".join(block_quote_lines)

    return block_quote


def expansion_to_string(expansions):
    # add blogs and insights to one long string\
    final_string = ""
    for theme, value in expansions.items():
        final_string += f"# {theme}\n\n"
        for insight in value["insights"]:
            final_string += f"* {insight}\n"
        final_string += "\n\n"
        final_string += "## Blog\n\n"
        final_string += create_block_quote(value["blog"])
        final_string += "\n\n"
        final_string += "<hr>"
        final_string += "\n\n\n\n"
    return final_string
