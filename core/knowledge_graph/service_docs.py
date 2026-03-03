# core/knowledge_graph/service_docs.py
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.knowledge_graph.models.nodes import DocumentNode, FAQNode


class KnowledgeGraphDocsMixin:
    """
    Subgraph 3: User Guide & Help Files Graph

    Nodes:
      - Document
      - FAQ

    Edges (per the design doc):
      - DOCUMENTS: Document -> Service/Product/Feature
      - ANSWERS:   FAQ -> Symptom/RootCause (we use Symptom for now)
    """

    # -----------------------
    # Write operations
    # -----------------------
    def add_document(
        self,
        doc: DocumentNode,
        service_ids: Optional[List[str]] = None,
        product_ids: Optional[List[str]] = None,
        feature_ids: Optional[List[str]] = None,
        coverage: str = "partial",
    ) -> Dict[str, Any]:
        """
        Create/merge a Document node and link it to Services/Products/Features via DOCUMENTS edges.
        """
        # 1) Create the Document node
        doc_row = self.create_node("Document", doc)

        # 2) DOCUMENTS edges (Document -> Service/Product/Feature)
        service_ids = service_ids or []
        product_ids = product_ids or []
        feature_ids = feature_ids or []

        for sid in service_ids:
            self.create_edge(
                "Document", "doc_id", doc.doc_id,
                "Service", "service_id", sid,
                "DOCUMENTS",
                {"tenant_id": self.tenant_id, "coverage": coverage},
            )

        for pid in product_ids:
            self.create_edge(
                "Document", "doc_id", doc.doc_id,
                "Product", "product_id", pid,
                "DOCUMENTS",
                {"tenant_id": self.tenant_id, "coverage": coverage},
            )

        for fid in feature_ids:
            self.create_edge(
                "Document", "doc_id", doc.doc_id,
                "Feature", "feature_id", fid,
                "DOCUMENTS",
                {"tenant_id": self.tenant_id, "coverage": coverage},
            )

        return {"ok": True, "doc_id": doc.doc_id, "document": doc_row}

    def add_faq(
        self,
        faq: FAQNode,
        related_symptoms: Optional[List[str]] = None,
        relevance_score: float = 0.8,
    ) -> Dict[str, Any]:
        """
        Create/merge an FAQ node and link to Symptom nodes via ANSWERS edges.

        NOTE on symptom IDs:
        - Your current incident seeding uses symptom_id values like "scenario::5xx_spike".
        - To be forgiving, we accept either:
            "5xx_spike" OR "scenario::5xx_spike"
          and normalize to the stored ID format.
        This does NOT change the graph design; it only ensures linking works with your existing seeds.
        """
        # 1) Create the FAQ node
        faq_row = self.create_node("FAQ", faq)

        # 2) ANSWERS edges (FAQ -> Symptom)
        symptom_ids: List[str] = []
        if related_symptoms:
            for s in related_symptoms:
                s = (s or "").strip()
                if not s:
                    continue
                if s.startswith("scenario::"):
                    symptom_ids.append(s)
                else:
                    symptom_ids.append(f"scenario::{s}")

        for sym_id in symptom_ids:
            self.create_edge(
                "FAQ", "faq_id", faq.faq_id,
                "Symptom", "symptom_id", sym_id,
                "ANSWERS",
                {"tenant_id": self.tenant_id, "relevance_score": float(relevance_score)},
            )

        return {"ok": True, "faq_id": faq.faq_id, "faq": faq_row}

    # -----------------------
    # Read operations
    # -----------------------
    def search_documents(
        self,
        query_tags: Optional[List[str]] = None,
        service_id: Optional[str] = None,
        doc_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search Documents by tags and optionally by service mapping + type.
        """
        limit = max(1, min(int(limit or 10), 200))
        query_tags = query_tags or []

        cypher = """
        MATCH (d:Document {tenant_id:$tenant_id})
        WHERE ($doc_type IS NULL OR d.type = $doc_type)

        OPTIONAL MATCH (d)-[m:DOCUMENTS {tenant_id:$tenant_id}]->(svc:Service {tenant_id:$tenant_id})
        WITH d, svc, m

        WHERE ($service_id IS NULL OR svc.service_id = $service_id)
        AND (
            size($query_tags) = 0
            OR ANY(t IN $query_tags WHERE t IN coalesce(apoc.convert.fromJsonList(d.tags), []))
        )

        RETURN d AS document, properties(m) AS mapping
        ORDER BY coalesce(d.last_updated, d.updated_at, d.created_at, "") DESC
        LIMIT $limit
        """

        rows = self.db.execute_read(
            cypher,
            {
                "tenant_id": self.tenant_id,
                "query_tags": query_tags,
                "service_id": service_id,
                "doc_type": doc_type,
                "limit": limit,
            },
        )
        return rows

    def find_relevant_docs_for_incident(
        self,
        service_id: str,
        symptom_types: Optional[List[str]] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Return:
          - docs: Documents linked to the Service
          - faqs: FAQs that ANSWER any of the given symptoms (if present)
        """
        limit = max(1, min(int(limit or 10), 200))
        symptom_types = symptom_types or []

        # Normalize symptoms to match existing symptom_id format from your seed ("scenario::...")
        symptom_ids: List[str] = []
        for s in symptom_types:
            s = (s or "").strip()
            if not s:
                continue
            symptom_ids.append(s if s.startswith("scenario::") else f"scenario::{s}")

        # Docs mapped to service
        docs_cypher = """
        MATCH (d:Document {tenant_id:$tenant_id})
              -[m:DOCUMENTS {tenant_id:$tenant_id}]->
              (svc:Service {tenant_id:$tenant_id, service_id:$service_id})
        RETURN d AS document, properties(m) AS mapping
        ORDER BY coalesce(d.last_updated, d.updated_at, d.created_at, "") DESC
        LIMIT $limit
        """

        docs = self.db.execute_read(
            docs_cypher,
            {"tenant_id": self.tenant_id, "service_id": service_id, "limit": limit},
        )

        # FAQs that answer symptoms (optional)
        faqs: List[Dict[str, Any]] = []
        if symptom_ids:
            faqs_cypher = """
            MATCH (f:FAQ {tenant_id:$tenant_id})
                  -[r:ANSWERS {tenant_id:$tenant_id}]->
                  (sym:Symptom {tenant_id:$tenant_id})
            WHERE sym.symptom_id IN $symptom_ids
            RETURN f AS faq, sym.symptom_id AS symptom_id, properties(r) AS mapping
            ORDER BY coalesce(r.relevance_score, 0.0) DESC
            LIMIT $limit
            """
            faqs = self.db.execute_read(
                faqs_cypher,
                {"tenant_id": self.tenant_id, "symptom_ids": symptom_ids, "limit": limit},
            )

        return {"service_id": service_id, "docs": docs, "faqs": faqs}