"""
Neo4j Knowledge Graph Converter
================================
Converts knowledge_graph.json to Neo4j-compatible formats:
1. Cypher queries (.cypher)
2. CSV import files (nodes.csv, edges.csv)
3. Direct to Neo4j database (optional)

Usage:
    # Generate Cypher queries
    python convert_to_neo4j.py --output cypher

    # Generate CSV for LOAD CSV
    python convert_to_neo4j.py --output csv

    # Import directly to Neo4j
    python convert_to_neo4j.py --output direct --neo4j-uri bolt://localhost:7687
"""

import json
import csv
import argparse
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class Neo4jConverter:
    """Converts Knowledge Graph JSON to Neo4j formats."""
    
    def __init__(self, json_file: Path, output_dir: Path):
        self.json_file = json_file
        self.output_dir = output_dir
        self.graph = None
        
        # Statistics
        self.stats = {
            'nodes': 0,
            'edges': 0,
            'node_types': set(),
            'edge_types': set()
        }
    
    def load_graph(self) -> None:
        """Loads the knowledge graph."""
        print(f"📖 Lade Knowledge Graph: {self.json_file}")
        with open(self.json_file, 'r', encoding='utf-8') as f:
            self.graph = json.load(f)
        
        self.stats['nodes'] = len(self.graph.get('nodes', []))
        self.stats['edges'] = len(self.graph.get('edges', []))
        self.stats['node_types'] = set(n['type'] for n in self.graph.get('nodes', []))
        self.stats['edge_types'] = set(e['type'] for e in self.graph.get('edges', []))
        
        print(f"   ✓ {self.stats['nodes']} Nodes, {self.stats['edges']} Edges")
        print(f"   ✓ {len(self.stats['node_types'])} Node-Types, {len(self.stats['edge_types'])} Edge-Types")
    
    def generate_cypher_queries(self, use_merge: bool = True) -> str:
        """Generates Cypher queries for Neo4j."""
        print(f"\n🔧 Generiere Cypher-Queries (Mode: {'MERGE' if use_merge else 'CREATE'})...")
        
        queries = []
        
        # Header
        queries.append("// ========================================")
        queries.append("// Knowledge Graph Import - Cypher Queries")
        queries.append(f"// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        queries.append(f"// Mode: {'MERGE (idempotent)' if use_merge else 'CREATE'}")
        queries.append(f"// Nodes: {self.stats['nodes']}, Edges: {self.stats['edges']}")
        queries.append("// ========================================\n")
        
        # Constraints (for performance and data integrity)
        queries.append("// --- Constraints ---")
        for node_type in sorted(self.stats['node_types']):
            queries.append(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{node_type}) REQUIRE n.id IS UNIQUE;")
        queries.append("")
        
        # Indexes (for faster queries)
        queries.append("// --- Indexes ---")
        for node_type in sorted(self.stats['node_types']):
            queries.append(f"CREATE INDEX IF NOT EXISTS FOR (n:{node_type}) ON (n.label);")
        queries.append("\n")
        
        # Create/update nodes
        command = "MERGE" if use_merge else "CREATE"
        queries.append(f"// --- {command} NODES ---\n")
        
        for node in self.graph.get('nodes', []):
            node_id = self._escape_cypher(node['id'])
            node_type = node['type']
            label = self._escape_cypher(node.get('label', ''))
            
            # Properties as JSON string for easy handling
            properties = node.get('properties', {})
            props_str = self._build_properties_string(properties)
            
            # Tags as array
            tags = node.get('tags', [])
            tags_str = json.dumps(tags)
            
            if use_merge:
                # MERGE für idempotente Updates
                query = (
                    f"MERGE (n:{node_type} {{{{id: '{node_id}'}}}}) "
                    f"ON CREATE SET n.label = '{label}', n.tags = {tags_str}{props_str} "
                    f"ON MATCH SET n.label = '{label}', n.tags = {tags_str}{props_str};"
                )
            else:
                query = f"CREATE (n:{node_type} {{{{id: '{node_id}', label: '{label}', tags: {tags_str}{props_str}}}}});"
            
            queries.append(query)
        
        queries.append(f"\n// --- {command} RELATIONSHIPS ---\n")
        
        # Create/update edges
        for edge in self.graph.get('edges', []):
            source = self._escape_cypher(edge['source'])
            target = self._escape_cypher(edge['target'])
            edge_type = edge['type']
            
            if use_merge:
                # MERGE for idempotent updates (no duplicates)
                query = (
                    f"MATCH (a {{{{id: '{source}'}}}}),(b {{{{id: '{target}'}}}}) "
                    f"MERGE (a)-[:{edge_type}]->(b);"
                )
            else:
                query = (
                    f"MATCH (a {{{{id: '{source}'}}}})  , (b {{{{id: '{target}'}}}}) "
                    f"CREATE (a)-[:{edge_type}]->(b);"
                )
            queries.append(query)
        
        # Summary
        queries.append("\n// --- DONE ---")
        queries.append(f"// Created {self.stats['nodes']} nodes and {self.stats['edges']} relationships")
        
        return "\n".join(queries)
    
    def _escape_cypher(self, text: str) -> str:
        """Escapes string for Cypher."""
        if not isinstance(text, str):
            text = str(text)
        return text.replace("'", "\\'").replace('"', '\\"')
    
    def _build_properties_string(self, properties: Dict[str, Any]) -> str:
        """Builds property string for Cypher."""
        if not properties:
            return ""
        
        props = []
        for key, value in properties.items():
            # Sanitize key (Neo4j doesn't allow special characters)
            safe_key = key.replace('-', '_').replace(' ', '_').replace('.', '_')
            
            if isinstance(value, str):
                # Escape string
                escaped_value = self._escape_cypher(value)
                # Shorten long strings
                if len(escaped_value) > 500:
                    escaped_value = escaped_value[:500] + "..."
                props.append(f"{safe_key}: '{escaped_value}'")
            elif isinstance(value, (int, float)):
                props.append(f"{safe_key}: {value}")
            elif isinstance(value, bool):
                props.append(f"{safe_key}: {str(value).lower()}")
            elif isinstance(value, list):
                props.append(f"{safe_key}: {json.dumps(value)}")
            else:
                # Complex objects as JSON string
                props.append(f"{safe_key}: '{json.dumps(value)}'")
        
        if props:
            return ", " + ", ".join(props)
        return ""
    
    def generate_csv_files(self) -> None:
        """Generates CSV files for LOAD CSV."""
        print("\n📊 Generating CSV files...")
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Nodes CSV
        nodes_file = self.output_dir / "nodes.csv"
        print(f"   Writing: {nodes_file}")
        
        with open(nodes_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow(['id', 'type', 'label', 'tags', 'properties'])
            
            for node in self.graph.get('nodes', []):
                writer.writerow([
                    node['id'],
                    node['type'],
                    node.get('label', ''),
                    json.dumps(node.get('tags', [])),
                    json.dumps(node.get('properties', {}))
                ])
        
        # Edges CSV
        edges_file = self.output_dir / "edges.csv"
        print(f"   Writing: {edges_file}")
        
        with open(edges_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow(['source', 'target', 'type'])
            
            for edge in self.graph.get('edges', []):
                writer.writerow([
                    edge['source'],
                    edge['target'],
                    edge['type']
                ])
        
        # Generate LOAD CSV Cypher script
        load_script = self.output_dir / "load_csv.cypher"
        print(f"   Writing: {load_script}")
        
        with open(load_script, 'w', encoding='utf-8') as f:
            f.write("// Load Nodes from CSV\n")
            f.write(f"LOAD CSV WITH HEADERS FROM 'file:///{nodes_file.name}' AS row\n")
            f.write("CALL {\n")
            f.write("  WITH row\n")
            f.write("  CALL apoc.create.node([row.type], \n")
            f.write("    {id: row.id, label: row.label, \n")
            f.write("     tags: apoc.convert.fromJsonList(row.tags),\n")
            f.write("     properties: apoc.convert.fromJsonMap(row.properties)}\n")
            f.write("  ) YIELD node\n")
            f.write("  RETURN node\n")
            f.write("} IN TRANSACTIONS OF 500 ROWS;\n\n")
            
            f.write("// Load Edges from CSV\n")
            f.write(f"LOAD CSV WITH HEADERS FROM 'file:///{edges_file.name}' AS row\n")
            f.write("CALL {\n")
            f.write("  WITH row\n")
            f.write("  MATCH (a {id: row.source})\n")
            f.write("  MATCH (b {id: row.target})\n")
            f.write("  CALL apoc.create.relationship(a, row.type, {}, b) YIELD rel\n")
            f.write("  RETURN rel\n")
            f.write("} IN TRANSACTIONS OF 1000 ROWS;\n")
        
        print(f"   ✓ CSV files created in directory: {self.output_dir}")
    
    def import_to_neo4j(self, uri: str, user: str, password: str) -> None:
        """Imports directly to Neo4j database."""
        try:
            from neo4j import GraphDatabase
        except ImportError:
            print("❌ Error: neo4j Python package not installed")
            print("   Install with: pip install neo4j")
            return
        
        print(f"\n🔗 Connecting to Neo4j: {uri}")
        
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            # Create constraints
            print("   Creating constraints...")
            for node_type in sorted(self.stats['node_types']):
                try:
                    session.run(
                        f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{node_type}) "
                        f"REQUIRE n.id IS UNIQUE"
                    )
                except Exception as e:
                    print(f"   ⚠️  Constraint for {node_type}: {e}")
            
            # Import nodes
            print(f"   Importing {self.stats['nodes']} nodes...")
            node_count = 0
            for node in self.graph.get('nodes', []):
                query = f"CREATE (n:{node['type']} $props)"
                props = {
                    'id': node['id'],
                    'label': node.get('label', ''),
                    'tags': node.get('tags', []),
                    **node.get('properties', {})
                }
                session.run(query, props=props)
                node_count += 1
                if node_count % 100 == 0:
                    print(f"      {node_count}/{self.stats['nodes']} nodes imported...")
            
            # Import edges
            print(f"   Importing {self.stats['edges']} edges...")
            edge_count = 0
            for edge in self.graph.get('edges', []):
                query = (
                    f"MATCH (a {{id: $source}}), (b {{id: $target}}) "
                    f"CREATE (a)-[:{edge['type']}]->(b)"
                )
                session.run(query, source=edge['source'], target=edge['target'])
                edge_count += 1
                if edge_count % 100 == 0:
                    print(f"      {edge_count}/{self.stats['edges']} edges imported...")
        
        driver.close()
        print(f"   ✅ Import completed!")
    
    def generate_delta_queries(self, previous_graph_file: Path) -> str:
        """Generates only delta queries (new/changed nodes and edges)."""
        print(f"\n🔍 Loading previous graph: {previous_graph_file}")
        
        with open(previous_graph_file, 'r', encoding='utf-8') as f:
            prev_graph = json.load(f)
        
        print(f"   Previous: {len(prev_graph.get('nodes', []))} Nodes, {len(prev_graph.get('edges', []))} Edges")
        
        # Create indexes
        prev_nodes = {n['id']: n for n in prev_graph.get('nodes', [])}
        prev_edges = {(e['source'], e['target'], e['type']) for e in prev_graph.get('edges', [])}
        
        curr_nodes = {n['id']: n for n in self.graph.get('nodes', [])}
        curr_edges = {(e['source'], e['target'], e['type']) for e in self.graph.get('edges', [])}
        
        # Find differences
        new_nodes = []
        updated_nodes = []
        deleted_nodes = []
        
        for node_id, node in curr_nodes.items():
            if node_id not in prev_nodes:
                new_nodes.append(node)
            elif node != prev_nodes[node_id]:
                updated_nodes.append(node)
        
        for node_id in prev_nodes:
            if node_id not in curr_nodes:
                deleted_nodes.append(prev_nodes[node_id])
        
        new_edges = [e for e in self.graph.get('edges', []) 
                     if (e['source'], e['target'], e['type']) not in prev_edges]
        
        deleted_edges = []
        for edge_key in prev_edges:
            if edge_key not in curr_edges:
                deleted_edges.append({
                    'source': edge_key[0],
                    'target': edge_key[1],
                    'type': edge_key[2]
                })
        
        print(f"\n📊 Delta analysis:")
        print(f"   ➕ Neue Nodes:      {len(new_nodes)}")
        print(f"   ✏️  Updated Nodes:   {len(updated_nodes)}")
        print(f"   ❌ Deleted Nodes:   {len(deleted_nodes)}")
        print(f"   ➕ Neue Edges:      {len(new_edges)}")
        print(f"   ❌ Deleted Edges:   {len(deleted_edges)}")
        
        # Generate delta queries
        queries = []
        
        queries.append("// ========================================")
        queries.append("// Knowledge Graph DELTA Update - Cypher Queries")
        queries.append(f"// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        queries.append(f"// New Nodes: {len(new_nodes)}, Updated: {len(updated_nodes)}, Deleted: {len(deleted_nodes)}")
        queries.append(f"// New Edges: {len(new_edges)}, Deleted: {len(deleted_edges)}")
        queries.append("// ========================================\n")
        
        # Neue Nodes
        if new_nodes:
            queries.append("// --- ADD NEW NODES ---\n")
            for node in new_nodes:
                node_id = self._escape_cypher(node['id'])
                node_type = node['type']
                label = self._escape_cypher(node.get('label', ''))
                properties = node.get('properties', {})
                props_str = self._build_properties_string(properties)
                tags = node.get('tags', [])
                tags_str = json.dumps(tags)
                
                query = (
                    f"CREATE (n:{node_type} {{id: '{node_id}', label: '{label}', "
                    f"tags: {tags_str}{props_str}}});"
                )
                queries.append(query)
            queries.append("")
        
        # Updated nodes
        if updated_nodes:
            queries.append("// --- UPDATE EXISTING NODES ---\n")
            for node in updated_nodes:
                node_id = self._escape_cypher(node['id'])
                node_type = node['type']
                label = self._escape_cypher(node.get('label', ''))
                properties = node.get('properties', {})
                props_str = self._build_properties_string(properties)
                tags = node.get('tags', [])
                tags_str = json.dumps(tags)
                
                query = (
                    f"MATCH (n:{node_type} {{id: '{node_id}'}}) "
                    f"SET n.label = '{label}', n.tags = {tags_str}{props_str};"
                )
                queries.append(query)
            queries.append("")
        
        # Deleted nodes
        if deleted_nodes:
            queries.append("// --- DELETE REMOVED NODES ---\n")
            for node in deleted_nodes:
                node_id = self._escape_cypher(node['id'])
                query = f"MATCH (n {{id: '{node_id}'}}) DETACH DELETE n;"
                queries.append(query)
            queries.append("")
        
        # New edges
        if new_edges:
            queries.append("// --- ADD NEW EDGES ---\n")
            for edge in new_edges:
                source = self._escape_cypher(edge['source'])
                target = self._escape_cypher(edge['target'])
                edge_type = edge['type']
                
                query = (
                    f"MATCH (a {{id: '{source}'}}), (b {{id: '{target}'}}) "
                    f"MERGE (a)-[:{edge_type}]->(b);"
                )
                queries.append(query)
            queries.append("")
        
        # Deleted edges
        if deleted_edges:
            queries.append("// --- DELETE REMOVED EDGES ---\n")
            for edge in deleted_edges:
                source = self._escape_cypher(edge['source'])
                target = self._escape_cypher(edge['target'])
                edge_type = edge['type']
                
                query = (
                    f"MATCH (a {{id: '{source}'}})-[r:{edge_type}]->(b {{id: '{target}'}}) "
                    f"DELETE r;"
                )
                queries.append(query)
            queries.append("")
        
        queries.append("// --- DONE ---")
        queries.append(f"// Delta update completed")
        
        return "\n".join(queries)
    
    def print_summary(self) -> None:
        """Shows summary."""
        print("\n" + "="*70)
        print("📊 CONVERSION SUMMARY")
        print("="*70)
        print(f"Input:  {self.json_file}")
        print(f"Output: {self.output_dir}")
        print(f"\nNodes:  {self.stats['nodes']}")
        print(f"Edges:  {self.stats['edges']}")
        print(f"\nNode Types: {', '.join(sorted(self.stats['node_types']))}")
        print(f"\nEdge Types: {', '.join(sorted(list(self.stats['edge_types'])[:10]))}")
        if len(self.stats['edge_types']) > 10:
            print(f"            ... and {len(self.stats['edge_types']) - 10} more")
        print("="*70)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Converts Knowledge Graph JSON to Neo4j formats"
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=Path(__file__).parent / 'knowledge_graph.json',
        help='Input JSON file (default: knowledge_graph.json)'
    )
    parser.add_argument(
        '--output',
        choices=['cypher', 'csv', 'direct', 'delta'],
        default='cypher',
        help='Output format (default: cypher)'
    )
    parser.add_argument(
        '--previous',
        type=Path,
        help='Previous knowledge_graph.json for delta mode'
    )
    parser.add_argument(
        '--use-merge',
        action='store_true',
        default=True,
        help='Use MERGE instead of CREATE for idempotent updates (default: True)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent / 'neo4j_output',
        help='Output directory (default: neo4j_output)'
    )
    parser.add_argument(
        '--neo4j-uri',
        default='bolt://localhost:7687',
        help='Neo4j URI for direct import'
    )
    parser.add_argument(
        '--neo4j-user',
        default='neo4j',
        help='Neo4j Username'
    )
    parser.add_argument(
        '--neo4j-password',
        default='password',
        help='Neo4j Password'
    )
    
    args = parser.parse_args()
    
    # Validation
    if not args.input.exists():
        print(f"❌ Error: Input file not found: {args.input}")
        return 1
    
    # Initialize converter
    converter = Neo4jConverter(args.input, args.output_dir)
    converter.load_graph()
    
    # Generate output
    if args.output == 'cypher':
        queries = converter.generate_cypher_queries(use_merge=args.use_merge)
        output_file = args.output_dir / 'import.cypher'
        args.output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(queries)
        
        print(f"\n✅ Cypher queries saved: {output_file}")
        print(f"\nExecute with:")
        print(f"  cat {output_file} | cypher-shell -u neo4j -p password")
        print(f"  or: Copy to Neo4j Browser")
    
    elif args.output == 'delta':
        if not args.previous:
            print("❌ Error: --previous required for delta mode")
            print("   Example: --output delta --previous knowledge_graph_old.json")
            return 1
        
        if not args.previous.exists():
            print(f"❌ Error: Previous graph not found: {args.previous}")
            return 1
        
        queries = converter.generate_delta_queries(args.previous)
        output_file = args.output_dir / 'delta_update.cypher'
        args.output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(queries)
        
        print(f"\n✅ Delta queries saved: {output_file}")
        print(f"\nExecute with:")
        print(f"  cat {output_file} | cypher-shell -u neo4j -p password")
    
    elif args.output == 'csv':
        converter.generate_csv_files()
        print(f"\n✅ CSV files created!")
        print(f"\nImport with:")
        print(f"  1. Copy nodes.csv and edges.csv to Neo4j import/ directory")
        print(f"  2. Execute load_csv.cypher in Neo4j Browser")
        print(f"  3. Or use neo4j-admin import")
    
    elif args.output == 'direct':
        converter.import_to_neo4j(
            args.neo4j_uri,
            args.neo4j_user,
            args.neo4j_password
        )
    
    converter.print_summary()
    
    return 0


if __name__ == '__main__':
    exit(main())
