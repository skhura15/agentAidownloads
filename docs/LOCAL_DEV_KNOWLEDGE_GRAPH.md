# SRE Knowledge Graph — Local Development Guide

This document explains:

- Project structure
- How to start/stop Neo4j
- Seed order
- How to test everything implemented so far
- How to visualize in Neo4j
- What is currently implemented

---

# 1) Project Structure

## Core Code

core/
└── knowledge_graph/
    ├── models/
    │   ├── base.py
    │   ├── nodes.py
    │   ├── edges.py
    │   └── enums.py
    │
    ├── db.py
    ├── config.py
    ├── errors.py
    ├── schema.py
    ├── service.py
    ├── service_context.py
    ├── service_incidents.py
    ├── service_sop.py
    ├── service_runbook.py
    ├── service_business.py

## Seed Scripts

scripts/
├── kg_seed_minimal.py
├── kg_seed_business_minimal.py
├── kg_seed_incidents_minimal.py
├── kg_seed_sop_minimal.py
├── kg_seed_runbooks_minimal.py

---

# 2) Starting Neo4j

Neo4j runs using Docker.

## Start

From project root:

docker compose up -d

Neo4j Browser:
http://localhost:7474

Bolt:
bolt://localhost:7687

Default credentials:
username: neo4j
password: password

---

## Stop

docker compose down

---

## Reset Database (DELETE EVERYTHING)

docker compose down -v
docker compose up -d

---

# 3) Seed Order (IMPORTANT)

Always run in this order:

Step 1 — Services (Subgraph 7)
python -m scripts.kg_seed_minimal

Step 2 — Business (Subgraphs 5 & 6)
python -m scripts.kg_seed_business_minimal

Step 3 — Incidents (Subgraph 8)
python -m scripts.kg_seed_incidents_minimal

Step 4 — SOP (Subgraph 1)
python -m scripts.kg_seed_sop_minimal

Step 5 — Runbooks (Subgraph 2)
python -m scripts.kg_seed_runbooks_minimal

---

# 4) Testing Commands

All use tenant_id = "tenant_demo"

## Blast Radius

python -c "from core.knowledge_graph.service import KnowledgeGraphService; import json; kg=KnowledgeGraphService('tenant_demo'); print(json.dumps(kg.get_blast_radius('svc_payment', depth=3), indent=2))"

---

## Incident History

python -c "from core.knowledge_graph.service import KnowledgeGraphService; import json; kg=KnowledgeGraphService('tenant_demo'); print(json.dumps(kg.get_incident_history('svc_payment', limit=20), indent=2))"

---

## Similar Incidents

python -c "from core.knowledge_graph.service import KnowledgeGraphService; import json; kg=KnowledgeGraphService('tenant_demo'); print(json.dumps(kg.find_similar_incidents(['5xx_spike','timeout_surge'], 'svc_payment', limit=5), indent=2))"

---

## SOP Lookup

python -c "from core.knowledge_graph.service import KnowledgeGraphService; import json; kg=KnowledgeGraphService('tenant_demo'); print(json.dumps(kg.find_sop_for_scenario('svc_payment','5xx_spike','P1',limit=5), indent=2))"

---

## Runbook Lookup

python -c "from core.knowledge_graph.service import KnowledgeGraphService; import json; kg=KnowledgeGraphService('tenant_demo'); print(json.dumps(kg.find_runbook_for_incident(['5xx_spike','timeout_surge'],'svc_payment',limit=5), indent=2))"

---

## Workarounds

python -c "from core.knowledge_graph.service import KnowledgeGraphService; import json; kg=KnowledgeGraphService('tenant_demo'); print(json.dumps(kg.find_workarounds('infrastructure',limit=5), indent=2))"

---

## Full Context (Everything Wired)

python -c "from core.knowledge_graph.service import KnowledgeGraphService; import json; kg=KnowledgeGraphService('tenant_demo'); print(json.dumps(kg.get_full_incident_context('svc_payment', symptoms=['5xx_spike','timeout_surge'], depth=3, history_limit=10, similar_limit=5), indent=2))"

---

# 5) Viewing in Neo4j Browser

Open:
http://localhost:7474

Login and run:

## Service Dependency Graph

MATCH (s:Service {tenant_id:'tenant_demo'})-[r:DEPENDS_ON {tenant_id:'tenant_demo'}]->(d:Service {tenant_id:'tenant_demo'})
RETURN s,r,d;

---

## Incidents for Payment

MATCH (svc:Service {tenant_id:'tenant_demo', service_id:'svc_payment'})
<-[:AFFECTED_SERVICE {tenant_id:'tenant_demo'}]-
(i:Incident {tenant_id:'tenant_demo'})
RETURN svc,i;

---

## Incident → Symptom → Resolution

MATCH (i:Incident {tenant_id:'tenant_demo'})
OPTIONAL MATCH (i)-[:EXHIBITED {tenant_id:'tenant_demo'}]->(sym:Symptom {tenant_id:'tenant_demo'})
OPTIONAL MATCH (i)-[:RESOLVED_BY {tenant_id:'tenant_demo'}]->(res:Resolution {tenant_id:'tenant_demo'})
RETURN i,sym,res;

---

## SOP + Steps

MATCH (s:SOP {tenant_id:'tenant_demo'})
-[:HAS_STEP {tenant_id:'tenant_demo'}]->
(st:SOPStep {tenant_id:'tenant_demo'})
RETURN s,st
ORDER BY st.order ASC;

---

## Runbook + Service + Symptoms

MATCH (rb:Runbook {tenant_id:'tenant_demo'})
-[:APPLIES_TO_SERVICE {tenant_id:'tenant_demo'}]->
(svc:Service {tenant_id:'tenant_demo'})
OPTIONAL MATCH (rb)-[:ADDRESSES_SYMPTOM {tenant_id:'tenant_demo'}]->
(sym:Symptom {tenant_id:'tenant_demo'})
RETURN rb,svc,sym;

---

# 6) What Is Implemented

Working:

Subgraph 7 — Service topology  
Subgraph 5 — Customers + SLA  
Subgraph 6 — Product + Feature  
Subgraph 8 — Incidents + similarity + resolutions  
Subgraph 1 — SOP (minimal)  
Subgraph 2 — Runbooks + workarounds (minimal)

Not implemented:

Subgraph 3 — Docs / FAQ  
Subgraph 4 — Releases / Deployments  
Subgraph 9 — Failure patterns  
Subgraph 10 — Change correlation  
Subgraph 11 — Teams / Expertise  
Subgraph 12 — SLO / Compliance  

---

# 7) Important Notes

- Read-only queries do NOT change data.
- Seeds are MERGE-based (safe to re-run).
- To reset everything:

docker compose down -v
docker compose up -d

---

# Current Status

We now have a working cross-subgraph incident intelligence system that connects:

Service → Customer → SLA → Product → Incident → Resolution → SOP → Runbook → Workaround

Subgraph 3 and beyond will be added later.