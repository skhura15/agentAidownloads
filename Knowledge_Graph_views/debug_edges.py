"""Debug script to understand edge inference"""
import json
import re

# Load the generated graph
with open('knowledge_graph_generated.json', 'r', encoding='utf-8') as f:
    kg = json.load(f)

# Create ID index
node_by_id = {node['id']: node for node in kg['nodes']}
print(f"Total nodes: {len(kg['nodes'])}")
print(f"Node IDs: {sorted(node_by_id.keys())}\n")

# Check for ID references
print("="*80)
print("Checking for ID references in properties...")
print("="*80)

found_refs = []
for node in kg['nodes']:
    node_id = node['id']
    node_type = node['type']
    
    for prop_key, prop_value in node.get('properties', {}).items():
        if not isinstance(prop_value, str):
            continue
        
        # Search for IDs
        referenced_ids = re.findall(r'\b([A-Z]{2,4}-[A-Z0-9\-]+)\b', prop_value)
        
        if referenced_ids:
            for ref_id in referenced_ids:
                if ref_id in node_by_id and ref_id != node_id:
                    found_refs.append((node_id, ref_id, node_type, node_by_id[ref_id]['type'], prop_key))
                    print(f"{node_id} ({node_type}) -> {ref_id} ({node_by_id[ref_id]['type']}) via {prop_key}")

print(f"\nTotal references found: {len(found_refs)}")

if not found_refs:
    print("\n⚠ NO REFERENCES FOUND!")
    print("Let's check what properties contain:")
    for node in kg['nodes'][:3]:  # First 3 nodes
        print(f"\n{node['id']} ({node['type']}):")
        for key, value in node.get('properties', {}).items():
            if isinstance(value, str) and len(value) > 100:
                print(f"  {key}: {value[:100]}...")
            else:
                print(f"  {key}: {value}")
