from ChatDigest.utils import Prompt

remove_PII_template = Prompt(
    "PII",
    """We want to de-identify some text by removing all personally identifiable information from this text so that it can be shared safely with external contractors.

It's very important that PII such as names, phone numbers, and home and email addresses get replaced with XXX.

Here is the text, inside <text></text> XML tags: 
<text>{text}<text>
""",
)

archetype_template = Prompt(
    "archetype",
    """I'm going to give you a conversation. Define characters that represent archetypes
in the conversation. Make up a name, create a short descriptor of the archetype and a longer
descriptor. There should be no more than six archetypes. The format should be as follows:

Archetype: <Archetype label>
Description: <One paragraph Archetype description>

Here is the conversation, inside <text></text> XML tags: 
<text>{text}<text>
""",
)

archetype_conversation_prompt = """
    I'd like you to create a new conversation that condenses the original using the created archetypes into a point-by-point transcript between these archetypes. Each point should be given in the style of casual, thoughtful human conversation.

    It should flow naturally, be responsive to other points, and be consistent to the archetype saying it. Aim to make each utterance ~200 words. Allow the points to be fleshed out. The points in the conversation should reflect the original conversation.

    Include a "Facilitator" to help direct the conversation while remaining neutral. The facilitator should be a new archetype, and should introduce themselves at the beginning.

    The goal is to distill the conversation reasonably, without losing any nuance in the overall flow of the conversation. The output is expected to be long, so as to not lose important information. Make the output mirror the conversation format.
"""

flesh_out_prompt = """
Try it again, this time making each utterance average 100-200 words. Allow the points to be fleshed out more. Some points may be longer than others, but try to keep the average length of each point to 100-200 words. The points in the conversation should reflect the original conversation.
"""

distill_template = Prompt(
    "distill",
    """I'm going to give you a conversation. I'd like you to distill it 
into a point-by-point transcript that mirrors the same form as the original transcript. 
The goal is to distill the conversation reasonably, without losing any nuance in the overall flow of the conversation. 
The output is expected to be long, so as to not lose important information. 

Importantly, this is not a summary. The final output should look and feel like the original conversation,
just more polished and slightly condensed.

Here is the text, inside <text></text> XML tags: 
<text>{text}<text>
""",
)

summary_template = Prompt(
    "distill",
    """I'm going to give you a conversation. I'd like you to summarize it.
The goal is to distill the conversation reasonably, highlighting important points of agreement
and tension, and extracting useful insights.
The output is expected to be long, so as to not lose important information. 


Here is the text, inside <text></text> XML tags: 
<text>{text}<text>
""",
)

twitter_template = Prompt(
    "twitter",
    """Create a twitter thread of six tweets that summarize the conversation in an informative and engaging fashion.  
The goal is to draw out of the discussion some interesting takeaways and incorporate them in the tweets.
Some approaches you can take: Use questions as hooks, highlight tensions in the conversation,
articulate ambiguities when unresolved, highlight important takeaways. Do not use hash tags.

Here is the text, inside <text></text> XML tags: 
<text>{text}<text>
""",
)
