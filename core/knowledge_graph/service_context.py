# core/knowledge_graph/service_context.py
from __future__ import annotations

from typing import Any, Dict, List, Optional


class KnowledgeGraphContextMixin:
    """
    Cross-graph composition utilities (wiring Subgraphs 5, 6, 7 together).

    Assumes the main service class provides:
      - self.tenant_id
      - get_dependents(service_id, depth)
      - get_service_dependencies(service_id, depth)
      - get_affected_customers(service_id)
      - get_customer_sla_exposure(service_id)
      - get_features_affected_by_service(service_id)
      - get_product_impact(service_id)
    """

    def get_blast_radius(self, service_id: str, depth: int = 3) -> Dict[str, Any]:
        """
        Doc: get_blast_radius(service_id)
        Now enriched with:
          - upstream dependents (subgraph 7)
          - downstream dependencies (subgraph 7)
          - affected customers (subgraph 5)
          - customer SLA exposure (subgraph 5)
          - product/feature impact (subgraph 6)

        Note: SLA breach risk stays None until Subgraph 12 error-budget logic exists.
        """

        # Subgraph 7 foundation
        dependents = self.get_dependents(service_id, depth=depth)
        dependencies = self.get_service_dependencies(service_id, depth=depth)

        # Subgraph 5: customers using THIS service
        affected_customers = self.get_affected_customers(service_id)
        sla_exposure = self.get_customer_sla_exposure(service_id)

        # Subgraph 6: features/products powered by THIS service
        features_affected = self.get_features_affected_by_service(service_id)
        product_impact = self.get_product_impact(service_id)

        return {
            "service_id": service_id,
            "depth": depth,
            "upstream_dependents": dependents,
            "downstream_dependencies": dependencies,
            "affected_customers": affected_customers,
            "sla_exposure": sla_exposure,          # includes breach_risk=None today (by design)
            "features_affected": features_affected,
            "product_impact": product_impact,      # includes total_revenue_impact
        }

    def get_blast_radius_from_dependency_chain(self, service_id: str, depth: int = 3) -> Dict[str, Any]:
        """
        Optional helper (future-proof): when a core dependency goes down,
        customers impacted should include customers using upstream dependents too.

        Today we keep it simple: only direct customers of the selected service_id.
        Use this later when you want "Customer → Service → Dependencies" style traversal.
        """

        base = self.get_blast_radius(service_id, depth=depth)

        # Future enhancement hook: compute services impacted = service_id + upstream dependents (or downstream)
        # and aggregate customers/SLA/product impact across that set.

        return base

    def get_full_incident_context(
        self,
        service_id: str,
        symptoms: Optional[List[str]] = None,
        depth: int = 3,
        history_limit: int = 20,
        similar_limit: int = 5,
        sop_limit: int = 5,
        runbook_limit: int = 5,
        workaround_limit: int = 5,
    ) -> Dict[str, Any]:
        """
        Composite "3 AM give me everything (phase 1)" context.

        Includes:
        - Blast radius (5/6/7)
        - Incident history for service (8)
        - Similar incidents by symptom overlap + same service (8) [if symptoms provided]
        - Resolution recommendations:
            * most effective resolution per symptom_type (8)
            * proven resolutions for top root-cause category seen in recent history (8)

        Extended (phase 1.5):
        - SOP matches (1)
        - Runbook matches + workarounds (2)

        Later we’ll extend this to Docs/Releases/Experts.
        """

        symptoms = [str(s).strip() for s in (symptoms or []) if str(s).strip()]
        history_limit = max(1, min(int(history_limit or 20), 200))
        similar_limit = max(1, min(int(similar_limit or 5), 50))
        sop_limit = max(1, min(int(sop_limit or 5), 50))
        runbook_limit = max(1, min(int(runbook_limit or 5), 50))
        workaround_limit = max(1, min(int(workaround_limit or 5), 50))

        # 1) 5/6/7 wiring
        blast = self.get_blast_radius(service_id, depth=depth)

        # 2) 8: incident history for this service
        incident_history = self.get_incident_history(service_id, limit=history_limit)

        # 2b) impacted customers for the most recent incident (if any)
        most_recent_incident_id = incident_history[0]["incident_id"] if incident_history else None
        impacted_customers_for_most_recent_incident = []
        most_recent_severity = incident_history[0].get("severity") if incident_history else None
        most_recent_severity = str(most_recent_severity or "P1")

        if most_recent_incident_id:
            impacted_customers_for_most_recent_incident = self.get_customers_impacted_by_incident(
                most_recent_incident_id
            )

        # 3) 8: similar incidents (only if caller provides symptoms)
        similar_incidents: List[Dict[str, Any]] = []
        if symptoms:
            similar_incidents = self.find_similar_incidents(
                symptoms=symptoms,
                affected_service=service_id,
                limit=similar_limit,
            )

        # 4) 8: resolution recommendations
        # 4a) best resolution per symptom type passed in
        best_resolutions_by_symptom: List[Dict[str, Any]] = []
        for st in symptoms:
            best = self.get_most_effective_resolution(st)
            if best:
                best_resolutions_by_symptom.append(
                    {
                        "symptom_type": st,
                        "best_resolution": best.get("resolution"),
                        "avg_effectiveness": best.get("avg_effectiveness"),
                        "used_in": best.get("used_in"),
                    }
                )

        # Dedupe: same Resolution can be "best" for multiple symptoms
        if best_resolutions_by_symptom:
            by_res_id: Dict[str, Dict[str, Any]] = {}
            ordered_res_ids: List[str] = []

            for item in best_resolutions_by_symptom:
                res = item.get("best_resolution") or {}
                res_id = res.get("resolution_id") or res.get("node_id") or ""

                # If we can't key it, leave it for the fallback append
                if not res_id:
                    continue

                if res_id not in by_res_id:
                    ordered_res_ids.append(res_id)
                    new_item = dict(item)

                    # Backward compatible:
                    # - keep "symptom_type" as the first symptom
                    # - add aggregated list "symptom_types"
                    st = item.get("symptom_type")
                    new_item["symptom_types"] = [st] if st else []

                    by_res_id[res_id] = new_item
                else:
                    agg = by_res_id[res_id]
                    agg.setdefault("symptom_types", [])
                    st = item.get("symptom_type")
                    if st and st not in agg["symptom_types"]:
                        agg["symptom_types"].append(st)

            # rebuild in stable order
            deduped: List[Dict[str, Any]] = []
            seen = set()
            for rid in ordered_res_ids:
                if rid in by_res_id and rid not in seen:
                    deduped.append(by_res_id[rid])
                    seen.add(rid)

            # append any items we couldn't key
            for item in best_resolutions_by_symptom:
                res = item.get("best_resolution") or {}
                rid = res.get("resolution_id") or res.get("node_id") or ""
                if not rid:
                    deduped.append(item)

            best_resolutions_by_symptom = deduped

        # 4b) top root-cause category from recent history -> proven resolutions
        top_root_cause_category = None
        for inc in incident_history:
            cat = (inc.get("root_cause_category") or "").strip()
            if cat:
                top_root_cause_category = cat
                break

        proven_resolutions_for_top_root_cause: List[Dict[str, Any]] = []
        if top_root_cause_category:
            proven_resolutions_for_top_root_cause = self.get_resolution_for_root_cause(
                top_root_cause_category
            )

        # 5) 1: SOP matches (only if symptoms provided)
        sop_matches: List[Dict[str, Any]] = []
        if symptoms:
            seen_sop_ids = set()
            for st in symptoms:
                rows = self.find_sop_for_scenario(
                    service_id=service_id,
                    symptom_type=st,
                    severity=most_recent_severity,
                    limit=sop_limit,
                )
                for r in rows or []:
                    sop = r.get("sop") or {}
                    sop_id = sop.get("sop_id")
                    if sop_id and sop_id in seen_sop_ids:
                        continue
                    if sop_id:
                        seen_sop_ids.add(sop_id)
                    sop_matches.append(r)

        # 6) 2: Runbooks (only if symptoms provided)
        recommended_runbooks: List[Dict[str, Any]] = []
        if symptoms:
            recommended_runbooks = self.find_runbook_for_incident(
                symptoms=symptoms,
                service_id=service_id,
                limit=runbook_limit,
            )

        # 7) 2: Workarounds by root-cause category derived from history
        workarounds_for_top_root_cause: List[Dict[str, Any]] = []
        if top_root_cause_category:
            workarounds_for_top_root_cause = self.find_workarounds(
                root_cause_category=top_root_cause_category,
                limit=workaround_limit,
            )

        # 8) 3: Docs/FAQs relevant to this incident (Subgraph 3)
        docs_content: Dict[str, Any] = {"service_id": service_id, "docs": [], "faqs": []}
        if symptoms:
            docs_content = self.find_relevant_docs_for_incident(
                service_id=service_id,
                symptom_types=symptoms,
                limit=10,
            )

        # Dedupe: same FAQ can be linked to multiple symptoms
        faqs = docs_content.get("faqs") or []
        if faqs:
            by_faq_id: Dict[str, Dict[str, Any]] = {}
            ordered_faq_ids: List[str] = []

            for row in faqs:
                faq = row.get("faq") or {}
                fid = faq.get("faq_id") or faq.get("node_id") or ""

                # If we can't key it, leave it for fallback append
                if not fid:
                    continue

                if fid not in by_faq_id:
                    ordered_faq_ids.append(fid)
                    new_row = dict(row)

                    # Backward compatible:
                    # - keep "symptom_id" as the first symptom
                    # - add aggregated list "symptom_ids"
                    sid = row.get("symptom_id")
                    new_row["symptom_ids"] = [sid] if sid else []

                    by_faq_id[fid] = new_row
                else:
                    agg = by_faq_id[fid]
                    agg.setdefault("symptom_ids", [])
                    sid = row.get("symptom_id")
                    if sid and sid not in agg["symptom_ids"]:
                        agg["symptom_ids"].append(sid)

            deduped_faqs: List[Dict[str, Any]] = []
            seen = set()
            for fid in ordered_faq_ids:
                if fid in by_faq_id and fid not in seen:
                    deduped_faqs.append(by_faq_id[fid])
                    seen.add(fid)

            # append any rows we couldn't key
            for row in faqs:
                faq = row.get("faq") or {}
                fid = faq.get("faq_id") or faq.get("node_id") or ""
                if not fid:
                    deduped_faqs.append(row)

            docs_content["faqs"] = deduped_faqs

        return {
            "service_id": service_id,
            "inputs": {
                "symptoms": symptoms,
                "depth": depth,
                "history_limit": history_limit,
                "similar_limit": similar_limit,
                "sop_limit": sop_limit,
                "runbook_limit": runbook_limit,
                "workaround_limit": workaround_limit,
            },
            "blast_radius": blast,  # 5/6/7
            "incident_intelligence": {  # 8 (+ 1/2 wiring)
                "most_recent_incident_id": most_recent_incident_id,
                "most_recent_severity": most_recent_severity,
                "impacted_customers_for_most_recent_incident": impacted_customers_for_most_recent_incident,
                "incident_history": incident_history,
                "similar_incidents": similar_incidents,
                "resolution_recommendations": {
                    "best_resolutions_by_symptom": best_resolutions_by_symptom,
                    "top_root_cause_category_from_history": top_root_cause_category,
                    "proven_resolutions_for_top_root_cause": proven_resolutions_for_top_root_cause,
                },
                "sop_matches": sop_matches,
                "recommended_runbooks": recommended_runbooks,
                "workarounds_for_top_root_cause": workarounds_for_top_root_cause,
                "docs_content": docs_content,
            },
        }
    

    def get_full_product_context(
        self,
        product_name: str,
        symptoms: Optional[List[str]] = None,
        depth: int = 3,
        history_limit: int = 10,
        similar_limit: int = 5,
    ) -> Dict[str, Any]:
        """
        POC: Product -> Services -> per-service incident context.
        This lets you demo: "Digital CCaaS is broken" -> show impacted services + context.
        """
        services = self.get_services_for_product_name(product_name)
        service_ids = []
        for row in services:
            s = row.get("s") if isinstance(row, dict) else row
            if isinstance(s, dict) and "service_id" in s:
                service_ids.append(s["service_id"])

        contexts = []
        for sid in service_ids:
            contexts.append(
                self.get_full_incident_context(
                    sid,
                    symptoms=symptoms or [],
                    depth=depth,
                    history_limit=history_limit,
                    similar_limit=similar_limit,
                )
            )

        return {
            "product_name": product_name,
            "service_count": len(service_ids),
            "service_ids": service_ids,
            "contexts": contexts,
        }