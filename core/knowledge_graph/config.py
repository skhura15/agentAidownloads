# core/knowledge_graph/config.py
from __future__ import annotations

import os
from dataclasses import dataclass


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


@dataclass(frozen=True)
class KnowledgeGraphSettings:
    """Runtime configuration for the Knowledge Graph module."""

    # Neo4j connection
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")
    neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j")

    # Feature flags
    knowledge_graph_enabled: bool = _get_bool("KNOWLEDGE_GRAPH_ENABLED", True)
    seed_on_startup: bool = _get_bool("SEED_KNOWLEDGE_GRAPH_ON_STARTUP", False)


def get_kg_settings() -> KnowledgeGraphSettings:
    """Return KG settings (reads env at call time)."""
    return KnowledgeGraphSettings()
