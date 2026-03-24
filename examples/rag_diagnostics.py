#!/usr/bin/env python
"""
RAG Diagnostic & Improvement Script

Use this script to:
1. Diagnose retrieval issues
2. Test query expansion
3. Compare embedding models
4. Re-ingest with improved chunking

Usage:
    python -m examples.rag_diagnostics --diagnose
    python -m examples.rag_diagnostics --test-queries
    python -m examples.rag_diagnostics --reingest
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")
except ImportError:
    pass  # dotenv not installed, use existing env vars


def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def diagnose_rag():
    """Run diagnostics on the current RAG setup."""
    from core import VectorStoreFactory
    
    print("\n" + "=" * 60)
    print("RAG DIAGNOSTICS")
    print("=" * 60)
    
    # Check vector store
    try:
        store = VectorStoreFactory.create("chroma", {
            "collection_name": "uta_knowledge",
            "persist_directory": "./data/chroma",
            "embedding_provider": "ollama",
            "embedding_model": "nomic-embed-text",
        })
        doc_count = store.count()
        print(f"\n✓ Vector Store: ChromaDB")
        print(f"✓ Documents indexed: {doc_count}")
        
        if doc_count == 0:
            print("\n⚠️  WARNING: No documents in vector store!")
            print("   Run: python -m examples.uta_ingest_knowledge --clear")
            return
    except Exception as e:
        print(f"\n✗ Vector store error: {e}")
        return
    
    # Check embedding model
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = [m["name"].split(":")[0] for m in response.json().get("models", [])]
        print(f"\n✓ Ollama running with models: {models}")
        
        if "nomic-embed-text" not in models:
            print("   ⚠️  nomic-embed-text not found. Consider running:")
            print("      ollama pull nomic-embed-text")
    except Exception as e:
        print(f"\n✗ Ollama not reachable: {e}")
    
    # Sample document stats
    try:
        all_ids = store.get_all_ids()
        doc_types = {}
        for doc_id in all_ids[:100]:  # Sample first 100
            parts = doc_id.split("_")
            if len(parts) > 0:
                dtype = parts[0] if parts[0] not in ["chunk"] else parts[0]
                doc_types[dtype] = doc_types.get(dtype, 0) + 1
        
        print(f"\n✓ Document types (sample):")
        for dtype, count in sorted(doc_types.items(), key=lambda x: -x[1]):
            print(f"   - {dtype}: {count}")
    except Exception as e:
        print(f"   Could not analyze document types: {e}")
    
    print()


def test_queries():
    """Test search with various queries."""
    from core import VectorStoreFactory
    from core.uta_query_enhancer import QueryEnhancer
    
    print("\n" + "=" * 60)
    print("QUERY TEST RESULTS")
    print("=" * 60)
    
    store = VectorStoreFactory.create("chroma", {
        "collection_name": "uta_knowledge",
        "persist_directory": "./data/chroma",
        "embedding_provider": "ollama",
        "embedding_model": "nomic-embed-text",
    })
    
    enhancer = QueryEnhancer(use_llm=False)
    
    test_queries = [
        "calls not routing to agents",
        "license error feature not available",
        "connection timeout websocket",
        "how to configure skill-based routing",
        "agent showing available but not receiving calls",
        "ERR-QUEUE-001",
    ]
    
    for query in test_queries:
        print(f"\n{'─' * 50}")
        print(f"Query: {query}")
        
        # Show query expansion
        enhanced = enhancer.enhance(query)
        print(f"Intent: {enhanced.intent}")
        print(f"Keywords: {enhanced.keywords}")
        print(f"Expanded queries: {len(enhanced.expanded_queries)}")
        
        # Test basic search
        results = store.search(query, top_k=3)
        print(f"\nBasic Search Results ({len(results)}):")
        for r in results:
            print(f"  [{r.score:.3f}] {r.document.id[:50]}...")
        
        # Test hybrid search
        results = store.hybrid_search(query, top_k=3, use_query_expansion=True)
        print(f"\nHybrid Search Results ({len(results)}):")
        for r in results:
            print(f"  [{r.score:.3f}] {r.document.id[:50]}...")
    
    print()


def reingest_documents(clear: bool = True):
    """Re-ingest documents with improved chunking."""
    from core import VectorStoreFactory
    from core.uta_document_loader import KnowledgeBaseIngester, ChunkConfig
    
    print("\n" + "=" * 60)
    print("RE-INGESTING WITH IMPROVED CHUNKING")
    print("=" * 60)
    
    knowledge_dir = Path("./data/uta_knowledge")
    if not knowledge_dir.exists():
        print(f"✗ Knowledge directory not found: {knowledge_dir}")
        return
    
    store = VectorStoreFactory.create("chroma", {
        "collection_name": "uta_knowledge",
        "persist_directory": "./data/chroma",
        "embedding_provider": "ollama",
        "embedding_model": "nomic-embed-text",
    })
    
    if clear:
        print("Clearing existing documents...")
        store.clear()
    
    # Use improved chunk config
    chunk_config = ChunkConfig(
        chunk_size=800,        # Smaller for better semantic coherence
        chunk_overlap=150,
        min_chunk_size=100,
        add_title_prefix=True,  # Adds section context to chunks
    )
    
    ingester = KnowledgeBaseIngester(store, chunk_config)
    
    print(f"Ingesting from: {knowledge_dir.absolute()}")
    stats = ingester.ingest_directory(str(knowledge_dir))
    
    print(f"\n✓ Ingestion Complete!")
    print(f"  Files: {stats['files']}")
    print(f"  Chunks: {stats['chunks']}")
    print(f"  Errors: {stats['errors']}")
    print(f"  Total docs: {store.count()}")


def show_embedding_recommendations():
    """Show embedding model recommendations."""
    print("\n" + "=" * 60)
    print("EMBEDDING MODEL RECOMMENDATIONS")
    print("=" * 60)
    
    print("""
