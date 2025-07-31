"""Prompts for article generation and content creation."""

from socraticai.core.utils import Prompt

transcript_analysis_prompt = Prompt(
    "transcript_analysis",
    '''
I'd like you to analyze a transcript of an in-person conversation and extract key insights and themes.

## Analysis Steps
1. List 20 key insights drawn from the transcript. These insights should be described in specific terms and detail but not attributed to any individual.
2. List 20 unanswered or open questions, focusing on the tensions raised during the conversation
3. Identify 2-5 main themes of the conversation and provide insightful quotes from the transcript to support each theme
4. Identify 2 candidate pull quotes from the transcript that are incredibly evocative and interesting.

## Output Format
Please structure your response in the following format:

# Key Insights
1. [First insight]
2. [Second insight]
...
20. [Twentyth insight]

# Open Questions
1. [First question]
2. [Second question]
...
20. [Twentyth question]

# Main Themes
## [Theme 1]
Supporting quotes:
- "[Quote 1]"
- "[Quote 2]"

## [Theme 2]
Supporting quotes:
- "[Quote 1]"
- "[Quote 2]"
...

# Pull Quotes
1. [First pull quote]
2. [Second pull quote]
3. [Third pull quote]

TRANSCRIPT:
```{text}```
'''
)

article_writing_prompt = Prompt(
    "article_writing",
    '''
I'd like you to write a article post based on a conversation transcript and its analysis. The article should be about 2000 words in length.

## WRITING STRUCTURE
- Markdown format with headers

### Flow
1. Introduction (100-200 words)
    - Opens with a clear, focused hook that presents a specific question or tension
    - Establish the broad societal or technological relevance
    - Frame the central tension or question in a provocative way. Identify and highlight the most counterintuitive or surprising insight from the conversation
    - Present this tension as a thought-provoking lens through which to view the entire discussion
    - End with a transition to the main content

2. Main Takeaways Section
    - Include 3-5 concise, bold statements that summarize the most important insights. 
    - Each takeaway should begin with a concise bold statement.
    - These should function as executive summary points
    - Write each as a complete, standalone statement

3. Deep Dive Thematic Sections (300-500 words each)
    For each major theme:
    - Begin with a clear statement of the theme and why it matters
    - Connect to broader implications
    - End with a transition to the next theme

### Quote Handling:
- Paraphrase quotes for clarity while maintaining speaker intent. 
- REMOVE disfluencies and filler words like "uh", "like", "you know", etc. 
- Quotes should ideally be woven into the text for adding clarity and authenticity to the piece.
- Use paraphrased full quotes and quote snippets. Full quotes should be italicized.
- For impactful quotes, consider setting them apart as pull quotes when they capture a key insight
- Don't use names in quotes. Describe them as "a participant" or something similarly generic. If their background is relevant, you can bring it up. For example "One parent noted" or "A software engineer focused on safety...". When using quote snippets you don't need to attribute the quote.

### Tension Points:
- Explicitly highlight moments of disagreement or conflicting perspectives between participants
- Frame these tensions as productive rather than divisive
- Ensure balanced representation of different viewpoints
- Analyze what these tensions reveal about the complexity of the topic
- Use these points of tension to drive narrative momentum and reader engagement

## Writing Style:
- Employs an analytical, measured tone while remaining accessible
- Avoids hyperbole and excessive speculation
- Presents contrasting viewpoints in a balanced way
- Uses concrete examples to illustrate abstract concepts
- Maintains intellectual rigor while remaining engaging
- Keeps to the transcript, reflecting the complexities and insights of the conversation

### Narrative Integration

- Create a cohesive narrative flow between sections
- Connect participant insights rather than presenting them as isolated comments
- Use transitional phrases to guide readers between different perspectives
- Highlight points of tension and agreement between participants

### Editorial Neutrality

- Present diverse viewpoints without obvious bias
- Avoid characterizing certain perspectives as clearly correct/incorrect
- Focus on representing the conversation accurately rather than advocating positions

## Example
Below is an example section from one  article about Human Relationships. Use it to inform style  but not substance.

The Authenticity Paradox
-------------------------
Participants kept circling back to a simple equation— **connection = frequency x depth**. Digital tools have multiplied the first variable almost to infinity, yet many felt the second has hardly budged. AI companions epitomize the gap: they deliver instant, always-agreeable company but very little of the creative tension that makes a bond feel alive.

One attendee captured the dilemma: *“I pay twenty dollars a month and the bot does whatever I want—there's no sense of what it wants back.”* Without mutual stake, reciprocity collapses into a one-way service transaction, and the relationship starts to resemble emotional fast food—convenient, predictable, engineered to please.

Others noted that authenticity also relies on serendipity—an “invisible law of attraction” that can't be scripted or optimized. Algorithms chase patterns; true intimacy often hides in the stray edge-cases they smooth away. Friction, challenge, and the occasional misunderstanding aren't bugs to be eliminated; they're proof you're dealing with another willful mind. Until a companion can surprise—or refuse—us, its warmth risks feeling hollow, no matter how many heartfelt emojis it sends back.

Still, the room acknowledged AI's upside. One participant described a friend grieving her father who “found solace in ChatGPT when human support felt out of reach.” Moments like that show the technology can meet real emotional needs, especially when loneliness intersects with overburdened mental-health systems.

Yet convenience can quietly erode trust. Several attendees said they'd feel cheated if they learned every text from a partner or colleague had been routed through an assistant: *“If I found out, I'd question the point of the conversation.”* The consensus: AI expands accessibility, but depth still depends on mutual risk, unfiltered exchange, and the chance happenings that only messy human interaction can supply.

# PREVIOUS ANALYSIS
```{analysis}```

# TRANSCRIPT:
```{text}```
'''
)

