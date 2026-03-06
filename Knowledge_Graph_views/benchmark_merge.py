"""
Performance-Benchmark: Merge vs. Direkt-Generierung
"""
import time
import json
from pathlib import Path

def simulate_merge_performance(existing_nodes: int, new_nodes: int):
    """Simuliert Merge-Performance."""
    print(f"\n📊 Merge: {existing_nodes} + {new_nodes} Nodes")
    
    start = time.time()
    
    # 1. Load existing graph (simulation: dict with node IDs)
    existing_graph = {f"NODE-{i}": {"id": f"NODE-{i}", "data": "..."} 
                      for i in range(existing_nodes)}
    load_time = time.time() - start
    
    # 2. Load new graph
    new_graph = {f"NEW-{i}": {"id": f"NEW-{i}", "data": "..."} 
                 for i in range(new_nodes)}
    
    # 3. Index-based merge (O(n+m))
    merge_start = time.time()
    for node_id, node in new_graph.items():
        if node_id in existing_graph:
            # Update
            existing_graph[node_id].update(node)
        else:
            # Add
            existing_graph[node_id] = node
    merge_time = time.time() - merge_start
    
    total_time = time.time() - start
    
    print(f"  Load Time:  {load_time*1000:.2f}ms")
    print(f"  Merge Time: {merge_time*1000:.2f}ms")
    print(f"  Total Time: {total_time*1000:.2f}ms")
    print(f"  Memory: {len(existing_graph) + len(new_graph)} nodes in RAM")
    
    return total_time


def simulate_direct_performance(total_nodes: int, parse_cost_ms: float = 10):
    """Simuliert Direkt-Generierung Performance."""
    print(f"\n📊 Direkt: {total_nodes} Nodes")
    
    start = time.time()
    
    # 1. Parse all text files (simulation: sleep per file)
    parse_time = (total_nodes * parse_cost_ms) / 1000  # Convert to seconds
    time.sleep(parse_time)
    
    # 2. Create graph
    graph = {f"NODE-{i}": {"id": f"NODE-{i}", "data": "..."} 
             for i in range(total_nodes)}
    
    # 3. Edge inference (O(n²) worst case, simplified to O(n*k))
    edge_infer_start = time.time()
    edges = []
    for i in range(min(100, total_nodes)):  # Simplified: only check first 100
        for j in range(min(100, total_nodes)):
            if i != j:
                edges.append((f"NODE-{i}", f"NODE-{j}"))
    edge_infer_time = time.time() - edge_infer_start
    
    total_time = time.time() - start
    
    print(f"  Parse Time: {parse_time*1000:.2f}ms ({total_nodes} files)")
    print(f"  Edge Inference: {edge_infer_time*1000:.2f}ms")
    print(f"  Total Time: {total_time*1000:.2f}ms")
    print(f"  Memory: {len(graph)} nodes in RAM")
    
    return total_time


if __name__ == '__main__':
    print("="*70)
    print("🔬 Performance Benchmark: Merge vs. Direkt-Generierung")
    print("="*70)
    
    # Scenario: 1000 existing + 20 new
    print("\n🎯 SCENARIO: 1000 existing Nodes + 20 neue Nodes")
    print("-"*70)
    
    merge_time = simulate_merge_performance(1000, 20)
    direct_time = simulate_direct_performance(1020, parse_cost_ms=5)
    
    print("\n" + "="*70)
    print("📈 ERGEBNIS:")
    print("="*70)
    print(f"Merge-Ansatz:   {merge_time*1000:.2f}ms")
    print(f"Direkt-Ansatz:  {direct_time*1000:.2f}ms")
    print(f"Speedup:        {direct_time/merge_time:.2f}x schneller mit Merge")
    print("="*70)
    
    # Larger scenario
    print("\n\n🎯 SCENARIO: 5000 existing Nodes + 100 neue Nodes")
    print("-"*70)
    
    merge_time_large = simulate_merge_performance(5000, 100)
    direct_time_large = simulate_direct_performance(5100, parse_cost_ms=5)
    
    print("\n" + "="*70)
    print("📈 ERGEBNIS:")
    print("="*70)
    print(f"Merge-Ansatz:   {merge_time_large*1000:.2f}ms")
    print(f"Direkt-Ansatz:  {direct_time_large*1000:.2f}ms")
    print(f"Speedup:        {direct_time_large/merge_time_large:.2f}x schneller mit Merge")
    print("="*70)
