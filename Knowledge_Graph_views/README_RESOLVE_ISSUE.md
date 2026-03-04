# Known Issue Resolver - Setup Guide

This guide explains how to set up and run the **resolve_issue.html** web interface for querying the Knowledge Graph to find and resolve known issues.

## Overview

The Known Issue Resolver provides a web interface to:
- Search for known issues by natural language problem descriptions
- View matched candidates with relevance scores
- Display full graph context (Runbooks, Documents, Services, SOPs, FAQs, etc.)
- View and download document content in a modal viewer

## Architecture

```
┌─────────────────┐
│   Browser       │
│ resolve_issue   │
│    .html        │
└────────┬────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌─────────────────┐  ┌──────────────┐
│  FastAPI Server │  │  HTTP Server │
│   Port 8000     │  │  Port 8080   │
│                 │  │              │
│ /kg/resolve_    │  │ Serves HTML  │
│     issue       │  │ & Documents  │
└────────┬────────┘  └──────────────┘
         │
         ▼
┌─────────────────┐
│   Neo4j DB      │
│  Ports 7474     │
│       7687      │
└─────────────────┘
```

## Prerequisites

- Python 3.8+
- Docker & Docker Compose
- Neo4j Community Edition (via Docker)

## Setup Steps

### 1. Start Neo4j Database

From the project root directory:

```powershell
docker-compose -f docker-compose.neo4j.yml up -d
```

**Services started:**
- Neo4j Browser: http://localhost:7474
- Neo4j Bolt: bolt://localhost:7687

**Default credentials:**
- Username: `neo4j`
- Password: `password`

**Verify Neo4j is running:**
```powershell
docker ps
# Should show container 'sre-kg-neo4j' running
```

### 2. Seed the Knowledge Graph Database

The database needs to be populated with Known Issues, Runbooks, Documents, and their relationships.

```powershell
# From project root
python scripts/kg_seed_ccas_poc.py
```

**This creates:**

**Nodes:**
- `KnownIssue` - Known problems with symptoms and solutions
- `Runbook` - Step-by-step resolution procedures
- `Document` - Reference documentation
- `SOP` - Standard Operating Procedures
- `FAQ` - Frequently Asked Questions
- `Service` - CCaaS services (Voice, Chat, Copilot, etc.)
- `Feature` - Product features
- `Customer` - Customer/tenant information
- `Incident` - Historical incidents

**Relationships:**
- `HAS_RUNBOOK` - Known Issue → Runbook
- `DOCUMENTED_IN` - Known Issue → Document
- `HAS_SOP` - Service → SOP
- `HAS_FAQ` - Service → FAQ
- `AFFECTS_SERVICE` - Known Issue → Service
- `USED_BY_CUSTOMER` - Service → Customer
- `HAS_KNOWN_ISSUE` - Service → Known Issue

**Verify seeding:**
```cypher
// In Neo4j Browser (http://localhost:7474)
MATCH (n) RETURN labels(n) as type, count(n) as count
```

### 3. Start the FastAPI Backend Server

The backend server provides the `/kg/resolve_issue` API endpoint that performs Knowledge Graph queries.

```powershell
# From project root
python -m uvicorn api.main:app --reload --port 8000
```

**API runs on:** http://127.0.0.1:8000

**Key endpoints:**
- `POST /kg/resolve_issue` - Main issue resolution endpoint
- `GET /health` - Health check
- `GET /docs` - FastAPI automatic documentation

**Test the API:**
```powershell
$body = @{
    tenant_id='tenant_demo'
    message='Voice calls are dropping after 3 seconds'
    limit=5
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://127.0.0.1:8000/kg/resolve_issue' `
    -Method Post `
    -Body $body `
    -ContentType 'application/json'
```

### 4. Start the Web Server

The HTTP server serves the HTML interface and static files (documents).

```powershell
# Navigate to Knowledge_Graph_views folder
cd Knowledge_Graph_views

