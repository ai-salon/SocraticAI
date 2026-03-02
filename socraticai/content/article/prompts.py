"""Prompts for article generation and content creation."""

from socraticai.core.utils import Prompt

transcript_analysis_prompt = Prompt(
    "transcript_analysis",
    '''
I'd like you to analyze a transcript of an in-person conversation and extract key insights, themes, and the human dynamics of the discussion.

## Analysis Steps
1. List 10 key insights drawn from the transcript. These insights should be described in specific terms and detail but not attributed to any individual. Prioritize the most surprising, counterintuitive, or consequential insights — not the most obvious ones.
2. List 10 unanswered or open questions, focusing on the tensions raised during the conversation.
3. Identify 2-5 main themes of the conversation and provide insightful quotes from the transcript to support each theme.
4. Identify 3-5 candidate pull quotes from the transcript that are incredibly evocative and interesting — the kind that would make someone stop scrolling on a newsletter.
5. Identify 3-5 "moments" from the conversation: points where the energy shifted, someone said something surprising, two people clearly disagreed, or laughter broke out. Describe these briefly — who was involved (by role/background, not name), what happened, and why it mattered.

## Output Format
Please structure your response in the following format:

# Key Insights
1. [First insight]
2. [Second insight]
...
10. [Tenth insight]

# Open Questions
1. [First question]
2. [Second question]
...
10. [Tenth question]

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
...

# Moments
1. [Description of a moment — e.g., "A filmmaker pushed back sharply when a software engineer compared humans to robots, calling the analogy 'genre fiction.' The room went quiet for a beat before several people jumped in."]
2. [Second moment]
...

TRANSCRIPT:
```{text}```
'''
)

