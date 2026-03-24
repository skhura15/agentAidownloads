#!/usr/bin/env python
"""
UTA Knowledge Base Ingestion Script

Loads all knowledge base documents into the vector store.

Usage:
    python -m examples.uta_ingest_knowledge
    
    # Or with custom options
    python -m examples.uta_ingest_knowledge --provider chroma --clear
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def setup_logging(level: str = "INFO"):
    """Configure logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main ingestion function."""
    parser = argparse.ArgumentParser(description="Ingest UTA knowledge base into vector store")
    parser.add_argument(
        "--provider",
        choices=["chroma", "cosmos", "azure_search"],
        default="chroma",
        help="Vector store provider (default: chroma)"
    )
    parser.add_argument(
        "--knowledge-dir",
        default="./data/uta_knowledge",
        help="Path to knowledge base directory"
    )
    parser.add_argument(
        "--persist-dir",
        default="./data/chroma",
        help="ChromaDB persistence directory"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing documents before ingestion"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("UTA Knowledge Base Ingestion")
    logger.info("=" * 60)
    
    # Import UTA modules
    try:
        from core import VectorStoreFactory
        from core.uta_document_loader import KnowledgeBaseIngester, ChunkConfig
    except ImportError as e:
        logger.error(f"Failed to import UTA modules: {e}")
        logger.error("Make sure you're running from the project root directory")
        sys.exit(1)
    
    # Check knowledge directory exists
    knowledge_dir = Path(args.knowledge_dir)
    if not knowledge_dir.exists():
        logger.error(f"Knowledge directory not found: {knowledge_dir}")
        sys.exit(1)
    
    logger.info(f"Provider: {args.provider}")
    logger.info(f"Knowledge directory: {knowledge_dir.absolute()}")
    
    # Create vector store from environment variables (includes Azure Foundry settings)
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check if using Azure Foundry for embeddings
        use_foundry = os.getenv("USE_FOUNDRY", "").lower() == "true"
        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "ollama")
        
        if args.provider == "chroma":
            if use_foundry or embedding_provider in ("azure_openai", "foundry"):
                # Use Azure AI Foundry embeddings
                config = {
                    "persist_directory": args.persist_dir,
                    "collection_name": "uta_knowledge_azure",
                    "embedding_provider": "azure_openai",
                    "embedding_model": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
                    "azure_openai_endpoint": os.getenv("FOUNDRY_PROJECT_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT"),
                    "azure_openai_key": os.getenv("FOUNDRY_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY"),
                    "use_foundry": use_foundry,
                }
                logger.info(f"Using Azure AI Foundry for embeddings: {config['embedding_model']}")
            else:
                # Use Ollama embeddings
                config = {
                    "persist_directory": args.persist_dir,
                    "collection_name": "uta_knowledge",
                    "embedding_provider": "ollama",
                    "embedding_model": os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
                    "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                }
                logger.info(f"Using Ollama for embeddings: {config['embedding_model']}")
            logger.info(f"Persistence directory: {args.persist_dir}")
        else:
            config = {}
        
        store = VectorStoreFactory.create(args.provider, config)
        logger.info(f"Vector store initialized: {type(store).__name__}")
        
    except Exception as e:
        logger.error(f"Failed to create vector store: {e}")
        sys.exit(1)
    
    # Clear if requested
    if args.clear:
        logger.warning("Clearing existing documents...")
        try:
            store.clear()
            logger.info("Documents cleared")
        except Exception as e:
            logger.error(f"Failed to clear documents: {e}")
    
    # Create ingester
    chunk_config = ChunkConfig(
        chunk_size=1000,
        chunk_overlap=200,
        min_chunk_size=100,
    )
    ingester = KnowledgeBaseIngester(store, chunk_config)
    
    # Run ingestion
    logger.info("Starting ingestion...")
    try:
        stats = ingester.ingest_directory(str(knowledge_dir))
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        sys.exit(1)
    
    # Print results
    logger.info("=" * 60)
    logger.info("Ingestion Complete!")
    logger.info("=" * 60)
    logger.info(f"Files processed: {stats['files']}")
    logger.info(f"Chunks created: {stats['chunks']}")
    logger.info(f"Errors: {stats['errors']}")
    logger.info(f"Total documents in store: {store.count()}")
    
    # Test search
    logger.info("\nTesting search...")
    test_queries = [
        "calls not routing to agents",
        "license error feature not available",
        "connection timeout",
    ]
    
    for query in test_queries:
        results = store.search(query, top_k=2)
        logger.info(f"\nQuery: '{query}'")
        for i, result in enumerate(results):
            logger.info(f"  {i+1}. [{result.score:.3f}] {result.document.doc_type.value}: {result.document.id}")
    
    logger.info("\n✅ Ingestion and test complete!")


if __name__ == "__main__":
    main()
