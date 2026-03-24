# core/knowledge_graph/models/nodes.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .base import GraphNode
from .enums import (
    ADRStatus,
    ChangelogEntryType,
    CustomerContactRole,
    CustomerEnvType,
    CustomerStatus,
    CustomerTier,
    DocumentSource,
    DocumentType,
    FeatureFlagStatus,
    FeatureStatus,
    IncidentSeverity,
    IncidentStatus,
    PreferredChannel,
    ProductLifecycleStage,
    ReleaseStatus,
    ReleaseType,
    ResolutionType,
    RiskLevel,
    RootCauseCategory,
    RunbookStepActionType,
    RunbookType,
    SOPCategory,
    SOPStatus,
    ServiceCriticality,
    ServiceEnvironment,
    ServiceStatus,
    SkillLevel,
    TrainingMaterialType,
    SymptomType,
    TargetSystem,
    ChannelMedium,
    QueueType,
    RoutingRuleType,
    KnownIssueSeverity,
    KnownIssueStatus,
)


# -------------------------
# Sub-graph 1: SOP & Procedures
# -------------------------
class SOPNode(GraphNode):
    sop_id: str
    title: str
    version: str
    category: SOPCategory
    status: SOPStatus
    owner_team: str
    approval_date: Optional[datetime] = None
    review_due_date: Optional[datetime] = None
    last_reviewed: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "sop_id": "sop_p0_ir",
                "title": "P0 Incident Response SOP",
                "version": "2.1",
                "category": "incident_response",
                "status": "active",
                "owner_team": "Platform",
                "approval_date": "2026-01-10T10:00:00Z",
                "review_due_date": "2026-07-10T10:00:00Z",
                "last_reviewed": "2026-01-10T10:00:00Z",
            }
        }


class SOPStepNode(GraphNode):
    step_id: str
    sop_id: str
    order: int
    instruction: str
    expected_outcome: Optional[str] = None
    estimated_duration: Optional[str] = None
    requires_approval: bool = False
    role_required: Optional[str] = None
    commands: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "step_id": "sopstep_001",
                "sop_id": "sop_p0_ir",
                "order": 1,
                "instruction": "Declare incident and open war room.",
                "expected_outcome": "Stakeholders aligned; comms started.",
                "requires_approval": False,
                "commands": [],
            }
        }


class SOPCategoryNode(GraphNode):
    category_id: str
    name: str

    class Config:
        json_schema_extra = {"example": {"tenant_id": "tenant_demo", "category_id": "cat_ir", "name": "Incident Response"}}


class ApprovalGateNode(GraphNode):
    gate_id: str
    approver_role: str
    conditions: str
    sla_minutes: int

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "gate_id": "gate_db_restart",
                "approver_role": "DBA On-Call",
                "conditions": "Database restart in prod",
                "sla_minutes": 15,
            }
        }


class EscalationPolicyNode(GraphNode):
    policy_id: str
    name: str
    levels: Dict[str, str] = Field(default_factory=dict)  # L1-L4 -> team
    time_thresholds_per_level: Dict[str, int] = Field(default_factory=dict)
    auto_escalate: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "policy_id": "esc_p0",
                "name": "P0 Escalation",
                "levels": {"L1": "Platform", "L2": "Data", "L3": "Security", "L4": "Leadership"},
                "time_thresholds_per_level": {"L1": 10, "L2": 20, "L3": 30, "L4": 45},
                "auto_escalate": True,
            }
        }


# -------------------------
# Sub-graph 2: Runbook & Troubleshooting
# -------------------------
class RunbookNode(GraphNode):
    runbook_id: str
    title: str
    description: str
    type: RunbookType
    steps: List[str] = Field(default_factory=list)
    success_rate: float = 0.0  # 0-1
    times_used: int = 0
    last_used: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    author: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "runbook_id": "rb_db_pool",
                "title": "Database Connection Pool Troubleshooting",
                "description": "Diagnose pool exhaustion and remediate safely.",
                "type": "diagnostic",
                "steps": ["Check pool usage", "Identify top queries", "Scale pool or restart safely"],
                "success_rate": 0.82,
                "times_used": 41,
                "author": "SRE Team",
            }
        }


