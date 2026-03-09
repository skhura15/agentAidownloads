import json
import re

# Load generated graph
with open('knowledge_graph_generated.json', 'r', encoding='utf-8') as f:
    graph = json.load(f)

nodes = graph['nodes']

print("Checking _full_text property...")
print("="*80)

for node in nodes[:5]:  # Check first 5 nodes
    has_full_text = '_full_text' in node.get('properties', {})
    full_text_len = len(node['properties'].get('_full_text', '')) if has_full_text else 0
    print(f"\n{node['id']} ({node['type']}): has _full_text={has_full_text}, length={full_text_len}")
    if has_full_text:
        print(f"Preview: {node['properties']['_full_text'][:300]}...")
    else:
        print("Properties:", list(node.get('properties', {}).keys()))
