# core/knowledge_graph/service_ccas.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple
from core.knowledge_graph.schema import UNIQUE_KEY_BY_LABEL

from core.knowledge_graph.models.nodes import (
    ChannelNode,
    QueueNode,
    RoutingRuleNode,
    CCAgentNode,
    KnownIssueNode,
)

logger = logging.getLogger(__name__)


class KnowledgeGraphCCaaSMixin:
    """
    CCaaS POC graph layer (additive) — aligned to the existing project contracts:

    - Uses KnowledgeGraphService.create_node(label, node)
    - Uses KnowledgeGraphService.create_edge(
        source_label, source_id_field, source_id_value,
        target_label, target_id_field, target_id_value,
        relationship, properties
      )

    Relationship names are LOCKED to core/knowledge_graph/models/edges.py:
      - (Channel)-[:FLOWS_THROUGH]->(Queue)
      - (Queue)-[:USES_ROUTING_RULE]->(RoutingRule)
      - (RoutingRule)-[:ROUTES_TO]->(Queue)
      - (Queue)-[:HANDLED_BY]->(CCAgent)
      - (Channel|Queue|RoutingRule)-[:POWERED_BY]->(Service)  (bridge)
      - (Service|Channel|Queue|RoutingRule)-[:HAS_KNOWN_ISSUE]->(KnownIssue)
      - (KnownIssue)-[:AFFECTS]->(Service|Channel|Queue|RoutingRule)          (optional)
      - (KnownIssue)-[:WORKAROUND_IN]->(Runbook|SOP|Document|FAQ)             (optional)
      - (KnownIssue)-[:FIXED_IN]->(Release)                                   (optional)
      - (RoutingRule)-[:APPLIES_TO]->(Channel)                                (optional)
    """

    # -------------------------
    # Internal helper
    # -------------------------

    def _edge(
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
        return self.create_edge(
            source_label,
            source_id_field,
            source_id_value,
            target_label,
            target_id_field,
            target_id_value,
            relationship,
            properties or {},
        )

    # -------------------------
    # Node upserts
    # -------------------------

    def add_channel(self, channel: ChannelNode) -> Dict[str, Any]:
        return self.create_node("Channel", channel)

    def add_queue(self, queue: QueueNode) -> Dict[str, Any]:
        return self.create_node("Queue", queue)

    def add_routing_rule(self, rule: RoutingRuleNode) -> Dict[str, Any]:
        return self.create_node("RoutingRule", rule)

    def add_cc_agent(self, agent: CCAgentNode) -> Dict[str, Any]:
        return self.create_node("CCAgent", agent)

    def add_known_issue(self, issue: KnownIssueNode) -> Dict[str, Any]:
        created = self.create_node("KnownIssue", issue)

        # Optional convenience: link fixed-in release if present on the node model
        if getattr(issue, "fixed_in_release_id", None):
            try:
                self.link_known_issue_fixed_in_release(issue.issue_id, issue.fixed_in_release_id)
            except Exception:
                logger.exception("Failed linking KnownIssue->Release for %s", issue.issue_id)

        return created

    # -------------------------
    # CCaaS core relationships
    # -------------------------

    def link_channel_flows_through_queue(
        self,
        channel_id: str,
        queue_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # (Channel)-[:FLOWS_THROUGH]->(Queue)
        return self._edge(
            "Channel",
            "channel_id",
            channel_id,
            "Queue",
            "queue_id",
            queue_id,
            "FLOWS_THROUGH",
            properties,
        )

    def link_queue_uses_routing_rule(
        self,
        queue_id: str,
        rule_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # (Queue)-[:USES_ROUTING_RULE]->(RoutingRule)
        return self._edge(
            "Queue",
            "queue_id",
            queue_id,
            "RoutingRule",
            "rule_id",
            rule_id,
            "USES_ROUTING_RULE",
            properties,
        )

    def link_routing_rule_routes_to_queue(
        self,
        rule_id: str,
        queue_id: str,
        condition: str = "default",
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # (RoutingRule)-[:ROUTES_TO {condition}]->(Queue)
        props = dict(properties or {})
        props.setdefault("condition", condition)
        return self._edge(
            "RoutingRule",
            "rule_id",
            rule_id,
            "Queue",
            "queue_id",
            queue_id,
            "ROUTES_TO",
            props,
        )

    def link_queue_handled_by_agent(
        self,
        queue_id: str,
        agent_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # (Queue)-[:HANDLED_BY]->(CCAgent)
        return self._edge(
            "Queue",
            "queue_id",
            queue_id,
            "CCAgent",
            "agent_id",
            agent_id,
            "HANDLED_BY",
            properties,
        )

    def link_routing_rule_applies_to_channel(
        self,
        rule_id: str,
        channel_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # (RoutingRule)-[:APPLIES_TO]->(Channel)
        return self._edge(
            "RoutingRule",
            "rule_id",
            rule_id,
            "Channel",
            "channel_id",
            channel_id,
            "APPLIES_TO",
            properties,
        )

    def link_ccas_entity_powered_by_service(
        self,
        source_label: str,
        source_id: str,
        service_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Bridge CCaaS entity -> Service (existing SRE graph):
          (Channel|Queue|RoutingRule)-[:POWERED_BY]->(Service)
        """
        if source_label not in {"Channel", "Queue", "RoutingRule"}:
            raise ValueError(f"Invalid source_label for POWERED_BY: {source_label}")

        source_id_field = {
            "Channel": "channel_id",
            "Queue": "queue_id",
            "RoutingRule": "rule_id",
        }[source_label]

        return self._edge(
            source_label,
            source_id_field,
            source_id,
            "Service",
            "service_id",
            service_id,
            "POWERED_BY",
            properties,
        )

    # -------------------------
    # KnownIssue relationships
    # -------------------------

    def link_entity_has_known_issue(
        self,
        source_label: str,
        source_id: str,
        issue_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Canonical direction recommended for traversal:
          (Service|Channel|Queue|RoutingRule)-[:HAS_KNOWN_ISSUE]->(KnownIssue)
        """
        if source_label not in {"Service", "Channel", "Queue", "RoutingRule"}:
            raise ValueError(f"Invalid source_label for HAS_KNOWN_ISSUE: {source_label}")

        source_id_field = {
            "Service": "service_id",
            "Channel": "channel_id",
            "Queue": "queue_id",
            "RoutingRule": "rule_id",
        }[source_label]

        return self._edge(
            source_label,
            source_id_field,
            source_id,
            "KnownIssue",
            "issue_id",
            issue_id,
            "HAS_KNOWN_ISSUE",
            properties,
        )

    def link_known_issue_affects(
        self,
        issue_id: str,
        target_label: str,
        target_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Optional direction:
          (KnownIssue)-[:AFFECTS]->(Service|Channel|Queue|RoutingRule)
        """
        if target_label not in {"Service", "Channel", "Queue", "RoutingRule"}:
            raise ValueError(f"Invalid target_label for AFFECTS: {target_label}")

        target_id_field = {
            "Service": "service_id",
            "Channel": "channel_id",
            "Queue": "queue_id",
            "RoutingRule": "rule_id",
        }[target_label]

        return self._edge(
            "KnownIssue",
            "issue_id",
            issue_id,
            target_label,
            target_id_field,
            target_id,
            "AFFECTS",
            properties,
        )

    def link_known_issue_workaround_in(
        self,
        issue_id: str,
        target_label: str,
        target_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Optional:
          (KnownIssue)-[:WORKAROUND_IN]->(Runbook|SOP|Document|FAQ)

        Note: WORKAROUND_IN is the single relationship type available in your EdgeFactory.
        """
        if target_label not in {"Runbook", "SOP", "Document", "FAQ"}:
            raise ValueError(f"Invalid target_label for WORKAROUND_IN: {target_label}")

        target_id_field = {
            "Runbook": "runbook_id",
            "SOP": "sop_id",
            "Document": "doc_id",
            "FAQ": "faq_id",
        }[target_label]

        return self._edge(
            "KnownIssue",
            "issue_id",
            issue_id,
            target_label,
            target_id_field,
            target_id,
            "WORKAROUND_IN",
            properties,
        )

    def link_known_issue_fixed_in_release(
        self,
        issue_id: str,
        release_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # (KnownIssue)-[:FIXED_IN]->(Release)
        return self._edge(
            "KnownIssue",
            "issue_id",
            issue_id,
            "Release",
            "release_id",
            release_id,
            "FIXED_IN",
            properties,
        )

    # -------------------------
    # Reads / searches
    # -------------------------

    def get_known_issue(self, issue_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.get_node("KnownIssue", "issue_id", issue_id)
        except Exception:
            logger.exception("get_known_issue failed for %s", issue_id)
            return None

    def search_known_issues(self, text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Lightweight search using CONTAINS on title/description.
        """
        q = (text or "").strip()
        if not q:
            return []

        limit = max(1, min(int(limit or 10), 100))

        cypher = """
        MATCH (k:KnownIssue)
        WHERE k.tenant_id = $tenant_id
          AND (
            toLower(k.title) CONTAINS toLower($q)
            OR toLower(coalesce(k.description, "")) CONTAINS toLower($q)
          )
        RETURN properties(k) AS issue
        ORDER BY coalesce(k.updated_at, k.created_at) DESC
        LIMIT $limit
        """
        rows = self.db.execute_read(cypher, {"tenant_id": self.tenant_id, "q": q, "limit": limit}) or []
        return [r["issue"] for r in rows if r.get("issue")]

    def _get_issue_affected_entities(self, issue_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Returns affected entities using either direction:
          - (KnownIssue)-[:AFFECTS]->(...)
          - (...)-[:HAS_KNOWN_ISSUE]->(KnownIssue)

        Output keys: services/channels/queues/routing_rules
        """
        params = {"tenant_id": self.tenant_id, "issue_id": issue_id}

        cypher_affects = """
        MATCH (k:KnownIssue {tenant_id:$tenant_id, issue_id:$issue_id})-[:AFFECTS]->(n)
        WHERE n.tenant_id = $tenant_id
        RETURN labels(n)[0] AS label, properties(n) AS node
        """
        rows1 = self.db.execute_read(cypher_affects, params) or []

        cypher_has = """
        MATCH (n)-[:HAS_KNOWN_ISSUE]->(k:KnownIssue {tenant_id:$tenant_id, issue_id:$issue_id})
        WHERE n.tenant_id = $tenant_id
        RETURN labels(n)[0] AS label, properties(n) AS node
        """
        rows2 = self.db.execute_read(cypher_has, params) or []

        buckets: Dict[str, List[Dict[str, Any]]] = {"Service": [], "Channel": [], "Queue": [], "RoutingRule": []}
        for r in (rows1 + rows2):
            lbl = r.get("label")
            node = r.get("node")
            if lbl in buckets and node:
                buckets[lbl].append(node)

        def dedupe(label: str, key: str) -> List[Dict[str, Any]]:
            seen = set()
            out: List[Dict[str, Any]] = []
            for n in buckets[label]:
                v = n.get(key)
                if not v or v in seen:
                    continue
                seen.add(v)
                out.append(n)
            return out

        return {
            "services": dedupe("Service", "service_id"),
            "channels": dedupe("Channel", "channel_id"),
            "queues": dedupe("Queue", "queue_id"),
            "routing_rules": dedupe("RoutingRule", "rule_id"),
        }

    def _get_issue_linked_knowledge(self, issue_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Optional direct links:
          - KnownIssue -[:WORKAROUND_IN]-> {Runbook|SOP|Document|FAQ}
          - KnownIssue -[:FIXED_IN]-> Release
        """
        params = {"tenant_id": self.tenant_id, "issue_id": issue_id}
        out: Dict[str, List[Dict[str, Any]]] = {
            "documents": [],
            "runbooks": [],
            "sops": [],
            "faqs": [],
            "releases": [],
        }

        # WORKAROUND_IN targets (typed by label)
        for label, key in [("Document", "documents"), ("Runbook", "runbooks"), ("SOP", "sops"), ("FAQ", "faqs")]:
            cypher = f"""
            MATCH (k:KnownIssue {{tenant_id:$tenant_id, issue_id:$issue_id}})-[:WORKAROUND_IN]->(n:{label})
            WHERE n.tenant_id = $tenant_id
            RETURN properties(n) AS node
            """
            rows = self.db.execute_read(cypher, params) or []
            out[key] = [r["node"] for r in rows if r.get("node")]

        # FIXED_IN -> Release
        cypher_release = """
        MATCH (k:KnownIssue {tenant_id:$tenant_id, issue_id:$issue_id})-[:FIXED_IN]->(r:Release)
        WHERE r.tenant_id = $tenant_id
        RETURN properties(r) AS node
        """
        rows = self.db.execute_read(cypher_release, params) or []
        out["releases"] = [r["node"] for r in rows if r.get("node")]

        return out

    def get_known_issue_context(
        self,
        issue_id: str,
        depth: int = 3,
        doc_tags: Optional[List[str]] = None,
        doc_type: Optional[str] = None,
        doc_limit: int = 10,
    ) -> Dict[str, Any]:
        """
        POC “give me everything about this known issue”.

        Returns:
          - issue
          - affected entities (services/channels/queues/routing_rules)
          - blast radius for affected services (if get_blast_radius exists in service)
          - linked knowledge (docs/runbooks/sops/faqs/releases) if present
          - fallback docs for affected services (optional)
        """
        issue = self.get_known_issue(issue_id)
        affected = self._get_issue_affected_entities(issue_id)
        linked_knowledge = self._get_issue_linked_knowledge(issue_id)

        service_impacts: List[Dict[str, Any]] = []
        for svc in affected.get("services", []):
            sid = svc.get("service_id")
            if not sid:
                continue
            try:
                service_impacts.append(
                    {
                        "service": svc,
                        "blast_radius": self.get_blast_radius(sid, depth=depth),
                    }
                )
            except Exception:
                logger.exception("get_blast_radius failed for %s", sid)

        fallback_docs: List[Dict[str, Any]] = []
        try:
            tags = [t for t in (doc_tags or []) if str(t).strip()]
            for svc in affected.get("services", []):
                sid = svc.get("service_id")
                if not sid:
                    continue

                effective_tags = list(tags)
                if not effective_tags:
                    name = (svc.get("name") or "").strip().lower()
                    if name:
                        effective_tags = [name]

                rows = self.search_documents(
                    query_tags=effective_tags,
                    service_id=sid,
                    doc_type=doc_type,
                    limit=doc_limit,
                )
                for r in rows or []:
                    fallback_docs.append(r)
        except Exception:
            logger.exception("fallback doc search failed for issue_id=%s", issue_id)

        return {
            "issue_id": issue_id,
            "issue": issue,
            "affected": affected,
            "service_impacts": service_impacts,
            "linked_knowledge": linked_knowledge,
            "fallback_docs": fallback_docs,
        }
    
    




    def get_known_issue_full_context(
        self,
        issue_id: str,
        include_relationships: bool = True,
        include_service_blast_radius: bool = False,
        blast_radius_depth: int = 2,
    ) -> Dict[str, Any]:
        """
        POC hero query:
        Given a KnownIssue, return a full operational context snapshot.

        Behavior:
        - 1-hop neighbors around KnownIssue (both directions)
        - PLUS targeted 2-hop expansion via:
            * affected Services (Service -[:HAS_KNOWN_ISSUE]-> KnownIssue)
            * FeatureFlags reached from KnownIssue (KnownIssue -[:WORKAROUND_IN]-> FeatureFlag)
        - De-dupes by UNIQUE_KEY_BY_LABEL[label]
        - Returns plain dicts (properties), not Neo4j Node objects
        """
        tenant_id = self.tenant_id

        # -------------------------
        # Issue (as properties)
        # -------------------------
        cypher_issue = """
        MATCH (k:KnownIssue {tenant_id:$tenant_id, issue_id:$issue_id})
        RETURN properties(k) AS issue
        LIMIT 1
        """
        rows_issue = self.db.execute_read(cypher_issue, {"tenant_id": tenant_id, "issue_id": issue_id}) or []
        issue = rows_issue[0]["issue"] if rows_issue else None
        if not issue:
            return {"ok": False, "issue_id": issue_id, "error": "KnownIssue not found"}

        # -------------------------
        # 1-hop neighbors (out + in)
        # -------------------------
        cypher_out = """
        MATCH (k:KnownIssue {tenant_id:$tenant_id, issue_id:$issue_id})-[r]->(n)
        WHERE n.tenant_id = $tenant_id
        RETURN labels(n)[0] AS label, type(r) AS rel, properties(n) AS node, properties(r) AS rel_props
        """
        cypher_in = """
        MATCH (n)-[r]->(k:KnownIssue {tenant_id:$tenant_id, issue_id:$issue_id})
        WHERE n.tenant_id = $tenant_id
        RETURN labels(n)[0] AS label, type(r) AS rel, properties(n) AS node, properties(r) AS rel_props
        """
        rows_out = self.db.execute_read(cypher_out, {"tenant_id": tenant_id, "issue_id": issue_id}) or []
        rows_in = self.db.execute_read(cypher_in, {"tenant_id": tenant_id, "issue_id": issue_id}) or []

        bucket_map = {
            "Service": "services",
            "Customer": "customers",
            "Deployment": "deployments",
            "FeatureFlag": "feature_flags",
            "Feature": "features",
            "Product": "products",
            "Incident": "incidents",
            "Engineer": "engineers",
            "Team": "teams",
            "Document": "documents",
            "Runbook": "runbooks",
            "SOP": "sops",
            "FAQ": "faqs",
            "Release": "releases",
            # CCaaS entities
            "Channel": "channels",
            "Queue": "queues",
            "RoutingRule": "routing_rules",
            "CCAgent": "agents",
            # If you have SPO in schema/seed:
            "SPO": "spos",
            "Infrastructure": "infrastructure",
            "Configuration": "configurations",
            "ReleaseNote": "release_notes",  # (only if you ever store as ReleaseNote label)
            "UserGuide": "user_guides",      # (only if you ever store as UserGuide label)
        }

        ctx: Dict[str, Any] = {
            "ok": True,
            "issue_id": issue_id,
            "issue": issue,
            "linked": {"runbooks": [], "sops": [], "faqs": [], "documents": [], "releases": []},
            "affected": {
                "services": [],
                "customers": [],
                "deployments": [],
                "feature_flags": [],
                "features": [],
                "products": [],
                "incidents": [],
                "engineers": [],
                "teams": [],
                "channels": [],
                "queues": [],
                "routing_rules": [],
                "agents": [],
                # optional buckets if present:
                "spos": [],
                "infrastructure": [],
                "configurations": [],
                "release_notes": [],
                "user_guides": [],
            },
            "relationships": [] if include_relationships else None,
            "service_blast_radius": [] if include_service_blast_radius else None,
        }

        def dedupe(label: str, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            key = UNIQUE_KEY_BY_LABEL.get(label)
            if not key:
                return nodes
            seen = set()
            out: List[Dict[str, Any]] = []
            for n in nodes:
                v = n.get(key)
                if not v or v in seen:
                    continue
                seen.add(v)
                out.append(n)
            return out

        LINK_RELS = {"HAS_RUNBOOK", "HAS_SOP", "HAS_FAQ", "DOCUMENTED_IN", "WORKAROUND_IN", "FIXED_IN", "RELATED_TO"}
        KNOWLEDGE_LABELS = {"Runbook", "SOP", "FAQ", "Document", "Release"}

        raw: Dict[str, List[Dict[str, Any]]] = {k: [] for k in bucket_map.keys()}

        def add_row(row: Dict[str, Any], direction: str) -> None:
            label = row.get("label")
            rel = row.get("rel")
            node = row.get("node") or {}
            rel_props = row.get("rel_props") or {}

            if label in raw:
                raw[label].append(node)

            if include_relationships:
                ctx["relationships"].append(
                    {
                        "direction": direction,
                        "rel": rel,
                        "from_label": "KnownIssue" if direction == "out" else label,
                        "to_label": label if direction == "out" else "KnownIssue",
                        "rel_props": rel_props,
                        "node": node,
                    }
                )

            # direct "linked" only if the neighbor is actually a knowledge artifact
            if rel in LINK_RELS and label in KNOWLEDGE_LABELS:
                if label == "Runbook":
                    ctx["linked"]["runbooks"].append(node)
                elif label == "SOP":
                    ctx["linked"]["sops"].append(node)
                elif label == "FAQ":
                    ctx["linked"]["faqs"].append(node)
                elif label == "Document":
                    ctx["linked"]["documents"].append(node)
                elif label == "Release":
                    ctx["linked"]["releases"].append(node)

        for r in rows_out:
            add_row(r, "out")
        for r in rows_in:
            add_row(r, "in")

        # -------------------------
        # Targeted 2-hop expansion
        # -------------------------
        # 2-hop via Services: service -> knowledge/config/etc
        service_ids = [n.get("service_id") for n in raw.get("Service", []) if n.get("service_id")]
        service_ids = list(dict.fromkeys(service_ids))  # preserve order, unique

        if service_ids:
            cypher_svc = """
            MATCH (s:Service {tenant_id:$tenant_id, service_id:$service_id})-[r]->(n)
            WHERE n.tenant_id = $tenant_id
            RETURN labels(n)[0] AS label, type(r) AS rel, properties(n) AS node, properties(r) AS rel_props
            """
            for sid in service_ids:
                rows = self.db.execute_read(cypher_svc, {"tenant_id": tenant_id, "service_id": sid}) or []
                for row in rows:
                    lbl = row.get("label")
                    if lbl in raw:
                        raw[lbl].append(row.get("node") or {})
                    if include_relationships:
                        ctx["relationships"].append(
                            {
                                "direction": "svc_out",
                                "rel": row.get("rel"),
                                "from_label": "Service",
                                "to_label": lbl,
                                "rel_props": row.get("rel_props") or {},
                                "node": row.get("node") or {},
                                "service_id": sid,
                            }
                        )
                    # promote knowledge artifacts into ctx.linked too
                    if row.get("rel") in LINK_RELS and lbl in KNOWLEDGE_LABELS:
                        if lbl == "Runbook":
                            ctx["linked"]["runbooks"].append(row["node"])
                        elif lbl == "SOP":
                            ctx["linked"]["sops"].append(row["node"])
                        elif lbl == "FAQ":
                            ctx["linked"]["faqs"].append(row["node"])
                        elif lbl == "Document":
                            ctx["linked"]["documents"].append(row["node"])
                        elif lbl == "Release":
                            ctx["linked"]["releases"].append(row["node"])

        # 2-hop via FeatureFlags: featureflag -[r]- neighbors (often runbooks)
        flag_ids = [n.get("flag_id") for n in raw.get("FeatureFlag", []) if n.get("flag_id")]
        flag_ids = list(dict.fromkeys(flag_ids))

        if flag_ids:
            cypher_ff = """
            MATCH (f:FeatureFlag {tenant_id:$tenant_id, flag_id:$flag_id})-[r]-(n)
            WHERE n.tenant_id = $tenant_id
            RETURN labels(n)[0] AS label, type(r) AS rel, properties(n) AS node, properties(r) AS rel_props
            """
            for fid in flag_ids:
                rows = self.db.execute_read(cypher_ff, {"tenant_id": tenant_id, "flag_id": fid}) or []
                for row in rows:
                    lbl = row.get("label")
                    if lbl in raw:
                        raw[lbl].append(row.get("node") or {})
                    if include_relationships:
                        ctx["relationships"].append(
                            {
                                "direction": "flag_any",
                                "rel": row.get("rel"),
                                "from_label": "FeatureFlag",
                                "to_label": lbl,
                                "rel_props": row.get("rel_props") or {},
                                "node": row.get("node") or {},
                                "flag_id": fid,
                            }
                        )
                    if row.get("rel") in LINK_RELS and lbl in KNOWLEDGE_LABELS:
                        if lbl == "Runbook":
                            ctx["linked"]["runbooks"].append(row["node"])
                        elif lbl == "SOP":
                            ctx["linked"]["sops"].append(row["node"])
                        elif lbl == "FAQ":
                            ctx["linked"]["faqs"].append(row["node"])
                        elif lbl == "Document":
                            ctx["linked"]["documents"].append(row["node"])
                        elif lbl == "Release":
                            ctx["linked"]["releases"].append(row["node"])

        # -------------------------
        # Fill ctx.affected buckets (deduped)
        # -------------------------
        for label, bucket_name in bucket_map.items():
            if bucket_name in ctx["affected"]:
                ctx["affected"][bucket_name] = dedupe(label, raw.get(label, []))

        # Dedup linked
        ctx["linked"]["runbooks"] = dedupe("Runbook", ctx["linked"]["runbooks"])
        ctx["linked"]["sops"] = dedupe("SOP", ctx["linked"]["sops"])
        ctx["linked"]["faqs"] = dedupe("FAQ", ctx["linked"]["faqs"])
        ctx["linked"]["documents"] = dedupe("Document", ctx["linked"]["documents"])
        ctx["linked"]["releases"] = dedupe("Release", ctx["linked"]["releases"])

        # blast radius stays off for now (you said ignore)
        if include_service_blast_radius:
            out = []
            for svc in ctx["affected"]["services"]:
                sid = svc.get("service_id")
                if not sid:
                    continue
                try:
                    out.append({"service_id": sid, "blast_radius": self.get_blast_radius(sid, depth=blast_radius_depth)})
                except Exception:
                    logger.exception("get_blast_radius failed for service_id=%s", sid)
            ctx["service_blast_radius"] = out

        return ctx