# core/knowledge_graph/service_sop.py
from __future__ import annotations

from typing import Any, Dict, List


class KnowledgeGraphSOPMixin:
    """
    Subgraph 1: SOP & Procedures
    Methods:
      - add_sop()
      - find_sop_for_scenario()
    """

    def add_sop(
        self,
        sop: Any,
        steps: List[Any],
        applicable_services: List[str],
        applicable_scenarios: List[str],
    ) -> Dict[str, Any]:
        """
        Creates:
          (:SOP)-[:HAS_STEP]->(:SOPStep)
          (:SOP)-[:APPLIES_TO_SERVICE]->(:Service)
          (:SOP)-[:APPLIES_TO_SCENARIO]->(:Symptom)  (scenario modeled as Symptom.type)
        """
        # 1) SOP node
        # NOTE: your create_node() does NOT accept id_field/id_value, so we pass only label + model
        self.create_node("SOP", sop)

        # 2) Steps + HAS_STEP
        for st in (steps or []):
            self.create_node("SOPStep", st)
            self.create_edge(
                source_label="SOP",
                source_id_field="sop_id",
                source_id_value=sop.sop_id,
                target_label="SOPStep",
                target_id_field="step_id",
                target_id_value=st.step_id,
                relationship="HAS_STEP",
                properties={"order": getattr(st, "order", None), "is_optional": False},
            )

        # 3) SOP applies to services
        for sid in (applicable_services or []):
            if not sid:
                continue
            self.create_edge(
                source_label="SOP",
                source_id_field="sop_id",
                source_id_value=sop.sop_id,
                target_label="Service",
                target_id_field="service_id",
                target_id_value=sid,
                relationship="APPLIES_TO_SERVICE",
                properties={},
            )

        # 4) SOP applies to scenarios (we model scenario as Symptom.type)
        # We'll MERGE a Symptom node for the scenario type so it can be linked cleanly.
        for symptom_type in (applicable_scenarios or []):
            symptom_type = str(symptom_type).strip()
            if not symptom_type:
                continue

            cypher_sym = """
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
            # stable ID so we don't create duplicates for scenario types
            symptom_id = f"scenario::{symptom_type}"
            self.db.execute_write(
                cypher_sym,
                {
                    "tenant_id": self.tenant_id,
                    "symptom_id": symptom_id,
                    "type": symptom_type,
                    "desc": f"Scenario type: {symptom_type}",
                    "now": self._now_iso(),
                },
            )

            self.create_edge(
                source_label="SOP",
                source_id_field="sop_id",
                source_id_value=sop.sop_id,
                target_label="Symptom",
                target_id_field="symptom_id",
                target_id_value=symptom_id,
                relationship="APPLIES_TO_SCENARIO",
                properties={},
            )

        return {"ok": True, "sop_id": sop.sop_id}

    def find_sop_for_scenario(
        self,
        service_id: str,
        symptom_type: str,
        severity: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Matches SOPs by:
          - SOP -[:APPLIES_TO_SERVICE]-> Service(service_id)
          - SOP -[:APPLIES_TO_SCENARIO]-> Symptom (via symptom_id = scenario::symptom_type)

        NOTE: severity is currently unused (kept for forward-compat with severity_threshold rules).
        """
        limit = max(1, min(int(limit or 10), 50))
        symptom_type = str(symptom_type).strip()
        scenario_id = f"scenario::{symptom_type}"

        cypher = """
        MATCH (sop:SOP {tenant_id:$tenant_id})
              -[:APPLIES_TO_SERVICE {tenant_id:$tenant_id}]->
              (svc:Service {tenant_id:$tenant_id, service_id:$service_id})

        MATCH (sop)
              -[:APPLIES_TO_SCENARIO {tenant_id:$tenant_id}]->
              (sc:Symptom {tenant_id:$tenant_id, symptom_id:$scenario_id})

        OPTIONAL MATCH (sop)-[hs:HAS_STEP {tenant_id:$tenant_id}]->(step:SOPStep {tenant_id:$tenant_id})
        WITH sop, step, hs
        ORDER BY hs.order ASC
        WITH sop, collect(step) AS steps
        RETURN sop AS sop, steps AS steps
        LIMIT $limit
        """

        return self.db.execute_read(
            cypher,
            {
                "tenant_id": self.tenant_id,
                "service_id": service_id,
                "scenario_id": scenario_id,
                "limit": limit,
            },
        )

    # tiny helper used above (keeps ISO timestamps consistent)
    def _now_iso(self) -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()
