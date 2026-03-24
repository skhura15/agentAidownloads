# core/knowledge_graph/models/base.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class GraphNode(BaseModel):
    node_id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    def to_neo4j_properties(self) -> Dict[str, Any]:
        """
        Per doc:
        - convert datetimes to ISO strings
        - flatten lists/dicts to JSON strings where needed
        """
        data = self.model_dump()
        out: Dict[str, Any] = {}
        for k, v in data.items():
            if isinstance(v, datetime):
                out[k] = v.isoformat()
            elif isinstance(v, (list, dict)):
                out[k] = json.dumps(v, ensure_ascii=False)
            else:
                out[k] = v
        return out

    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "b4f0e5c0-9a66-4a6a-8f7b-5d0ac2d6d2d1",
                "tenant_id": "tenant_demo",
                "created_at": "2026-02-16T10:00:00Z",
                "updated_at": "2026-02-16T10:00:00Z",
            }
        }


class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    tenant_id: str
    properties: Dict[str, Any] = Field(default_factory=dict)

    def to_neo4j_properties(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"tenant_id": self.tenant_id}
        for k, v in self.properties.items():
            if isinstance(v, datetime):
                out[k] = v.isoformat()
            elif isinstance(v, (list, dict)):
                out[k] = json.dumps(v, ensure_ascii=False)
            else:
                out[k] = v
        return out

    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "svc_payment",
                "target_id": "svc_db",
                "relationship_type": "DEPENDS_ON",
                "tenant_id": "tenant_demo",
                "properties": {"dependency_type": "database", "is_critical": True, "weight": 0.9},
            }
        }
