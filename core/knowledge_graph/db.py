# core/knowledge_graph/db.py
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Dict, Optional

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from core.knowledge_graph.config import get_kg_settings
from core.knowledge_graph.errors import KnowledgeGraphQueryError
from neo4j.graph import Node, Relationship

logger = logging.getLogger(__name__)


class GraphDB:
    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        database: str,
        max_connection_lifetime: int = 3600,
        max_connection_pool_size: int = 50,
    ) -> None:
        self._uri = uri
        self._user = user
        self._password = password
        self._database = database
        self._driver = GraphDatabase.driver(
            uri,
            auth=(user, password),
            max_connection_lifetime=max_connection_lifetime,
            max_connection_pool_size=max_connection_pool_size,
        )

    @property
    def database(self) -> str:
        return self._database

    @contextmanager
    def get_session(self):
        session = self._driver.session(database=self._database)
        try:
            yield session
        finally:
            session.close()

    def _normalize_value(self, v: Any) -> Any:
        # Neo4j Node -> dict + labels
        if isinstance(v, Node):
            d = dict(v)
            d["labels"] = list(v.labels)
            return d

        # Neo4j Relationship -> dict + type
        if isinstance(v, Relationship):
            d = dict(v)
            d["type"] = v.type
            return d
        
        # Relationship triple shape -> normalize to dict
        # Example: [<start node dict>, "USES_SERVICE", {..props..}]
        if isinstance(v, (list, tuple)) and len(v) == 3 and isinstance(v[1], str) and isinstance(v[2], dict):
            rel_props = self._normalize_value(v[2])
            rel_props["type"] = v[1]
            return rel_props

        # Lists/tuples -> normalize items
        if isinstance(v, (list, tuple)):
            return [self._normalize_value(x) for x in v]

        # Dict -> normalize values
        if isinstance(v, dict):
            return {k: self._normalize_value(val) for k, val in v.items()}

        return v


    def _normalize_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        return {k: self._normalize_value(v) for k, v in row.items()}

    def execute_query(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> list[dict]:
        params = params or {}
        try:
            with self.get_session() as session:
                result = session.run(cypher, params)
                return [self._normalize_row(r.data()) for r in result]
        except Neo4jError as e:
            logger.exception("Neo4j query failed")
            raise KnowledgeGraphQueryError(str(e)) from e

    def execute_read(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> list[dict]:
        params = params or {}

        def _tx(tx):
            res = tx.run(cypher, params)
            return [self._normalize_row(r.data()) for r in res]

        try:
            with self.get_session() as session:
                return session.execute_read(_tx)
        except Neo4jError as e:
            logger.exception("Neo4j read failed")
            raise KnowledgeGraphQueryError(str(e)) from e

    def execute_write(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> list[dict]:
        params = params or {}

        def _tx(tx):
            res = tx.run(cypher, params)
            return [self._normalize_row(r.data()) for r in res]

        try:
            with self.get_session() as session:
                return session.execute_write(_tx)
        except Neo4jError as e:
            logger.exception("Neo4j write failed")
            raise KnowledgeGraphQueryError(str(e)) from e

    def health_check(self) -> bool:
        try:
            rows = self.execute_read("RETURN 1 AS ok")
            return bool(rows) and rows[0].get("ok") == 1
        except Exception:
            return False

    def close(self) -> None:
        try:
            self._driver.close()
        except Exception:
            logger.exception("Failed to close Neo4j driver")


_graph_db_singleton: Optional[GraphDB] = None


def get_graph_db() -> GraphDB:
    """
    Module-level singleton accessor (per your doc).
    """
    global _graph_db_singleton
    if _graph_db_singleton is not None:
        return _graph_db_singleton

    s = get_kg_settings()
    _graph_db_singleton = GraphDB(
        uri=s.neo4j_uri,
        user=s.neo4j_user,
        password=s.neo4j_password,
        database=s.neo4j_database,
    )
    return _graph_db_singleton


def close_graph_db() -> None:
    """Close and clear the module singleton (useful for graceful shutdown/tests)."""
    global _graph_db_singleton
    if _graph_db_singleton is None:
        return
    try:
        _graph_db_singleton.close()
    finally:
        _graph_db_singleton = None
