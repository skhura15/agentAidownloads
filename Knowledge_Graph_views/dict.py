import json
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Tuple, Union, Optional
from datetime import datetime

NODE_TYPES = [
    "Product", "Service", "SPO", "ReleaseNote", "UserGuide",
    "KnownIssue", "Runbook", "SOP", "Incident", "Expert",
    "Team", "Customer", "Infrastructure", "Configuration", "FAQ", "Feature"
]

EDGE_RULES: Dict[Tuple[str, str], Union[str, List[str]]] = {
    # Product edges
    ("Product", "HAS_SERVICE"): "Service",
    ("Product", "BELONGS_TO_SPO"): "SPO",
    ("Product", "HAS_RELEASE_NOTE"): "ReleaseNote",
    ("Product", "HAS_SOP"): "SOP",
    ("Product", "HAS_FEATURE"): "Feature",
    
    # Service edges
    ("Service", "RUNS_ON"): "Infrastructure",
    ("Service", "CONFIGURED_BY"): "Configuration",
    ("Service", "DEPENDS_ON"): ["Service", "Infrastructure"],
    ("Service", "DOCUMENTED_IN"): "UserGuide",
    ("Service", "HAS_KNOWN_ISSUE"): "KnownIssue",
    ("Service", "HAS_RUNBOOK"): "Runbook",
    ("Service", "HAS_FAQ"): "FAQ",
    ("Service", "HAS_FEATURE"): "Feature",
    
    # KnownIssue edges
    ("KnownIssue", "FIXED_IN"): "ReleaseNote",
    ("KnownIssue", "WORKAROUND_IN"): "Configuration",
    ("KnownIssue", "RELATED_TO"): ["Incident", "Runbook", "UserGuide", "Configuration"],
    
    # Customer edges
    ("Customer", "REPORTED_INCIDENT"): "Incident",
    ("Customer", "SUBSCRIBES_TO"): "SPO",
    
    # Incident edges
    ("Incident", "IMPACTED_BY"): "Service",
    ("Incident", "RESOLVED_BY"): "Runbook",
    ("Incident", "ASSIGNED_TO"): "Expert",
    ("Incident", "RELATED_TO"): ["KnownIssue", "Runbook", "Configuration", "UserGuide"],
    
    # Runbook edges
    ("Runbook", "RELATED_TO"): ["Configuration", "UserGuide", "KnownIssue"],
    
    # Team edges
    ("Team", "OWNS"): "Service",
    ("Team", "ASSIGNED_TO"): "Expert",
    
    # SOP edges
    ("SOP", "ESCALATES_TO"): "Team",
    
    # SPO edges
    ("SPO", "HAS_SERVICE"): "Service",
}


def get_all_edge_types() -> List[str]:
    """Extract all unique edge types from EDGE_RULES."""
    edge_types = set()
    for (src_type, edge_type), _ in EDGE_RULES.items():
        edge_types.add(edge_type)
    return sorted(list(edge_types))


def generate_metadata(nodes: List[Dict[str, Any]], edges: List[Dict[str, str]], 
                     graph_name: str = "Microsoft CCaaS — Support AI Knowledge Graph",
                     product: str = "Microsoft Dynamics 365 Contact Center (CCaaS)") -> Dict[str, Any]:
    """Generate metadata section for the knowledge graph."""
    return {
        "graph_name": graph_name,
        "version": "2.0.0",
        "description": "Knowledge graph for Support AI Agent to resolve Microsoft Dynamics 365 Contact Center (CCaaS) tickets. Covers services, SPOs, release notes, user guides, known issues, runbooks, SOPs, incidents, experts, and customers.",
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "product": product,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "schema_version": "v2"
    }


def get_ai_agent_instructions() -> Dict[str, Any]:
    """Generate AI agent instructions for using the knowledge graph."""
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


