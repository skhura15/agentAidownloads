#!/usr/bin/env python3
"""
UTA RAG Pipeline Test Script

Tests the complete RAG pipeline:
1. ChromaDB vector store with Ollama embeddings
2. Knowledge base ingestion
3. UTA Agent with llama3.1:8b-instruct-q8_0

Prerequisites:
    1. Ollama running: ollama serve
    2. Models pulled: 
       - ollama pull nomic-embed-text
       - ollama pull llama3.1:8b-instruct-q8_0
    3. Dependencies: pip install -r uta/requirements.txt

Usage:
    python -m examples.uta_test_rag_pipeline
    python -m examples.uta_test_rag_pipeline --skip-ingest  # Skip ingestion
    python -m examples.uta_test_rag_pipeline --query "my question"  # Custom query
"""

import argparse
import logging
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def setup_logging(level: str = "INFO"):
    """Configure logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def check_ollama_models():
    """Verify required Ollama models are available."""
    import requests
    
    print("\n" + "=" * 60)
    print("CHECKING OLLAMA MODELS")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        model_names = [m.get("name", "") for m in models]
        
        print(f"✓ Ollama is running")
        print(f"  Available models: {model_names}")
        
        # Check required models
        required = ["nomic-embed-text", "llama3.1:8b-instruct-q8_0"]
        missing = []
        
        for req in required:
            found = any(req in m for m in model_names)
            if found:
                print(f"  ✓ {req} - FOUND")
            else:
                print(f"  ✗ {req} - MISSING")
                missing.append(req)
        
        if missing:
            print(f"\n⚠ Missing models. Run:")
            for m in missing:
                print(f"  ollama pull {m}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ Ollama is not running!")
        print("  Start it with: ollama serve")
        return False


def ingest_knowledge_base(store, knowledge_path: str):
    """Ingest the sample knowledge base."""
    from core import KnowledgeBaseIngester
    
    print("\n" + "=" * 60)
    print("INGESTING KNOWLEDGE BASE")
    print("=" * 60)
    
    ingester = KnowledgeBaseIngester(store)
    stats = ingester.ingest_directory(knowledge_path)
    
    print(f"✓ Ingestion complete:")
    print(f"  Files processed: {stats.get('files', 0)}")
    print(f"  Chunks created: {stats.get('chunks', 0)}")
    print(f"  Documents in store: {store.count()}")
    
    return stats


def test_vector_search(store):
    """Test vector search functionality."""
    print("\n" + "=" * 60)
    print("TESTING VECTOR SEARCH")
    print("=" * 60)
    
    test_queries = [
        "calls not routing to agents",
        "license error activation",
        "connectivity timeout issues",
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = store.search(query, top_k=3)
        
        if results:
            for i, r in enumerate(results, 1):
                print(f"  {i}. [{r.score:.3f}] {r.document.doc_type.value}: {r.document.id[:50]}")
        else:
            print("  No results found")


def test_uta_agent(store, custom_query: str = None):
    """Test the UTA Agent."""
    from agents import UTAAgent
    from core import OllamaClient
    
    print("\n" + "=" * 60)
    print("TESTING UTA AGENT")
    print("=" * 60)
    
    # Initialize agent
    agent = UTAAgent(
        vector_store=store,
        llm_model="llama3.1:8b-instruct-q8_0",
    )
    print("✓ UTA Agent initialized")
    
    # Test ticket
    test_ticket = custom_query or """
    Customer: Contoso Corp (Tenant ID: contoso-001)
    Issue: Inbound calls are not reaching agents. The queue shows calls waiting 
    but agents with Available status are not receiving them. Error in logs: 
    ERR-QUEUE-001. This started after a capacity profile change yesterday.
    Impact: 50+ agents affected, calls dropping after timeout.
    """
    
    print(f"\n--- Test Ticket ---")
    print(test_ticket.strip())
    print("-" * 40)
    
    # Analyze ticket
    print("\n⏳ Analyzing ticket (this may take 30-60 seconds)...")
    result = agent.analyze_ticket(test_ticket)
    
    print(f"\n--- Analysis Result ---")
    print(f"Summary: {result.ticket_summary}")
    print(f"Category: {result.category.value}")
    print(f"Severity: {result.severity}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Escalation Needed: {result.escalation_needed}")
    
    print(f"\nRelevant Documents ({len(result.relevant_docs)}):")
    for doc in result.relevant_docs[:3]:
        print(f"  - {doc.document.id} ({doc.score:.2f})")
    
    print(f"\nSuggested Steps:")
    for i, step in enumerate(result.suggested_steps[:5], 1):
        print(f"  {i}. {step}")
    
    if result.known_issues:
        print(f"\nKnown Issues:")
        for ki in result.known_issues[:3]:
            print(f"  - {ki.get('issue', 'N/A')}")
    
    # Test quick answer
    print("\n--- Quick Answer Test ---")
    question = "What is the default queue timeout?"
    print(f"Question: {question}")
    print("⏳ Generating answer...")
    answer = agent.quick_answer(question)
    print(f"Answer: {answer[:500]}...")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Test UTA RAG Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Skip knowledge base ingestion (use existing data)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before ingestion",
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Custom query to test",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    
    args = parser.parse_args()
    setup_logging(args.log_level)
    
    print("=" * 60)
    print("UTA RAG PIPELINE TEST")
    print("=" * 60)
    
    # Check Ollama
    if not check_ollama_models():
        print("\n❌ Prerequisites not met. Exiting.")
        sys.exit(1)
    
    # Initialize vector store
    print("\n" + "=" * 60)
    print("INITIALIZING VECTOR STORE")
    print("=" * 60)
    
    from core import VectorStoreFactory
    
    store = VectorStoreFactory.create(
        provider="chroma",
        config={
            "collection_name": "uta_knowledge_test",
            "persist_directory": "./data/chroma_test",
            "embedding_provider": "ollama",
            "embedding_model": "nomic-embed-text",
        },
    )
    print(f"✓ ChromaDB initialized")
    print(f"  Documents in store: {store.count()}")
    
    # Clear if requested
    if args.clear:
        store.clear()
        print("  Cleared existing data")
    
    # Ingest knowledge base
    if not args.skip_ingest:
        knowledge_path = os.path.join(project_root, "uta", "knowledge")
        if os.path.exists(knowledge_path):
            ingest_knowledge_base(store, knowledge_path)
        else:
            print(f"⚠ Knowledge path not found: {knowledge_path}")
    
    # Test vector search
    if store.count() > 0:
        test_vector_search(store)
        
        # Test UTA Agent
        test_uta_agent(store, args.query)
    else:
        print("\n⚠ No documents in store. Run without --skip-ingest first.")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