class RunbookStepNode(GraphNode):
    step_id: str
    runbook_id: str
    order: int
    action_type: RunbookStepActionType
    instruction: str
    command: Optional[str] = None
    expected_output: Optional[str] = None
    failure_action: Optional[str] = None  # skip/abort/escalate
    rollback_command: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "step_id": "rbstep_001",
                "runbook_id": "rb_db_pool",
                "order": 1,
                "action_type": "check",
                "instruction": "Check current DB connections and pool usage.",
            }
        }


class DecisionNode(GraphNode):
    decision_id: str
    question: str
    condition: str
    yes_path_step_id: str
    no_path_step_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "decision_id": "dec_001",
                "question": "Are connections near max?",
                "condition": "active_connections > 0.9 * max_connections",
                "yes_path_step_id": "rbstep_003",
                "no_path_step_id": "rbstep_004",
            }
        }


class DiagnosticCommandNode(GraphNode):
    command_id: str
    command: str
    description: str
    target_system: TargetSystem
    output_format: Optional[str] = None
    safe_in_production: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "command_id": "cmd_redis_info",
                "command": "redis-cli INFO",
                "description": "Basic health and stats",
                "target_system": "redis",
                "safe_in_production": True,
            }
        }


class KnownWorkaroundNode(GraphNode):
    workaround_id: str
    description: str
    steps: List[str] = Field(default_factory=list)
    risk_level: RiskLevel
    temporary: bool = True
    expiry_date: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "workaround_id": "wa_redis_splitbrain",
                "description": "Temporarily force failover to primary node.",
                "steps": ["Freeze writes", "Promote primary", "Re-enable writes"],
                "risk_level": "high",
                "temporary": True,
            }
        }


# -------------------------
# Sub-graph 3: User Guides & Help
# -------------------------
class DocumentNode(GraphNode):
    doc_id: str
    title: str
    type: DocumentType
    source: DocumentSource
    url: str
    content_hash: Optional[str] = None
    author: Optional[str] = None
    last_updated: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    content_summary: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "doc_id": "doc_oncall_guide",
                "title": "On-Call Guide",
                "type": "guide",
                "source": "confluence",
                "url": "https://confluence/...",
                "tags": ["oncall", "incident"],
                "content_summary": "How we run incidents and escalation.",
            }
        }


class DocumentSectionNode(GraphNode):
    section_id: str
    doc_id: str
    heading: str
    content_summary: str
    keywords: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "section_id": "sec_001",
                "doc_id": "doc_oncall_guide",
                "heading": "Escalation rules",
                "content_summary": "When and how to escalate.",
                "keywords": ["escalation", "p0", "p1"],
            }
        }


class FAQNode(GraphNode):
    faq_id: str
    question: str
    answer: str
    category: str
    helpful_votes: int = 0
    created_by: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "faq_id": "faq_restart_api",
                "question": "How do I restart API Gateway?",
                "answer": "Use the runbook RB-API-RESTART and get approval if prod.",
                "category": "operations",
                "helpful_votes": 12,
            }
        }


class TrainingMaterialNode(GraphNode):
    training_id: str
    title: str
    type: TrainingMaterialType # video/doc/hands_on_lab (doc didn’t force enum here)
    skill_level: SkillLevel
    topics: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "training_id": "train_payment_oncall",
                "title": "Payment Service On-Call Lab",
                "type": "hands_on_lab",
                "skill_level": "intermediate",
                "topics": ["payment", "incidents", "debugging"],
            }
        }


class ArchitectureDecisionRecordNode(GraphNode):
    adr_id: str
    title: str
    status: ADRStatus
    context: str
    decision: str
    consequences: str

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "adr_id": "adr_001",
                "title": "Use Redis Cluster for session storage",
                "status": "accepted",
                "context": "Need low-latency session reads.",
                "decision": "Adopt Redis Cluster with sentinel.",
                "consequences": "Requires monitoring split-brain risks.",
            }
        }


# -------------------------
# Sub-graph 4: Release & Change Docs
# -------------------------
class ReleaseNode(GraphNode):
    release_id: str
    version: str
    service: str
    release_date: datetime
    release_type: ReleaseType
    status: ReleaseStatus
    breaking_changes: bool = False
    release_notes_url: Optional[str] = None
    feature_flags_added: List[str] = Field(default_factory=list)
    feature_flags_removed: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "release_id": "rel_pay_2_5_1",
                "version": "2.5.1",
                "service": "Payment Service",
                "release_date": "2026-02-10T12:00:00Z",
                "release_type": "patch",
                "status": "deployed",
                "breaking_changes": False,
                "release_notes_url": "https://git/releases/...",
            }
        }


