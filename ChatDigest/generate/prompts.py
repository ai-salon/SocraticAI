from ChatDigest.utils import Prompt

copy_edit_prompt = Prompt(
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

basic_question_prompt = Prompt(
    "question",
    """
I will give you a piece of conversation. I want you to extract the most
interesting unresolved questions brought up. These questions should be
interesting and prompt further insight and reflection by the reader.

The conversation is between ```:
```{text}```

Give the unresolved questions to me as a bulleted list where each question is 1 sentence. Do not include any filler content, only the questions themselves.

```Output Format```
* [Question 1]
* [Question 2]
...
""",
)

basic_argument_prompt = Prompt(
    "disagreement",
    """
I will give you a piece of conversation. I want you to extract the most
interesting disagreement that came up.

The conversation is between ```:
```{text}```

Give the disagreements to me as a bulleted list where each disagreement is 2-4 sentences. Do not include any filler content, only the disagreements themselves.
Don't attribute the disagreement to specific speakers. Instead indicate the
main points of disagreement.

```Output Format```
* [Disagreement 1]
* [Disagreement 2]
...
""",
)

basic_prompts = {
    "insight": basic_insight_prompt,
    "question": basic_question_prompt,
    "disagreement": basic_argument_prompt,
}

aggregator_prompt = Prompt(
    "takeaway_aggregator",
    """
I will give you a list of takeaways derived from a conversation. I want you to
aggregate them into a single list of takeaways where each takeaways is 2-4 sentences. Remove duplicates and group
together similar takeaways.

These takeaways are each {takeaway_type} derived from the conversation.

```takeaway list```
{takeaway_list}

```Output Format```
* [takeaway 1]
* [takeaway 2]
* [takeaway 3]
...
""",
)

categorizer_prompt = Prompt(
    "takeaway_categorizer",
    """
I will give you a list of takeaways derived from a conversation. I want you to
categorize them into 2-4 named categories. If there are multiple types of 
takeaways, attempt to make each category have some number of each type of takeaway.

```takeaway list```
{takeaway_list}

```Output Format```
Return data in a valid json format. Make sure all original takeaways are
included in the output.
{{
    <"category 1">: [
        <takeaway 1>,
        <takeaway 2>,
        <takeaway 3>,
        ...
    ],
    <"category 2">: [
        <takeaway 4>,
        <takeaway 5>,
        ...
    ],
    ...
}}
""",
)

expand_prompt = Prompt(
    "takeaway_expand",
    """
I will give you a theme and a list of takeaways derived from a conversation. 

```theme```
{theme}

```output list```
{takeaway_list}

Please write a 500-600 word blog post incorporating these takeaways derived from the theme. Focus on generating an engaging lead that hooks readers, and smoothly connecting the different takeaways into a cohesive whole. Use subheadings to break up the sections with markdown format. Maintain a conversational but authoritative tone, providing enough background for readers new to AI and the theme. Share your own perspective where relevant. The goal is an insightful post that distills the essence of the conversation for a general audience interested in technology's meaning and impact.
""",
)

article_prompt = Prompt(
    "article",
    """
I will give you a series of small blogs derived from insights from the same
conversation. I will also give you some open questions and disagreements
that came up in that same conversation. Weave all of these together into
one cohesive multi-part article

```Blogs```
{blogs}

```Disagreements```
{disagreements}

```Open Questions```
{open_questions}

```Style Guide```
Depth and Nuance: Delve into the intricacies of your subject matter with rigor. Avoid surface-level analysis; instead, aim for a deeper dive that brings out the subtleties and complexities of the topic.

Cohesiveness and Narrative: Construct a clear narrative that links data, theory, and personal insights. Your writing should guide the reader through a logical progression of ideas, building towards a comprehensive understanding.

Balanced Examination: Address various perspectives and examine different facets of an issue. While maintaining your authorial voice, present a balanced view that considers counterarguments and alternative viewpoints.

Engagement and Authority: Write with confidence and authority, but also strive to engage your readers. Use a conversational tone where appropriate to make complex ideas more relatable.

Challenging Assumptions: Do not shy away from questioning established beliefs or popular opinions. Offer well-reasoned critiques and fresh perspectives that encourage readers to think critically.

Eloquence and Accessibility: Your language should be clear and articulate, avoiding unnecessary jargon. Strive to make your writing accessible to both experts and laypeople, ensuring that it is both informative and readable.

Forward-Thinking: Look beyond the current discourse and anticipate future developments and implications. Aim to provide insights that are not just relevant today but will also resonate with future trends and patterns.

```Task```
Please write a {length} word blog post incorporating the different elements I have provided. The goal is an insightful post that distills the essence of the conversation for a general audience interested in technology's meaning and impact.
""",
)


multi_convo_prompt = Prompt(
    "multi_convo",
    """
I will give you a list of insights derived from multiple conversations

```Conversations```
{text}

```Task```

Please write a 300-500 word summary of the insights derived from the different conversations. Be sure
to highlight the commonalities and differences across the conversations. Also pull out the
most interesting insights from all of the conversations. Provide your response in markdown format
""",
)