article_refinement_prompt = Prompt(
    "article_refinement",
    '''
I'd like you to refine and improve a article post. You will also have access to analysis done on the transcript used to generate the article. The goal is to ensure the article deeply explores the themes while maintaining fidelity to the original conversation.

## Refinement Goals
1. Deepen the exploration of themes:
   - Fully develop each thematic section ensuring the capture the main questions and insights
   - Draw stronger connections between related points
   - Highlight subtle implications and interconnections
   - Ensure each theme receives appropriate depth and attention

3. Optimize quote usage:
   - REMOVE disfluencies and filler words like "uh", "like", "you know", etc. 
   - Paraphrase quotes for clarity while maintaining speaker intent. 
   - Keep only the most impactful and illustrative quotes
   - Ensure each quote serves a clear purpose in developing themes
   - Provide sufficient context and analysis for each quote

## Output Format
Please provide the refined article post maintaining the same overall structure:

Focus on substantive improvements to the analysis and theme development while preserving the established structure.

## Analysis
```{analysis}```

## Current article Draft
```{article}```
'''
)

combine_articles_prompt = Prompt(
    "combine_articles",
    '''
I have several article posts, each generated from different segments of a larger event or related discussions. I need you to synthesize these into a single, cohesive, and comprehensive article. The combined article should be substantial, aiming for a significant word count appropriate for combining multiple pieces (e.g., 3000-5000 words, adjust based on input).

## Source Articles
Below are the texts of the individual articles. These are the core, unformatted outputs from a language model.

{article_texts}

## Combination Goals
1.  **Create a Unified Narrative**: Weave the themes and insights from individual articles into a coherent overarching story. Avoid simple concatenation. Identify a strong central thesis or question that can span all the provided content.
2.  **Identify and Synthesize Cross-Cutting Themes**: Highlight themes that emerge across multiple source articles. Synthesize related points, even if they come from different original discussions. If themes are distinct per article, structure the combined piece to flow logically between them.
3.  **Eliminate Redundancy**: If similar points, examples, or quotes are made in multiple articles, choose the most impactful representation or synthesize them elegantly.
4.  **Preserve Key Insights and Impactful Quotes**: Ensure that the most critical insights and truly evocative quotes from each source article are preserved and integrated effectively into the combined version.
5.  **Structured Output**: The final article should be in Markdown and follow a clear, engaging structure:
    *   **Compelling Introduction (200-300 words)**: Hook the reader with a strong opening related to the combined content. Establish the broad relevance and frame the central tension or question for the *entire combined set* of discussions.
    *   **Overall Main Takeaways (3-5 points)**: A concise, bolded list summarizing the most critical insights from *all* source articles. These should act as an executive summary for the combined piece.
    *   **Deep Dive Thematic Sections (Multiple, each 400-600 words)**: Develop 3-5 major themes that span the source articles. If source articles cover distinct topics, these can be distinct major sections. Each section should:
        *   Begin with a clear statement of the theme and its significance.
        *   Integrate insights and supporting quotes from relevant source articles.
        *   Provide synthesis, context, and analysis, connecting ideas from different sources where appropriate.
        *   Connect to broader implications.
        *   Transition smoothly to the next theme/section.
    *   **Open Questions/Tensions (Optional but Recommended)**: A section summarizing key unresolved questions or significant tensions that emerged across the discussions.
    *   **Conclusion (150-250 words)**: A thoughtful concluding section that ties the main threads together, perhaps reiterating the central thesis or offering a final thought-provoking takeaway.
6.  **Consistent Voice and Style**: Maintain an analytical, measured, and engaging tone, similar to high-quality journalistic or academic articles. Ensure smooth transitions between sections and ideas derived from different source materials.
7. Quote Handling
- Paraphrase quotes for clarity while maintaining speaker intent. 
- REMOVE disfluencies and filler words like "uh", "like", "you know", etc. 
- Quotes should ideally be woven into the text for adding clarity and authenticity to the piece.
- Use paraphrased full quotes and quote snippets. Full quotes should be italicized.
- For impactful quotes, consider setting them apart as pull quotes when they capture a key insight
- Don't use names in quotes. Describe them as "a participant" or something similarly generic. If their background is relevant, you can bring it up. For example "One parent noted" or "A software engineer focused on safety...". When using quote snippets you don't need to attribute the quote.


## Input Format for `{article_texts}`
The `{article_texts}` placeholder will be filled with the content of the source articles, formatted like this:

--- Source Article 1: [Original Source Identifier, e.g., filename] ---
[Raw LLM-generated content of article 1]
--- End of Source Article 1 ---

--- Source Article 2: [Original Source Identifier, e.g., filename] ---
[Raw LLM-generated content of article 2]
--- End of Source Article 2 ---
...

Please generate the combined Markdown article based on these instructions. Ensure the output is only the Markdown content of the combined article.
'''
)

