"""Module for managing knowledge graph entities."""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from socraticai.core.llm import LLMChain
from socraticai.content.knowledge_graph.prompts import (
    entity_extraction_prompt,
    relationship_analysis_prompt
)
from socraticai.core.utils import get_output_path

logger = logging.getLogger(__name__)

class EntityManager:
    """
    Manages the extraction, storage, and relationships of knowledge graph entities.
    
    This class is responsible for:
    1. Extracting entities from text content using LLM-based analysis
    2. Maintaining a central store of all known entities
    3. Managing relationships between entities
    4. Preventing duplicate entities through similarity analysis
    5. Handling entity merging and updates
    
    The entity store is persisted as a YAML file, allowing for continuous
    growth of the knowledge graph across multiple sessions.
    
    Each entity contains:
    - Unique ID (normalized name)
    - Category (concept, model, AI player, question)
    - Description
    - Source references
    - Relationships to other entities
    - Hierarchical position
    """

    def __init__(self, llm_chain: Optional[LLMChain] = None):
        self.llm_chain = llm_chain or LLMChain()
        self.output_dir = Path(get_output_path()) / "knowledge_graph"
        self.entities_file = self.output_dir / "entities.yaml"
        self._load_entities()
        logger.info(f"Initialized EntityManager with output directory: {self.output_dir}")
        
    def _load_entities(self):
        """Load existing entities from storage."""
        self.entities = {}
        if self.entities_file.exists():
            with open(self.entities_file, 'r') as f:
                self.entities = yaml.safe_load(f) or {}
                logger.info(f"Loaded {len(self.entities)} existing entities")
        else:
            logger.info("No existing entities found, starting fresh")
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self._save_entities()
            
    def _save_entities(self):
        """Save entities to storage."""
        with open(self.entities_file, 'w') as f:
            yaml.dump(self.entities, f, sort_keys=False, indent=2)
        logger.info(f"Saved {len(self.entities)} entities to {self.entities_file}")
            
    def extract_entities(self, text: str, source_id: str) -> List[Dict[str, Any]]:
        """
        Extract entities from text while considering existing entities.
        
        Args:
            text: The text to extract entities from
            source_id: Identifier for the source document
            
        Returns:
            List of extracted and processed entities
        """
        logger.info(f"Extracting entities from text (source: {source_id})")
        
        # Extract initial entities
        extraction_response = self.llm_chain.generate(
            prompt=entity_extraction_prompt(
                text=text,
                existing_entities=yaml.dump(self.entities, sort_keys=False)
            ),
            temperature=0.7
        )
        
        try:
            extraction_result = yaml.safe_load(extraction_response.content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse entity extraction response: {e}")
            raise
            
        # Process new entities
        new_entities = []
        for entity in extraction_result["entities"]:
            # Analyze relationships with existing entities
            analysis_response = self.llm_chain.generate(
                prompt=relationship_analysis_prompt(
                    entity=yaml.dump(entity, sort_keys=False),
                    existing_entities=yaml.dump(self.entities, sort_keys=False)
                ),
                temperature=0.7
            )
            
            try:
                analysis_result = yaml.safe_load(analysis_response.content)
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse relationship analysis response: {e}")
                continue
                
            if analysis_result["entity_status"] == "new":
                # Add new entity
                entity_id = self._normalize_entity_name(entity["name"])
                self.entities[entity_id] = {
                    **entity,
                    "id": entity_id,
                    "created_at": datetime.now().isoformat(),
                    "sources": [source_id],
                    "relationships": analysis_result["relationships"],
                    "hierarchy": analysis_result["hierarchy_position"]
                }
                new_entities.append(self.entities[entity_id])
                logger.info(f"Added new entity: {entity_id}")
                
            elif analysis_result["entity_status"] == "merge":
                # Merge with existing entity
                target_id = analysis_result["merge_target"]
                if target_id in self.entities:
                    self._merge_entity(entity, target_id, source_id)
                    logger.info(f"Merged entity into existing: {target_id}")
                    
            elif analysis_result["entity_status"] == "update":
                # Update existing entity
                entity_id = self._normalize_entity_name(entity["name"])
                if entity_id in self.entities:
                    self._update_entity(entity_id, entity, analysis_result, source_id)
                    logger.info(f"Updated existing entity: {entity_id}")
                    
        # Process reused entities
        for reused in extraction_result.get("reused_entities", []):
            entity_id = self._normalize_entity_name(reused["name"])
            if entity_id in self.entities:
                self._update_entity_references(
                    entity_id,
                    reused["new_relationships"],
                    reused["new_source_text"],
                    source_id
                )
                logger.info(f"Updated references for entity: {entity_id}")
                
        # Save changes
        self._save_entities()
        return new_entities
    
    def _normalize_entity_name(self, name: str) -> str:
        """Convert entity name to a normalized ID."""
        return name.lower().replace(" ", "_")
    
    def _merge_entity(self, entity: Dict[str, Any], target_id: str, source_id: str):
        """Merge a new entity into an existing one."""
        target = self.entities[target_id]
        target["sources"].append(source_id)
        target["relationships"].extend(entity.get("relationships", []))
        if "source_text" in entity:
            target.setdefault("source_texts", []).append(entity["source_text"])
            
    def _update_entity(self, 
                      entity_id: str, 
                      new_data: Dict[str, Any],
                      analysis: Dict[str, Any],
                      source_id: str):
        """Update an existing entity with new information."""
        entity = self.entities[entity_id]
        entity["sources"].append(source_id)
        entity["relationships"].extend(analysis["relationships"])
        entity["hierarchy"] = analysis["hierarchy_position"]
        if "source_text" in new_data:
            entity.setdefault("source_texts", []).append(new_data["source_text"])
            
    def _update_entity_references(self,
                                entity_id: str,
                                new_relationships: List[Dict[str, Any]],
                                new_source_text: str,
                                source_id: str):
        """Update references and relationships for an existing entity."""
        entity = self.entities[entity_id]
        entity["sources"].append(source_id)
        entity["relationships"].extend(new_relationships)
        if new_source_text:
            entity.setdefault("source_texts", []).append(new_source_text)
            
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity by its ID."""
        return self.entities.get(entity_id)
    
    def get_related_entities(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all entities related to the given entity."""
        entity = self.get_entity(entity_id)
        if not entity:
            return []
            
        related_ids = set()
        for rel in entity.get("relationships", []):
            related_ids.add(self._normalize_entity_name(rel["target"]))
            
        return [
            self.entities[rid] for rid in related_ids 
            if rid in self.entities
        ] 