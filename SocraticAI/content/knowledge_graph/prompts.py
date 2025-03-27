"""Prompts for knowledge graph generation."""

from socraticai.core.utils import Prompt
from datetime import datetime

entity_extraction_prompt = Prompt(
    "entity_extraction",
    '''
Extract key entities from the provided text, categorizing them into concepts, models, AI players, and questions.

## Input Text
```{text}```

## Existing Entities
```{existing_entities}```

## Task
Extract entities from the text while considering existing entities. For each entity:
1. Check if it's similar to an existing entity - if so, use that entity instead
2. Identify its category (insight, technology, AI player, question)
3. Extract a brief one paragraph description
4. Note key relationships to other entities

## Entity Categories
- **Insight**: A new insight or observation about the topic
- **Technology**: A new technology or tool that is relevant to the topic, e.g. AI models, hardware, evaluation tools, alignment techniques
- **AI Player**: A new AI company, organization, or government that is relevant to the topic
- **Question**: A new question or topic that is relevant to the topic

## Output Format
```yaml
entities:
  - name: entity_name
    category: insight|technology|ai_player|question
    description: Brief description
    relationships:
      - target: other_entity_name
        type: is_a|part_of|related_to|implements|asks|answers
        description: Description of relationship

reused_entities:
  - name: existing_entity_name
    new_relationships:
      - target: other_entity_name
        type: relationship_type
        description: Description of new relationship
    new_source_text: Additional relevant quote
```
'''
)

relationship_analysis_prompt = Prompt(
    "relationship_analysis",
    '''
Analyze relationships between entities and identify potential connections with existing entities.

## New Entity
```{entity}```

## Existing Entities
```{existing_entities}```

## Task
1. Review the new entity against existing entities
2. Identify potential relationships, hierarchies, and connections
3. Suggest merges if entities are too similar
4. Validate and enhance relationship descriptions

## Output Format
```yaml
entity_status: new|merge|update
merge_target: existing_entity_name  # If status is merge
relationships:
  - target: entity_name
    type: relationship_type
    description: Detailed description of relationship
hierarchy_position:
  parent_entities:
    - entity_name1
    - entity_name2
  child_entities:
    - entity_name3
    - entity_name4
```
'''
)

node_content_prompt = Prompt(
    "node_content",
    '''
Generate content for a knowledge graph node, incorporating information from multiple sources.

## Entity Information
```{entity}```

## Source References
```{sources}```

## Related Entities
```{related_entities}```

## Task
Create a comprehensive node document that:
1. Synthesizes information from all sources
2. Maintains consistent terminology
3. Explicitly references sources
4. Uses Obsidian-style links ([[entity_name]]) for all entity references

## Output Format
# {entity_name}

## Overview
[Synthesized description incorporating all sources, using [[entity_name]] format for references]

## Key Notes
- [Key point 1 with source reference and [[entity_name]] links]
- [Key point 2 with source reference and [[entity_name]] links]
...

## Relationships
- Is part of: [[parent_entity]]
- Contains: [[child_entity]]
- Related to: [[related_entity]] - [relationship description]
- Implements: [[implemented_entity]]
- Answers: [[question_entity]]
...

## Sources
- [Source reference 1]
- [Source reference 2]
...

## Metadata
- Category: {entity[category]}
- Created: {entity[created_at]}
- Last Updated: {datetime.now().isoformat()}
'''
) 