# core/knowledge_graph/service.py
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from core.knowledge_graph.db import get_graph_db
from core.knowledge_graph.models.base import GraphNode
from core.knowledge_graph.schema import UNIQUE_KEY_BY_LABEL
from core.knowledge_graph.service_business import KnowledgeGraphBusinessMixin
from core.knowledge_graph.service_incidents import KnowledgeGraphIncidentsMixin
from core.knowledge_graph.service_context import KnowledgeGraphContextMixin
from core.knowledge_graph.service_sop import KnowledgeGraphSOPMixin
from core.knowledge_graph.service_runbooks import KnowledgeGraphRunbooksMixin
from core.knowledge_graph.service_docs import KnowledgeGraphDocsMixin
from core.knowledge_graph.service_ccas import KnowledgeGraphCCaaSMixin
from core.knowledge_graph.issue_router import resolve_known_issue_from_text

logger = logging.getLogger(__name__)


class KnowledgeGraphService(KnowledgeGraphBusinessMixin,
                            KnowledgeGraphIncidentsMixin,
                            KnowledgeGraphContextMixin,
                            KnowledgeGraphSOPMixin,
                            KnowledgeGraphDocsMixin,
                            KnowledgeGraphRunbooksMixin,
                            KnowledgeGraphCCaaSMixin,):
    """
    Tenant-scoped Knowledge Graph service.
    All queries MUST include tenant isolation filter.
    """

    _SAFE_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    def __init__(self, tenant_id: str) -> None:
        self.tenant_id = tenant_id
        self.db = get_graph_db()
        

    def _validate_name(self, value: str, kind: str) -> None:
        if not self._SAFE_NAME_RE.match(value or ""):
            raise ValueError(f"Invalid {kind}: {value}")

    # -------------------------
    # Generic CRUD
    # -------------------------
    def create_node(self, label: str, node: GraphNode) -> Dict[str, Any]:
        """
        STRICT MERGE on (tenant_id + business-id).
        No fallback to node_id.
        """

        props = node.to_neo4j_properties()
        props["tenant_id"] = self.tenant_id

        if label not in UNIQUE_KEY_BY_LABEL:
            raise ValueError(
                f"Label '{label}' missing business-id mapping in schema.py"
            )

        business_key = UNIQUE_KEY_BY_LABEL[label]

        if business_key not in props or not props[business_key]:
            raise ValueError(
                f"Missing required business id '{business_key}' for label '{label}'"
            )

        cypher = f"""
        MERGE (n:{label} {{ tenant_id: $tenant_id, {business_key}: $business_value }})
        SET n += $props,
            n.updated_at = $updated_at
        RETURN n AS node
        """

        params = {
            "tenant_id": self.tenant_id,
            "business_value": props[business_key],
            "props": props,
            "updated_at": props.get("updated_at"),
        }

        rows = self.db.execute_write(cypher, params)
        return rows[0]["node"] if rows else {}

    def create_edge(
        self,
        source_label: str,
        source_id_field: str,
        source_id_value: str,
        target_label: str,
        target_id_field: str,
        target_id_value: str,
        relationship: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        properties = dict(properties or {})
        properties["tenant_id"] = self.tenant_id

        self._validate_name(source_label, "label")
        self._validate_name(target_label, "label")
        self._validate_name(source_id_field, "property name")
        self._validate_name(target_id_field, "property name")
        self._validate_name(relationship, "relationship type")

        if source_label not in UNIQUE_KEY_BY_LABEL:
            raise ValueError(f"{source_label} missing business-id mapping")
        if target_label not in UNIQUE_KEY_BY_LABEL:
            raise ValueError(f"{target_label} missing business-id mapping")

        # relationship type cannot be parameterized; keep it safe
        if not relationship.isidentifier():
            raise ValueError(f"Invalid relationship type: {relationship}")

        cypher = f"""
        MATCH (a:{source_label} {{ tenant_id: $tenant_id, {source_id_field}: $source_id }})
        MATCH (b:{target_label} {{ tenant_id: $tenant_id, {target_id_field}: $target_id }})
        MERGE (a)-[r:{relationship}]->(b)
        SET r.tenant_id = $tenant_id
        SET r += $props
        RETURN r AS rel
        """
        params = {
            "tenant_id": self.tenant_id,
            "source_id": source_id_value,
            "target_id": target_id_value,
            "props": properties,
        }
        rows = self.db.execute_write(cypher, params)
        return rows[0]["rel"] if rows else {}


    def delete_node(self, label: str, id_field: str, id_value: str) -> bool:
        cypher = f"""
        MATCH (n:{label} {{ tenant_id: $tenant_id, {id_field}: $id_value }})
        DETACH DELETE n
        """
        self.db.execute_write(cypher, {"tenant_id": self.tenant_id, "id_value": id_value})
        return True

    def get_node(self, label: str, id_field: str, id_value: str) -> Optional[Dict[str, Any]]:
        cypher = f"""
        MATCH (n:{label} {{ tenant_id: $tenant_id, {id_field}: $id_value }})
        RETURN n AS node
        LIMIT 1
        """
        rows = self.db.execute_read(cypher, {"tenant_id": self.tenant_id, "id_value": id_value})
        return rows[0]["node"] if rows else None

    def search_nodes(self, label: str, filters: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
        self._validate_name(label, "label")
        where = ["n.tenant_id = $tenant_id"]
        params: Dict[str, Any] = {"tenant_id": self.tenant_id, "limit": limit}

        for i, (k, v) in enumerate(filters.items()):
            self._validate_name(k, "property name")
            param_key = f"p{i}"
            where.append(f"n.{k} = ${param_key}")
            params[param_key] = v

        cypher = f"""
        MATCH (n:{label})
        WHERE {" AND ".join(where)}
        RETURN n AS node
        LIMIT $limit
        """
        rows = self.db.execute_read(cypher, params)
        return [r["node"] for r in rows]

    # -------------------------
    # Sub-graph 7: Service & Infra
    # -------------------------
    def ingest_services(self, services_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Two-pass ingestion:
        Pass 1 → create all Service nodes
        Pass 2 → create dependency edges
        """

        created = 0
        edges = 0

        # -------------------------
        # PASS 1 — CREATE NODES
        # -------------------------
        for svc in services_data:
            node_props = {
                "tenant_id": self.tenant_id,
                "service_id": svc["service_id"],
                "name": svc.get("name", svc["service_id"]),
                "description": svc.get("description"),
                "owner_team": svc.get("owner_team"),
                "criticality": svc.get("criticality"),
                "environment": svc.get("environment"),
                "status": svc.get("status"),
                "slo_target": svc.get("slo_target"),
                "sla_target": svc.get("sla_target"),
                "business_impact": svc.get("business_impact"),
                "tags": svc.get("tags"),
            }

            cypher = """
            MERGE (s:Service {tenant_id: $tenant_id, service_id: $service_id})
            SET s += $props
            RETURN s
            """

            self.db.execute_write(
                cypher,
                {
                    "tenant_id": self.tenant_id,
                    "service_id": svc["service_id"],
                    "props": node_props,
                },
            )

            created += 1
        
    

        # -------------------------
        # PASS 2 — CREATE EDGES
        # -------------------------
        for svc in services_data:
            for dep in svc.get("depends_on", []):

                rel_props = {
                    "dependency_type": dep.get("dependency_type", "unknown"),
                    "is_critical": bool(dep.get("is_critical", False)),
                    "weight": float(dep.get("weight", 1.0)),
                }

                edge_cypher = """
                MATCH (a:Service {tenant_id: $tenant_id, service_id: $src})
                MATCH (b:Service {tenant_id: $tenant_id, service_id: $dst})
                MERGE (a)-[r:DEPENDS_ON]->(b)
                SET r.tenant_id = $tenant_id
                SET r += $props
                RETURN count(r) AS c
                """

                rows = self.db.execute_write(
                    edge_cypher,
                    {
                        "tenant_id": self.tenant_id,
                        "src": svc["service_id"],
                        "dst": dep["service_id"],
                        "props": rel_props,
                    },
                )

                if not rows or rows[0]["c"] == 0:
                    raise RuntimeError(
                        f"Edge not created: {svc['service_id']} -> {dep['service_id']}"
                    )

                edges += 1

        return {
            "services_processed": created,
            "dependency_edges_processed": edges,
        }
    
    def add_service(self, service: GraphNode) -> Dict[str, Any]:
        """Doc: add_service(service: ServiceNode) — create/update one service."""
        return self.create_node("Service", service)


    def add_dependency(
        self,
        from_service_id: str,
        to_service_id: str,
        dependency_type: str = "unknown",
        is_critical: bool = False,
        weight: float = 1.0,
    ) -> Dict[str, Any]:
        """Doc: add_dependency(from_service_id, to_service_id, dependency_type, is_critical)."""
        cypher = """
        MATCH (a:Service {tenant_id:$tenant_id, service_id:$src})
        MATCH (b:Service {tenant_id:$tenant_id, service_id:$dst})
        MERGE (a)-[r:DEPENDS_ON]->(b)
        SET r.tenant_id = $tenant_id
        SET r.dependency_type = $dependency_type
        SET r.is_critical = $is_critical
        SET r.weight = $weight
        RETURN r AS rel
        """
        rows = self.db.execute_write(
            cypher,
            {
                "tenant_id": self.tenant_id,
                "src": from_service_id,
                "dst": to_service_id,
                "dependency_type": dependency_type,
                "is_critical": bool(is_critical),
                "weight": float(weight),
            },
        )
        return rows[0]["rel"] if rows else {}


    def remove_dependency(self, from_service_id: str, to_service_id: str) -> bool:
        """Doc: remove_dependency(from_service_id, to_service_id)."""
        cypher = """
        MATCH (:Service {tenant_id:$tenant_id, service_id:$src})-[r:DEPENDS_ON]->(:Service {tenant_id:$tenant_id, service_id:$dst})
        DELETE r
        RETURN count(r) AS deleted
        """
        rows = self.db.execute_write(
            cypher,
            {"tenant_id": self.tenant_id, "src": from_service_id, "dst": to_service_id},
        )
        return bool(rows and rows[0]["deleted"] > 0)


    def get_full_dependency_graph(self) -> Dict[str, Any]:
        """Doc: get_full_dependency_graph() — return nodes + edges for visualization."""
        nodes_cypher = """
        MATCH (s:Service {tenant_id:$tenant_id})
        RETURN s AS node
        ORDER BY coalesce(s.name, s.service_id)
        """
        edges_cypher = """
        MATCH (a:Service {tenant_id:$tenant_id})-[r:DEPENDS_ON]->(b:Service {tenant_id:$tenant_id})
        RETURN a.service_id AS source, b.service_id AS target, r AS rel
        """

        node_rows = self.db.execute_read(nodes_cypher, {"tenant_id": self.tenant_id})
        edge_rows = self.db.execute_read(edges_cypher, {"tenant_id": self.tenant_id})

        nodes = [r["node"] for r in node_rows]
        edges = [
            {
                "source": r["source"],
                "target": r["target"],
                "relationship": "DEPENDS_ON",
                "properties": r["rel"],
            }
            for r in edge_rows
        ]

        return {"nodes": nodes, "edges": edges}



    def get_service_dependencies(self, service_id: str, depth: int = 3) -> List[Dict[str, Any]]:
        depth = max(1, min(depth, 10))  # safety clamp

        cypher = f"""
        MATCH (s:Service {{tenant_id:$tenant_id, service_id:$service_id}})
        CALL (s) {{
        MATCH p=(s)-[:DEPENDS_ON*1..{depth}]->(d:Service {{tenant_id:$tenant_id}})
        RETURN d AS service, min(length(p)) AS hops
        }}
        RETURN service, hops
        ORDER BY hops ASC
        """


        rows = self.db.execute_read(
            cypher,
            {
                "tenant_id": self.tenant_id,
                "service_id": service_id,
            },
        )

        return [{"service": r["service"], "hops": r["hops"]} for r in rows]


    def get_dependents(self, service_id: str, depth: int = 3) -> List[Dict[str, Any]]:
        depth = max(1, min(depth, 10))  # safety clamp

        cypher = f"""
        MATCH (s:Service {{tenant_id:$tenant_id, service_id:$service_id}})
        CALL (s) {{
        MATCH p=(u:Service {{tenant_id:$tenant_id}})-[:DEPENDS_ON*1..{depth}]->(s)
        RETURN u AS service, min(length(p)) AS hops
        }}
        RETURN service, hops
        ORDER BY hops ASC
        """

        rows = self.db.execute_read(
            cypher,
            {
                "tenant_id": self.tenant_id,
                "service_id": service_id,
            },
        )

        return [{"service": r["service"], "hops": r["hops"]} for r in rows]
    
    def resolve_known_issue_from_message(self, message: str, limit: int = 3) -> Dict[str, Any]:
    
        return resolve_known_issue_from_text(self, message=message, limit=limit)


    # def get_blast_radius(self, service_id: str, depth: int = 3) -> Dict[str, Any]:
    #     """
    #     Per doc: should eventually include upstream services + customer impact + SLA exposure.
    #     Today returns upstream services + downstream deps (foundation). You can expand after customer graph is wired.
    #     """
    #     dependents = self.get_dependents(service_id, depth=depth)
    #     dependencies = self.get_service_dependencies(service_id, depth=depth)
    #     return {
    #         "service_id": service_id,
    #         "upstream_dependents": dependents,
    #         "downstream_dependencies": dependencies,
    #     }
