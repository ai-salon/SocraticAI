import random
import spacy
import logging

logger = logging.getLogger(__name__)

NAME_LIST = [
    "Kwame",
    "Aisha",
    "Jose",
    "Ahmed",
    "Leila",
    "Emma",
    "Yaw",
    "Olga",
    "Sanjay",
    "Michael",
    "Joshua",
    "Sarah",
    "Anastasia",
    "Kofi",
    "Zara",
    "Chen",
    "Ryan",
    "Hannah",
    "Natalia",
    "David",
    "Raj",
    "Jennifer",
    "Carlos",
    "Kwesi",
    "Rin",
    "Ekaterina",
    "Sofia",
    "Jason",
    "Priya",
    "Hiroshi",
    "Amara",
    "Matthew",
    "Anya",
    "Jamal",
    "Mei",
    "Gabriel",
    "Emily",
    "Dante",
    "Yuki",
    "Ethan",
    "Tariq",
    "Megan",
    "Kenji",
    "Amir",
    "Chloe",
    "Tyler",
    "Indira",
    "Brittany",
    "Chika",
    "Andrew"
]


def get_name_list():
    name_list = NAME_LIST.copy()
    random.shuffle(name_list)
    return name_list


def anonymize_transcript(file_path, save_path=None):
    """
    Anonymize a transcript by replacing all names with a generic name.

    Args:
        file_path (str): The path to the input file.
        save_file (bool, optional): Whether to save the processed text to a new file. Defaults to True.

    Returns:
        str: The processed text as a single string.
    """
    logger.info(f"Anonymizing {file_path}...")
    # Read the file
    with open(file_path, "r") as f:
        text = f.read()

    # assume names of people are in the first 1/6 of the text
    first_sixth = text[: len(text) // 6]
    nlp = spacy.load("en_core_web_lg")
    doc = nlp(first_sixth)
    persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    name_list = get_name_list()
    remapping = {person: name_list[i] for i, person in enumerate(persons)}
    for person, name in remapping.items():
        text = text.replace(person, name)
    text = "Names have been changed to preserve anonymity.\n\n" + text
    logger.info(f"Finished anonymizing {file_path}")
    if save_path:
        with open(save_path, "w") as f:
            f.write(text)
    return text
