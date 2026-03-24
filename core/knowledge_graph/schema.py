# core/knowledge_graph/schema.py
from __future__ import annotations

import logging
from typing import List

from core.knowledge_graph.db import get_graph_db

logger = logging.getLogger(__name__)


# (Label, unique_key) pairs
# We use tenant_id + <business_id> for idempotent merges.
UNIQUE_KEYS = [
    ("Service", "service_id"),
    ("Incident", "incident_id"),
    ("RootCause", "root_cause_id"),
    ("Symptom", "symptom_id"),
    ("Resolution", "resolution_id"),
    ("Runbook", "runbook_id"),
    ("KnownWorkaround", "workaround_id"),
    ("SOP", "sop_id"),
    ("SOPStep", "step_id"),
    ("Document", "doc_id"),
    ("Customer", "customer_id"),
    ("Product", "product_id"),
    ("Feature", "feature_id"),
    ("Release", "release_id"),
    ("Engineer", "engineer_id"),
    ("ErrorSignature", "signature_id"),
    ("Deployment", "deployment_id"),
    ("FAQ", "faq_id"),
    ("FeatureFlag", "flag_id"),
    ("CustomerContact", "contact_id"),
    ("Team", "team_id"),
    ("SLAContract", "sla_id"),

    # -------------------------
    # CCaaS POC additions
    # -------------------------
    ("Channel", "channel_id"),
    ("Queue", "queue_id"),
    ("RoutingRule", "rule_id"),
    ("CCAgent", "agent_id"),
    ("KnownIssue", "issue_id"),
]

UNIQUE_KEY_BY_LABEL = {label: key for label, key in UNIQUE_KEYS}

INDEXES = [
    # tenant isolation / speed
    ("Service", ["tenant_id"]),
    ("Incident", ["tenant_id"]),
    ("Customer", ["tenant_id"]),
    ("Product", ["tenant_id"]),
    ("Feature", ["tenant_id"]),
    ("SOP", ["tenant_id"]),
    ("SOPStep", ["tenant_id"]),
    ("Runbook", ["tenant_id"]),
    ("RootCause", ["tenant_id"]),
    ("KnownWorkaround", ["tenant_id"]),
    ("Symptom", ["tenant_id"]),
    ("Deployment", ["tenant_id"]),
    ("Release", ["tenant_id"]),
    ("Document", ["tenant_id"]),
    ("Engineer", ["tenant_id"]),
    ("Team", ["tenant_id"]),
    ("FAQ", ["tenant_id"]),
    ("FeatureFlag", ["tenant_id"]),
    ("ErrorSignature", ["tenant_id"]),
    ("SLAContract", ["tenant_id"]),
    ("CustomerContact", ["tenant_id"]),

    # CCaaS tenant isolation
    ("Channel", ["tenant_id"]),
    ("Queue", ["tenant_id"]),
    ("RoutingRule", ["tenant_id"]),
    ("CCAgent", ["tenant_id"]),
    ("KnownIssue", ["tenant_id"]),

    # common search indexes
    ("Service", ["name"]),
    ("Product", ["name"]),
    ("Customer", ["name"]),
    ("Feature", ["name"]),

    # Incident patterns
    ("Incident", ["severity"]),
    ("Incident", ["created_at"]),
    ("RootCause", ["category"]),
    ("SOP", ["category"]),

    # CCaaS search
    ("Channel", ["name"]),
    ("Queue", ["name"]),
    ("RoutingRule", ["name"]),
    ("CCAgent", ["name"]),
    ("KnownIssue", ["status"]),
]


def init_graph_db() -> bool:
    """
    Creates constraints and indexes.
    Must NOT crash the app if Neo4j is unreachable.
    Returns True if initialization succeeded, else False.
    """
    db = get_graph_db()
    if not db.health_check():
        logger.warning("Neo4j unreachable. Knowledge Graph features will be disabled.")
        return False

    # Constraints
    for label, key in UNIQUE_KEYS:
        name = f"uq_{label.lower()}_{key.lower()}_tenant"
        cypher = f"""
        CREATE CONSTRAINT {name} IF NOT EXISTS
        FOR (n:{label})
        REQUIRE (n.tenant_id, n.{key}) IS UNIQUE
        """
        try:
            db.execute_write(cypher)
        except Exception:
            logger.exception("Failed creating constraint %s", name)

    # Indexes
    for label, props in INDEXES:
        idx_name = f"idx_{label.lower()}_{'_'.join([p.lower() for p in props])}"
        props_cypher = ", ".join([f"n.{p}" for p in props])
        cypher = f"""
        CREATE INDEX {idx_name} IF NOT EXISTS
        FOR (n:{label})
        ON ({props_cypher})
        """
        try:
            db.execute_write(cypher)
        except Exception:
            logger.exception("Failed creating index %s", idx_name)

    logger.info("Neo4j schema initialization complete.")
    return True