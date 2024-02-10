from SocraticAI.utils import Prompt

copy_edit_prompt = Prompt(
    "copy_edit",
    """
I want you to act as an editor to remove filler content from a partial conversation transcript. You will be given a component of a transcript of a multi-hour conversation between two or more people. Your goal is to remove only the fluff - do not summarize or shorten the meaningful content itself. Focus on identifying and eliminating:

- Filler words like "um", "uh", "you know", "like", etc.
- Repeated or redundant phrases and dialog
- Verbal tics like "I mean", "basically", "actually", etc.
- Tangents and side conversations that veer off topic
- Excessively long monologues or stories that can be tightened up
- Any dialog that does not move the core conversation forward

You should trim ONLY fluff - keep all content that contains substantive ideas, insights, questions, or dialog central to the topic. The edited version should retain the full conversation content and all speakers, just tightened up by removing fluff and filler. Do not change the original content itself beyond cleaning up the fluff. Please provide the edited transcript without any summarization.

Start your response by saying "Processed Transcript!".

The conversation is below between two ```:

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

quote_extraction_prompt = Prompt(
    "quote_extraction",
    """
I will give you a piece of conversation as well as some insights derived from the conversation.
I want you to extract supportive 1-3 quotes from the conversation for each insight.

The conversation subset is between ```:
```{text}```

```insight list```
{insight_list}


```Output Format```
Return the output as a json with the insights as keys and the supporting quotes as values.
{{
    [Insight 1]: [Quote 1], [Quote 2], ...
    [Insight 2]: [Quote 4], 
    [Insight 3]: [Quote 5], [Quote 6], ...,
}}
""",
)

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

```takeaway list```
{takeaway_list}

```Style Guide```
Depth and Nuance: Delve into the intricacies of your subject matter with rigor. Avoid surface-level analysis; instead, aim for a deeper dive that brings out the subtleties and complexities of the topic.

Cohesiveness and Narrative: Construct a clear narrative that links data, theory, and personal insights. Your writing should guide the reader through a logical progression of ideas, building towards a comprehensive understanding.

Balanced Examination: Address various perspectives and examine different facets of an issue. While maintaining your authorial voice, present a balanced view that considers counterarguments and alternative viewpoints.

Engagement and Authority: Write with confidence and authority, but also strive to engage your readers. Use a conversational tone where appropriate to make complex ideas more relatable.

Challenging Assumptions: Do not shy away from questioning established beliefs or popular opinions. Offer well-reasoned critiques and fresh perspectives that encourage readers to think critically.

Eloquence and Accessibility: Your language should be clear and articulate, avoiding unnecessary jargon. Strive to make your writing accessible to both experts and laypeople, ensuring that it is both informative and readable.

Forward-Thinking: Look beyond the current discourse and anticipate future developments and implications. Aim to provide insights that are not just relevant today but will also resonate with future trends and patterns.

```Task```
Please write a 500-600 word blog post incorporating these takeaways derived from the theme. The goal is an insightful post that distills the essence of the conversation for a general audience interested in technology's meaning and impact.
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

```Example Article```
In the realm of artificial intelligence, its integration into human relationships and social structures is a burgeoning field with profound implications. The possibility of AI moderation in difficult conversations is an intriguing one. It posits AI as a neutral third party, a concept that harks back to Rawls' theory of justice and the veil of ignorance. Achieving neutrality, however, is a labyrinthine task, laden with the complexity of human emotions and biases. The AI's credibility hinges on its ability to navigate this maze with fairness and sensitivity.

The therapeutic potential of AI is another fascinating avenue. AI conversational agents, for instance, could facilitate Internal Family Systems (IFS) therapy by roleplaying different aspects of an individual's psyche, such as the wounded inner child. This approach could provide a private, non-judgmental space for individuals to explore and reconcile internal conflicts. It resonates with Carl Jung's exploration of the psyche and the need for integrating various aspects of the self for holistic healing.

Privacy concerns, however, shadow the benefits of AI in handling sensitive personal information. The promise of anonymity might encourage more open sharing, yet the specter of data exploitation looms large. Here, local processing of data emerges as a potential safeguard, mitigating the risks associated with extensive data sharing. This concern reflects a broader societal apprehension about privacy in the digital age, reminiscent of Foucault's panopticism, where surveillance is a pervasive aspect of society.

AI's foray into intimate relationships raises complex questions about human-AI dynamics, including issues of intimacy, exclusivity, and jealousy. These relationships provide a playground for exploring unconventional relationship models, such as open relationships. This exploration sheds light on the evolving nature of relationships and human needs, echoing the works of Esther Perel on modern relationships and their complexities.

The concept of AI optimizing relationship compatibility by simulating potential lifetimes rapidly is intriguing but fraught with philosophical conundrums. It challenges the traditional notions of compatibility, suggesting a dynamic rather than a static understanding. This idea is reminiscent of Heraclitus' philosophy that change is the only constant in life. The evolving nature of human beings makes the prediction of long-term compatibility a Sisyphean task.

In dissecting the purpose and fitness function of relationships, one must consider the varying needs and commitments, from biological reproduction to emotional fulfillment. This approach underscores the importance of collaboration in relationships, aligning with John Stuart Mill's utilitarian perspective on the greatest happiness principle. It also raises questions about the spiritual belief in predestined connections, positing a dichotomy between organic relationship development and algorithm-driven compatibility.

The transactional view of dating, likened to a shopping list negotiation, is problematic. It reduces the complexity of human connections to a mere exchange of needs, overlooking the unpredictable chemistry that often defines relationships. This unpredictability is a testament to the limitations of AI in fully comprehending the human experience, a theme explored in Hannah Arendt's writings on the human condition.

The potential bifurcation of the dating pool, with some individuals preferring AI partners and others seeking human connections, especially for child-rearing, opens a Pandora's box of social and ethical questions. The idea of AI children, devoid of shared genetics but capable of propagating values, further complicates the traditional understanding of family and kinship, reminiscent of the family structures explored in Aldous Huxley's "Brave New World."

As AI continues to develop, its impact on social structures, including families and gender dynamics, warrants cautious consideration. This technological evolution reflects back societal issues, such as human loneliness and the need for socialization. It underscores the importance of understanding the cultural context in AI development, given the predominance of English and Western frameworks in technology.

The role of randomness in AI conversations to simulate naturalness, the value of adversity in human development, and the balancing act between leveraging sensitive data and ensuring privacy are all critical aspects in the evolution of AI. These issues echo broader societal and philosophical debates about individual freedom versus societal structures, the unintended consequences of technological advancements, and the tension between innovation and ethical responsibility.

In conclusion, the development of AI in the context of human relationships and social structures is a multi-faceted issue that requires thoughtful consideration from various perspectives. The works of social theorists such as John Rawls, Carl Jung, Michel Foucault, Esther Perel, Heraclitus, John Stuart Mill, Hannah Arendt, and Aldous Huxley provide valuable insights into these complex topics, offering a lens through which we can better understand and navigate this brave new world.

```Task```
Please write a {length} word blog post incorporating the different elements I have provided. The goal is an insightful post that distills the essence of the conversation for a general audience interested in technology's meaning and impact. Sections should flow smoothly into each other and the article should have a clear overall narrative arc. Use markdown format for headings and subheadings. Start your response by saying "Written Article!"
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
