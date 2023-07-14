from interpret_utils import PromptTemplate

remove_PII_template = PromptTemplate(
    "PII",
    """We want to de-identify some text by removing all personally identifiable information from this text so that it can be shared safely with external contractors.

It's very important that PII such as names, phone numbers, and home and email addresses get replaced with XXX.

Here is the text, inside <text></text> XML tags: 
<text>{text}<text>
""",
)

archetype_template = PromptTemplate(
    "archetype",
    """I'm going to give you a conversation. First define new characters that represent archetypes
in the conversation. Then I'd like you to create a new conversation that condenses this one
into a point-by-point transcript between these archetypes. Use the same format as the original transcript.

The goal is to distill the conversation reasonably, 
without losing any nuance in the overall flow of the conversation. The output is expected to be long,
so as to not lose important information. Make the output mirror the conversation format.

Here is the text, inside <text></text> XML tags: 
<text>{text}<text>
""",
)

distill_template = PromptTemplate(
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


twitter_template = PromptTemplate(
    "twitter",
    """Create a twitter thread of six tweets that summarize the conversation in an informative and engaging fashion.  
The goal is to draw out of the discussion some interesting takeaways and incorporate them in the tweets.
Some approaches you can take: Use questions as hooks, highlight tensions in the conversation,
articulate ambiguities when unresolved, highlight important takeaways. Do not use hash tags.

Here is the text, inside <text></text> XML tags: 
<text>{text}<text>
""",
)
