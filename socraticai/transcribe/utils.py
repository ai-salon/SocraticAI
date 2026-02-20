import random
import re
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

# Lazy-loaded spaCy model cache
_nlp_model = None


def _get_nlp_model():
    """Lazy-load and cache the spaCy model."""
    global _nlp_model
    if _nlp_model is None:
        _nlp_model = spacy.load("en_core_web_lg")
    return _nlp_model


def get_name_list():
    name_list = NAME_LIST.copy()
    random.shuffle(name_list)
    return name_list


def anonymize_transcript(file_path, save_path=None):
    """
    Anonymize a transcript by replacing all names with a generic name.

    Args:
        file_path (str): The path to the input file.
        save_path (str, optional): Path to save the anonymized text.

    Returns:
        tuple: (processed_text, entities_count) - The processed text and number of entities found.
    """
    logger.info(f"Anonymizing {file_path}...")
    # Read the file
    with open(file_path, "r") as f:
        text = f.read()

    nlp = _get_nlp_model()
    doc = nlp(text)
    persons = list(dict.fromkeys(ent.text for ent in doc.ents if ent.label_ == "PERSON"))
    name_list = get_name_list()
    remapping = {person: name_list[i] for i, person in enumerate(persons)}
    entities_count = len(persons)

    for person, name in remapping.items():
        text = re.sub(r'\b' + re.escape(person) + r'\b', name, text)
    text = "Names have been changed to preserve anonymity.\n\n" + text
    logger.info(f"Finished anonymizing {file_path}")
    if save_path:
        with open(save_path, "w") as f:
            f.write(text)
    return text, entities_count
