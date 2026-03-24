import json

# Lade knowledge_graph.json
with open('knowledge_graph.json', 'r', encoding='utf-8') as f:
    kg = json.load(f)

# Erstelle Node-Type Index
node_types = {}
for node in kg['nodes']:
    node_types[node['id']] = node['type']

# Analysiere Edges und erstelle Edge-Regeln
edge_rules = {}
for edge in kg['edges']:
    source_type = node_types.get(edge['source'], 'Unknown')
    target_type = node_types.get(edge['target'], 'Unknown')
    edge_type = edge['type']
    
    key = (source_type, edge_type)
    
    if key not in edge_rules:
        edge_rules[key] = set()
    edge_rules[key].add(target_type)

# Ausgabe der Edge-Regeln
print('EDGE_RULES: Dict[Tuple[str, str], Union[str, List[str]]] = {')
for (source_type, edge_type), target_types in sorted(edge_rules.items()):
    target_list = sorted(list(target_types))
    if len(target_list) == 1:
        print(f'    ("{source_type}", "{edge_type}"): "{target_list[0]}",')
    else:
        formatted_targets = json.dumps(target_list)
        print(f'    ("{source_type}", "{edge_type}"): {formatted_targets},')
print('}')

print('\n\n=== STATISTIK ===')
print(f'Anzahl verschiedener Edge-Regeln: {len(edge_rules)}')
print(f'Anzahl verschiedener Edge-Types: {len(set(e for _, e in edge_rules.keys()))}')
print(f'Anzahl verschiedener Source-Types: {len(set(s for s, _ in edge_rules.keys()))}')

print('\n\n=== GRUPPIERUNG NACH SOURCE-TYPE ===')
by_source = {}
for (source_type, edge_type), target_types in sorted(edge_rules.items()):
    if source_type not in by_source:
        by_source[source_type] = []
    target_list = sorted(list(target_types))
    by_source[source_type].append((edge_type, target_list))

for source_type, rules in sorted(by_source.items()):
    print(f'\n{source_type}:')
    for edge_type, targets in rules:
        if len(targets) == 1:
            print(f'  - {edge_type} → {targets[0]}')
        else:
            print(f'  - {edge_type} → {targets}')
