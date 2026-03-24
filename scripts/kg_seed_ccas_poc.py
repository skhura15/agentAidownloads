# scripts/kg_seed_ccas_poc.py
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any, Dict

from core.knowledge_graph.service import KnowledgeGraphService
from core.knowledge_graph.schema import UNIQUE_KEY_BY_LABEL


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_node_label(node_type: str) -> str:
    """
    Use JSON type directly as label.
    Only minimal aliasing for known special cases.
    """
    if not node_type:
        raise ValueError("Node type missing")

    t = node_type.strip()

    # Minimal aliases only
    if t == "ReleaseNote":
        return "Release"

    if t == "UserGuide":
        return "Document"

    if t == "SPO":
        return "Document"

    if t == "Expert":
        return "Engineer"

    if t == "Infrastructure":
        return "Deployment"

    if t == "Configuration":
        return "FeatureFlag"

    return t


def _get_unique_key(label: str) -> str:
    key = UNIQUE_KEY_BY_LABEL.get(label)
    if not key:
        raise ValueError(
            f"Label '{label}' missing from UNIQUE_KEY_BY_LABEL in schema.py"
        )
    return key


def _merge_node(
    kg: KnowledgeGraphService,
    label: str,
    unique_key: str,
    node_id: str,
    props: Dict[str, Any],
):
    now = _utc_now_iso()
    p = dict(props or {})
    p.setdefault("created_at", now)
    p["updated_at"] = now

    # ✅ critical: avoid re-setting unique keys / tenant_id
    p.pop(unique_key, None)
    p.pop("tenant_id", None)

    cypher = f"""
    MERGE (n:{label} {{ tenant_id: $tenant_id, {unique_key}: $node_id }})
    ON CREATE SET n.created_at = $created_at
    SET n += $props,
        n.updated_at = $updated_at
    """

    kg.db.execute_write(
        cypher,
        {
            "tenant_id": kg.tenant_id,
            "node_id": node_id,
            "created_at": p.get("created_at"),
            "updated_at": p.get("updated_at"),
            "props": p,
        },
    )


def _merge_edge(
    kg: KnowledgeGraphService,
    src_label: str,
    src_key: str,
    src_id: str,
    dst_label: str,
    dst_key: str,
    dst_id: str,
    rel: str,
    props: Dict[str, Any],
):
    now = _utc_now_iso()
    p = dict(props or {})
    p.setdefault("created_at", now)
    p["updated_at"] = now

    cypher = f"""
    MATCH (a:{src_label} {{ tenant_id: $tenant_id, {src_key}: $src_id }})
    MATCH (b:{dst_label} {{ tenant_id: $tenant_id, {dst_key}: $dst_id }})
    MERGE (a)-[r:{rel} {{ tenant_id: $tenant_id }}]->(b)
    ON CREATE SET r.created_at = $created_at
    SET r += $props,
        r.updated_at = $updated_at
    """

    kg.db.execute_write(
        cypher,
        {
            "tenant_id": kg.tenant_id,
            "src_id": src_id,
            "dst_id": dst_id,
            "created_at": p.get("created_at"),
            "updated_at": p.get("updated_at"),
            "props": p,
        },
    )


def main():
    parser = argparse.ArgumentParser(description="Seed CCaaS Knowledge Graph into Neo4j")
    parser.add_argument("--tenant-id", default="tenant_demo")
    parser.add_argument("--kg-json", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    with open(args.kg_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    kg = KnowledgeGraphService(args.tenant_id)

    node_index = {}

    # ---------------------
    # NODES
    # ---------------------
    for n in nodes:
        node_id = n.get("id")
        node_type = n.get("type")
        props = n.get("properties", {})

        label = _normalize_node_label(node_type)
        unique_key = _get_unique_key(label)

        # Ensure business id property exists
        props = dict(props)
        props.setdefault(unique_key, node_id)

        node_index[node_id] = (label, unique_key)

        if not args.dry_run:
            _merge_node(kg, label, unique_key, node_id, props)

    # ---------------------
    # EDGES
    # ---------------------
    for e in edges:
        src = e.get("source")
        dst = e.get("target")
        rel = e.get("type")
        props = e.get("properties", {})

        if src not in node_index or dst not in node_index:
            continue

        src_label, src_key = node_index[src]
        dst_label, dst_key = node_index[dst]

        if not args.dry_run:
            _merge_edge(
                kg,
                src_label,
                src_key,
                src,
                dst_label,
                dst_key,
                dst,
                rel,
                props,
            )

    print(
        {
            "ok": True,
            "tenant_id": args.tenant_id,
            "nodes_in_file": len(nodes),
            "edges_in_file": len(edges),
            "dry_run": args.dry_run,
        }
    )


if __name__ == "__main__":
    main()