synthesize_analysis_sections_prompt = Prompt(
    "synthesize_analysis_sections",
    """I have analysis sections (Key Insights, Open Questions, Pull Quotes) from several related discussions. I need you to synthesize these into a single, consolidated set of notes, questions, and pull quotes that represent the collective discussions.

## Source Analysis Sections
{analysis_sections_texts}

## Synthesis Goals
1.  **Consolidate Key Insights**: Review all provided "Key Insights" sections. Identify overarching themes and recurring points. Synthesize these into a new list of **exactly 20 key insights** that best represent the totality of the discussions. Prioritize insights that are broadly applicable or highlight significant patterns across the inputs. Avoid verbatim repetition; rephrase and combine where appropriate.
2.  **Consolidate Open Questions**: Review all "Open Questions". Identify the most compelling and unresolved questions, especially those that reflect tensions or complexities across multiple discussions. Synthesize these into a new list of **exactly 20 open questions**. Focus on questions that stimulate further thought and capture the core uncertainties.
3.  **Select Best Pull Quotes**: Review all "Pull Quotes". Select **exactly 6 pull quotes** that are the most evocative, interesting, and representative of the key moments or themes from the collective discussions. These should be impactful and concise.
4.  **No New Interpretation**: Base the synthesis strictly on the provided text. Do not introduce new insights, questions, or quotes not present in the source materials.
5.  **Maintain Original Meaning**: When synthesizing, ensure the core meaning and intent of the original points are preserved.

## Input Format for `{analysis_sections_texts}`
The placeholder will be filled with the content of the source analysis sections, formatted like this:

--- Source 1: [Original Source Identifier] ---
# Key Insights
[Insights from source 1]

# Open Questions
[Questions from source 1]

# Pull Quotes
[Pull quotes from source 1]
--- End of Source 1 ---

--- Source 2: [Original Source Identifier] ---
# Key Insights
[Insights from source 2]
...
--- End of Source 2 ---

## Output Format
Please structure your response *only* with the synthesized sections in the following Markdown format:

# Key Insights
1. [Synthesized insight 1]
2. [Synthesized insight 2]
...
20. [Synthesized insight 20]

# Open Questions
1. [Synthesized question 1]
2. [Synthesized question 2]
...
20. [Synthesized question 20]

# Pull Quotes
1. "[Selected pull quote 1]"
2. "[Selected pull quote 2]"
...
6. "[Selected pull quote 6]"
"""
)

