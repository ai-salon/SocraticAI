from ChatDigest.utils import Prompt

COPY_EDIT = Prompt(
    "copy_edit",
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
```{text}```
""",
)


basic_insight_prompt = Prompt(
    "insight",
    """
I will give you a piece of conversation. I want you to extract the most
creative and unexpected insights from the conversation.

The conversation is between ```:
```{text}```

Give the insights to me as a bulleted list where each insight is 2-4 sentences.
Do not include any filler content, only the insights themselves.

```Output Format```
* [Insight 1]
* [Insight 2]
* [Insight 3]
...
""",
)

insight_aggregator_prompt = Prompt(
    "insight_aggregator",
    """
I will give you a list of insights derived from a conversation. I want you to
aggregate them into a single list of insights. Remove duplicates and group
together similar insights.

```insight list```
{insight_list}
""",
)
