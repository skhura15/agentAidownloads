from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from core.knowledge_graph.service import KnowledgeGraphService

router = APIRouter(tags=["knowledge-graph"])


class ResolveIssueRequest(BaseModel):
    tenant_id: str = Field(..., description="Tenant identifier, e.g. tenant_demo")
    message: str = Field(..., min_length=3, description="User incident text")
    limit: int = Field(3, ge=1, le=10, description="How many candidates to return")


@router.post("/resolve_issue")
def resolve_issue(req: ResolveIssueRequest):
    try:
        kg = KnowledgeGraphService(req.tenant_id)
        # This already does keyword extraction + candidate scoring + fetch full context
        return kg.resolve_known_issue_from_message(req.message, limit=req.limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))