class ChangelogEntryNode(GraphNode):
    entry_id: str
    type: ChangelogEntryType
    description: str
    jira_ticket: Optional[str] = None
    pr_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "entry_id": "chg_001",
                "type": "bugfix",
                "description": "Fix retry loop in payment capture.",
                "jira_ticket": "PAY-123",
                "pr_url": "https://github.com/.../pull/99",
            }
        }


class MigrationGuideNode(GraphNode):
    migration_id: str
    from_version: str
    to_version: str
    breaking_changes: bool = False
    steps: List[str] = Field(default_factory=list)
    rollback_steps: List[str] = Field(default_factory=list)
    data_migration_required: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "migration_id": "mig_251",
                "from_version": "2.5.0",
                "to_version": "2.5.1",
                "breaking_changes": False,
                "steps": ["Deploy", "Verify", "Enable flag"],
                "rollback_steps": ["Disable flag", "Rollback"],
                "data_migration_required": False,
            }
        }


class FeatureFlagNode(GraphNode):
    flag_id: str
    name: str
    status: FeatureFlagStatus
    rollout_percentage: Optional[int] = None
    owner: Optional[str] = None
    services_affected: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "flag_id": "ff_checkout_v2",
                "name": "checkout_v2",
                "status": "percentage_rollout",
                "rollout_percentage": 20,
                "owner": "Payments",
                "services_affected": ["svc_payment"],
            }
        }


class DeploymentChecklistNode(GraphNode):
    checklist_id: str
    release_id: str
    pre_deploy_checks: List[str] = Field(default_factory=list)
    post_deploy_checks: List[str] = Field(default_factory=list)
    rollback_criteria: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "checklist_id": "chk_rel_pay_2_5_1",
                "release_id": "rel_pay_2_5_1",
                "pre_deploy_checks": ["Smoke test", "DB migrations validated"],
                "post_deploy_checks": ["Latency baseline OK"],
                "rollback_criteria": ["5xx > 2% for 5 minutes"],
            }
        }


class RollbackProcedureNode(GraphNode):
    rollback_id: str
    release_id: str
    steps: List[str] = Field(default_factory=list)
    estimated_duration: Optional[str] = None
    data_implications: Optional[str] = None
    tested: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "rollback_id": "rb_rel_pay_2_5_1",
                "release_id": "rel_pay_2_5_1",
                "steps": ["Disable flag", "Rollback deployment", "Verify"],
                "data_implications": "May require replaying messages.",
                "tested": True,
            }
        }


# -------------------------
# Sub-graphs 5 & 6: Customer / Product / Feature
# -------------------------
class CustomerNode(GraphNode):
    customer_id: str
    name: str
    tier: CustomerTier
    status: CustomerStatus
    account_manager: Optional[str] = None
    region: Optional[str] = None
    industry: Optional[str] = None
    revenue_impact_per_hour: float = 0.0
    vip: bool = False
    onboarded_date: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "customer_id": "cust_001",
                "name": "Acme Corp",
                "tier": "enterprise",
                "status": "active",
                "region": "EU",
                "revenue_impact_per_hour": 12000.0,
                "vip": True,
            }
        }


class SLAContractNode(GraphNode):
    sla_id: str
    customer_id: str
    availability_target: float
    response_time_sla: Dict[str, int] = Field(default_factory=dict)  # P0-P4 -> minutes
    penalty_clause: Optional[str] = None
    contract_end_date: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "sla_id": "sla_001",
                "customer_id": "cust_001",
                "availability_target": 99.95,
                "response_time_sla": {"P0": 15, "P1": 30, "P2": 60, "P3": 240, "P4": 1440},
                "penalty_clause": "Credit 10% monthly fee per breach",
            }
        }


class CustomerEnvironmentNode(GraphNode):
    env_id: str
    customer_id: str
    type: CustomerEnvType
    region: str
    special_configs: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "env_id": "env_cust_001",
                "customer_id": "cust_001",
                "type": "dedicated",
                "region": "eu-west-1",
                "special_configs": {"rate_limit": "high"},
            }
        }