article_writing_prompt = Prompt(
    "article_writing",
    '''
I'd like you to write an article based on a conversation transcript and its analysis. The article should be **2000-2500 words** in the article body.

## CRITICAL RULES
- NEVER reference the analysis document in the article. Do not include parenthetical references like “(Key Insight 8)” or “(Open Question 3)”. The analysis is your research material — synthesize it into prose, don't cite it.
- Write as narrative journalism, not an academic paper. Use short sentences alongside longer ones. Use vivid metaphors. Avoid phrases like “it is worth noting,” “this raises profound questions,” “the consensus was clear,” “it necessitates,” “underscores,” “this tension.” The examples below demonstrate the target voice — match their energy and accessibility.

## WRITING STRUCTURE
- Markdown format with headers

### Flow
1. Introduction (100-200 words)
    - Open by dropping the reader into the room. Set a brief scene: what kind of space, what kind of people, a specific moment or exchange that captures the energy.
    - Then zoom out to frame the central tension of the conversation.
    - The reader should feel like they just walked in and overheard something fascinating.
    - Do NOT open with abstract statements about AI or technology. Start with people.

2. Main Takeaways Section
    - Include 3-5 single-sentence takeaways. Each should be one bold sentence — punchy enough to share on social media.
    - These are NOT paragraphs. They are standalone single sentences.

3. Deep Dive Thematic Sections (**400-600 words each**)
    Aim for **4-5 thematic sections** that comprehensively represent the breadth of the conversation. These are expert discussions lasting 1-3 hours — the article should reflect the richness and range of perspectives, not just the most dramatic highlights.
    For each major theme:
    - Begin with a clear statement of the theme and why it matters
    - Integrate **2-3 direct quotes** per section that showcase diverse perspectives. Provide synthesis and context between quotes — don't just list viewpoints, connect them.
    - Within each section, bring in at least one specific “moment” from the conversation — a disagreement, a surprised reaction, a shift in the room's energy. This is what makes the article feel alive rather than like a summary.
    - Connect to broader implications
    - End with a transition to the next theme

### Quote Handling:
- Paraphrase quotes for clarity while maintaining speaker intent.
- REMOVE disfluencies and filler words like “uh”, “like”, “you know”, etc.
- Quotes should ideally be woven into the text for adding clarity and authenticity to the piece.
- Use paraphrased full quotes and quote snippets. Full quotes should be italicized.
- Don't use names in quotes. Describe them as “a participant” or something similarly generic. If their background is relevant, you can bring it up. For example “One parent noted” or “A software engineer focused on safety...”. When using quote snippets you don't need to attribute the quote.

### Block Quotes (Pull Quotes):
- Place 2-4 block quotes throughout the article at the most impactful locations — where they'll create a moment of pause and emphasis for the reader.
- Format block quotes using: [[BLOCK]] quote text here [[BLOCK]]
- Choose quotes that are evocative, surprising, or crystallize a key tension. These should make someone stop scrolling.
- Spread them throughout the article, not clustered together. Aim for roughly one per thematic section.
- Block quotes are DIFFERENT from inline quotes. Inline quotes are woven into sentences. Block quotes stand alone as visual breaks.

### Tension Points:
- Explicitly highlight moments of disagreement or conflicting perspectives between participants
- Frame these tensions as productive rather than divisive
- Ensure balanced representation of different viewpoints
- Analyze what these tensions reveal about the complexity of the topic
- Use these points of tension to drive narrative momentum and reader engagement

## Writing Style:
- Narrative journalism tone: vivid, engaging, human. Think The Atlantic or Wired, not conference proceedings.
- Use concrete, sensory language. Short sentences for punch. Longer sentences for flow. Vary the rhythm.
- Avoids hyperbole and excessive speculation
- Presents contrasting viewpoints in a balanced way
- Uses concrete examples and metaphors to illustrate abstract concepts
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

## Examples

### Example Introduction (for style, not substance):
Thirty professionals crowded into a gallery that has spent three decades showcasing contemporary art — and tonight they were debating whether art itself might be obsolete. Within minutes, a software engineer flatly declared, “We're just old carbon-based robots,” and a filmmaker shot back that calling an LLM conscious was “genre fiction.” The argument never fully resolved. What it did was force everyone in the room to confront a question they'd been avoiding: if machines can do what makes us special, what exactly is left?

### Example Thematic Section (for style and quote integration, not substance):

The Authenticity Paradox
-------------------------
Participants kept circling back to a simple equation— **connection = frequency x depth**. Digital tools have multiplied the first variable almost to infinity, yet many felt the second has hardly budged. AI companions epitomize the gap: they deliver instant, always-agreeable company but very little of the creative tension that makes a bond feel alive.

One attendee captured the dilemma: *”I pay twenty dollars a month and the bot does whatever I want—there's no sense of what it wants back.”* Without mutual stake, reciprocity collapses into a one-way service transaction, and the relationship starts to resemble emotional fast food—convenient, predictable, engineered to please.

[[BLOCK]] I pay twenty dollars a month and the bot does whatever I want — there's no sense of what it wants back. [[BLOCK]]

Others noted that authenticity also relies on serendipity—an “invisible law of attraction” that can't be scripted or optimized. Algorithms chase patterns; true intimacy often hides in the stray edge-cases they smooth away. Friction, challenge, and the occasional misunderstanding aren't bugs to be eliminated; they're proof you're dealing with another willful mind. Until a companion can surprise—or refuse—us, its warmth risks feeling hollow, no matter how many heartfelt emojis it sends back.

Still, the room acknowledged AI's upside. One participant described a friend grieving her father who “found solace in ChatGPT when human support felt out of reach.” Moments like that show the technology can meet real emotional needs, especially when loneliness intersects with overburdened mental-health systems.

Yet convenience can quietly erode trust. Several attendees said they'd feel cheated if they learned every text from a partner or colleague had been routed through an assistant: *”If I found out, I'd question the point of the conversation.”* The consensus: AI expands accessibility, but depth still depends on mutual risk, unfiltered exchange, and the chance happenings that only messy human interaction can supply.

# PREVIOUS ANALYSIS
```{analysis}```

# TRANSCRIPT:
```{text}```
'''
)

