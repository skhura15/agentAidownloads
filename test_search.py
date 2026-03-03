"""Quick test script to diagnose search issues."""

from core.uta_chroma_store import ChromaVectorStore

store = ChromaVectorStore(
    persist_directory='./data/chroma',
    collection_name='uta_knowledge',
    embedding_provider='ollama',
    embedding_model='nomic-embed-text'
)
store.initialize()

print("Testing hybrid_search for 'What does error code ERR-QUEUE-001 mean?'...")
results = store.hybrid_search('What does error code ERR-QUEUE-001 mean?', top_k=5)
print(f"Results: {len(results)}")
for r in results:
    print(f"  [{r.score:.4f}] {r.document.id}")
    if r.score > 0.3:
        print(f"    Content: {r.document.content[:150]}...")

print()
print("Testing hybrid_search for 'ERR-QUEUE-001'...")
results2 = store.hybrid_search('ERR-QUEUE-001', top_k=5)
print(f"Results: {len(results2)}")
for r in results2:
    print(f"  [{r.score:.4f}] {r.document.id}")
