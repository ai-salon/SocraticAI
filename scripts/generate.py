from langchain.text_splitter import RecursiveCharacterTextSplitter

from ChatDigest.interpret.interpret import *
from ChatDigest.prompts.interpret_prompts import (
    archetype_conversation_prompt,
    archetype_template,
    distill_template,
    flesh_out_prompt,
    summary_template,
    twitter_template,
)
from ChatDigest.utils import Prompt

# load up the conversation
file_path = "data/2023-05-25 - Salon: Relationships_transcript.txt"
# Read the file
with open(file_path, "r") as f:
    text = f.read()


p = Prompt(
    "test",
    """
I want you to act as an editor to remove filler content from a conversation transcript. You will be given a long transcript of a multi-hour conversation between two or more people. Your goal is to remove only the fluff - do not summarize or shorten the meaningful content itself. Focus on identifying and eliminating:

Filler words like "um", "uh", "you know", "like", etc.
Repeated or redundant phrases and dialog
Verbal tics like "I mean", "basically", "actually", etc.
Tangents and side conversations that veer off topic
Excessively long monologues or stories that can be tightened up
Any dialog that does not move the core conversation forward
You should trim ONLY fluff - keep all content that contains substantive ideas, insights, questions, or dialog central to the topic. The edited version should retain the full conversation content and all speakers, just tightened up by removing fluff and filler. Do not change the original content itself beyond cleaning up the fluff. Please provide the edited transcript without any summarization.

The conversation is below between two ```:

The conversation is between ```:
```{conversation}```
""",
)


def chunk_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=5000,
        chunk_overlap=0,
    )
    docs = text_splitter.create_documents([text])
    chunks = [d.page_content for d in docs]
    return chunks


text_chunks = chunk_text(text)

processed_chunks = []
for chunk in text_chunks:
    processed = chat_completion(p(conversation=chunk), "claude-2", 10000)
    # remove text at beginning of string
    to_remove = (
        "Here is an edited version of the conversation with filler content removed:"
    )
    processed = processed.replace(to_remove, "")
    processed_chunks.append(processed)
processed_text = "\n".join(processed_chunks)
output_file = file_path.replace(".txt", "_processed.txt")
with open(output_file, "w") as f:
    f.write(processed_text)


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
