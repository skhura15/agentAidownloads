# core/knowledge_graph/models/edges.py
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import GraphEdge


class EdgeFactory:
    @staticmethod
    def DependsOn(tenant_id: str, source_id: str, target_id: str, dependency_type: str, is_critical: bool, weight: float = 1.0) -> GraphEdge:
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="DEPENDS_ON",
            properties={"dependency_type": dependency_type, "is_critical": is_critical, "weight": weight},
        )

    @staticmethod
    def CausedBy(tenant_id: str, source_id: str, target_id: str, confidence_score: float) -> GraphEdge:
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="CAUSED_BY",
            properties={"confidence_score": confidence_score},
        )

    @staticmethod
    def Exhibited(tenant_id: str, source_id: str, target_id: str, timeline_position: Optional[str] = None) -> GraphEdge:
        props: Dict[str, Any] = {}
        if timeline_position is not None:
            props["timeline_position"] = timeline_position
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="EXHIBITED",
            properties=props,
        )

    @staticmethod
    def ResolvedBy(tenant_id: str, source_id: str, target_id: str, effectiveness_score: float) -> GraphEdge:
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="RESOLVED_BY",
            properties={"effectiveness_score": effectiveness_score},
        )

    @staticmethod
    def SimilarTo(tenant_id: str, source_id: str, target_id: str, similarity_score: float, shared_symptoms: List[str]) -> GraphEdge:
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="SIMILAR_TO",
            properties={"similarity_score": similarity_score, "shared_symptoms": shared_symptoms},
        )

    @staticmethod
    def AppliesTo(tenant_id: str, source_id: str, target_id: str, conditions: Optional[str] = None, severity_threshold: Optional[str] = None) -> GraphEdge:
        props: Dict[str, Any] = {}
        if conditions is not None:
            props["conditions"] = conditions
        if severity_threshold is not None:
            props["severity_threshold"] = severity_threshold
        return GraphEdge(tenant_id=tenant_id, source_id=source_id, target_id=target_id, relationship_type="APPLIES_TO", properties=props)

    @staticmethod
    def ImpactedBy(tenant_id: str, source_id: str, target_id: str, impact_level: str, notified: bool) -> GraphEdge:
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="IMPACTED_BY",
            properties={"impact_level": impact_level, "notified": notified},
        )

    @staticmethod
    def PoweredBy(tenant_id: str, source_id: str, target_id: str, is_critical_path: bool) -> GraphEdge:
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="POWERED_BY",
            properties={"is_critical_path": is_critical_path},
        )

    @staticmethod
    def UsesService(tenant_id: str, source_id: str, target_id: str, usage_level: str, custom_config: Optional[str] = None) -> GraphEdge:
        props: Dict[str, Any] = {"usage_level": usage_level}
        if custom_config is not None:
            props["custom_config"] = custom_config
        return GraphEdge(tenant_id=tenant_id, source_id=source_id, target_id=target_id, relationship_type="USES_SERVICE", properties=props)

    @staticmethod
    def DocumentsService(tenant_id: str, source_id: str, target_id: str, coverage: str) -> GraphEdge:
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="DOCUMENTS",
            properties={"coverage": coverage},
        )

    @staticmethod
    def PrecededIncident(tenant_id: str, source_id: str, target_id: str, time_delta_minutes: int) -> GraphEdge:
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="PRECEDED_INCIDENT",
            properties={"time_delta_minutes": time_delta_minutes},
        )

    @staticmethod
    def HasStep(tenant_id: str, source_id: str, target_id: str, order: int, is_optional: bool = False) -> GraphEdge:
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="HAS_STEP",
            properties={"order": order, "is_optional": is_optional},
        )

    @staticmethod
    def AddressesSymptom(tenant_id: str, source_id: str, target_id: str, effectiveness_score: float) -> GraphEdge:
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="ADDRESSES_SYMPTOM",
            properties={"effectiveness_score": effectiveness_score},
        )

    @staticmethod
    def BrokeService(tenant_id: str, source_id: str, target_id: str, confirmed: bool) -> GraphEdge:
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="BROKE",
            properties={"confirmed": confirmed},
        )
    
        # -------------------------
    # CCaaS POC edges (minimal)
    # -------------------------
    @staticmethod
    def FlowsThrough(tenant_id: str, source_id: str, target_id: str) -> GraphEdge:
        # Channel -> Queue
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="FLOWS_THROUGH",
            properties={},
        )

    @staticmethod
    def UsesRoutingRule(tenant_id: str, source_id: str, target_id: str) -> GraphEdge:
        # Queue -> RoutingRule
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="USES_ROUTING_RULE",
            properties={},
        )

    @staticmethod
    def RoutesTo(tenant_id: str, source_id: str, target_id: str, condition: str = "default") -> GraphEdge:
        # RoutingRule -> Queue
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="ROUTES_TO",
            properties={"condition": condition},
        )

    @staticmethod
    def HandledBy(tenant_id: str, source_id: str, target_id: str) -> GraphEdge:
        # Queue -> CCAgent
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="HANDLED_BY",
            properties={},
        )

    @staticmethod
    def PowersCCAS(tenant_id: str, source_id: str, target_id: str) -> GraphEdge:
        # Queue/Channel/RoutingRule -> Service (bridge into your existing Service graph)
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="POWERED_BY",
            properties={},
        )

    @staticmethod
    def HasKnownIssue(tenant_id: str, source_id: str, target_id: str) -> GraphEdge:
        # Service/Queue/Channel -> KnownIssue
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="HAS_KNOWN_ISSUE",
            properties={},
        )

    @staticmethod
    def FixedIn(tenant_id: str, source_id: str, target_id: str) -> GraphEdge:
        # KnownIssue -> Release
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="FIXED_IN",
            properties={},
        )

    @staticmethod
    def WorkaroundIn(tenant_id: str, source_id: str, target_id: str) -> GraphEdge:
        # KnownIssue -> Runbook/SOP/Document
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="WORKAROUND_IN",
            properties={},
        )
    
        # -------------------------
    # CCaaS POC edges (additive)
    # -------------------------

    @staticmethod
    def Affects(tenant_id: str, source_id: str, target_id: str) -> GraphEdge:
        # KnownIssue -> Service/Queue/Channel/RoutingRule
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="AFFECTS",
            properties={},
        )

    @staticmethod
    def MemberOf(tenant_id: str, source_id: str, target_id: str) -> GraphEdge:
        # CCAgent -> Team
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="MEMBER_OF",
            properties={},
        )

    @staticmethod
    def AppliesToChannel(tenant_id: str, source_id: str, target_id: str) -> GraphEdge:
    # RoutingRule -> Channel
        return GraphEdge(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type="APPLIES_TO",
            properties={},
        )