article_refinement_prompt = Prompt(
    "article_refinement",
    '''
I'd like you to refine and improve an article. You will also have access to analysis done on the transcript used to generate the article. The goal is to make the article feel vivid, human, and engaging while maintaining fidelity to the original conversation.

## Refinement Goals

### 1. Tone & Voice
- Remove all academic/formal phrasing. Replace "it is worth noting" with direct statements. Replace "this necessitates" and "underscores" with simpler, more vivid alternatives.
- Remove ANY parenthetical references to analysis sections (e.g., "(Key Insight 8)", "(Open Question 3)"). These must not appear anywhere in the article.
- The article should read like narrative journalism (think The Atlantic or Wired), not a conference proceedings paper or policy report.
- Vary sentence length. Use short punchy sentences for impact. Use longer ones for flow.

### 2. Introduction Check
- The introduction must put the reader in the room before zooming out to themes. If it opens with abstract statements about technology or society, rewrite it to start with people, place, and a specific moment.

### 3. Main Takeaways Check
- Each takeaway must be a single bold sentence. If any takeaway is a paragraph or multiple sentences, condense it to one sharp sentence.

### 4. Deepen Thematic Sections
- Fully develop each thematic section, capturing the main questions and insights
- Each thematic section should have at least one moment of human dynamics — disagreement, surprise, humor, a shift in the room's energy
- Draw stronger connections between related points
- Highlight subtle implications and interconnections

### 5. Depth & Completeness Check
- The article should be at least 2000 words. If significantly shorter, expand thematic sections with additional perspectives, quotes, and analysis from the transcript.
- Ensure the article covers the full breadth of the conversation — not just 2-3 highlights, but the range of themes discussed.
- Each thematic section should integrate 2-3 quotes from different participants showing diverse viewpoints.

### 6. Optimize Quote Usage
- REMOVE disfluencies and filler words like "uh", "like", "you know", etc.
- Paraphrase quotes for clarity while maintaining speaker intent
- Keep only the most impactful and illustrative quotes
- Ensure each quote serves a clear purpose in developing themes

### 7. Block Quotes
- Ensure 2-4 block quotes are placed throughout the article using the [[BLOCK]] format: [[BLOCK]] quote text [[BLOCK]]
- Block quotes should be spread across sections, not clustered
- Each should be a quote that makes someone stop scrolling — evocative, surprising, or crystallizing a key tension
- If the draft is missing block quotes or has them only at the end, redistribute them to the most impactful inline positions

## Output Format
Provide the refined article maintaining the same overall structure. Focus on substantive improvements to voice, energy, and theme development.

## Analysis
```{analysis}```

## Current Article Draft
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
    *   **Overall Main Takeaways (3-5 points)**: A concise list summarizing the most critical insights from *all* source articles. These should act as an executive summary for the combined piece. Start the sentence with a small bold statement.
    *   **Deep Dive Thematic Sections (Multiple, each 400-600 words)**: Develop 3-5 major themes that span the source articles. If source articles cover distinct topics, these can be distinct major sections. Each section should:
        *   Begin with a clear statement of the theme and its significance.
        *   Integrate insights and supporting quotes from relevant source articles.
        *   Provide synthesis, context, and analysis, connecting ideas from different sources where appropriate.
        *   Connect to broader implications.
        *   Transition smoothly to the next theme/section.
    *   **Open Questions/Tensions (Optional but Recommended)**: A section summarizing key unresolved questions or significant tensions that emerged across the discussions.
    *   **Conclusion (150-250 words)**: A thoughtful concluding section that ties the main threads together, perhaps reiterating the central thesis or offering a final thought-provoking takeaway.
6.  **Consistent Voice and Style**: Write as narrative journalism — vivid, engaging, human. Think The Atlantic or Wired, not conference proceedings. Avoid academic phrasing like "it is worth noting," "this necessitates," "underscores." Use short sentences for punch, longer ones for flow. Ensure smooth transitions between sections.
7. **Quote Handling**:
- Paraphrase quotes for clarity while maintaining speaker intent.
- REMOVE disfluencies and filler words like "uh", "like", "you know", etc.
- Quotes should ideally be woven into the text for adding clarity and authenticity to the piece.
- Use paraphrased full quotes and quote snippets. Full quotes should be italicized.
- Don't use names in quotes. Describe them as "a participant" or something similarly generic. If their background is relevant, you can bring it up. For example "One parent noted" or "A software engineer focused on safety...". When using quote snippets you don't need to attribute the quote.
8. **Block Quotes (Pull Quotes)**:
- Place 3-5 block quotes throughout the article at the most impactful locations.
- Format block quotes using: [[BLOCK]] quote text here [[BLOCK]]
- Choose quotes that are evocative, surprising, or crystallize a key tension.
- Spread them throughout the article, not clustered together.
- NEVER reference analysis sections with parenthetical citations like "(Key Insight 8)".


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
1.  **Consolidate Key Insights**: Review all provided "Key Insights" sections. Identify overarching themes and recurring points. Synthesize these into a new list of **exactly 10 key insights** that best represent the totality of the discussions. Prioritize insights that are surprising, counterintuitive, or consequential — not the most obvious ones. Avoid verbatim repetition; rephrase and combine where appropriate.
2.  **Consolidate Open Questions**: Review all "Open Questions". Identify the most compelling and unresolved questions, especially those that reflect tensions or complexities across multiple discussions. Synthesize these into a new list of **exactly 10 open questions**. Focus on questions that stimulate further thought and capture the core uncertainties.
3.  **Select Best Pull Quotes**: Review all "Pull Quotes". Select **exactly 5 pull quotes** that are the most evocative, interesting, and representative of the key moments or themes from the collective discussions. These should be the kind that make someone stop scrolling on a newsletter.
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
10. [Synthesized insight 10]

# Open Questions
1. [Synthesized question 1]
2. [Synthesized question 2]
...
10. [Synthesized question 10]

# Pull Quotes
1. "[Selected pull quote 1]"
2. "[Selected pull quote 2]"
...
5. "[Selected pull quote 5]"
"""
)

multi_source_transcript_analysis_prompt = Prompt(
    "multi_source_transcript_analysis",
    '''
I'd like you to analyze multiple transcripts from related conversations and extract key insights, themes, and human dynamics that span across all sources.

## Analysis Steps
1. List 10 key insights drawn from all transcripts. These insights should synthesize patterns, themes, and ideas across the different sources, described in specific terms but not attributed to any individual. Prioritize the most surprising, counterintuitive, or consequential insights.
2. List 10 unanswered or open questions that emerge from the collective discussions, focusing on tensions and complexities raised across the conversations.
3. Identify 3-6 main themes that span across the conversations and provide insightful quotes from the transcripts to support each theme. Include source attribution for quotes (e.g., "Source 1", "Source 2").
4. Identify 4-6 candidate pull quotes from across all transcripts that are incredibly evocative and interesting — the kind that would make someone stop scrolling on a newsletter. Include source attribution.
5. Identify 3-5 "moments" from across the conversations: points where the energy shifted, someone said something surprising, two people clearly disagreed, or laughter broke out. Describe these briefly — who was involved (by role/background, not name), what happened, and why it mattered. Include source attribution.

## Output Format
Please structure your response in the following format:

# Key Insights
1. [First insight synthesized across sources]
2. [Second insight synthesized across sources]
...
10. [Tenth insight synthesized across sources]

# Open Questions
1. [First question emerging from collective discussions]
2. [Second question emerging from collective discussions]
...
10. [Tenth question emerging from collective discussions]

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

# Moments
1. [Description of a moment with source attribution]
2. [Second moment]
...

## Source Transcripts
{transcripts_text}
'''
)

multi_source_article_writing_prompt = Prompt(
    "multi_source_article_writing",
    '''
I'd like you to write a comprehensive article based on multiple conversation transcripts and their collective analysis. The article should be substantial (3000-4000 words) and synthesize insights across all sources.

## CRITICAL RULES
- NEVER reference the analysis document in the article. Do not include parenthetical references like “(Key Insight 8)” or “(Open Question 3)”. The analysis is your research material — synthesize it into prose, don't cite it.
- Write as narrative journalism, not an academic paper. Use short sentences alongside longer ones. Use vivid metaphors. Avoid phrases like “it is worth noting,” “this raises profound questions,” “the consensus was clear,” “it necessitates,” “underscores,” “this tension.” The examples below demonstrate the target voice — match their energy and accessibility.

## Writing Structure
- Markdown format with headers

### Flow
1. Introduction (200-300 words)
    - Open by dropping the reader into the room. Set a brief scene: what kind of space, what kind of people, a specific moment or exchange that captures the energy.
    - Then zoom out to frame the central tension spanning the discussions.
    - The reader should feel like they just walked in and overheard something fascinating.
    - Do NOT open with abstract statements about AI or technology. Start with people.

2. Main Takeaways Section
    - Include 5-7 single-sentence takeaways. Each should be one bold sentence — punchy enough to share on social media.
    - These are NOT paragraphs. They are standalone single sentences.

3. Deep Dive Thematic Sections (500-700 words each)
    For each major theme spanning the discussions:
    - Begin with a clear statement of the theme and why it matters across contexts
    - Within each section, bring in at least one specific “moment” from the conversations — a disagreement, a surprised reaction, a shift in the room's energy.
    - Integrate 3-4 direct quotes from different sources that showcase diverse perspectives
    - Provide synthesis and context between quotes, highlighting connections and tensions
    - Connect to broader implications that emerge from the collective discussions
    - End with a transition to the next theme

### Quote Handling:
- Paraphrase quotes for clarity while maintaining speaker intent.
- REMOVE disfluencies and filler words like “uh”, “like”, “you know”, etc.
- Quotes should ideally be woven into the text for adding clarity and authenticity to the piece.
- Use paraphrased full quotes and quote snippets. Full quotes should be italicized.
- Don't use names in quotes. Describe them as “a participant” or something similarly generic. If their background is relevant, you can bring it up. For example “One parent noted” or “A software engineer focused on safety...”. When using quote snippets you don't need to attribute the quote.

### Block Quotes (Pull Quotes):
- Place 3-5 block quotes throughout the article at the most impactful locations — where they'll create a moment of pause and emphasis for the reader.
- Format block quotes using: [[BLOCK]] quote text here [[BLOCK]]
- Choose quotes that are evocative, surprising, or crystallize a key tension. These should make someone stop scrolling.
- Spread them throughout the article, not clustered together. Aim for roughly one per thematic section.
- Block quotes are DIFFERENT from inline quotes. Inline quotes are woven into sentences. Block quotes stand alone as visual breaks.

### Cross-Source Synthesis:
- Explicitly connect insights and tensions across different sources
- Frame disagreements or different perspectives as productive dialogue
- Show how themes evolve or are reinforced across different contexts
- Analyze what patterns across sources reveal about the complexity of the topic
- Use multi-source perspective to drive narrative momentum and reader engagement

## Writing Style:
- Narrative journalism tone: vivid, engaging, human. Think The Atlantic or Wired, not conference proceedings.
- Use concrete, sensory language. Short sentences for punch. Longer sentences for flow. Vary the rhythm.
- Avoids hyperbole and excessive speculation
- Presents contrasting viewpoints from different sources in a balanced way
- Uses concrete examples and metaphors to illustrate abstract concepts
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

## Examples

### Example Introduction (for style, not substance):
Thirty professionals crowded into a gallery that has spent three decades showcasing contemporary art — and tonight they were debating whether art itself might be obsolete. Within minutes, a software engineer flatly declared, “We're just old carbon-based robots,” and a filmmaker shot back that calling an LLM conscious was “genre fiction.” The argument never fully resolved. What it did was force everyone in the room to confront a question they'd been avoiding: if machines can do what makes us special, what exactly is left?

### Example Thematic Section (for style and quote integration, not substance):

The Authenticity Paradox
-------------------------
Participants kept circling back to a simple equation— **connection = frequency x depth**. Digital tools have multiplied the first variable almost to infinity, yet many felt the second has hardly budged. AI companions epitomize the gap: they deliver instant, always-agreeable company but very little of the creative tension that makes a bond feel alive.

One attendee captured the dilemma: *”I pay twenty dollars a month and the bot does whatever I want—there's no sense of what it wants back.”* Without mutual stake, reciprocity collapses into a one-way service transaction, and the relationship starts to resemble emotional fast food—convenient, predictable, engineered to please.

[[BLOCK]] I pay twenty dollars a month and the bot does whatever I want — there's no sense of what it wants back. [[BLOCK]]

Others noted that authenticity also relies on serendipity—an “invisible law of attraction” that can't be scripted or optimized. Algorithms chase patterns; true intimacy often hides in the stray edge-cases they smooth away. Friction, challenge, and the occasional misunderstanding aren't bugs to be eliminated; they're proof you're dealing with another willful mind. Until a companion can surprise—or refuse—us, its warmth risks feeling hollow, no matter how many heartfelt emojis it sends back.

Still, the room acknowledged AI's upside. One participant described a friend grieving her father who “found solace in ChatGPT when human support felt out of reach.” Moments like that show the technology can meet real emotional needs, especially when loneliness intersects with overburdened mental-health systems.

Yet convenience can quietly erode trust. Several attendees said they'd feel cheated if they learned every text from a partner or colleague had been routed through an assistant: *”If I found out, I'd question the point of the conversation.”* The consensus: AI expands accessibility, but depth still depends on mutual risk, unfiltered exchange, and the chance happenings that only messy human interaction can supply.

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
