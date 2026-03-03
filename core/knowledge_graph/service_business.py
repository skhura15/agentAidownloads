# core/knowledge_graph/service_business.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # These are only for type hints to avoid circular imports at runtime
    from core.knowledge_graph.models.nodes import (
        CustomerNode,
        SLAContractNode,
        CustomerContactNode,
        ProductNode,
        FeatureNode,
    )


class KnowledgeGraphBusinessMixin:
    """
    Sub-graphs 5 & 6: Customer/SLA + Product/Feature

    This mixin assumes the main service class provides:
      - self.tenant_id: str
      - self.db with execute_read / execute_write
      - create_node(label, node)
      - create_edge(source_label, source_id, target_label, target_id, relationship, properties, ...)
    """

    # -------------------------
    # Sub-graph 5: Customer & Tenant
    # -------------------------

    def add_customer(
        self,
        customer: "CustomerNode",
        service_ids: List[str],
        sla: Optional["SLAContractNode"] = None,
        contacts: Optional[List["CustomerContactNode"]] = None,
    ) -> Dict[str, Any]:
        """
        Doc: add_customer(customer, service_ids, sla, contacts)
        Creates/updates:
          - Customer node
          - optional SLAContract node + HAS_SLA edge
          - optional CustomerContact nodes + HAS_CONTACT edges
          - USES_SERVICE edges to services (idempotent)
        """
        # 1) Customer node
        cust_node = self.create_node("Customer", customer)

        # 2) SLA node + edge
        if sla is not None:
            self.create_node("SLAContract", sla)
            self.create_edge(
                source_label="Customer",
                source_id=customer.customer_id,
                target_label="SLAContract",
                target_id=sla.sla_id,
                relationship="HAS_SLA",
                properties={},
                source_id_field="customer_id",
                target_id_field="sla_id",
            )

        # 3) Contacts + edges
        for c in (contacts or []):
            self.create_node("CustomerContact", c)
            self.create_edge(
                source_label="Customer",
                source_id=customer.customer_id,
                target_label="CustomerContact",
                target_id=c.contact_id,
                relationship="HAS_CONTACT",
                properties={},
                source_id_field="customer_id",
                target_id_field="contact_id",
            )

        # 4) USES_SERVICE edges
        cypher = """
        UNWIND $service_ids AS sid
        MATCH (c:Customer {tenant_id:$tenant_id, customer_id:$customer_id})
        MATCH (s:Service  {tenant_id:$tenant_id, service_id:sid})
        MERGE (c)-[r:USES_SERVICE]->(s)
        SET r.tenant_id = $tenant_id
        RETURN count(r) AS merged
        """
        self.db.execute_write(
            cypher,
            {
                "tenant_id": self.tenant_id,
                "customer_id": customer.customer_id,
                "service_ids": service_ids,
            },
        )

        return cust_node

    def get_affected_customers(self, service_id: str) -> List[Dict[str, Any]]:
        """
        Doc: get_affected_customers(service_id) — all customers using this service
        """
        cypher = """
        MATCH (c:Customer {tenant_id:$tenant_id})-[r:USES_SERVICE]->(s:Service {tenant_id:$tenant_id, service_id:$service_id})
        RETURN c AS customer, r AS rel
        ORDER BY coalesce(c.vip,false) DESC, coalesce(c.tier,"") DESC, coalesce(c.name,"") ASC
        """
        rows = self.db.execute_read(
            cypher, {"tenant_id": self.tenant_id, "service_id": service_id}
        )
        return [{"customer": r["customer"], "usage": r["rel"]} for r in rows]

    def get_customer_sla_exposure(self, service_id: str) -> Dict[str, Any]:
        """
        Doc: get_customer_sla_exposure(service_id)
        First-pass: returns customers + SLA object if present.
        Real breach risk requires Subgraph 12 (SLO/SLA/error budget), so breach_risk=None for now.
        """
        cypher = """
        MATCH (c:Customer {tenant_id:$tenant_id})-[u:USES_SERVICE]->(s:Service {tenant_id:$tenant_id, service_id:$service_id})
        OPTIONAL MATCH (c)-[:HAS_SLA]->(sla:SLAContract {tenant_id:$tenant_id})
        RETURN c AS customer, u AS usage, sla AS sla
        ORDER BY coalesce(c.vip,false) DESC, coalesce(c.tier,"") DESC, coalesce(c.name,"") ASC
        """
        rows = self.db.execute_read(
            cypher, {"tenant_id": self.tenant_id, "service_id": service_id}
        )

        customers: List[Dict[str, Any]] = []
        for r in rows:
            customers.append(
                {
                    "customer": r["customer"],
                    "usage": r["usage"],
                    "sla": r["sla"],
                    "breach_risk": None,
                }
            )

        return {"service_id": service_id, "customers": customers}

    def get_customer_escalation_contacts(
        self, customer_id: str, severity: str
    ) -> List[Dict[str, Any]]:
        """
        Doc: get_customer_escalation_contacts(customer_id, severity)

        Simple mapping:
          P0 -> level >= 4
          P1 -> level >= 3
          P2 -> level >= 2
          P3/P4 -> level >= 1
        """
        sev = (severity or "").upper()
        min_level = 1
        if sev == "P0":
            min_level = 4
        elif sev == "P1":
            min_level = 3
        elif sev == "P2":
            min_level = 2

        cypher = """
        MATCH (c:Customer {tenant_id:$tenant_id, customer_id:$customer_id})-[:HAS_CONTACT]->(cc:CustomerContact {tenant_id:$tenant_id})
        WHERE coalesce(cc.escalation_level, 1) >= $min_level
        RETURN cc AS contact
        ORDER BY cc.escalation_level DESC, coalesce(cc.name,"") ASC
        """
        rows = self.db.execute_read(
            cypher,
            {"tenant_id": self.tenant_id, "customer_id": customer_id, "min_level": min_level},
        )
        return [r["contact"] for r in rows]

    # -------------------------
    # Sub-graph 6: Product & Feature
    # -------------------------

    def add_product(
        self,
        product: "ProductNode",
        features: List["FeatureNode"],
        service_mappings: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Doc: add_product(product, features, service_mappings)

        Recommended service_mappings format:
        {
          "<feature_id>": {
            "services": ["svc_api_gateway", "svc_auth"],
            "is_critical_path": true
          },
          ...
        }
        """
        prod_node = self.create_node("Product", product)

        for f in features:
            self.create_node("Feature", f)

            # Feature -> Product (PART_OF)
            self.create_edge(
                source_label="Feature",
                source_id=f.feature_id,
                target_label="Product",
                target_id=product.product_id,
                relationship="PART_OF",
                properties={},
                source_id_field="feature_id",
                target_id_field="product_id",
            )

            mapping = service_mappings.get(f.feature_id, {}) if isinstance(service_mappings, dict) else {}
            services = mapping.get("services", []) if isinstance(mapping, dict) else []
            is_critical_path = bool(mapping.get("is_critical_path", False)) if isinstance(mapping, dict) else False

            # Feature -> Service (POWERED_BY)
            cypher = """
            UNWIND $service_ids AS sid
            MATCH (feat:Feature {tenant_id:$tenant_id, feature_id:$feature_id})
            MATCH (svc:Service  {tenant_id:$tenant_id, service_id:sid})
            MERGE (feat)-[r:POWERED_BY]->(svc)
            SET r.tenant_id = $tenant_id
            SET r.is_critical_path = $is_critical_path
            RETURN count(r) AS merged
            """
            self.db.execute_write(
                cypher,
                {
                    "tenant_id": self.tenant_id,
                    "feature_id": f.feature_id,
                    "service_ids": services,
                    "is_critical_path": is_critical_path,
                },
            )

        return prod_node

    def get_features_affected_by_service(self, service_id: str) -> List[Dict[str, Any]]:
        """
        Doc: get_features_affected_by_service(service_id)
        """
        cypher = """
        MATCH (f:Feature {tenant_id:$tenant_id})-[r:POWERED_BY]->(s:Service {tenant_id:$tenant_id, service_id:$service_id})
        OPTIONAL MATCH (f)-[:PART_OF]->(p:Product {tenant_id:$tenant_id})
        RETURN f AS feature, p AS product, r AS rel
        ORDER BY coalesce(p.name,"") ASC, coalesce(f.name,"") ASC
        """
        rows = self.db.execute_read(
            cypher, {"tenant_id": self.tenant_id, "service_id": service_id}
        )
        return [{"feature": r["feature"], "product": r["product"], "mapping": r["rel"]} for r in rows]

    def get_product_impact(self, service_id: str) -> Dict[str, Any]:
        """
        Doc: get_product_impact(service_id)
        First-pass: aggregate Product.revenue_contribution across impacted products.
        """
        cypher = """
        MATCH (f:Feature {tenant_id:$tenant_id})-[:POWERED_BY]->(s:Service {tenant_id:$tenant_id, service_id:$service_id})
        MATCH (f)-[:PART_OF]->(p:Product {tenant_id:$tenant_id})
        RETURN p AS product, collect(DISTINCT f) AS features
        """
        rows = self.db.execute_read(
            cypher, {"tenant_id": self.tenant_id, "service_id": service_id}
        )

        products: List[Dict[str, Any]] = []
        total_revenue_impact = 0.0

        for r in rows:
            p = r["product"]
            feats = r["features"] or []
            rev = float(p.get("revenue_contribution", 0.0)) if isinstance(p, dict) else 0.0
            total_revenue_impact += rev
            products.append(
                {"product": p, "features": feats, "revenue_contribution": rev}
            )

        return {
            "service_id": service_id,
            "products": products,
            "total_revenue_impact": total_revenue_impact,
        }
    

        # -------------------------
    # POC helpers: reverse lookup
    # -------------------------
    def get_services_for_product(self, product_id: str) -> List[dict]:
        """
        Product -> Features -> Services (reverse of get_product_impact).
        """
        cypher = """
        MATCH (p:Product {tenant_id:$tenant_id, product_id:$product_id})
        MATCH (f:Feature {tenant_id:$tenant_id})-[:PART_OF]->(p)
        MATCH (f)-[:POWERED_BY]->(s:Service {tenant_id:$tenant_id})
        RETURN DISTINCT s
        """
        return self.db.execute_read(cypher, {"tenant_id": self.tenant_id, "product_id": product_id})

    def get_services_for_product_name(self, product_name: str) -> List[dict]:
        """
        Find product by name, then return services powering its features.
        """
        cypher = """
        MATCH (p:Product {tenant_id:$tenant_id, name:$name})
        MATCH (f:Feature {tenant_id:$tenant_id})-[:PART_OF]->(p)
        MATCH (f)-[:POWERED_BY]->(s:Service {tenant_id:$tenant_id})
        RETURN DISTINCT s
        """
        return self.db.execute_read(cypher, {"tenant_id": self.tenant_id, "name": product_name})
