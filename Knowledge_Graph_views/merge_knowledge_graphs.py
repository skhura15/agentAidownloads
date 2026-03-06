"""
Knowledge Graph Merger
======================
Merges a generated sub-graph (knowledge_graph_generated.json) 
with the main graph (knowledge_graph.json).

Usage:
    python merge_knowledge_graphs.py
    python merge_knowledge_graphs.py --source generated.json --target main.json
    python merge_knowledge_graphs.py --dry-run  # Shows what would be changed
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Set
from datetime import datetime


class KnowledgeGraphMerger:
    """Merges two knowledge graphs intelligently."""
    
    def __init__(self, target_file: Path, source_file: Path, dry_run: bool = False):
        self.target_file = target_file
        self.source_file = source_file
        self.dry_run = dry_run
        
        self.target_graph = None
        self.source_graph = None
        
        # Statistics
        self.stats = {
            'nodes_added': 0,
            'nodes_updated': 0,
            'nodes_unchanged': 0,
            'edges_added': 0,
            'edges_duplicate': 0
        }
    
    def load_graphs(self) -> None:
        """Loads both knowledge graphs."""
        print(f"📖 Lade Target-Graph: {self.target_file}")
        with open(self.target_file, 'r', encoding='utf-8') as f:
            self.target_graph = json.load(f)
        
        print(f"📖 Lade Source-Graph: {self.source_file}")
        with open(self.source_file, 'r', encoding='utf-8') as f:
            self.source_graph = json.load(f)
        
        print(f"   ✓ Target: {len(self.target_graph.get('nodes', []))} Nodes, {len(self.target_graph.get('edges', []))} Edges")
        print(f"   ✓ Source: {len(self.source_graph.get('nodes', []))} Nodes, {len(self.source_graph.get('edges', []))} Edges")
    
    def merge_nodes(self) -> None:
        """Merges nodes: adds new ones, updates existing ones."""
        print("\n🔄 Merge nodes...")
        
        # Create index of target nodes
        target_nodes_by_id = {node['id']: node for node in self.target_graph['nodes']}
        
        for source_node in self.source_graph.get('nodes', []):
            node_id = source_node['id']
            
            if node_id in target_nodes_by_id:
                # Node already exists - check if update needed
                target_node = target_nodes_by_id[node_id]
                
                if self._should_update_node(target_node, source_node):
                    self._update_node(target_node, source_node)
                    self.stats['nodes_updated'] += 1
                    print(f"   ✏️  Updated: {node_id} ({source_node['type']}) - {source_node.get('label', '')}")
                else:
                    self.stats['nodes_unchanged'] += 1
            else:
                # New node - add it
                self.target_graph['nodes'].append(source_node)
                self.stats['nodes_added'] += 1
                print(f"   ✅ Added: {node_id} ({source_node['type']}) - {source_node.get('label', '')}")
    
    def _should_update_node(self, target_node: Dict, source_node: Dict) -> bool:
        """Checks if a node should be updated."""
        # Update if:
        # 1. Properties are different
        # 2. Tags are different
        # 3. Label is different
        
        if target_node.get('label') != source_node.get('label'):
            return True
        
        if target_node.get('properties') != source_node.get('properties'):
            return True
        
        target_tags = set(target_node.get('tags', []))
        source_tags = set(source_node.get('tags', []))
        if target_tags != source_tags:
            return True
        
        return False
    
    def _update_node(self, target_node: Dict, source_node: Dict) -> None:
        """Updates an existing node."""
        # Update label
        if source_node.get('label'):
            target_node['label'] = source_node['label']
        
        # Merge properties (source overwrites target)
        target_props = target_node.get('properties', {})
        source_props = source_node.get('properties', {})
        target_props.update(source_props)
        target_node['properties'] = target_props
        
        # Merge tags (union)
        target_tags = set(target_node.get('tags', []))
        source_tags = set(source_node.get('tags', []))
        merged_tags = sorted(list(target_tags | source_tags))
        target_node['tags'] = merged_tags
    
    def merge_edges(self) -> None:
        """Merges edges: deduplicates and adds new ones."""
        print("\n🔗 Merge edges...")
        
        # Create set of existing edges
        existing_edges = set()
        for edge in self.target_graph.get('edges', []):
            key = (edge['source'], edge['target'], edge['type'])
            existing_edges.add(key)
        
        # Add new edges
        for source_edge in self.source_graph.get('edges', []):
            key = (source_edge['source'], source_edge['target'], source_edge['type'])
            
            if key in existing_edges:
                self.stats['edges_duplicate'] += 1
            else:
                self.target_graph['edges'].append(source_edge)
                existing_edges.add(key)
                self.stats['edges_added'] += 1
                print(f"   ✅ Added Edge: {source_edge['source']} --[{source_edge['type']}]--> {source_edge['target']}")
    
    def merge_node_types(self) -> None:
        """Merges node_types (union)."""
        target_types = set(self.target_graph.get('node_types', []))
        source_types = set(self.source_graph.get('node_types', []))
        merged_types = sorted(list(target_types | source_types))
        self.target_graph['node_types'] = merged_types
    
    def merge_edge_types(self) -> None:
        """Merges edge_types (union)."""
        target_types = set(self.target_graph.get('edge_types', []))
        source_types = set(self.source_graph.get('edge_types', []))
        merged_types = sorted(list(target_types | source_types))
        self.target_graph['edge_types'] = merged_types
    
    def update_metadata(self) -> None:
        """Updates metadata."""
        print("\n📊 Update Metadata...")
        
        metadata = self.target_graph.get('metadata', {})
        metadata['last_updated'] = datetime.now().strftime("%Y-%m-%d")
        metadata['total_nodes'] = len(self.target_graph['nodes'])
        metadata['total_edges'] = len(self.target_graph['edges'])
        
        # Add merge info
        if 'merge_history' not in metadata:
            metadata['merge_history'] = []
        
        metadata['merge_history'].append({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'source': str(self.source_file.name),
            'nodes_added': self.stats['nodes_added'],
            'nodes_updated': self.stats['nodes_updated'],
            'edges_added': self.stats['edges_added']
        })
        
        self.target_graph['metadata'] = metadata
    
    def save(self) -> None:
        """Saves the merged graph."""
        if self.dry_run:
            print("\n🔍 DRY RUN - No changes saved")
            return
        
        # Create backup
        backup_file = self.target_file.parent / f"{self.target_file.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        print(f"\n💾 Create backup: {backup_file}")
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(self.target_graph, f, indent=2, ensure_ascii=False)
        
        # Save merged graph
        print(f"💾 Save merged graph: {self.target_file}")
        with open(self.target_file, 'w', encoding='utf-8') as f:
            json.dump(self.target_graph, f, indent=2, ensure_ascii=False)
    
    def print_summary(self) -> None:
        """Shows summary."""
        print("\n" + "="*70)
        print("📊 MERGE SUMMARY")
        print("="*70)
        print(f"Nodes:")
        print(f"  ✅ Added:     {self.stats['nodes_added']}")
        print(f"  ✏️  Updated:   {self.stats['nodes_updated']}")
        print(f"  ⏭️  Unchanged: {self.stats['nodes_unchanged']}")
        print(f"\nEdges:")
        print(f"  ✅ Added:     {self.stats['edges_added']}")
        print(f"  ⏭️  Duplicate: {self.stats['edges_duplicate']}")
        print(f"\nTotal in target graph:")
        print(f"  📊 Nodes:     {len(self.target_graph['nodes'])}")
        print(f"  🔗 Edges:     {len(self.target_graph['edges'])}")
        print("="*70)
    
    def merge(self) -> None:
        """Executes the complete merge process."""
        print("="*70)
        print("🔀 Knowledge Graph Merger")
        print("="*70)
        
        self.load_graphs()
        self.merge_nodes()
        self.merge_edges()
        self.merge_node_types()
        self.merge_edge_types()
        self.update_metadata()
        self.print_summary()
        self.save()
        
        if not self.dry_run:
            print("\n✅ Merge completed successfully!")
        else:
            print("\n🔍 Dry-run completed - No changes made")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Merges two knowledge graphs together"
    )
    parser.add_argument(
        '--target',
        type=Path,
        default=Path(__file__).parent / 'knowledge_graph.json',
        help='Target graph (will be updated, default: knowledge_graph.json)'
    )
    parser.add_argument(
        '--source',
        type=Path,
        default=Path(__file__).parent / 'knowledge_graph_generated.json',
        help='Source graph (will be read, default: knowledge_graph_generated.json)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Shows only what would be changed, without saving'
    )
    
    args = parser.parse_args()
    
    # Validation
    if not args.target.exists():
        print(f"❌ Error: Target graph not found: {args.target}")
        return 1
    
    if not args.source.exists():
        print(f"❌ Error: Source graph not found: {args.source}")
        return 1
    
    # Execute merge
    merger = KnowledgeGraphMerger(args.target, args.source, args.dry_run)
    merger.merge()
    
    return 0


if __name__ == '__main__':
    exit(main())
