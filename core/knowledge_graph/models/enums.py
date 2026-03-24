# core/knowledge_graph/models/enums.py
from __future__ import annotations
from enum import Enum


class SOPCategory(str, Enum):
    incident_response = "incident_response"
    change_management = "change_management"
    escalation = "escalation"
    maintenance = "maintenance"
    security = "security"
    disaster_recovery = "disaster_recovery"
    capacity_planning = "capacity_planning"


class SOPStatus(str, Enum):
    active = "active"
    draft = "draft"
    deprecated = "deprecated"
    archived = "archived"


class RunbookType(str, Enum):
    diagnostic = "diagnostic"
    remediation = "remediation"
    recovery = "recovery"
    maintenance = "maintenance"


class RunbookStepActionType(str, Enum):
    command = "command"
    check = "check"
    decision = "decision"
    manual = "manual"


class TargetSystem(str, Enum):
    linux = "linux"
    k8s = "k8s"
    database = "database"
    redis = "redis"
    network = "network"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class DocumentType(str, Enum):
    wiki = "wiki"
    guide = "guide"
    faq = "faq"
    training = "training"
    architecture_doc = "architecture_doc"
    design_doc = "design_doc"
    adr = "adr"


class DocumentSource(str, Enum):
    confluence = "confluence"
    notion = "notion"
    sharepoint = "sharepoint"
    git = "git"
    internal = "internal"


class ADRStatus(str, Enum):
    proposed = "proposed"
    accepted = "accepted"
    deprecated = "deprecated"
    superseded = "superseded"


class ReleaseType(str, Enum):
    major = "major"
    minor = "minor"
    patch = "patch"
    hotfix = "hotfix"


class ReleaseStatus(str, Enum):
    planned = "planned"
    deployed = "deployed"
    rolled_back = "rolled_back"


class ChangelogEntryType(str, Enum):
    feature = "feature"
    bugfix = "bugfix"
    improvement = "improvement"
    deprecation = "deprecation"
    security_fix = "security_fix"


class FeatureFlagStatus(str, Enum):
    enabled = "enabled"
    disabled = "disabled"
    percentage_rollout = "percentage_rollout"


class CustomerTier(str, Enum):
    free = "free"
    pro = "pro"
    enterprise = "enterprise"


class CustomerStatus(str, Enum):
    active = "active"
    churned = "churned"
    trial = "trial"


class CustomerEnvType(str, Enum):
    dedicated = "dedicated"
    shared = "shared"


class CustomerContactRole(str, Enum):
    technical = "technical"
    business = "business"
    executive = "executive"


class PreferredChannel(str, Enum):
    email = "email"
    slack = "slack"
    phone = "phone"


class ProductLifecycleStage(str, Enum):
    ga = "ga"
    beta = "beta"
    deprecated = "deprecated"
    eol = "eol"


class FeatureStatus(str, Enum):
    active = "active"
    beta = "beta"
    disabled = "disabled"
    deprecated = "deprecated"


class IncidentSeverity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class IncidentStatus(str, Enum):
    open = "open"
    investigating = "investigating"
    mitigating = "mitigating"
    resolved = "resolved"
    closed = "closed"


class RootCauseCategory(str, Enum):
    infrastructure = "infrastructure"
    application = "application"
    configuration = "configuration"
    external_dependency = "external_dependency"
    resource_exhaustion = "resource_exhaustion"
    security = "security"
    unknown = "unknown"


class SymptomType(str, Enum):
    error_spike = "error_spike"
    latency_increase = "latency_increase"
    spike_5xx = "5xx_spike"
    timeout_surge = "timeout_surge"
    connection_exhaustion = "connection_exhaustion"
    memory_leak = "memory_leak"
    cpu_spike = "cpu_spike"
    disk_full = "disk_full"
    other = "other"


class ResolutionType(str, Enum):
    rollback = "rollback"
    hotfix = "hotfix"
    config_change = "config_change"
    restart = "restart"
    scale_up = "scale_up"
    failover = "failover"
    code_fix = "code_fix"
    manual_intervention = "manual_intervention"


class ServiceCriticality(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ServiceEnvironment(str, Enum):
    prod = "prod"
    staging = "staging"
    dev = "dev"


class ServiceStatus(str, Enum):
    healthy = "healthy"
    degraded = "degraded"
    down = "down"
    unknown = "unknown"

class TrainingMaterialType(str, Enum):
    video = "video"
    doc = "doc"
    hands_on_lab = "hands_on_lab"


class SkillLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

# -------------------------
# CCaaS POC enums (minimal)
# -------------------------

class ChannelMedium(str, Enum):
    voice = "voice"
    chat = "chat"
    email = "email"
    sms = "sms"
    social = "social"
    other = "other"


class QueueType(str, Enum):
    inbound = "inbound"
    outbound = "outbound"
    blended = "blended"
    other = "other"


class RoutingRuleType(str, Enum):
    skill_based = "skill_based"
    priority = "priority"
    time_based = "time_based"
    percentage = "percentage"
    fallback = "fallback"
    other = "other"


class KnownIssueSeverity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class KnownIssueStatus(str, Enum):
    open = "open"
    mitigated = "mitigated"
    fixed = "fixed"
    monitoring = "monitoring"

class ChannelType(str, Enum):
    voice = "voice"
    chat = "chat"
    email = "email"
    social = "social"


class RoutingStrategy(str, Enum):
    skills = "skills"
    priority = "priority"
    round_robin = "round_robin"


class AgentStatus(str, Enum):
    available = "available"
    busy = "busy"
    offline = "offline"