def extract_zip(zip_path: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(dest_dir)


def detect_node_type_from_filename(filename: str) -> Optional[str]:
    # Example accepted:
    # Product.json, Product_001.json, Product-MS.json
    base = Path(filename).name
    for nt in NODE_TYPES:
        if base.startswith(nt):
            return nt
    return None


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_id_index(nodes: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    idx = {}
    for n in nodes:
        nid = n.get("id")
        if not nid:
            raise ValueError(f"Node missing 'id': {n}")
        if nid in idx:
            raise ValueError(f"Duplicate node id found: {nid}")
        idx[nid] = n
    return idx


def allowed_target_types(src_type: str, edge_type: str) -> List[str]:
    rule = EDGE_RULES.get((src_type, edge_type))
    if rule is None:
        return []
    return rule if isinstance(rule, list) else [rule]


def generate_edges(nodes: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    id_index = build_id_index(nodes)
    edges: List[Dict[str, str]] = []

    for n in nodes:
        src_id = n["id"]
        src_type = n.get("type")
        # Check both 'relations' and '_relations' for backward compatibility
        rels = (n.get("relations") or n.get("_relations") or {})

        if not src_type:
            raise ValueError(f"Node {src_id} missing 'type'")

        for edge_type, targets in rels.items():
            if not isinstance(targets, list):
                raise ValueError(f"Node {src_id} relations.{edge_type} must be a list")

            valid_target_types = allowed_target_types(src_type, edge_type)
            if not valid_target_types:
                # Unknown / disallowed edge type for this source type
                # You can choose: skip OR raise error. I'm skipping but logging would be ideal.
                continue

            for tgt_id in targets:
                if tgt_id not in id_index:
                    # target missing in this scenario dataset
                    # choose: skip or raise; usually skip with warning
                    continue

                tgt_type = id_index[tgt_id].get("type")
                if tgt_type not in valid_target_types:
                    # violates dictionary map constraint
                    continue

                edges.append({"source": src_id, "target": tgt_id, "type": edge_type})

    # Optional: de-duplicate edges
    dedup = {}
    for e in edges:
        key = (e["source"], e["target"], e["type"])
        dedup[key] = e
    return list(dedup.values())


def transform_node_to_schema(node: Dict[str, Any]) -> Dict[str, Any]:
    """Transform node structure to match knowledge_graph.json schema.
    
    Converts relations to separate tracking and ensures properties/tags structure.
    """
    node_id = node.get("id")
    node_type = node.get("type")
    label = node.get("label", node_id)
    
    # Extract relations for edge generation (will be removed from final node)
    relations = node.get("relations", {})
    
    # Extract properties and tags
    properties = node.get("properties", {})
    tags = node.get("tags", [])
    
    # Build the compliant node structure
    transformed = {
        "id": node_id,
        "type": node_type,
        "label": label,
        "properties": properties,
        "tags": tags
    }
    
    # Store relations separately for edge generation
    if relations:
        transformed["_relations"] = relations
    
    return transformed


def load_scenario_nodes(scenario_dir: Path) -> List[Dict[str, Any]]:
    nodes: List[Dict[str, Any]] = []

    # scan all json files
    for p in scenario_dir.rglob("*.json"):
        nt = detect_node_type_from_filename(p.name)
        if not nt:
            continue

        data = load_json(p)

        # Normalize / enforce minimum schema
        # If the file doesn't contain type, set it from filename prefix
        data.setdefault("type", nt)

        # If id is missing, you can infer from filename (optional)
        if "id" not in data:
            # Example inference: Service_SVC-001.json -> id=SVC-001
            stem = p.stem  # filename without extension
            parts = stem.split("_")
            if len(parts) >= 2:
                data["id"] = parts[1]

        if "id" not in data:
            raise ValueError(f"Could not determine id for file: {p}")

        # Ensure label exists
        data.setdefault("label", data["id"])

        # Ensure relations exists (empty is ok) - will be used for edge generation
        data.setdefault("relations", {})
        
        # Ensure properties and tags exist
        data.setdefault("properties", {})
        data.setdefault("tags", [])

        nodes.append(data)

    return nodes


def process_kgdata(kg_zip: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir = output_dir / "_work"
    work_dir.mkdir(parents=True, exist_ok=True)

    # 1) Extract KGData.zip
    kg_root = work_dir / "KGData_extracted"
    extract_zip(kg_zip, kg_root)

    # 2) Find scenario zips
    scenario_zips = sorted(kg_root.rglob("Scenario*.zip"))
    if not scenario_zips:
        raise ValueError("No Scenario*.zip files found inside KGData.zip")

    for scen_zip in scenario_zips:
        scen_name = scen_zip.stem  # Scenario1, Scenario2...
        scen_dir = work_dir / scen_name
        extract_zip(scen_zip, scen_dir)

        # Load nodes
        nodes = load_scenario_nodes(scen_dir)
        
        # Generate edges from relations
        edges = generate_edges(nodes)
        
        # Transform nodes to compliant schema (removes _relations)
        transformed_nodes = []
        for node in nodes:
            transformed = transform_node_to_schema(node)
            # Remove internal _relations field from final output
            if "_relations" in transformed:
                del transformed["_relations"]
            transformed_nodes.append(transformed)
        
        # Build compliant knowledge graph structure
        graph = {
            "metadata": generate_metadata(transformed_nodes, edges, 
                                         graph_name=f"Knowledge Graph - {scen_name}"),
            "node_types": NODE_TYPES,
            "edge_types": get_all_edge_types(),
            "nodes": transformed_nodes,
            "edges": edges,
            "ai_agent_instructions": get_ai_agent_instructions()
        }
        
        out_path = output_dir / f"{scen_name}_graph.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)

        print(f"[OK] {scen_name}: nodes={len(transformed_nodes)}, edges={len(edges)} -> {out_path}")


if __name__ == "__main__":
    # Example usage:
    # python build_graph.py KGData.zip out
    import sys
    if len(sys.argv) < 3:
        print("Usage: python build_graph.py <KGData.zip> <output_dir>")
        raise SystemExit(1)

    process_kgdata(Path(sys.argv[1]), Path(sys.argv[2]))
