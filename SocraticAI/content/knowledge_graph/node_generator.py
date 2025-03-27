"""Module for generating knowledge graph nodes."""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from socraticai.core.llm import LLMChain
from socraticai.content.knowledge_graph.prompts import node_content_prompt
from socraticai.core.utils import get_output_path

logger = logging.getLogger(__name__)

class NodeGenerator:
    """
    Generates and manages Obsidian-compatible markdown nodes for the knowledge graph.
    
    This class is responsible for:
    1. Converting entities into readable, well-structured markdown documents
    2. Maintaining proper Obsidian formatting (e.g., [[entity]] links)
    3. Managing the filesystem storage of nodes
    4. Handling node updates and deletions
    
    Each node file contains:
    - Overview section with entity description
    - Key notes with source references
    - Relationships section with Obsidian links
    - Source references
    - Metadata about the entity
    
    The nodes are stored in a directory structure compatible with Obsidian,
    allowing for immediate use in an Obsidian vault.
    """

    def __init__(self, llm_chain: Optional[LLMChain] = None):
        self.llm_chain = llm_chain or LLMChain()
        self.output_dir = Path(get_output_path()) / "knowledge_graph" / "nodes"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized NodeGenerator with output directory: {self.output_dir}")
        
    def generate_node(self, 
                     entity: Dict[str, Any],
                     sources: Dict[str, Any],
                     related_entities: List[Dict[str, Any]]) -> Path:
        """
        Generate an Obsidian node file for an entity.
        
        Args:
            entity: The entity to generate a node for
            sources: Dictionary of source documents referenced by the entity
            related_entities: List of entities related to this one
            
        Returns:
            Path to the generated node file
        """
        logger.info(f"Generating node for entity: {entity['name']}")
        
        # Generate node content
        content_response = self.llm_chain.generate(
            prompt=node_content_prompt(
                entity=yaml.dump(entity, sort_keys=False),
                sources=yaml.dump(sources, sort_keys=False),
                related_entities=yaml.dump(related_entities, sort_keys=False)
            ),
            temperature=0.7
        )
        
        # Save node file
        node_path = self._get_node_path(entity["id"])
        with open(node_path, 'w') as f:
            f.write(content_response.content)
            
        logger.info(f"Generated node file: {node_path}")
        return node_path
        
    def _get_node_path(self, entity_id: str) -> Path:
        """Get the file path for an entity's node."""
        return self.output_dir / f"{entity_id}.md"
        
    def update_node(self,
                   entity: Dict[str, Any],
                   sources: Dict[str, Any],
                   related_entities: List[Dict[str, Any]]) -> Path:
        """
        Update an existing node file with new information.
        
        Args:
            entity: The updated entity information
            sources: Dictionary of source documents
            related_entities: List of related entities
            
        Returns:
            Path to the updated node file
        """
        logger.info(f"Updating node for entity: {entity['name']}")
        return self.generate_node(entity, sources, related_entities)
        
    def delete_node(self, entity_id: str):
        """Delete a node file."""
        node_path = self._get_node_path(entity_id)
        if node_path.exists():
            node_path.unlink()
            logger.info(f"Deleted node file: {node_path}")
        else:
            logger.warning(f"Node file not found: {node_path}")
            
    def get_node_content(self, entity_id: str) -> Optional[str]:
        """Get the content of a node file."""
        node_path = self._get_node_path(entity_id)
        if node_path.exists():
            with open(node_path, 'r') as f:
                return f.read()
        return None 