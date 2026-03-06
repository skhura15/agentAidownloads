"""
Intelligent Knowledge Graph Generator
=====================================
Automatically generates knowledge_graph.json from text files in the data/ directory.

The script:
- Scans all .txt files in the data/ folder
- Extracts node type from filename (KnownIssue_, Runbook_, UserGuide_, etc.)
- Parses structured information from text files
- Automatically generates properties and tags
- Creates a complete knowledge_graph.json

Usage:
    python generate_knowledge_graph.py
    python generate_knowledge_graph.py --data-dir ./data --output knowledge_graph.json
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import argparse


# Node type mapping (filename prefix -> node type)
NODE_TYPE_MAPPING = {
    "KnownIssue": "KnownIssue",
    "Runbook": "Runbook",
    "UserGuide": "UserGuide",
    "SOP": "SOP",
    "SPO": "SPO",
    "FAQ": "FAQ",
    "ReleaseNotes": "ReleaseNote",
    "Configuration": "Configuration",
    "Infrastructure": "Infrastructure",
}

# All node types
ALL_NODE_TYPES = [
    "Product", "Service", "SPO", "ReleaseNote", "UserGuide",
    "KnownIssue", "Runbook", "SOP", "Incident", "Expert",
    "Team", "Customer", "Infrastructure", "Configuration", "FAQ", "Feature"
]

# All edge types
ALL_EDGE_TYPES = [
    "HAS_SERVICE", "DEPENDS_ON", "BELONGS_TO_SPO", "HAS_RELEASE_NOTE",
    "DOCUMENTED_IN", "HAS_KNOWN_ISSUE", "RESOLVED_BY", "HAS_RUNBOOK",
    "HAS_SOP", "REPORTED_INCIDENT", "ASSIGNED_TO", "OWNS", "IMPACTED_BY",
    "SUBSCRIBES_TO", "RUNS_ON", "CONFIGURED_BY", "RELATED_TO",
    "ESCALATES_TO", "FIXED_IN", "HAS_FAQ", "HAS_FEATURE", "WORKAROUND_IN"
]


class TextDocumentParser:
    """Parser for structured text documents."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = self._read_file()
        self.filename = file_path.stem  # Filename without extension
        
    def _read_file(self) -> str:
        """Reads the text file."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def detect_node_type(self) -> Optional[str]:
        """Detects the node type from the filename."""
        for prefix, node_type in NODE_TYPE_MAPPING.items():
            if self.filename.startswith(prefix):
                return node_type
        return None
    
    def extract_id(self, node_type: str) -> str:
        """
        Extracts or generates an ID.
        Examples:
        - KnownIssue_VoiceTransferDrop.txt -> KI-2025-001 (from content) or KI-VOICE-TRANSFER
        - Runbook_VoiceOutage.txt -> RB-VOICE-001 (from content) or RB-VOICE-OUTAGE
        """
        # Try to extract ID from content
        patterns = [
            r'(?:Issue ID|Runbook ID|SOP ID|FAQ ID)\s*:\s*([A-Z0-9\-]+)',
            r'^([A-Z]{2,3}-\d{4}-\d{3})',  # KI-2025-001 format
            r'^([A-Z]{2,3}-[A-Z]+-\d{3})',  # RB-VOICE-001 format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.content, re.MULTILINE)
            if match:
                return match.group(1)
        
        # Generate ID from filename
        prefix_map = {
            "KnownIssue": "KI",
            "Runbook": "RB",
            "UserGuide": "UG",
            "SOP": "SOP",
            "SPO": "SPO",
            "FAQ": "FAQ",
            "ReleaseNotes": "RN",
            "Configuration": "CFG",
            "Infrastructure": "INFRA",
        }
        
        prefix = prefix_map.get(node_type, "NODE")
        
        # Remove node type prefix from filename and create ID
        id_part = self.filename
        for key in NODE_TYPE_MAPPING.keys():
            if id_part.startswith(key):
                id_part = id_part[len(key):].lstrip('_')
                break
        
        # Shorten and format
        id_part = id_part.replace('_', '-').upper()[:20]
        return f"{prefix}-{id_part}"
    
    def extract_label(self) -> str:
        """Extracts the label (title) from the document."""
        # Search for title in different formats
        patterns = [
            r'^={3,}\n(.+?)\n={3,}',  # Title between ======
            r'^KNOWN ISSUE\s*[—-]\s*(.+?)$',
            r'^RUNBOOK\s*[—-]\s*(.+?)$',
            r'^USER GUIDE\s*[—-]\s*(.+?)$',
            r'^STANDARD OPERATING PROCEDURE\s*[—-]\s*(.+?)$',
            r'^FAQ:\s*(.+?)$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.content, re.MULTILINE | re.IGNORECASE)
            if match:
                label = match.group(1).strip()
                # Remove ID from label
                label = re.sub(r'^[A-Z]{2,3}-\d{4}-\d{3}\s*', '', label)
                label = re.sub(r'^[A-Z]{2,3}-[A-Z]+-\d{3}\s*', '', label)
                return label
        
        # Fallback: Use filename
        clean_name = self.filename
        for prefix in NODE_TYPE_MAPPING.keys():
            if clean_name.startswith(prefix):
                clean_name = clean_name[len(prefix):].lstrip('_')
                break
        return clean_name.replace('_', ' ').title()
    
    def extract_key_value_pairs(self) -> Dict[str, Any]:
        """
        Extracts key-value pairs from the document.
        Format: "Key : Value" or "Key: Value"
        """
        properties = {}
        
        # Pattern for Key: Value pairs
        pattern = r'^([A-Za-z][A-Za-z\s]+?)\s*:\s*(.+?)$'
        matches = re.finditer(pattern, self.content, re.MULTILINE)
        
        for match in matches:
            key = match.group(1).strip()
            value = match.group(2).strip()
            
            # Normalize key
            key_normalized = key.lower().replace(' ', '_')
            
            # Filter out too long keys (probably not a real key-value pair)
            if len(key) > 50:
                continue
                
            properties[key_normalized] = value
        
        return properties
    
    def extract_severity(self) -> Optional[str]:
        """Extracts severity (for KnownIssues)."""
        patterns = [
            r'Severity\s*:\s*(P[0-4])',
            r'Priority\s*:\s*(P[0-4])',
            r'(P[0-4])\s*\(Critical\)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.content, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None
    
    def extract_status(self) -> Optional[str]:
        """Extracts status."""
        pattern = r'Status\s*:\s*(.+?)(?:\n|$)'
        match = re.search(pattern, self.content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
    
    def extract_tags(self) -> List[str]:
        """
        Extracts tags from the document.
        Searches for:
        - Explicit tags
        - Technology keywords
        - Service names
        """
        tags = set()
        
        # Explicit tags section
        tags_match = re.search(r'(?:Tags|Keywords)\s*:\s*(.+?)(?:\n|$)', self.content, re.IGNORECASE)
        if tags_match:
            tag_list = re.split(r'[,;]', tags_match.group(1))
            tags.update(t.strip() for t in tag_list if t.strip())
        
        # Technology keywords
        tech_keywords = [
            'Azure', 'ACS', 'Copilot', 'Dynamics', 'Teams', 'OpenAI',
            'Power BI', 'Dataverse', 'Voice', 'Chat', 'SMS', 'WhatsApp',
            'Routing', 'IVR', 'Analytics', 'WFM', 'QM', 'API'
        ]
        
        for keyword in tech_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', self.content, re.IGNORECASE):
                tags.add(keyword)
        
        # Severity as tag
        severity = self.extract_severity()
        if severity:
            tags.add(severity)
        
        return sorted(list(tags))[:10]  # Max 10 tags
    
    def extract_sections(self) -> Dict[str, str]:
        """Extracts named sections from the document."""
        sections = {}
        
        # Pattern for sections (ALL CAPS or with underscores)
        pattern = r'^([A-Z][A-Z\s]+?):\s*\n-+\n((?:(?!^[A-Z][A-Z\s]+?:\s*\n-).)+)'
        matches = re.finditer(pattern, self.content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            section_name = match.group(1).strip()
            section_content = match.group(2).strip()
            sections[section_name.lower().replace(' ', '_')] = section_content[:500]  # Limited to 500 characters
        
        return sections
    
    def parse_to_node(self) -> Optional[Dict[str, Any]]:
        """Parses the document into a Knowledge Graph node."""
        node_type = self.detect_node_type()
        
        if not node_type:
            print(f"⚠ Could not detect node type for: {self.file_path.name}")
            return None
        
        node_id = self.extract_id(node_type)
        label = self.extract_label()
        properties = self.extract_key_value_pairs()
        tags = self.extract_tags()
        
        # Add general properties
        properties['document'] = f"data/{self.file_path.name}"
        
        # Type-specific properties
        if node_type == "KnownIssue":
            properties['severity'] = self.extract_severity() or "Unknown"
            properties['status'] = self.extract_status() or "Unknown"
        
        elif node_type == "Runbook":
            properties['category'] = properties.get('category', 'General')
            estimated_time = re.search(r'Estimated Time\s*:\s*(.+?)(?:\n|$)', self.content)
            if estimated_time:
                properties['estimated_time'] = estimated_time.group(1).strip()
        
        elif node_type == "UserGuide":
            properties['audience'] = properties.get('audience', 'All Users')
        
        # Extract sections for extended information
        sections = self.extract_sections()
        if 'symptoms' in sections:
            properties['symptoms'] = sections['symptoms'][:200]
        if 'workaround' in sections:
            properties['workaround'] = sections['workaround'][:200]
        
        node = {
            "id": node_id,
            "type": node_type,
            "label": label,
            "properties": properties,
            "tags": tags
        }
        
        return node


class KnowledgeGraphGenerator:
    """Generates knowledge_graph.json from text files."""
    
    def __init__(self, data_dir: Path, output_file: Path):
        self.data_dir = data_dir
        self.output_file = output_file
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, str]] = []
    
    def scan_and_parse_documents(self) -> None:
        """Scans the data/ directory and parses all .txt files."""
        txt_files = sorted(self.data_dir.glob("*.txt"))
        
        if not txt_files:
            print(f"⚠ No .txt files found in {self.data_dir}")
            return
        
        print(f"📄 Found: {len(txt_files)} text files")
        
        for txt_file in txt_files:
            print(f"   Parsing: {txt_file.name}...", end=" ")
            parser = TextDocumentParser(txt_file)
            node = parser.parse_to_node()
            
            if node:
                self.nodes.append(node)
                print(f"✓ [{node['type']}] {node['id']}")
            else:
                print("✗ Skipped")
    
    def add_hardcoded_nodes(self) -> None:
        """
        Adds hardcoded nodes that are not from text files.
        (e.g. Product, Service, Team, Expert, Customer, etc.)
        """
        # These can be manually added or loaded from other sources
        hardcoded_nodes = [
            {
                "id": "PROD-001",
                "type": "Product",
                "label": "MS Dynamics 365 Contact Center",
                "properties": {
                    "full_name": "Microsoft Dynamics 365 Contact Center (CCaaS)",
                    "vendor": "Microsoft",
                    "version": "2025 Release Wave 2",
                    "category": "Contact Center as a Service",
                    "deployment": "Cloud (Azure)"
                },
                "tags": ["CCaaS", "Omnichannel", "Copilot", "Azure"]
            },
        ]
        
        print(f"\n📌 Adding {len(hardcoded_nodes)} hardcoded nodes...")
        self.nodes.extend(hardcoded_nodes)
    
    def infer_edges(self) -> None:
        """
        Infers edges between nodes based on:
        - References in text
        - Node IDs in properties
        - Conventions (e.g. Runbook resolves KnownIssue)
        """
        print("\n🔗 Inferring edges...")
        
        # Create ID index for fast lookups
        node_by_id = {node['id']: node for node in self.nodes}
        
        for node in self.nodes:
            node_id = node['id']
            node_type = node['type']
            
            # Search for referenced IDs in properties
            for prop_key, prop_value in node.get('properties', {}).items():
                if not isinstance(prop_value, str):
                    continue
                
                # Search for IDs in format XX-XXX-XXX or XX-XXXX
                referenced_ids = re.findall(r'\b([A-Z]{2,4}-[A-Z0-9\-]+)\b', prop_value)
                
                for ref_id in referenced_ids:
                    if ref_id in node_by_id and ref_id != node_id:
                        target_node = node_by_id[ref_id]
                        
                        # Determine edge type based on node types
                        edge_type = self._determine_edge_type(node_type, target_node['type'])
                        
                        if edge_type:
                            self.edges.append({
                                "source": node_id,
                                "target": ref_id,
                                "type": edge_type
                            })
        
        # Deduplicate edges
        unique_edges = {}
        for edge in self.edges:
            key = (edge['source'], edge['target'], edge['type'])
            unique_edges[key] = edge
        
        self.edges = list(unique_edges.values())
        print(f"   ✓ {len(self.edges)} edges created")
    
    def _determine_edge_type(self, source_type: str, target_type: str) -> Optional[str]:
        """Determines the edge type based on source and target node types."""
        edge_rules = {
            # Product edges
            ("Product", "Service"): "HAS_SERVICE",
            ("Product", "SPO"): "BELONGS_TO_SPO",
            ("Product", "ReleaseNote"): "HAS_RELEASE_NOTE",
            ("Product", "SOP"): "HAS_SOP",
            ("Product", "Feature"): "HAS_FEATURE",
            
            # Service edges
            ("Service", "Infrastructure"): "RUNS_ON",
            ("Service", "Configuration"): "CONFIGURED_BY",
            ("Service", "Service"): "DEPENDS_ON",
            ("Service", "UserGuide"): "DOCUMENTED_IN",
            ("Service", "KnownIssue"): "HAS_KNOWN_ISSUE",
            ("Service", "Runbook"): "HAS_RUNBOOK",
            ("Service", "FAQ"): "HAS_FAQ",
            ("Service", "Feature"): "HAS_FEATURE",
            
            # KnownIssue edges
            ("KnownIssue", "ReleaseNote"): "FIXED_IN",
            ("KnownIssue", "Configuration"): "WORKAROUND_IN",
            ("KnownIssue", "Incident"): "RELATED_TO",
            ("KnownIssue", "Runbook"): "RELATED_TO",
            ("KnownIssue", "UserGuide"): "RELATED_TO",
            
            # Customer edges
            ("Customer", "Incident"): "REPORTED_INCIDENT",
            ("Customer", "SPO"): "SUBSCRIBES_TO",
            
            # Incident edges
            ("Incident", "Service"): "IMPACTED_BY",
            ("Incident", "Runbook"): "RESOLVED_BY",
            ("Incident", "Expert"): "ASSIGNED_TO",
            ("Incident", "KnownIssue"): "RELATED_TO",
            ("Incident", "Configuration"): "RELATED_TO",
            ("Incident", "UserGuide"): "RELATED_TO",
            
            # Runbook edges
            ("Runbook", "Configuration"): "RELATED_TO",
            ("Runbook", "UserGuide"): "RELATED_TO",
            ("Runbook", "KnownIssue"): "RELATED_TO",
            
            # Team edges
            ("Team", "Service"): "OWNS",
            ("Team", "Expert"): "ASSIGNED_TO",
            
            # SOP edges
            ("SOP", "Team"): "ESCALATES_TO",
            
            # SPO edges
            ("SPO", "Service"): "HAS_SERVICE",
        }
        
        return edge_rules.get((source_type, target_type))
    
    def generate_metadata(self) -> Dict[str, Any]:
        """Generates the metadata section."""
        return {
            "graph_name": "Microsoft CCaaS — Support AI Knowledge Graph",
            "version": "2.0.0",
            "description": "Automatically generated Knowledge Graph for Support AI Agent. Based on text documents in the data/ directory.",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "product": "Microsoft Dynamics 365 Contact Center (CCaaS)",
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "schema_version": "v2",
            "generated_by": "generate_knowledge_graph.py"
        }
    
    def generate_ai_instructions(self) -> Dict[str, Any]:
        """Generates AI agent instructions."""
        return {
            "purpose": "When a support ticket arrives for Microsoft Dynamics 365 Contact Center (CCaaS), traverse this graph to find the best resolution path.",
            "resolution_workflow": [
                "1. PARSE: Extract product, service, error messages, symptoms, customer name from ticket",
                "2. IDENTIFY SERVICE: Map symptoms to the affected service node",
                "3. CHECK KNOWN ISSUES: Search KnownIssue nodes matching symptoms — provide workaround immediately",
                "4. CHECK RELEASE NOTES: Follow FIXED_IN edges for available fixes in newer versions",
                "5. FIND RUNBOOK: Follow HAS_RUNBOOK edges for step-by-step recovery",
                "6. CHECK FAQ: Follow HAS_FAQ edges for common questions",
                "7. REVIEW PAST INCIDENTS: Search similar past incidents and their resolutions",
                "8. FIND DOCUMENTS: Retrieve relevant User Guides, SPOs, Release Notes",
                "9. IDENTIFY EXPERTS: Follow OWNS/ASSIGNED_TO edges to find the expert team",
                "10. ESCALATE: If P1, follow SOP for escalation workflow"
            ]
        }
    
    def build_knowledge_graph(self) -> Dict[str, Any]:
        """Creates the complete knowledge graph structure."""
        return {
            "metadata": self.generate_metadata(),
            "node_types": ALL_NODE_TYPES,
            "edge_types": ALL_EDGE_TYPES,
            "nodes": self.nodes,
            "edges": self.edges,
            "ai_agent_instructions": self.generate_ai_instructions()
        }
    
    def save_to_file(self) -> None:
        """Saves the knowledge graph JSON to a file."""
        kg = self.build_knowledge_graph()
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(kg, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Knowledge Graph saved: {self.output_file}")
        print(f"   📊 Nodes: {len(self.nodes)}")
        print(f"   🔗 Edges: {len(self.edges)}")
    
    def run(self) -> None:
        """Executes the entire generation process."""
        print("=" * 80)
        print("🚀 Knowledge Graph Generator")
        print("=" * 80)
        print(f"📁 Data Directory: {self.data_dir}")
        print(f"📝 Output File: {self.output_file}")
        print()
        
        self.scan_and_parse_documents()
        self.add_hardcoded_nodes()
        self.infer_edges()
        self.save_to_file()
        
        print("\n" + "=" * 80)
        print("✅ Done!")
        print("=" * 80)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generates knowledge_graph.json from text files in the data/ directory"
    )
    parser.add_argument(
        '--data-dir',
        type=Path,
        default=Path(__file__).parent / 'data',
        help='Directory with text files (default: ./data)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).parent / 'knowledge_graph_generated.json',
        help='Output JSON file (default: ./knowledge_graph_generated.json)'
    )
    
    args = parser.parse_args()
    
    # Validation
    if not args.data_dir.exists():
        print(f"❌ Error: Data directory not found: {args.data_dir}")
        return 1
    
    # Execute generator
    generator = KnowledgeGraphGenerator(args.data_dir, args.output)
    generator.run()
    
    return 0


if __name__ == '__main__':
    exit(main())