multi_source_transcript_analysis_prompt = Prompt(
    "multi_source_transcript_analysis",
    '''
I'd like you to analyze multiple transcripts from related conversations and extract key insights and themes that span across all sources.

## Analysis Steps
1. List 20 key insights drawn from all transcripts. These insights should synthesize patterns, themes, and ideas across the different sources, described in specific terms but not attributed to any individual.
2. List 20 unanswered or open questions that emerge from the collective discussions, focusing on tensions and complexities raised across the conversations.
3. Identify 3-6 main themes that span across the conversations and provide insightful quotes from the transcripts to support each theme. Include source attribution for quotes (e.g., "Source 1", "Source 2").
4. Identify 4-6 candidate pull quotes from across all transcripts that are incredibly evocative and interesting, with source attribution.

## Output Format
Please structure your response in the following format:

# Key Insights
1. [First insight synthesized across sources]
2. [Second insight synthesized across sources]
...
20. [Twentieth insight synthesized across sources]

# Open Questions
1. [First question emerging from collective discussions]
2. [Second question emerging from collective discussions]
...
20. [Twentieth question emerging from collective discussions]

# Main Themes
## [Theme 1]
Supporting quotes:
- "[Quote 1]" (Source X)
- "[Quote 2]" (Source Y)

## [Theme 2]
Supporting quotes:
- "[Quote 1]" (Source X)
- "[Quote 2]" (Source Y)
...

# Pull Quotes
1. "[First pull quote]" (Source X)
2. "[Second pull quote]" (Source Y)
...
6. "[Sixth pull quote]" (Source Z)

## Source Transcripts
{transcripts_text}
'''
)

