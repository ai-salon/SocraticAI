from ChatDigest.interpret.process import process_file
from ChatDigest.llm_utils import *
from ChatDigest.prompts.interpret_prompts import (
    archetype_conversation_prompt,
    archetype_template,
    distill_template,
    flesh_out_prompt,
    summary_template,
    twitter_template,
)
from ChatDigest.utils import Prompt, chunk_text

# load up the conversation
file_path = "data/2023-05-25 - Salon: Relationships_transcript.txt"
# Read the file
with open(file_path, "r") as f:
    text = f.read()

text = process_file(file_path)


out = chain_completion(
    [archetype_template(text=text), archetype_conversation_prompt, flesh_out_prompt],
    model="claude-2",
)


archetype_conversation_prompt = """
 I'd like you to create a new conversation that condenses the original using the created
    archetypes into a point-by-point transcript between these archetypes. Use the same format as the original transcript. Each point should be given in the style of casual human conversation.
    
    It should flow naturally, be responsive to other points, and be consistent to the archetype
    saying it. The points in the conversation should reflect the original conversation.

    The goal is to distill the conversation reasonably, without losing any nuance in the overall flow of the conversation. The output is expected to be long,
    so as to not lose important information. Make the output mirror the conversation format.

    Include a "Facilitator" to help direct the conversation while remaining neutral. The facilitator should be a new archetype, and should introduce themselves at the beginning.
"""

flesh_out_prompt = """
Try it again, this time making each utterance 100-200 words. Allow the points to be fleshed out more
"""

continue_prompt = (
    "continue if the conversation isn't finished yet. Otherwise say <<DONE>>"
)
out2 = chain_completion(
    [
        archetype_template(text=text),
        archetype_conversation_prompt,
        flesh_out_prompt,
        continue_prompt,
        continue_prompt,
    ],
    model="claude-2",
)
final_text = out2[2]
for addition in out2[3:]:
    if addition != "<<DONE>>":
        final_text += addition

templates = [archetype_template, distill_template, summary_template, twitter_template]


template = templates[0]
prompt = template(text=text)
pyperclip.copy(prompt)


outputs = {}
for template in templates:
    prompt = template(text=text)
    outputs[template.name] = chat_completion(prompt, "claude-2")