class CustomerContactNode(GraphNode):
    contact_id: str
    name: str
    role: CustomerContactRole
    email: str
    phone: Optional[str] = None
    escalation_level: int = 1  # 1-4
    preferred_channel: PreferredChannel

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "contact_id": "ct_001",
                "name": "Jane Doe",
                "role": "executive",
                "email": "jane@acme.com",
                "escalation_level": 4,
                "preferred_channel": "phone",
            }
        }


class CustomerTicketNode(GraphNode):
    ticket_id: str
    customer_id: str
    type: str  # support/bug/feature_request
    status: str
    priority: str
    sla_breach: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "ticket_id": "t_1001",
                "customer_id": "cust_001",
                "type": "support",
                "status": "open",
                "priority": "P1",
                "sla_breach": False,
            }
        }


class ProductNode(GraphNode):
    product_id: str
    name: str
    description: str
    business_owner: str
    lifecycle_stage: ProductLifecycleStage
    revenue_contribution: float = 0.0

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "product_id": "prod_api_platform",
                "name": "API Platform",
                "description": "Public-facing API suite",
                "business_owner": "VP Product",
                "lifecycle_stage": "ga",
                "revenue_contribution": 0.25,
            }
        }


class FeatureNode(GraphNode):
    feature_id: str
    name: str
    product_id: str
    status: FeatureStatus
    flag_name: Optional[str] = None
    launch_date: Optional[datetime] = None
    owner_team: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "feature_id": "feat_checkout",
                "name": "Checkout",
                "product_id": "prod_api_platform",
                "status": "active",
                "flag_name": "checkout_v2",
                "owner_team": "Payments",
            }
        }


# -------------------------
# Sub-graphs 7–10: Service, Incident, Pattern, Change
# -------------------------
class ServiceNode(GraphNode):
    service_id: str
    name: str
    description: Optional[str] = None
    owner_team: Optional[str] = None
    criticality: Optional[ServiceCriticality] = None
    environment: Optional[ServiceEnvironment] = None
    status: Optional[ServiceStatus] = None
    slo_target: Optional[float] = None
    sla_target: Optional[float] = None
    business_impact: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "service_id": "svc_payment",
                "name": "Payment Service",
                "owner_team": "Platform",
                "criticality": "critical",
                "environment": "prod",
                "status": "healthy",
                "tags": ["payments", "revenue"],
            }
        }


class IncidentNode(GraphNode):
    incident_id: str
    title: str
    severity: IncidentSeverity
    status: IncidentStatus
    root_cause_category: Optional[str] = None
    duration_seconds: Optional[int] = None
    mttr_seconds: Optional[int] = None
    affected_services: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    started_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    workflow_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "incident_id": "inc_2026_001",
                "title": "Payment outage due to DB failover",
                "severity": "P0",
                "status": "resolved",
                "affected_services": ["svc_payment", "svc_db_cluster"],
                "summary": "DB cluster failover caused connection drops.",
            }
        }


class RootCauseNode(GraphNode):
    root_cause_id: str
    category: RootCauseCategory
    description: str
    frequency: int = 1
    avg_confidence: float = 0.0
    recommended_fix: Optional[str] = None
    prevention_measures: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "root_cause_id": "rc_db_failover",
                "category": "infrastructure",
                "description": "DB cluster failover misconfigured timeouts.",
                "frequency": 7,
                "avg_confidence": 0.74,
            }
        }


class SymptomNode(GraphNode):
    symptom_id: str
    type: SymptomType
    description: str
    error_pattern: Optional[str] = None
    affected_service: Optional[str] = None
    frequency: int = 1

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "symptom_id": "sym_5xx_payment",
                "type": "5xx_spike",
                "description": "5xx spike on /checkout",
                "error_pattern": "HTTP 502 from upstream",
                "affected_service": "svc_payment",
                "frequency": 15,
            }
        }


class ResolutionNode(GraphNode):
    resolution_id: str
    type: ResolutionType
    description: str
    steps: List[str] = Field(default_factory=list)
    time_to_apply_seconds: Optional[int] = None
    effectiveness_score: float = 0.0
    success_count: int = 0
    failure_count: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "resolution_id": "res_failover_fix",
                "type": "config_change",
                "description": "Updated connection timeouts and recycled pods",
                "steps": ["Update config", "Roll restart", "Verify error rate"],
                "effectiveness_score": 0.86,
                "success_count": 12,
                "failure_count": 2,
            }
        }


