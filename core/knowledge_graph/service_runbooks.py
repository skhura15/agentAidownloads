# core/knowledge_graph/service_runbooks.py
from __future__ import annotations

from typing import Any, Dict, List, Optional


class KnowledgeGraphRunbooksMixin:
    """
    Subgraph 2: Runbook & Troubleshooting

    Implements the Task-3 required operations:
      - add_runbook()
      - find_runbook_for_incident()
      - add_workaround()
      - find_workarounds()
      - record_runbook_execution()

    Notes:
      - We model "applicable symptom" as a stable Symptom node with symptom_id = "scenario::<type>"
        (same approach as SOP) so we can link runbooks to symptom types deterministically.
      - We keep this file focused on Task-3 scope; richer DecisionNode/DiagnosticCommand modeling can be added later.
    """

    # -------------------------
    # Runbooks
    # -------------------------
    def add_runbook(
        self,
        runbook: Any,
        applicable_services: List[str],
        applicable_symptoms: List[str],
    ) -> Dict[str, Any]:
        """
        Creates:
          (:Runbook)
          (:Runbook)-[:APPLIES_TO_SERVICE]->(:Service)
          (:Runbook)-[:ADDRESSES_SYMPTOM]->(:Symptom)  (symptom types via scenario::<type>)
        """
        # 1) Runbook node
        self.create_node("Runbook", runbook)

        # 2) Applies to services
        for sid in (applicable_services or []):
            sid = str(sid).strip()
            if not sid:
                continue
            self.create_edge(
                source_label="Runbook",
                source_id_field="runbook_id",
                source_id_value=runbook.runbook_id,
                target_label="Service",
                target_id_field="service_id",
                target_id_value=sid,
                relationship="APPLIES_TO_SERVICE",
                properties={},
            )

        # 3) Addresses symptoms (store as Symptom nodes with stable IDs)
        for symptom_type in (applicable_symptoms or []):
            symptom_type = str(symptom_type).strip()
            if not symptom_type:
                continue

            symptom_id = f"scenario::{symptom_type}"
            self._ensure_scenario_symptom(symptom_id=symptom_id, symptom_type=symptom_type)

            self.create_edge(
                source_label="Runbook",
                source_id_field="runbook_id",
                source_id_value=runbook.runbook_id,
                target_label="Symptom",
                target_id_field="symptom_id",
                target_id_value=symptom_id,
                relationship="ADDRESSES_SYMPTOM",
                properties={"effectiveness_score": None},
            )

        return {"ok": True, "runbook_id": runbook.runbook_id}

    def find_runbook_for_incident(
        self,
        symptoms: List[str],
        service_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Ranked runbook search:
          - must apply to service
          - must address >=1 of the provided symptom types
        Sort by:
          - success_rate desc
          - times_used desc
        """
        limit = max(1, min(int(limit or 10), 50))
        service_id = str(service_id).strip()
        symptom_ids = [f"scenario::{str(s).strip()}" for s in (symptoms or []) if str(s).strip()]

        cypher = """
        MATCH (rb:Runbook {tenant_id:$tenant_id})
              -[:APPLIES_TO_SERVICE {tenant_id:$tenant_id}]->
              (svc:Service {tenant_id:$tenant_id, service_id:$service_id})

        OPTIONAL MATCH (rb)-[:ADDRESSES_SYMPTOM {tenant_id:$tenant_id}]->(sym:Symptom {tenant_id:$tenant_id})
        WITH rb, collect(distinct sym.symptom_id) AS addressed_symptom_ids

        WITH rb,
             [sid IN $symptom_ids WHERE sid IN addressed_symptom_ids] AS matched_symptoms
        WHERE size(matched_symptoms) > 0

        RETURN
            rb AS runbook,
            matched_symptoms AS matched_symptoms
        ORDER BY
            coalesce(rb.success_rate, 0.0) DESC,
            coalesce(rb.times_used, 0) DESC,
            coalesce(rb.last_used, rb.last_updated, rb.created_at, "") DESC
        LIMIT $limit
        """

        return self.db.execute_read(
            cypher,
            {
                "tenant_id": self.tenant_id,
                "service_id": service_id,
                "symptom_ids": symptom_ids,
                "limit": limit,
            },
        )

    def record_runbook_execution(
        self,
        runbook_id: str,
        incident_id: str,
        success: bool,
        duration_seconds: float,
    ) -> Dict[str, Any]:
        """
        Creates:
          (:Runbook)-[:APPLIED_IN]->(:Incident)

        Updates:
          - times_used += 1
          - last_used = now
          - success_rate recalculated as successes / times_used
        """
        runbook_id = str(runbook_id).strip()
        incident_id = str(incident_id).strip()
        now = self._now_iso()

        # 1) Link runbook to incident (idempotent)
        self.create_edge(
            source_label="Runbook",
            source_id_field="runbook_id",
            source_id_value=runbook_id,
            target_label="Incident",
            target_id_field="incident_id",
            target_id_value=incident_id,
            relationship="APPLIED_IN",
            properties={
                "success": bool(success),
                "duration_seconds": float(duration_seconds) if duration_seconds is not None else None,
                "timestamp": now,
            },
        )

        # 2) Update runbook stats
        cypher = """
        MATCH (rb:Runbook {tenant_id:$tenant_id, runbook_id:$runbook_id})
        SET rb.times_used = coalesce(rb.times_used, 0) + 1,
            rb.last_used = $now,
            rb.success_count = coalesce(rb.success_count, 0) + CASE WHEN $success THEN 1 ELSE 0 END,
            rb.failure_count = coalesce(rb.failure_count, 0) + CASE WHEN $success THEN 0 ELSE 1 END
        WITH rb
        SET rb.success_rate =
            CASE
              WHEN coalesce(rb.times_used, 0) = 0 THEN 0.0
              ELSE toFloat(coalesce(rb.success_count, 0)) / toFloat(rb.times_used)
            END
        RETURN rb AS runbook
        """
        rows = self.db.execute_write(
            cypher,
            {"tenant_id": self.tenant_id, "runbook_id": runbook_id, "success": bool(success), "now": now},
        )

        return {"ok": True, "runbook_id": runbook_id, "incident_id": incident_id, "runbook": (rows[0]["runbook"] if rows else None)}

    # -------------------------
    # Workarounds
    # -------------------------
    def add_workaround(self, workaround: Any, root_cause_id: str) -> Dict[str, Any]:
        """
        Creates:
          (:KnownWorkaround)
          (:RootCause)-[:HAS_WORKAROUND]->(:KnownWorkaround)
        """
        root_cause_id = str(root_cause_id).strip()

        self.create_node("KnownWorkaround", workaround)

        self.create_edge(
            source_label="RootCause",
            source_id_field="root_cause_id",
            source_id_value=root_cause_id,
            target_label="KnownWorkaround",
            target_id_field="workaround_id",
            target_id_value=workaround.workaround_id,
            relationship="HAS_WORKAROUND",
            properties={},
        )

        return {"ok": True, "workaround_id": workaround.workaround_id, "root_cause_id": root_cause_id}

    def find_workarounds(self, root_cause_category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Finds workarounds by RootCause.category.
        """
        limit = max(1, min(int(limit or 10), 50))
        root_cause_category = str(root_cause_category).strip()

        cypher = """
        MATCH (rc:RootCause {tenant_id:$tenant_id, category:$category})
              -[:HAS_WORKAROUND {tenant_id:$tenant_id}]->
              (w:KnownWorkaround {tenant_id:$tenant_id})
        RETURN rc AS root_cause, w AS workaround
        ORDER BY coalesce(w.expiry_date, "9999-12-31") ASC
        LIMIT $limit
        """
        return self.db.execute_read(
            cypher,
            {"tenant_id": self.tenant_id, "category": root_cause_category, "limit": limit},
        )

    # -------------------------
    # Helpers
    # -------------------------
    def _ensure_scenario_symptom(self, symptom_id: str, symptom_type: str) -> None:
        """
        Ensures a stable Symptom node exists for a scenario/symptom type.
        Used for linking SOPs/Runbooks by symptom type deterministically.
        """
        cypher = """
        MERGE (s:Symptom {tenant_id:$tenant_id, symptom_id:$symptom_id})
        ON CREATE SET
            s.type=$type,
            s.description=$desc,
            s.created_at=$now,
            s.updated_at=$now
        ON MATCH SET
            s.updated_at=$now
        RETURN s
        """
        self.db.execute_write(
            cypher,
            {
                "tenant_id": self.tenant_id,
                "symptom_id": symptom_id,
                "type": symptom_type,
                "desc": f"Scenario type: {symptom_type}",
                "now": self._now_iso(),
            },
        )

    def _now_iso(self) -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()