┌──────────────────────────────┬────────────┬─────────────┬───────────────┐
│ Model                        │ Dimensions │ Quality     │ Setup         │
├──────────────────────────────┼────────────┼─────────────┼───────────────┤
│ nomic-embed-text (current)   │ 768        │ Good        │ Local/Ollama  │
│ mxbai-embed-large            │ 1024       │ Better      │ Local/Ollama  │
│ bge-large-en-v1.5            │ 1024       │ Excellent   │ SentenceTransf│
│ text-embedding-3-large       │ 3072       │ Best        │ Azure OpenAI  │
└──────────────────────────────┴────────────┴─────────────┴───────────────┘

To switch embedding models:

1. For Ollama (local, free):
   ollama pull mxbai-embed-large
   
   Then update config:
   embedding_model: "mxbai-embed-large"

2. For Azure OpenAI (best quality):
   Set environment variables:
   
   $env:EMBEDDING_PROVIDER = "azure_openai"
   $env:AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
   $env:AZURE_OPENAI_API_KEY = "your-api-key"
   $env:AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "text-embedding-3-large"
   
   Or use directly in code:
   
   store = VectorStoreFactory.create("chroma", {
       "embedding_provider": "azure_openai",
       "embedding_model": "text-embedding-3-large",
       "azure_openai_endpoint": "https://your-resource.openai.azure.com/",
       "azure_openai_key": "your-api-key",
   })

3. For Azure AI Foundry (recommended - uses DefaultAzureCredential):
   
   First, login to Azure:
   az login
   
   Set environment variables:
   $env:USE_FOUNDRY = "true"
   $env:FOUNDRY_PROJECT_ENDPOINT = "https://your-project.inference.ai.azure.com/"
   $env:AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "text-embedding-3-large"
   
   Or in code:
   
   store = VectorStoreFactory.create("chroma", {
       "embedding_provider": "foundry",  # or "azure_openai" with use_foundry=True
       "embedding_model": "text-embedding-3-large",
       "azure_openai_endpoint": "https://your-project.inference.ai.azure.com/",
       "use_foundry": True,  # Uses DefaultAzureCredential, no API key needed
   })

⚠️  IMPORTANT: After changing embedding model, you MUST re-ingest:
   python -m examples.rag_diagnostics --reingest-azure

