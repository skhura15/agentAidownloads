# agents/knowledge_graph/knowledge_graph_agent.py
from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent, AgentResponse


# -----------------------------
# Minimal fallbacks for demo
# -----------------------------
class _NullStateManager:
    async def update_agent_state(self, agent_id: str, payload: Dict[str, Any]) -> None:
        return


class _NullConfigManager:
    pass


def _safe_json_loads(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        # best-effort: extract JSON object from text
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def _build_azure_openai_client():
    # Azure OpenAI SDK (OpenAI python v1+)
    from openai import AzureOpenAI

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")

    if not endpoint or not key:
        raise RuntimeError(
            "Missing Azure env vars. Need AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY."
        )

    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=key,
        api_version=api_version,
    )


class KnowledgeGraphAgent(BaseAgent):
    """
    Demo Knowledge Graph Agent (LLM router + KG queries)

    Supports:
    - full_context (service broken)
    - product_full_context (product broken -> powered services -> full_context per service)

    Notes:
    - Azure only
    - Safe with dummy/no state_manager
    """

    def __init__(
        self,
        config_manager=None,
        state_manager=None,
        tenant_id: str = "tenant_demo",
        default_service_id: str = "svc_payment",
    ):
        # Import here to avoid cyclic import issues during test script sys.path hacks
        from core.knowledge_graph.service import KnowledgeGraphService

        super().__init__(
            agent_id="knowledge-graph",
            agent_name="Knowledge Graph",
            description="Queries the SRE Knowledge Graph for blast radius, incidents, SOPs, runbooks, customer impact, and docs.",
            capabilities=[
                "full_context",
                "product_full_context",
                "blast_radius",
                "customer_impact",
                "product_impact",
                "incident_history",
                "similar_incidents",
                "document_search",
            ],
            config_manager=config_manager or _NullConfigManager(),
            state_manager=state_manager or _NullStateManager(),
        )

        self.tenant_id = tenant_id
        self.default_service_id = default_service_id
        self.kg = KnowledgeGraphService(tenant_id=self.tenant_id)

        self._client = None
        self._deployment = None

    async def _load_configuration(self) -> None:
        # Azure deployment name (NOT "model name")
        self._deployment = os.getenv("KG_AGENT_MODEL") or "gpt-40-mini"

    async def _setup_tools(self) -> None:
        self._client = _build_azure_openai_client()

    async def _execute_logic(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        context = context or {}

        query_obj = await self._classify_query(user_input, context=context)
        query_type = query_obj.get("query_type") or "full_context"
        params = query_obj.get("parameters") or {}

        # defaults
        params.setdefault("depth", context.get("depth", 3))
        params.setdefault("history_limit", context.get("history_limit", 10))
        params.setdefault("similar_limit", context.get("similar_limit", 5))
        params.setdefault("symptoms", context.get("symptoms", []))

        # route
        if query_type == "product_full_context":
            result = self._handle_product_full_context(params)
            content = self._format_product_full_context(result, params)
            return AgentResponse(
                content=content,
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                metadata={"query_type": query_type, "parameters": params},
                tools_used=["azure_llm_router", "kg::product_full_context"],
            )

        # default: service full context
        service_id = params.get("service_id") or context.get("service_id") or self.default_service_id
        symptoms = params.get("symptoms") or []
        depth = int(params.get("depth", 3))
        history_limit = int(params.get("history_limit", 10))
        similar_limit = int(params.get("similar_limit", 5))

        result = self.kg.get_full_incident_context(
            service_id,
            symptoms=symptoms,
            depth=depth,
            history_limit=history_limit,
            similar_limit=similar_limit,
        )

        content = self._format_service_full_context(result)
        return AgentResponse(
            content=content,
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            metadata={"query_type": "full_context", "parameters": {"service_id": service_id, **params}},
            tools_used=["azure_llm_router", "kg::get_full_incident_context"],
        )

    # -----------------------------
    # LLM routing
    # -----------------------------
    async def _classify_query(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns JSON:
          {"query_type": "...", "parameters": {...}}
        """

        system = """You are a router for an SRE Knowledge Graph.
Return ONLY valid JSON with keys: query_type, parameters.

query_type allowed:
- product_full_context : when user says a PRODUCT is broken/down/outage/degraded
- full_context : when user says a SERVICE is broken/down/outage/degraded
- blast_radius, customer_impact, product_impact, incident_history, similar_incidents, document_search (optional)

Parameters:
- product_name (string) if product_full_context
- service_id (string) if full_context
- symptoms (list) if user mentions (5xx_spike, timeout_surge, latency_increase, etc.)
- depth (int), history_limit (int), similar_limit (int) if mentioned

Rules:
- If user message mentions a product name + "broken/down/outage/degraded", use product_full_context.
- If user message mentions a service id like svc_xxx, use full_context and set service_id.
- If unsure, default to full_context without service_id (caller will use default).
"""

        user = f"""User message: {message}
Default service: {context.get("service_id", "svc_payment")}
Return JSON now.
"""

        # hard timeout so your test never "hangs"
        client = self._client.with_options(timeout=20)

        print(f"[KG_AGENT] Calling Azure LLM deployment={self._deployment} ...", flush=True)

        resp = client.chat.completions.create(
            model=self._deployment,  # Azure deployment name
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0,
        )

        text = resp.choices[0].message.content or "{}"
        obj = _safe_json_loads(text)

        if "query_type" not in obj:
            obj["query_type"] = "full_context"
        if "parameters" not in obj or obj["parameters"] is None:
            obj["parameters"] = {}

        return obj

    # -----------------------------
    # Product -> Services -> Context
    # -----------------------------
    def _find_product_by_name(self, product_name: str) -> Optional[Dict[str, Any]]:
        name = (product_name or "").strip()
        if not name:
            return None

        # Try exact match via service search_nodes
        hits = self.kg.search_nodes(label="Product", filters={"name": name}, limit=10)
        if hits:
            for p in hits:
                if (p.get("name") or "").lower() == name.lower():
                    return p
            return hits[0]

        # Fallback: partial match (demo)
        all_prods = self.kg.search_nodes(label="Product", filters={}, limit=50)
        name_l = name.lower()
        for p in all_prods:
            if name_l in (p.get("name") or "").lower():
                return p
        return None

    def _get_services_powering_product(self, product_id: str) -> List[Dict[str, Any]]:
        """
        Product -> Feature -> Service (POWERED_BY)
        Uses KnowledgeGraphService.db.execute_read (available in your service.py).
        """
        cypher = """
        MATCH (p:Product {tenant_id: $tenant_id, product_id: $product_id})
        MATCH (f:Feature {tenant_id: $tenant_id})-[:PART_OF]->(p)
        MATCH (f)-[:POWERED_BY]->(s:Service {tenant_id: $tenant_id})
        RETURN DISTINCT s AS service
        """
        rows = self.kg.db.execute_read(
            cypher,
            {"tenant_id": self.tenant_id, "product_id": product_id},
        ) or []

        services: List[Dict[str, Any]] = []
        for r in rows:
            s = r.get("service")
            if isinstance(s, dict):
                services.append(s)
        return services

    def _handle_product_full_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        product_name = params.get("product_name") or params.get("product") or ""
        product = self._find_product_by_name(product_name)

        if not product:
            return {
                "error": "product_not_found",
                "product_name": product_name,
            }

        product_id = product.get("product_id")
        if not product_id:
            return {"error": "product_missing_id", "product": product}

        services = self._get_services_powering_product(product_id)

        depth = int(params.get("depth", 3))
        history_limit = int(params.get("history_limit", 10))
        similar_limit = int(params.get("similar_limit", 5))
        symptoms = params.get("symptoms") or []

        contexts: List[Dict[str, Any]] = []
        for s in services:
            sid = s.get("service_id")
            if not sid:
                continue
            ctx = self.kg.get_full_incident_context(
                sid,
                symptoms=symptoms,
                depth=depth,
                history_limit=history_limit,
                similar_limit=similar_limit,
            )
            contexts.append(ctx)

        return {
            "product": product,
            "services": services,
            "service_contexts": contexts,
        }

    # -----------------------------
    # Formatting (demo-friendly)
    # -----------------------------
    def _format_service_full_context(self, ctx: Dict[str, Any]) -> str:
        service_id = ctx.get("service_id", "unknown_service")
        blast = ctx.get("blast_radius") or {}
        intel = ctx.get("incident_intelligence") or {}

        upstream = blast.get("upstream_dependents") or []
        downstream = blast.get("downstream_dependencies") or []
        customers = blast.get("affected_customers") or []
        product_impact = blast.get("product_impact") or {}

        lines: List[str] = []
        lines.append(f"🧠 Knowledge Graph Context for **{service_id}**")
        lines.append("")
        lines.append(f"### Service: **{service_id}**")
        lines.append(f"- Upstream dependents: {len(upstream)}")
        lines.append(f"- Downstream dependencies: {len(downstream)}")
        lines.append(f"- Affected customers: {len(customers)}")
        if product_impact:
            lines.append(f"- Product revenue impact (demo): {product_impact.get('total_revenue_impact')}")

        lines.append(f"- Most recent incident: {intel.get('most_recent_incident_id')} ({intel.get('most_recent_severity')})")

        # best resolution (already deduped in your service_context improvements)
        recs = (intel.get("resolution_recommendations") or {})
        best = recs.get("best_resolutions_by_symptom") or []
        if best:
            b0 = best[0]
            r = b0.get("best_resolution") or {}
            lines.append(f"- Best known resolution: {r.get('type')} — {r.get('description')}")

        # SOP + Runbook
        sops = intel.get("sop_matches") or []
        if sops:
            sop = (sops[0].get("sop") or {})
            lines.append(f"- SOP: {sop.get('title')}")

        rbs = intel.get("recommended_runbooks") or []
        if rbs:
            rb = (rbs[0].get("runbook") or {})
            lines.append(f"- Runbook: {rb.get('title')} (success_rate={rb.get('success_rate')})")

        # Docs & FAQs
        docs_content = intel.get("docs_content") or {}
        docs = docs_content.get("docs") or []
        faqs = docs_content.get("faqs") or []
        if docs or faqs:
            lines.append("")
            lines.append("## 📚 Docs & FAQs")
            if docs:
                d0 = docs[0].get("document") if isinstance(docs[0], dict) else None
                if d0:
                    lines.append(f"- Doc: {d0.get('title')} ({d0.get('url')})")
            if faqs:
                f0 = faqs[0].get("faq") if isinstance(faqs[0], dict) else None
                if f0:
                    lines.append(f"- FAQ: {f0.get('question')}")

        return "\n".join(lines)

    def _format_product_full_context(self, result: Dict[str, Any], params: Dict[str, Any]) -> str:
        if result.get("error") == "product_not_found":
            return f"❌ Product not found in graph: '{result.get('product_name')}'."

        if result.get("error") == "product_missing_id":
            return "❌ Product node exists but is missing product_id."

        product = result.get("product") or {}
        services = result.get("services") or []
        contexts = result.get("service_contexts") or []

        lines: List[str] = []
        lines.append(f"🧠 Knowledge Graph Context for **Product: {product.get('name')}**")
        lines.append("")

        lines.append(f"## 🔌 Powered services ({len(services)})")
        for s in services:
            lines.append(f"- {s.get('service_id')} — {s.get('name')} (owner: {s.get('owner_team')})")

        lines.append("")
        lines.append("## 🔥 Full incident context (per service)")
        for ctx in contexts:
            lines.append("")
            lines.append(self._format_service_full_context(ctx))

        return "\n".join(lines)