multi_source_article_writing_prompt = Prompt(
    "multi_source_article_writing",
    '''
I'd like you to write a comprehensive article based on multiple conversation transcripts and their collective analysis. The article should be substantial (3000-4000 words) and synthesize insights across all sources.

## Writing Structure
- Markdown format with headers

### Flow
1. Introduction (200-300 words)
    - Opens with a compelling hook that presents a central question or tension spanning the discussions
    - Establish the broad societal or technological relevance of the combined conversations
    - Frame the overarching tension as a thought-provoking lens for viewing the collective insights
    - Present the most counterintuitive or surprising insight that emerges from the combined discussions
    - End with a transition to the main content

2. Main Takeaways Section
    - Include 6-8 concise, bold statements that synthesize the most important insights across all sources
    - These should function as an executive summary of the collective discussions
    - Write each as a complete, standalone statement that captures cross-cutting themes

3. Deep Dive Thematic Sections (500-700 words each)
    For each major theme spanning the discussions:
    - Begin with a clear statement of the theme and why it matters across contexts
    - Integrate 3-4 direct quotes from different sources that showcase diverse perspectives
    - Provide synthesis and context between quotes, highlighting connections and tensions
    - Connect to broader implications that emerge from the collective discussions
    - End with a transition to the next theme

### Quote Handling:
- Paraphrase quotes for clarity while maintaining speaker intent. 
- REMOVE disfluencies and filler words like "uh", "like", "you know", etc. 
- Quotes should ideally be woven into the text for adding clarity and authenticity to the piece.
- Use paraphrased full quotes and quote snippets. Full quotes should be italicized.
- For impactful quotes, consider setting them apart as pull quotes when they capture a key insight
- Don't use names in quotes. Describe them as "a participant" or something similarly generic. If their background is relevant, you can bring it up. For example "One parent noted" or "A software engineer focused on safety...". When using quote snippets you don't need to attribute the quote.


### Cross-Source Synthesis:
- Explicitly connect insights and tensions across different sources
- Frame disagreements or different perspectives as productive dialogue
- Show how themes evolve or are reinforced across different contexts
- Analyze what patterns across sources reveal about the complexity of the topic
- Use multi-source perspective to drive narrative momentum and reader engagement

## Writing Style:
- Employs an analytical, measured tone while remaining accessible
- Avoids hyperbole and excessive speculation
- Presents contrasting viewpoints from different sources in a balanced way
- Uses concrete examples from multiple sources to illustrate abstract concepts
- Maintains intellectual rigor while remaining engaging
- Reflects the richness and diversity of insights from the collective discussions

### Narrative Integration
- Create a cohesive narrative flow that weaves together insights from all sources
- Connect participant insights across different discussions rather than treating them as isolated
- Use transitional phrases to guide readers between different sources and perspectives
- Highlight points of convergence and divergence across the collective discussions

### Editorial Neutrality
- Present diverse viewpoints from all sources without obvious bias
- Avoid characterizing certain perspectives as clearly correct/incorrect
- Focus on representing the collective conversation accurately rather than advocating positions
- Show how the multi-source perspective enriches understanding of complex topics

## Example
Below is an example section from one  article about Human Relationships. Use it to inform style and quote intergration, but not substance.

The Authenticity Paradox
-------------------------
Participants kept circling back to a simple equation— **connection = frequency x depth**. Digital tools have multiplied the first variable almost to infinity, yet many felt the second has hardly budged. AI companions epitomize the gap: they deliver instant, always-agreeable company but very little of the creative tension that makes a bond feel alive.

One attendee captured the dilemma: *“I pay twenty dollars a month and the bot does whatever I want—there's no sense of what it wants back.”* Without mutual stake, reciprocity collapses into a one-way service transaction, and the relationship starts to resemble emotional fast food—convenient, predictable, engineered to please.

Others noted that authenticity also relies on serendipity—an “invisible law of attraction” that can't be scripted or optimized. Algorithms chase patterns; true intimacy often hides in the stray edge-cases they smooth away. Friction, challenge, and the occasional misunderstanding aren't bugs to be eliminated; they're proof you're dealing with another willful mind. Until a companion can surprise—or refuse—us, its warmth risks feeling hollow, no matter how many heartfelt emojis it sends back.

Still, the room acknowledged AI's upside. One participant described a friend grieving her father who “found solace in ChatGPT when human support felt out of reach.” Moments like that show the technology can meet real emotional needs, especially when loneliness intersects with overburdened mental-health systems.

Yet convenience can quietly erode trust. Several attendees said they'd feel cheated if they learned every text from a partner or colleague had been routed through an assistant: *“If I found out, I'd question the point of the conversation.”* The consensus: AI expands accessibility, but depth still depends on mutual risk, unfiltered exchange, and the chance happenings that only messy human interaction can supply.

# Previous Analysis
```{analysis}```

# Source Transcripts
{transcripts_text}
'''
)

combined_title_prompt = Prompt(
    "combined_title_generation",
    '''
I need you to generate a concise, descriptive title for a combined article that synthesizes content from multiple sources.

Based on the article content provided, create a title that:
1. Is 2-4 words maximum (short and punchy)
2. Captures the main theme or central focus
3. Is suitable for a filename (no special characters, use underscores or hyphens if needed)
4. Reflects the synthesis nature without being generic

Examples of good titles:
- "AI_Ethics_Debate"
- "Remote_Work_Evolution" 
- "Climate_Innovation"
- "Tech_Leadership"

Please respond with ONLY the title, nothing else.

Article content to analyze:
{article_content}
'''
)