""")


def test_azure_openai_embeddings():
    """Test Azure OpenAI/Foundry embeddings if configured."""
    import os
    
    print("\n" + "=" * 60)
    print("AZURE AI FOUNDRY / OPENAI EMBEDDING TEST")
    print("=" * 60)
    
    # Check for Foundry first, then Azure OpenAI
    use_foundry = os.getenv("USE_FOUNDRY", "").lower() == "true"
    foundry_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
    
    endpoint = foundry_endpoint or azure_endpoint
    
    if not endpoint:
        print("\n⚠️  Azure AI Foundry / OpenAI not configured.")
        print("   For Azure AI Foundry (recommended):")
        print("   - Set USE_FOUNDRY=true")
        print("   - Set FOUNDRY_PROJECT_ENDPOINT=https://your-project.inference.ai.azure.com/")
        print("   - Set AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large")
        print("   - Ensure you're logged in: az login")
        print("")
        print("   For Azure OpenAI:")
        print("   - Set AZURE_OPENAI_ENDPOINT")
        print("   - Set AZURE_OPENAI_API_KEY")
        print("   - Set AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        return False
    
    # Auto-detect Foundry from endpoint
    if foundry_endpoint or "inference.ai.azure.com" in (endpoint or ""):
        use_foundry = True
    
    provider = "Azure AI Foundry" if use_foundry else "Azure OpenAI"
    print(f"\n✓ Provider: {provider}")
    print(f"✓ Endpoint: {endpoint[:50]}...")
    print(f"✓ Deployment: {deployment}")
    if use_foundry:
        print("✓ Authentication: DefaultAzureCredential (no API key needed)")
    
    try:
        from core.uta_azure_openai_embeddings import AzureOpenAIEmbeddingFunction
        
        embedding_fn = AzureOpenAIEmbeddingFunction(
            endpoint=endpoint,
            api_key=api_key if not use_foundry else None,
            deployment_name=deployment,
            use_foundry=use_foundry,
        )
        
        # Test embedding generation
        test_texts = [
            "How do I configure skill-based routing?",
            "Connection timeout error when agents login",
        ]
        
        print("\nGenerating test embeddings...")
        embeddings = embedding_fn.embed_documents(test_texts)
        
        print(f"✓ Generated {len(embeddings)} embeddings")
        print(f"✓ Embedding dimension: {len(embeddings[0])}")
        
        # Test query embedding
        query_embedding = embedding_fn.embed_query("routing issue")
        print(f"✓ Query embedding dimension: {len(query_embedding)}")
        
        print(f"\n✅ {provider} embeddings working correctly!")
        return True
        
    except ImportError as e:
        print(f"\n✗ Missing dependency: {e}")
        print("   Run: pip install openai>=1.0.0 azure-identity")
        return False
    except Exception as e:
        print(f"\n✗ {provider} error: {e}")
        if use_foundry and "authentication" in str(e).lower():
            print("   Try: az login")
        return False


def reingest_with_azure_openai():
    """Re-ingest documents using Azure OpenAI/Foundry embeddings."""
    import os
    from core import VectorStoreFactory
    from core.uta_document_loader import KnowledgeBaseIngester, ChunkConfig
    
    print("\n" + "=" * 60)
    print("RE-INGESTING WITH AZURE AI FOUNDRY EMBEDDINGS")
    print("=" * 60)
    
    use_foundry = os.getenv("USE_FOUNDRY", "").lower() == "true"
    foundry_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    endpoint = foundry_endpoint or azure_endpoint
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
    
    if not endpoint:
        print("\n✗ Azure AI Foundry/OpenAI not configured. Set environment variables first.")
        return
    
    # Auto-detect Foundry
    if foundry_endpoint or "inference.ai.azure.com" in (endpoint or ""):
        use_foundry = True
    
    knowledge_dir = Path("./data/uta_knowledge")
    if not knowledge_dir.exists():
        print(f"✗ Knowledge directory not found: {knowledge_dir}")
        return
    
    provider = "Azure AI Foundry" if use_foundry else "Azure OpenAI"
    
    # Create store with Azure embeddings
    store = VectorStoreFactory.create("chroma", {
        "collection_name": "uta_knowledge_azure",  # New collection for Azure embeddings
        "persist_directory": "./data/chroma_azure",
        "embedding_provider": "azure_openai",
        "embedding_model": deployment,
        "azure_openai_endpoint": endpoint,
        "azure_openai_key": api_key if not use_foundry else None,
        "use_foundry": use_foundry,
    })
    
    print(f"✓ Using {provider} embeddings: {deployment}")
    print("  Clearing existing documents...")
    store.clear()
    
    # Use improved chunk config
    chunk_config = ChunkConfig(
        chunk_size=800,
        chunk_overlap=150,
        min_chunk_size=100,
        add_title_prefix=True,
    )
    
    ingester = KnowledgeBaseIngester(store, chunk_config)
    
    print(f"  Ingesting from: {knowledge_dir.absolute()}")
    stats = ingester.ingest_directory(str(knowledge_dir))
    
    print(f"\n✓ Ingestion Complete!")
    print(f"  Files: {stats['files']}")
    print(f"  Chunks: {stats['chunks']}")
    print(f"  Total docs: {store.count()}")
    print(f"\n  Data stored in: ./data/chroma_azure")


def main():
    parser = argparse.ArgumentParser(description="RAG Diagnostics & Improvements")
    parser.add_argument("--diagnose", action="store_true", help="Run diagnostics")
    parser.add_argument("--test-queries", action="store_true", help="Test search queries")
    parser.add_argument("--reingest", action="store_true", help="Re-ingest with improved chunking")
    parser.add_argument("--embeddings", action="store_true", help="Show embedding model recommendations")
    parser.add_argument("--test-azure", action="store_true", help="Test Azure OpenAI embeddings")
    parser.add_argument("--reingest-azure", action="store_true", help="Re-ingest using Azure OpenAI embeddings")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING"])
    
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    
    if not any([args.diagnose, args.test_queries, args.reingest, args.embeddings, args.test_azure, args.reingest_azure]):
        # Default: run all diagnostics
        args.diagnose = True
        args.test_queries = True
        args.embeddings = True
    
    if args.diagnose:
        diagnose_rag()
    
    if args.test_queries:
        test_queries()
    
    if args.embeddings:
        show_embedding_recommendations()
    
    if args.reingest:
        reingest_documents()
    
    if args.test_azure:
        test_azure_openai_embeddings()
    
    if args.reingest_azure:
        if test_azure_openai_embeddings():
            reingest_with_azure_openai()


if __name__ == "__main__":
    main()
