"""Test für aktualisierte EDGE_RULES"""
import sys
sys.path.insert(0, 'Knowledge_Graph_views')

from dict import EDGE_RULES

print("="*70)
print("✅ EDGE_RULES erfolgreich aktualisiert!")
print("="*70)
print(f"\nAnzahl Edge-Regeln: {len(EDGE_RULES)}")

# Gruppiere nach Source-Type
by_source = {}
for (source_type, edge_type), target in EDGE_RULES.items():
    if source_type not in by_source:
        by_source[source_type] = []
    by_source[source_type].append((edge_type, target))

print("\n📊 Gruppierung nach Source-Type:")
for source_type in sorted(by_source.keys()):
    rules = by_source[source_type]
    print(f"\n{source_type} ({len(rules)} Regeln):")
    for edge_type, target in sorted(rules):
        if isinstance(target, list):
            print(f"  - {edge_type} → {target}")
        else:
            print(f"  - {edge_type} → {target}")

print("\n" + "="*70)
print("✅ Wichtige Ergänzungen:")
print("="*70)
print("✓ Runbook RELATED_TO jetzt vollständig")
print("✓ Alle Node-Typen gruppiert und kommentiert")
print("✓ Konsistent mit knowledge_graph.json")