# Start Python HTTP server
python -m http.server 8080
```

**Server runs on:** http://localhost:8080

**Serves:**
- `resolve_issue.html` - Main UI
- `support_agent.html` - Support Agent UI (alternative interface)
- `data/*.txt` - Document files (Runbooks, Known Issues, etc.)

### 5. Open in Browser

Navigate to:
```
http://localhost:8080/resolve_issue.html
```

## Usage

### Search for Known Issues

1. **Enter problem description** in the text area:
   ```
   Voice calls are dropping after 3 seconds. Agents in US East region affected.
   ```

2. **Click Search** (or press Enter)

3. **View Results:**
   - **Keywords** - Extracted from your query
   - **Candidates** - Matching Known Issues with scores
   - **Selected Issue** - Best match with full details

4. **Explore Graph Context:**
   - Affected Services
   - Linked Runbooks (clickable)
   - Documents (clickable)
   - SOPs, FAQs
   - Features, Customers, Incidents

### View Documents

Click on any **Runbook** or **Document** in the Graph Context panel to:
- View content in a modal viewer
- Download the file
- See monospaced text for code/configuration files

## Data Structure

### Document Files Location

Documents should be placed in the `data/` folder:

```
Knowledge_Graph_views/
  data/
    KnownIssue_VoiceOutage.txt
    KnownIssue_CopilotDelay.txt
    KnownIssue_WFMScheduleStale.txt
    Runbook_VoiceOutage.txt
    Runbook_CopilotDelay.txt
    Runbook_WFMScheduleStale.txt
    Document_Architecture.txt
    Document_APIReference.txt
```

### Neo4j Node Properties

**Runbook nodes** should reference documents:
```cypher
CREATE (r:Runbook {
  runbook_id: 'RUN-001',
  title: 'Voice Channel Outage Recovery',
  document: 'data/Runbook_VoiceOutage.txt',
  estimated_time: '15 minutes',
  complexity: 'Medium'
})
```

**Document nodes** should reference files:
```cypher
CREATE (d:Document {
  document_id: 'DOC-001',
  title: 'CCaaS Architecture Overview',
  url: 'data/Document_Architecture.txt',
  doc_type: 'Architecture'
})
```

## API Request/Response

### Request to `/kg/resolve_issue`

```json
{
  "tenant_id": "tenant_demo",
  "message": "WFM forecast updated but schedules not regenerating",
  "limit": 5
}
```

### Response Structure

```json
{
  "ok": true,
  "keywords": ["wfm", "forecast", "schedule", "stale"],
  "candidates": [
    {
      "issue_id": "KI-WFM-002",
      "title": "WFM Schedule Not Auto-Regenerating",
      "score": 85,
      "symptoms": "...",
      "root_cause": "...",
      "solution": "..."
    }
  ],
  "selected_issue_id": "KI-WFM-002",
  "selected_context": {
    "issue": { ... },
    "affected": {
      "services": [ ... ],
      "customers": [ ... ],
      "features": [ ... ],
      "incidents": [ ... ]
    },
    "linked": {
      "runbooks": [
        {
          "runbook_id": "RUN-003",
          "title": "WFM Schedule Regeneration",
          "document": "data/Runbook_WFMScheduleStale.txt"
        }
      ],
      "documents": [ ... ],
      "sops": [ ... ],
      "faqs": [ ... ]
    }
  }
}
```

## Troubleshooting

### Issue: "Failed to connect to API"

**Check:**
1. FastAPI server is running: `http://127.0.0.1:8000/health`
2. No CORS errors in browser console
3. Port 8000 is not blocked by firewall

### Issue: "No candidates found"

**Check:**
1. Neo4j database is running: `docker ps`
2. Database was seeded: Check in Neo4j Browser
3. Query contains relevant keywords

### Issue: "Failed to load document"

**Check:**
1. HTTP server is running on port 8080
2. Document files exist in `data/` folder
3. Runbook/Document nodes have correct `document`/`url` properties
4. File paths are relative: `data/Runbook_*.txt`

### Issue: API server won't start

**Error:** `python api/main.py` exits with code 1

**Solution:** Use uvicorn instead:
```powershell
python -m uvicorn api.main:app --reload --port 8000
```

## Related Files

- [support_agent.html](support_agent.html) - Alternative LLM-powered interface
- [graph_explorer.html](graph_explorer.html) - Interactive graph visualization
- [index.html](index.html) - Dashboard/landing page

## Development

### Modifying the UI

Edit [resolve_issue.html](resolve_issue.html):
- Styles are inline in `<style>` section
- JavaScript is in `<script>` section
- No build process required - just reload browser

### Modifying the Backend

Edit API endpoints in:
- `api/routes/resolve_issue.py` - Route handler
- `core/knowledge_graph/issue_router.py` - Core resolution logic
- `core/knowledge_graph/service_ccas.py` - Graph traversal

Restart FastAPI server after changes (auto-reloads with `--reload` flag).

### Adding New Known Issues

1. Create text file: `data/KnownIssue_NewIssue.txt`
2. Create Runbook file: `data/Runbook_NewIssue.txt`
3. Add to database via `scripts/kg_seed_ccas_poc.py` or Cypher:

```cypher
CREATE (ki:KnownIssue {
  issue_id: 'KI-NEW-001',
  title: 'New Issue Title',
  severity: 'P2',
  symptoms: 'Description of symptoms',
  root_cause: 'Root cause analysis',
  solution: 'Step-by-step solution',
  document: 'data/KnownIssue_NewIssue.txt'
})

CREATE (rb:Runbook {
  runbook_id: 'RUN-NEW-001',
  title: 'New Issue Recovery Procedure',
  document: 'data/Runbook_NewIssue.txt',
  estimated_time: '10 minutes'
})

CREATE (ki)-[:HAS_RUNBOOK]->(rb)
```

## Architecture Notes

### Keyword Extraction

The backend extracts keywords from the user's message using predefined categories:
- `outage`, `voice`, `chat`, `routing`, `copilot`, `wfm`, etc.

See `core/knowledge_graph/issue_router.py` for the full list.

### Scoring Algorithm

Candidates are scored based on:
- Keyword matches in issue title, symptoms, root cause
- Category relevance
- Historical frequency (if available)

### Graph Traversal

The system performs:
1. **1-hop traversal** from Known Issue to directly connected nodes
2. **2-hop traversal** to find indirectly related resources
3. **Deduplication** by unique identifiers (issue_id, runbook_id, etc.)

---

**Last Updated:** March 2026
