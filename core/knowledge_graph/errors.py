# core/knowledge_graph/errors.py
from __future__ import annotations


class KnowledgeGraphError(Exception):
    """Base exception for Knowledge Graph failures."""


class KnowledgeGraphDisabledError(KnowledgeGraphError):
    """Raised when KG is disabled by configuration."""


class KnowledgeGraphUnavailableError(KnowledgeGraphError):
    """Raised when KG is enabled but Neo4j is unreachable."""


class KnowledgeGraphQueryError(KnowledgeGraphError):
    """Raised for Cypher/query execution failures."""
