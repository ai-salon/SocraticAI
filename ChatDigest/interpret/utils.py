import textwrap


def expansion_to_string(expansions):
    # add blogs and insights to one long string\
    final_string = ""
    for theme, value in expansions.items():
        final_string += f"## {theme}\n\n"
        for insight in value["insights"]:
            final_string += f"* {insight}\n"
        final_string += "\n\n"
        final_string += "## Blog\n\n"
        final_string += textwrap.fill(value["blog"])
        final_string += "\n\n"
        final_string += "*" * 80
        final_string += "\n\n"
    return final_string
