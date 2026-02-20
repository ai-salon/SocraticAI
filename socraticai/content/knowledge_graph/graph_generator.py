"""Module for generating knowledge graphs from content."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from socraticai.core.llm import LLMChain
from socraticai.content.knowledge_graph.entity_manager import EntityManager
from socraticai.content.knowledge_graph.node_generator import NodeGenerator

logger = logging.getLogger(__name__)

class KnowledgeGraphGenerator:
    """
    Main coordinator for knowledge graph generation from content.
    
    This class orchestrates the entire process of:
    1. Processing articles to extract entities
    2. Managing the knowledge graph's growth
    3. Handling entity relationships and merging
    4. Generating and updating Obsidian nodes
    
    The knowledge graph is built incrementally, with each new article
    potentially adding new entities or enhancing existing ones. The system
    maintains consistency by:
    - Reusing existing entities when possible
    - Updating relationships as new connections are discovered
    - Maintaining bidirectional links between related entities
    - Preserving source references for all information
    
    The resulting graph can be viewed and navigated in Obsidian, with
    entities linked through Obsidian's [[entity]] syntax.
    """

    def __init__(self, llm_chain: Optional[LLMChain] = None):
        self.llm_chain = llm_chain or LLMChain()
        self.entity_manager = EntityManager(llm_chain)
        self.node_generator = NodeGenerator(llm_chain)
        logger.info("Initialized KnowledgeGraphGenerator")
        
    def process_article(self, content: str, source_id: str) -> List[Path]:
        """
        Process an article and generate/update knowledge graph nodes.
        
        Args:
            content: The article content
            source_id: Unique identifier for the article
            
        Returns:
            List of paths to generated/updated node files
        """
        logger.info(f"Processing article: {source_id}")
        
        # Extract entities from the article
        new_entities = self.entity_manager.extract_entities(content, source_id)
        logger.info(f"Extracted {len(new_entities)} new entities")
        
        # Generate or update nodes for affected entities
        updated_nodes = []
        for entity in new_entities:
            # Get related entities
            related = self.entity_manager.get_related_entities(entity["id"])
            
            # Generate node
            node_path = self.node_generator.generate_node(
                entity=entity,
                sources={source_id: content},
                related_entities=related
            )
            updated_nodes.append(node_path)
            
            # Update related nodes to reflect new relationships
            for related_entity in related:
                related_sources = self._get_entity_sources(related_entity)
                related_entities = self.entity_manager.get_related_entities(related_entity["id"])
                
                node_path = self.node_generator.update_node(
                    entity=related_entity,
                    sources=related_sources,
                    related_entities=related_entities
                )
                if node_path not in updated_nodes:
                    updated_nodes.append(node_path)
                    
        logger.info(f"Generated/updated {len(updated_nodes)} nodes")
        return updated_nodes
    
    def _get_entity_sources(self, entity: Dict[str, Any]) -> Dict[str, str]:
        """Get all source contents for an entity."""
        sources = {}
        for source_id in entity.get("sources", []):
            # Here you would implement logic to retrieve the source content
            # This could involve reading from a database or file system
            pass
        return sources
        
    def merge_entities(self, source_id: str, target_id: str) -> Optional[Path]:
        """
        Merge two entities and update their nodes.
        
        Args:
            source_id: ID of the entity to merge
            target_id: ID of the entity to merge into
            
        Returns:
            Path to the updated target node if successful
        """
        source = self.entity_manager.get_entity(source_id)
        target = self.entity_manager.get_entity(target_id)
        
        if not source or not target:
            logger.error(f"Entity not found: {source_id if not source else target_id}")
            return None
            
        # Merge entities
        self.entity_manager._merge_entity(source, target_id, source.get("sources", [])[0])
        
        # Delete source node
        self.node_generator.delete_node(source_id)
        
        # Update target node
        related = self.entity_manager.get_related_entities(target_id)
        sources = self._get_entity_sources(target)
        
        node_path = self.node_generator.update_node(
            entity=target,
            sources=sources,
            related_entities=related
        )
        
        logger.info(f"Merged entity {source_id} into {target_id}")
        return node_path
        
    def get_entity_node(self, entity_id: str) -> Optional[str]:
        """Get the content of an entity's node."""
        return self.node_generator.get_node_content(entity_id) 