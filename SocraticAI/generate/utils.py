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


def expansion_to_string(takeaways):
    # add blogs and insights to one long string\
    final_string = ""
    for theme, value in takeaways.items():
        final_string += f"# {theme}\n\n"
        for insight in value["insights"]:
            final_string += f"* {insight}\n"
        final_string += "\n\n"
        final_string += "## Blog\n\n"
        final_string += create_block_quote(strip_preamble(value["blog"]))
        final_string += "\n\n"
        final_string += "<hr>"
        final_string += "\n\n\n\n"
    return final_string


def dict_to_markdown(dict):
    markdown_string = ""
    for section, points in dict.items():
        markdown_string += f"## {section}\n"
        for point in points:
            markdown_string += f"- {point}\n"
        markdown_string += "\n"  # Add a newline for spacing between sections
    return markdown_string