class DeploymentNode(GraphNode):
    deployment_id: str
    service_name: str
    version: str
    author: Optional[str] = None
    commit_hash: Optional[str] = None
    deployed_at: Optional[datetime] = None
    rollback_available: bool = True
    change_summary: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "deployment_id": "dep_pay_251",
                "service_name": "Payment Service",
                "version": "2.5.1",
                "author": "dev1",
                "commit_hash": "abc123",
                "rollback_available": True,
                "change_summary": "Fix retry loop",
            }
        }


class ErrorSignatureNode(GraphNode):
    signature_id: str
    pattern: str  # regex
    service: str
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    occurrence_count: int = 0
    severity_hint: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "signature_id": "sig_redis_timeout",
                "pattern": ".*RedisTimeoutException.*",
                "service": "Auth Service",
                "occurrence_count": 220,
                "severity_hint": "P1",
            }
        }


# -------------------------
# Sub-graph 11: Team & Expertise
# -------------------------
class EngineerNode(GraphNode):
    engineer_id: str
    name: str
    email: str
    team: str
    role: str
    timezone: Optional[str] = None
    on_call_schedule: Optional[str] = None  # you can later model this as a node if needed

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "engineer_id": "eng_001",
                "name": "A. Engineer",
                "email": "a@company.com",
                "team": "Platform",
                "role": "SRE",
                "timezone": "UTC+5:30",
                "on_call_schedule": "weekdays",
            }
        }


class TeamNode(GraphNode):
    team_id: str
    name: str
    slack_channel: Optional[str] = None
    escalation_chain: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "team_id": "team_platform",
                "name": "Platform",
                "slack_channel": "#platform-oncall",
                "escalation_chain": ["team_platform", "team_data", "team_security"],
            }
        }


# -------------------------
# CCaaS POC domain nodes (minimal, additive)
# -------------------------

class ChannelNode(GraphNode):
    channel_id: str
    name: str
    medium: ChannelMedium = ChannelMedium.other
    region: Optional[str] = None
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "channel_id": "ch_voice",
                "name": "Voice",
                "medium": "voice",
                "region": "US",
                "description": "Inbound voice channel",
            }
        }


class QueueNode(GraphNode):
    queue_id: str
    name: str
    queue_type: QueueType = QueueType.other
    region: Optional[str] = None
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "queue_id": "q_sales_us",
                "name": "Sales Queue (US)",
                "queue_type": "inbound",
                "region": "US",
                "description": "Primary inbound queue for sales calls",
            }
        }


class RoutingRuleNode(GraphNode):
    rule_id: str
    name: str
    rule_type: RoutingRuleType = RoutingRuleType.other
    expression: Optional[str] = None
    priority: Optional[int] = None
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "rule_id": "rr_skill_sales",
                "name": "Skill Based Sales Routing",
                "rule_type": "skill_based",
                "expression": "skill == 'sales' AND region == 'US'",
                "priority": 10,
            }
        }


class CCAgentNode(GraphNode):
    agent_id: str
    name: str
    email: Optional[str] = None
    team: Optional[str] = None
    timezone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "agent_id": "agent_001",
                "name": "Alex Doe",
                "email": "alex@example.com",
                "team": "Support",
                "timezone": "America/Los_Angeles",
                "skills": ["voice", "routing", "supervisor-tools"],
            }
        }


class KnownIssueNode(GraphNode):
    issue_id: str
    title: str
    description: Optional[str] = None
    severity: KnownIssueSeverity = KnownIssueSeverity.P2
    status: KnownIssueStatus = KnownIssueStatus.open

    workaround_summary: Optional[str] = None
    workaround_steps: List[str] = Field(default_factory=list)

    fixed_in_release_id: Optional[str] = None  # links to ReleaseNode.release_id if known
    affected_entities: List[str] = Field(default_factory=list)  # queue_ids, channel_ids, service_ids, etc.

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_demo",
                "issue_id": "ki_safari_chat",
                "title": "Safari chat widget fails to load",
                "description": "Chat widget intermittently fails in Safari due to cookie policy mismatch.",
                "severity": "P2",
                "status": "open",
                "workaround_summary": "Use Chrome/Edge or disable strict tracking prevention for the tenant domain.",
                "workaround_steps": ["Switch browser", "Verify widget loads", "Confirm tenant settings"],
                "fixed_in_release_id": "rel_2025_w2",
                "affected_entities": ["ch_chat", "q_support_us", "svc_routing"],
            }
        }