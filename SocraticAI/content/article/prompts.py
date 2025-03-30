"""Prompts for article generation and content creation."""

from socraticai.core.utils import Prompt

transcript_analysis_prompt = Prompt(
    "transcript_analysis",
    '''
I'd like you to analyze a transcript of an in-person conversation and extract key insights and themes.

## Analysis Steps
1. List 20 key insights drawn from the transcript
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

## Previous Analysis
```{analysis}```

## Writing Structure
- Markdown format with headers

### Flow
1. Introduction (100-200 words)
    - Opens with a clear, focused hook that presents a specific question or tension
    - Establish the broad societal or technological relevance
    - Frame the central tension or question
    - Provide brief context for why this matters
    - End with a transition to the main content

2. Main Takeaways Section
    - Include 5-7 concise, bold statements that summarize the most important insights
    - These should function as executive summary points
    - Write each as a complete, standalone statement

3. Thematic Sections (300-500 words each)
    For each major theme:
    - Begin with a clear statement of the theme and why it matters
    - Integrate 2-3 direct quotes that showcase diverse perspectives
    - Provide synthesis and context between quotes
    - Connect to broader implications
    - End with a transition to the next theme

### Paragraph Structure:
- Opens each section with a clear thesis or main point
- Follows a pattern of: introduce idea → explore tension → provide example/quote → analyze implications
- Uses transitional phrases to connect ideas naturally

### Quote Integration:
- Paraphrase quotes for clarity while maintaining speaker intent
- Use quote attributions that describe the person when relevant like "[Name], a [descriptive aspect of the person]" as well as more generic "As one participant noted..." or "One participant observed...". Example: "Jen, a software engineer...". The names are anonymized so make sure you don't describe characteristics of the person that are identifying and leave company names and titled out if mentioned.
- Maintain consistent quote attribution format throughout

## Writing Style:
- Employs an analytical, measured tone while remaining accessible
- Avoids hyperbole and excessive speculation
- Presents contrasting viewpoints in a balanced way
- Uses concrete examples to illustrate abstract concepts
- Maintains intellectual rigor while remaining engaging
- Keeps to the transcript, reflecting the complexities and insights of the conversation

### Narrative Integration

Create a cohesive narrative flow between sections
Connect participant insights rather than presenting them as isolated comments
Use transitional phrases to guide readers between different perspectives
Highlight points of tension and agreement between participants

### Editorial Neutrality

Present diverse viewpoints without obvious bias
Avoid characterizing certain perspectives as clearly correct/incorrect
Focus on representing the conversation accurately rather than advocating positions

TRANSCRIPT:
```{text}```
'''
)

article_refinement_prompt = Prompt(
    "article_refinement",
    '''
I'd like you to refine and improve a article post based on its source transcript and analysis. The goal is to ensure the article deeply explores the themes while maintaining fidelity to the original conversation.

## Original Transcript
```{text}```

## Analysis
```{analysis}```

## Current article Draft
```{article}```

## Refinement Goals
1. Ensure strict fidelity to the content and insights from the transcript:
   - Verify all claims and interpretations are supported by the transcript
   - Remove any speculative or unsupported statements
   - Ensure the article accurately represents the conversation's context and nuances

2. Deepen the exploration of themes:
   - Fully develop each thematic section
   - Draw stronger connections between related points
   - Highlight subtle implications and interconnections
   - Ensure each theme receives appropriate depth and attention

3. Optimize quote usage:
   - Keep only the most impactful and illustrative quotes
   - Ensure each quote serves a clear purpose in developing themes
   - Provide sufficient context and analysis for each quote
   - Remove redundant or less impactful quotes

## Output Format
Please provide the refined article post maintaining the same overall structure:
- Main Takeaways section at the start
- Thematic sections in the middle

Focus on substantive improvements to the analysis and theme development while preserving the established structure.
'''
)
