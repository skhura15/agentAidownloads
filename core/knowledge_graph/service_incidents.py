# core/knowledge_graph/service_incidents.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.knowledge_graph.models.nodes import (
        IncidentNode,
        RootCauseNode,
        SymptomNode,
        ResolutionNode,
    )


class KnowledgeGraphIncidentsMixin:
    """
    Sub-graph 8: Incident Knowledge Graph

    Assumes the main service class provides:
      - self.tenant_id: str
      - self.db with execute_read / execute_write
      - create_node(label, node)
      - create_edge(... signature used in service.py)
    """

    # -------------------------
    # Core: Record Incident (with all edges)
    # -------------------------
    def record_incident(
        self,
        incident: "IncidentNode",
        root_causes: List["RootCauseNode"],
        symptoms: List["SymptomNode"],
        resolution: Optional["ResolutionNode"],
        affected_service_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Doc: record_incident(incident, root_causes, symptoms, resolution, affected_service_ids)
        Creates:
          - Incident node
          - RootCause nodes
          - Symptom nodes
          - optional Resolution node
          - Edges:
              Incident -[:AFFECTED_SERVICE]-> Service
              Incident -[:CAUSED_BY]-> RootCause
              Incident -[:EXHIBITED]-> Symptom
              Incident -[:RESOLVED_BY]-> Resolution (optional)
        Also:
          - auto-links similar incidents via SIMILAR_TO if similarity > 0.6
        """

        # 1) Merge Incident node
        inc_node = self.create_node("Incident", incident)

        # 2) Affected services edges (Incident -> Service)
        for sid in (affected_service_ids or []):
            self.create_edge(
                source_label="Incident",
                source_id_field="incident_id",
                source_id_value=incident.incident_id,
                target_label="Service",
                target_id_field="service_id",
                target_id_value=sid,
                relationship="AFFECTED_SERVICE",
                properties={},
            )

        # 2b) Customer impact edges (Customer -> Incident)
        impact_summary = self._link_impacted_customers_for_incident(
            incident_id=incident.incident_id,
            affected_service_ids=affected_service_ids,
        )


        # 3) Merge RootCause nodes + edges
        for rc in (root_causes or []):
            self._merge_root_cause_with_frequency_bump(rc)
            self.create_edge(
                source_label="Incident",
                source_id_field="incident_id",
                source_id_value=incident.incident_id,
                target_label="RootCause",
                target_id_field="root_cause_id",
                target_id_value=rc.root_cause_id,
                relationship="CAUSED_BY",
                properties={"confidence_score": float(getattr(rc, "avg_confidence", 0.0) or 0.0)},
            )

        # 4) Merge Symptom nodes + edges
        for s in (symptoms or []):
            self.create_node("Symptom", s)
            self.create_edge(
                source_label="Incident",
                source_id_field="incident_id",
                source_id_value=incident.incident_id,
                target_label="Symptom",
                target_id_field="symptom_id",
                target_id_value=s.symptom_id,
                relationship="EXHIBITED",
                properties={},
            )

        # 5) Merge Resolution + edge (optional)
        if resolution is not None:
            self.create_node("Resolution", resolution)
            self.create_edge(
                source_label="Incident",
                source_id_field="incident_id",
                source_id_value=incident.incident_id,
                target_label="Resolution",
                target_id_field="resolution_id",
                target_id_value=resolution.resolution_id,
                relationship="RESOLVED_BY",
                properties={"effectiveness_score": float(getattr(resolution, "effectiveness_score", 0.0) or 0.0)},
            )

        # 6) Auto-link similar incidents (symptom type overlap + affected service match)
        symptom_types = [getattr(x, "type", None) for x in (symptoms or [])]
        symptom_types = [str(x) for x in symptom_types if x is not None]

        primary_service = (affected_service_ids or [None])[0]
        if primary_service and symptom_types:
            sims = self.find_similar_incidents(
                symptoms=symptom_types,
                affected_service=primary_service,
                limit=5,
                exclude_incident_id=incident.incident_id,
            )
            for row in sims:
                if float(row.get("similarity_score", 0.0)) > 0.6:
                    self.link_similar_incidents(
                        incident_a=incident.incident_id,
                        incident_b=row["incident_id"],
                        similarity_score=float(row["similarity_score"]),
                        shared_symptoms=row.get("shared_symptoms", []),
                    )

        return {"incident": inc_node, "customer_impact": impact_summary,"incident_id": incident.incident_id}

    # -------------------------
    # Similar Incidents
    # -------------------------
    def find_similar_incidents(
        self,
        symptoms: List[str],
        affected_service: str,
        limit: int = 5,
        exclude_incident_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Doc: match by shared symptoms and service, rank by similarity.

        similarity_score = |intersection| / |union|   (Jaccard on symptom types)
        Only considers incidents that affected the same service_id.
        """

        limit = max(1, min(int(limit or 5), 50))
        symptoms = [str(s) for s in (symptoms or []) if str(s).strip()]
        if not symptoms:
            return []

        cypher = """
        MATCH (i:Incident {tenant_id:$tenant_id})-[:AFFECTED_SERVICE]->(svc:Service {tenant_id:$tenant_id, service_id:$service_id})
        WHERE ($exclude IS NULL OR i.incident_id <> $exclude)

        // symptoms for each incident
        OPTIONAL MATCH (i)-[:EXHIBITED]->(sym:Symptom {tenant_id:$tenant_id})
        WITH i, collect(DISTINCT sym.type) AS incident_symptom_types, $query_symptoms AS query_symptoms

        WITH i,
             incident_symptom_types,
             query_symptoms,
             [x IN incident_symptom_types WHERE x IN query_symptoms] AS intersection,
             apoc.coll.toSet(incident_symptom_types + query_symptoms) AS union_set

        WITH i,
             intersection,
             union_set,
             CASE
               WHEN size(union_set) = 0 THEN 0.0
               ELSE (toFloat(size(intersection)) / toFloat(size(union_set)))
             END AS similarity_score

        WHERE similarity_score > 0.0
        RETURN
          i.incident_id AS incident_id,
          i.title AS title,
          i.severity AS severity,
          i.status AS status,
          i.started_at AS started_at,
          i.resolved_at AS resolved_at,
          similarity_score AS similarity_score,
          intersection AS shared_symptoms
        ORDER BY similarity_score DESC, coalesce(i.started_at, "") DESC
        LIMIT $limit
        """

        params = {
            "tenant_id": self.tenant_id,
            "service_id": affected_service,
            "query_symptoms": symptoms,
            "exclude": exclude_incident_id,
            "limit": limit,
        }

        # NOTE: uses APOC (apoc.coll.toSet). Your docker compose enables APOC.
        rows = self.db.execute_read(cypher, params)
        return rows

    def link_similar_incidents(
        self,
        incident_a: str,
        incident_b: str,
        similarity_score: float,
        shared_symptoms: List[str],
    ) -> Dict[str, Any]:
        """
        Doc: link_similar_incidents(incident_a, incident_b, similarity_score, shared_symptoms)
        Creates SIMILAR_TO edge (both directions optional; here we do one direction).
        """
        similarity_score = float(similarity_score or 0.0)
        shared_symptoms = [str(s) for s in (shared_symptoms or [])]

        cypher = """
        MATCH (a:Incident {tenant_id:$tenant_id, incident_id:$a})
        MATCH (b:Incident {tenant_id:$tenant_id, incident_id:$b})
        MERGE (a)-[r:SIMILAR_TO]->(b)
        SET r.tenant_id = $tenant_id
        SET r.similarity_score = $similarity_score
        SET r.shared_symptoms = $shared_symptoms
        RETURN r AS rel
        """
        rows = self.db.execute_write(
            cypher,
            {
                "tenant_id": self.tenant_id,
                "a": incident_a,
                "b": incident_b,
                "similarity_score": similarity_score,
                "shared_symptoms": shared_symptoms,
            },
        )
        return rows[0]["rel"] if rows else {}

    # -------------------------
    # Incident history for a service
    # -------------------------
    def get_incident_history(self, service_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Doc: get_incident_history(service_id, limit)
        Chronological incident list for a service.
        """
        limit = max(1, min(int(limit or 20), 200))
        cypher = """
        MATCH (i:Incident {tenant_id:$tenant_id})-[:AFFECTED_SERVICE]->(s:Service {tenant_id:$tenant_id, service_id:$service_id})
        RETURN i AS incident
        ORDER BY coalesce(i.started_at, i.created_at, "") DESC
        LIMIT $limit
        """
        rows = self.db.execute_read(cypher, {"tenant_id": self.tenant_id, "service_id": service_id, "limit": limit})
        return [r["incident"] for r in rows]

    # -------------------------
    # Resolutions
    # -------------------------
    def get_resolution_for_root_cause(self, root_cause_category: str) -> List[Dict[str, Any]]:
        """
        Doc: get_resolution_for_root_cause(root_cause_category)
        Finds proven resolutions for incidents caused by a given root cause category.
        """
        cypher = """
        MATCH (i:Incident {tenant_id:$tenant_id})-[:CAUSED_BY]->(rc:RootCause {tenant_id:$tenant_id, category:$category})
        MATCH (i)-[:RESOLVED_BY]->(res:Resolution {tenant_id:$tenant_id})
        RETURN res AS resolution, count(DISTINCT i) AS incident_count
        ORDER BY coalesce(res.effectiveness_score, 0.0) DESC, incident_count DESC
        """
        rows = self.db.execute_read(cypher, {"tenant_id": self.tenant_id, "category": root_cause_category})
        return rows

    def get_most_effective_resolution(self, symptom_type: str) -> Optional[Dict[str, Any]]:
        """
        Doc: get_most_effective_resolution(symptom_type)
        Best resolution among incidents that exhibited this symptom type.
        """
        cypher = """
        MATCH (i:Incident {tenant_id:$tenant_id})-[:EXHIBITED]->(sym:Symptom {tenant_id:$tenant_id, type:$symptom_type})
        MATCH (i)-[:RESOLVED_BY]->(res:Resolution {tenant_id:$tenant_id})
        RETURN res AS resolution, avg(coalesce(res.effectiveness_score, 0.0)) AS avg_effectiveness, count(DISTINCT i) AS used_in
        ORDER BY avg_effectiveness DESC, used_in DESC
        LIMIT 1
        """
        rows = self.db.execute_read(cypher, {"tenant_id": self.tenant_id, "symptom_type": symptom_type})
        return rows[0] if rows else None

    def update_resolution_effectiveness(self, resolution_id: str, success: bool) -> Dict[str, Any]:
        """
        Doc: increment success_count/failure_count and recalc effectiveness_score.
        effectiveness_score = success_count / (success_count + failure_count)
        """
        cypher = """
        MATCH (r:Resolution {tenant_id:$tenant_id, resolution_id:$resolution_id})
        SET r.success_count = coalesce(r.success_count, 0) + CASE WHEN $success THEN 1 ELSE 0 END,
            r.failure_count = coalesce(r.failure_count, 0) + CASE WHEN $success THEN 0 ELSE 1 END
        WITH r,
             toFloat(coalesce(r.success_count, 0)) AS s,
             toFloat(coalesce(r.failure_count, 0)) AS f
        SET r.effectiveness_score =
          CASE WHEN (s + f) = 0 THEN 0.0 ELSE (s / (s + f)) END
        RETURN r AS resolution
        """
        rows = self.db.execute_write(
            cypher,
            {"tenant_id": self.tenant_id, "resolution_id": resolution_id, "success": bool(success)},
        )
        return rows[0]["resolution"] if rows else {}

    # -------------------------
    # Helpers
    # -------------------------
    def _merge_root_cause_with_frequency_bump(self, root_cause: "RootCauseNode") -> Dict[str, Any]:
        """
        The doc says RootCause should MERGE and increment frequency if it already exists.
        We'll do that explicitly here.
        """
        props = root_cause.to_neo4j_properties()
        props["tenant_id"] = self.tenant_id

        cypher = """
        MERGE (rc:RootCause {tenant_id:$tenant_id, root_cause_id:$root_cause_id})
        ON CREATE SET rc += $props,
                      rc.frequency = coalesce(rc.frequency, 1)
        ON MATCH  SET rc += $props,
                      rc.frequency = coalesce(rc.frequency, 0) + 1
        RETURN rc AS root_cause
        """
        rows = self.db.execute_write(
            cypher,
            {
                "tenant_id": self.tenant_id,
                "root_cause_id": props["root_cause_id"],
                "props": props,
            },
        )
        return rows[0]["root_cause"] if rows else {}
    

    def _link_impacted_customers_for_incident(
        self,
        incident_id: str,
        affected_service_ids: List[str],
        impact_level: str = "unknown",
        notified: bool = False,
        compensation_required: bool = False,
    ) -> Dict[str, Any]:
        """
        Creates Customer -[:IMPACTED_BY]-> Incident edges based on affected services.

        Uses existing business method:
        - self.get_affected_customers(service_id)

        Returns a small summary with counts.
        """
        impacted_customer_ids: set[str] = set()

        for sid in (affected_service_ids or []):
            rows = self.get_affected_customers(sid)  # returns [{"customer": {...}, "usage": {...}}, ...]
            for r in rows or []:
                cust = r.get("customer") or {}
                cid = cust.get("customer_id")
                if cid:
                    impacted_customer_ids.add(cid)

        # Create edges (idempotent MERGE via create_edge)
        for cid in sorted(impacted_customer_ids):
            self.create_edge(
                source_label="Customer",
                source_id_field="customer_id",
                source_id_value=cid,
                target_label="Incident",
                target_id_field="incident_id",
                target_id_value=incident_id,
                relationship="IMPACTED_BY",
                properties={
                    "impact_level": impact_level,
                    "notified": bool(notified),
                    "compensation_required": bool(compensation_required),
                },
            )

        return {"impacted_customers_count": len(impacted_customer_ids), "impacted_customer_ids": sorted(impacted_customer_ids)}
    
    #later for API's

    def get_customers_impacted_by_incident(self, incident_id: str) -> List[Dict[str, Any]]:
        cypher = """
        MATCH (c:Customer {tenant_id:$tenant_id})-[r:IMPACTED_BY {tenant_id:$tenant_id}]->(i:Incident {tenant_id:$tenant_id, incident_id:$incident_id})
        RETURN c AS customer, properties(r) AS impact
        ORDER BY coalesce(c.vip, false) DESC, c.tier DESC, c.name ASC
        """
        rows = self.db.execute_read(cypher, {"tenant_id": self.tenant_id, "incident_id": incident_id})
        return rows


    def get_incidents_for_customer(self, customer_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        limit = max(1, min(int(limit or 20), 200))
        cypher = """
        MATCH (c:Customer {tenant_id:$tenant_id, customer_id:$customer_id})-[r:IMPACTED_BY {tenant_id:$tenant_id}]->(i:Incident {tenant_id:$tenant_id})
        RETURN i AS incident, properties(r) AS impact
        ORDER BY coalesce(i.started_at, i.created_at, "") DESC
        LIMIT $limit
        """
        rows = self.db.execute_read(
            cypher,
            {"tenant_id": self.tenant_id, "customer_id": customer_id, "limit": limit},
        )
        return rows


