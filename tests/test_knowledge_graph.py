"""Test script for knowledge graph generation."""

import os
from pathlib import Path
import logging
import yaml

from socraticai.content.knowledge_graph import KnowledgeGraphGenerator
from socraticai.core.utils import get_output_path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Run through the knowledge graph generation process."""
    
    # Initialize the generator
    generator = KnowledgeGraphGenerator()
    
    # Step 1: Process a single article
    article_path = Path("data/outputs/articles/example_article.md")
    if not article_path.exists():
        logger.error(f"Article not found: {article_path}")
        logger.info("Please run 'socraticai substack generate' first to create an article")
        return
        
    logger.info(f"Processing article: {article_path}")
    with open(article_path, 'r') as f:
        content = f.read()
        
    # Generate knowledge graph nodes
    updated_nodes = generator.process_article(content, article_path.stem)
    
    # Step 2: Review the generated entities
    logger.info("\nGenerated/updated nodes:")
    for node_path in updated_nodes:
        logger.info(f"  - {node_path}")
        # Print the content of each node
        with open(node_path, 'r') as f:
            logger.info("\nNode content:")
            logger.info(f.read())
            logger.info("-" * 80)
            
    # Step 3: Check entity relationships
    entities_file = Path(get_output_path()) / "knowledge_graph" / "entities.yaml"
    if entities_file.exists():
        with open(entities_file, 'r') as f:
            entities = yaml.safe_load(f)
            
        logger.info("\nEntity relationships:")
        for entity_id, entity in entities.items():
            logger.info(f"\nEntity: {entity['name']}")
            logger.info("Relationships:")
            for rel in entity.get('relationships', []):
                logger.info(f"  - {rel['type']} -> {rel['target']}: {rel['description']}")
                
    # Step 4: Test entity merging
    if len(entities) >= 2:
        # Get first two entities for testing
        entity_ids = list(entities.keys())[:2]
        logger.info(f"\nTesting entity merging: {entity_ids[0]} -> {entity_ids[1]}")
        
        updated_node = generator.merge_entities(entity_ids[0], entity_ids[1])
        if updated_node:
            logger.info(f"Successfully merged entities. Updated node: {updated_node}")
            with open(updated_node, 'r') as f:
                logger.info("\nMerged node content:")
                logger.info(f.read())
                
    logger.info("\nTest complete!")

if __name__ == "__main__":
    main() 