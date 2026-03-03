# 🗺️ Support AI Agent — Project Roadmap

> **Project:** Support AI Agent for Microsoft Dynamics 365 Contact Center (CCaaS)  
> **Team:** AI CoE, HCLTech ISL  
> **Duration:** 4 Weeks (POC)  
> **Developer Level:** New to the stack (Python, Knowledge Graphs, LLM, Azure)  
> **Goal:** Deliver a working POC that demonstrates AI-powered support ticket resolution using Knowledge Graph traversal + LLM, deployed on Azure, ready for future Azure OpenAI integration.

---

## 📌 Table of Contents

1. [Current State of the Project](#1-current-state-of-the-project)
2. [Architecture & AI Agent Flow](#2-architecture--ai-agent-flow)
3. [Pending Development Features](#3-pending-development-features)
4. [Simulated Data Requirements](#4-simulated-data-requirements)
5. [Week-by-Week Plan](#5-week-by-week-plan)
6. [Azure Deployment Plan](#6-azure-deployment-plan)
7. [Future Roadmap (Post-POC)](#7-future-roadmap-post-poc)
8. [Key Deliverables Summary](#8-key-deliverables-summary)

---

## 1. Current State of the Project

### What's Built ✅

| Component | File(s) | Status |
|-----------|---------|--------|
| Knowledge Graph (JSON) | `knowledge_graph.json` | ✅ 62 nodes, 95 edges, 16 node types |
| Sample Documents | `data/` (13 files) | ✅ SPOs, Release Notes, User Guides, Known Issues, Runbooks, SOPs |
| Python Backend | `server.py` (~757 lines) | ✅ HTTP server, graph traversal, Ollama LLM integration, streaming SSE |
| Chat UI | `support_agent.html` | ✅ Dark theme, sample tickets, context panel, streaming response |
| Graph Viewer | `graph_explorer.html` | ✅ D3.js force-directed graph, search, filter by node type |
| Dashboard | `index.html` | ✅ Landing page with links to Agent & Graph Explorer |

### Tech Stack (Current)

| Layer | Technology |
|-------|------------|
| Frontend | Vanilla HTML/CSS/JS, D3.js v7 |
| Backend | Python 3.12 (stdlib only — `http.server`, `urllib`) |
| LLM | Ollama (local) — `gemma3:4b` model |
| Data | Static JSON knowledge graph + text documents |
| Deployment | Local only (`localhost:8080`) |

---

## 2. Architecture & AI Agent Flow

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     USER (Support Engineer)                  │
│              Enters ticket text / selects sample             │
└──────────────────┬───────────────────────────────────────────┘
                   │ POST /api/chat-stream
                   ▼
┌──────────────────────────────────────────────────────────────┐
│                  PYTHON BACKEND (server.py)                   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ Step 1: KEYWORD EXTRACTION                          │     │
│  │   • Parse ticket text                               │     │
│  │   • Match against 16 CCaaS keyword categories       │     │
│  │   • Output: keyword list (e.g., voice, routing)     │     │
│  └──────────────┬──────────────────────────────────────┘     │
│                 ▼                                            │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ Step 2: KNOWLEDGE GRAPH TRAVERSAL                   │     │
│  │   • Score all 62 nodes by keyword match             │     │
│  │   • Take top-10 nodes                               │     │
│  │   • Follow edges to neighbors (both directions)     │     │
│  │   • Collect: Services, Known Issues, Runbooks,      │     │
│  │     SOPs, FAQs, Experts, Past Incidents, Documents  │     │
│  │   • Read linked .txt documents (capped at 1000ch)   │     │
│  └──────────────┬──────────────────────────────────────┘     │
│                 ▼                                            │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ Step 3: PROMPT CONSTRUCTION                         │     │
│  │   • System role: "Support AI Agent for MS CCaaS"    │     │
│  │   • Ticket text + keywords                          │     │
│  │   • Structured sections: Known Issues, Runbooks,    │     │
│  │     FAQs, SOPs, Past Incidents, Experts, Services   │     │
│  │   • Up to 2 document excerpts (500 chars each)      │     │
│  │   • Instructions: Root Cause, Steps, Escalation     │     │
│  └──────────────┬──────────────────────────────────────┘     │
│                 ▼                                            │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ Step 4: LLM CALL (Streaming)                        │     │
│  │   • POST to Ollama /api/generate (stream: true)     │     │
│  │   • Model: gemma3:4b | temp: 0.3 | max: 1024 tok   │     │
│  │   • Tokens streamed back via SSE                    │     │
│  └──────────────┬──────────────────────────────────────┘     │
│                 ▼                                            │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ Step 5: RESPONSE DELIVERY                           │     │
│  │   • SSE events: context → token → token → done      │     │
│  │   • Frontend renders markdown incrementally         │     │
│  │   • Context panel shows graph traversal results     │     │
│  └─────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

### Fallback Mode (Graph-Only)

When the LLM toggle is OFF or Ollama is unavailable, the agent returns a **structured markdown response** built entirely from graph data — no LLM call. This ensures the system always provides value even without AI.

---

## 3. Pending Development Features

These are features that are **not yet implemented** and should be completed during the 4-week plan.

### 3.1 Backend Enhancements

| # | Feature | Priority | Description |
|---|---------|----------|-------------|
| B1 | **Conversation History** | 🔴 High | Current chat is single-turn. Add multi-turn context so the LLM remembers previous questions in the same session. Store last 3-5 exchanges and include them in the prompt. |
| B2 | **Ticket Classification** | 🔴 High | Auto-classify incoming tickets by severity (P1/P2/P3/P4) and category (Voice/Chat/Routing/Copilot) before graph traversal. Use keyword rules first, LLM refinement later. |
| B3 | **Graph Hot-Reload** | 🟡 Medium | Currently the knowledge graph is loaded once at server startup. Add a `/api/reload-graph` endpoint to reload `knowledge_graph.json` without restarting the server. |
| B4 | **Response Rating/Feedback** | 🟡 Medium | Add POST `/api/feedback` endpoint to log thumbs-up/down + optional comment for each response. Store in a `feedback.json` file. |
| B5 | **Structured Logging** | 🟡 Medium | Replace `print()` debug logs with Python `logging` module. Add log levels (DEBUG/INFO/WARN/ERROR). Write logs to `server.log` file. |
| B6 | **Error Handling Hardening** | 🟡 Medium | Add try/catch around graph traversal, document reading, JSON parsing. Return meaningful error messages to the frontend. |
| B7 | **Azure OpenAI Integration** | 🔴 High | Add support for Azure OpenAI as an alternative to Ollama. Environment variable toggle: `LLM_PROVIDER=ollama|azure_openai`. Use `openai` Python SDK. |
| B8 | **Health Dashboard Endpoint** | 🟢 Low | Enhance `/api/health` to return uptime, request count, average response time, last error. |
| B9 | **CORS Configuration** | 🟢 Low | Make CORS configurable via environment variable instead of hardcoded `*`. |
| B10 | **Rate Limiting** | 🟢 Low | Add basic rate limiting (e.g., max 10 requests/minute per IP) to prevent abuse. |

### 3.2 Frontend Enhancements

| # | Feature | Priority | Description |
|---|---------|----------|-------------|
| F1 | **Chat History Persistence** | 🔴 High | Save chat messages to `localStorage` so conversations survive page reload. Add "Clear Chat" button. |
| F2 | **Ticket Template Builder** | 🟡 Medium | Let users fill a structured form (Service, Severity, Description, Customer) instead of free-text only. Auto-compose the ticket text from the form. |
| F3 | **Graph Context Visualization** | 🟡 Medium | When the agent returns context, show a mini knowledge graph in the side panel highlighting the traversed nodes and edges (reuse D3.js from graph_explorer). |
| F4 | **Export Chat to PDF/Markdown** | 🟢 Low | "Export" button to download the current conversation as a `.md` or `.pdf` file for incident documentation. |
| F5 | **Dark/Light Theme Toggle** | 🟢 Low | Add a theme switcher. Currently hardcoded dark theme. |
| F6 | **Mobile Responsive Layout** | 🟢 Low | Make `support_agent.html` responsive for tablet/mobile screens. |
| F7 | **Typing Speed Indicator** | 🟢 Low | Show tokens-per-second and elapsed time during streaming responses. |

### 3.3 Knowledge Graph Enhancements

| # | Feature | Priority | Description |
|---|---------|----------|-------------|
| G1 | **Expand Node Count** | 🔴 High | Grow from 62 → 150+ nodes. Add more services, known issues, runbooks, FAQs, past incidents. |
| G2 | **Edge Weights** | 🟡 Medium | Add `weight` property to edges (0.0–1.0) so graph traversal can prioritize stronger relationships. |
| G3 | **Temporal Filtering** | 🟡 Medium | Add `created_date` and `valid_until` to nodes. Allow filtering by recency (e.g., only show known issues from last 90 days). |
| G4 | **Graph Validation Script** | 🟡 Medium | Python script to validate `knowledge_graph.json`: check for orphan nodes, missing required properties, broken edge references. |
| G5 | **Graph Import from CSV** | 🟢 Low | Tool to import nodes/edges from CSV files so non-developers can contribute data. |

---

## 4. Simulated Data Requirements

Since this is a **POC with simulated data**, the following data should be created to make the demo realistic and cover key support scenarios.

### 4.1 Additional Knowledge Graph Nodes to Create

| Category | Current Count | Target Count | What to Add |
|----------|--------------|--------------|-------------|
| Services | 8 | 12 | Add: Workforce Management, Quality Management, Customer Voice Survey, Omnichannel Provisioning |
| Known Issues | 3 | 10 | Add: SSO login failures, Sentiment analysis inaccuracy, Custom dashboard widget crash, Unified routing capacity mismatch, Voicemail transcription errors, WhatsApp template rejection, Copilot hallucination in summaries |
| Runbooks | 2 | 6 | Add: SSO Recovery, Chat Widget Emergency Fix, Copilot Reset Procedure, Data Migration Rollback |
| SOPs | 1 | 4 | Add: P2 Incident Handling, Customer Escalation Communication, Post-Incident Review, Change Request Process |
| FAQs | 3 | 10 | Add: "How to configure skills-based routing?", "How to enable Copilot for agents?", "How to set up WhatsApp channel?", "What are the SLA targets for voice?", "How to view real-time agent metrics?", "How to configure auto-assignment rules?", "How to integrate Customer Voice surveys?" |
| Experts | 3 | 6 | Add: AI/Copilot Specialist, Telephony Integration Lead, Customer Success Manager |
| Past Incidents | 2 | 6 | Add: Major routing outage (customer-impacting), Copilot service degradation, WhatsApp connector failure, Supervisor dashboard downtime |
| Customers | 3 | 5 | Add: Woodgrove Bank, Adventure Works |
| Infrastructure | 3 | 5 | Add: Azure Communication Services, Azure Bot Service |

### 4.2 Additional Document Files to Create

| File Name | Type | Content Description |
|-----------|------|---------------------|
| `data/KnownIssue_SSOLoginFailure.txt` | Known Issue | SSO SAML assertion timeout, affected environments, workaround steps |
| `data/KnownIssue_SentimentInaccuracy.txt` | Known Issue | AI sentiment model returning wrong scores for multi-language chats |
| `data/KnownIssue_UnifiedRoutingMismatch.txt` | Known Issue | Capacity profiles not updating in real-time |
| `data/KnownIssue_CopilotHallucination.txt` | Known Issue | Copilot summary referencing closed cases incorrectly |
| `data/Runbook_SSORecovery.txt` | Runbook | Step-by-step SSO recovery: check Entra ID, validate SAML, clear tokens |
| `data/Runbook_ChatWidgetFix.txt` | Runbook | Emergency chat widget restart procedure |
| `data/Runbook_CopilotReset.txt` | Runbook | Reset Copilot feature flags, clear cache, verify model endpoint |
| `data/SOP_P2_Incident.txt` | SOP | P2 incident handling: triage, communicate, resolve within 4 hours |
| `data/SOP_PostIncidentReview.txt` | SOP | PIR process: timeline, root cause, corrective actions, sign-off |
| `data/SOP_ChangeRequest.txt` | SOP | Change request process: submit, review, approve, implement, verify |
| `data/UserGuide_CopilotSetup.txt` | User Guide | How to enable and configure Copilot for agents |
| `data/UserGuide_WhatsAppChannel.txt` | User Guide | WhatsApp Business channel setup and template management |
| `data/ReleaseNotes_2026W1.txt` | Release Notes | Upcoming features: enhanced Copilot, new routing engine |

### 4.3 Simulated Ticket Scenarios to Add

Add these as sample buttons in the chat UI for compelling demos:

| # | Ticket Scenario | Expected Graph Hits |
|---|----------------|---------------------|
| T1 | "SSO login is failing for all agents at Contoso Corp. They see a SAML assertion error after Entra ID redirect. This is P1 — 200 agents cannot log in." | KnownIssue_SSO, Runbook_SSORecovery, SOP_P1_Escalation, Expert (Security) |
| T2 | "Copilot is generating incorrect case summaries. It's referencing cases from other customers. Fabrikam's compliance team is concerned." | KnownIssue_CopilotHallucination, Runbook_CopilotReset, Expert (AI Specialist) |
| T3 | "WhatsApp messages are not being delivered to agents. The channel shows as connected but messages queue up and never route." | KnownIssue (WhatsApp), Runbook_ChatWidgetFix, UserGuide_WhatsApp, Expert (Digital Channel) |
| T4 | "Supervisor real-time dashboard is showing stale data. Agent presence is not updating. Metrics show agents as 'available' but they are on calls." | KnownIssue (routing mismatch), UserGuide_Supervisor, Expert (Analytics) |
| T5 | "Post-call survey (Customer Voice) integration stopped working after the last release update." | ReleaseNotes, Service (Customer Voice), Runbook, SOP_PostIncidentReview |

---

## 5. Week-by-Week Plan

### 🏁 Prerequisites (Before Week 1)

The developer should have:
- [ ] Windows/Mac machine with Python 3.10+ installed
- [ ] VS Code with Python extension
- [ ] Git installed and configured
- [ ] Ollama installed locally (`ollama pull gemma3:4b`)
- [ ] Azure subscription access (for Week 3-4)
- [ ] Read access to this repository

---

### 📅 4-Week Execution Plan

| Week | Task | Details |
|------|------|---------|
| **Week 1** | Set up local environment | Clone repo, install Python 3.12, install Ollama, pull `gemma3:4b` model |
| | Run project locally | `python server.py` → open `localhost:8080` → test all 5 sample tickets |
| | Study `server.py` | Understand: `extract_keywords()`, `traverse_graph_for_ticket()`, `build_llm_prompt()`, `stream_ollama()`, `_handle_chat_stream()` |
| | Study `knowledge_graph.json` | Understand node/edge schema, 16 node types, 22 edge types. Sketch the graph on paper |
| | Study frontend files | Understand SSE streaming in `support_agent.html` and D3.js in `graph_explorer.html` |
| | Add new Services | Add 4 services: Workforce Management, Quality Management, Customer Voice, Omnichannel Provisioning |
| | Add new Known Issues | Add 7 known issues (SSO failure, sentiment inaccuracy, routing mismatch, Copilot hallucination, etc.) |
| | Add new Runbooks + SOPs | Add 4 runbooks (SSO Recovery, Chat Widget Fix, Copilot Reset, Data Migration Rollback) + 3 SOPs |
| | Add FAQs, Experts, Customers, Incidents | Add 7 FAQs, 3 experts, 2 customers, 4 past incidents + connect all new edges |
| | Verify expanded graph | Restart server, check `/api/graph-stats`, browse in Graph Explorer |
| | Create 13 new document files | Realistic content for all new nodes in `data/` folder (see Section 4.2) |
| | Add 5 new sample ticket buttons | SSO, Copilot, WhatsApp, Supervisor, Customer Voice scenarios (see Section 4.3) |
| | End-to-end test all scenarios | Submit each ticket, verify graph hits + LLM response quality |
| | **Week 1 Deliverables** | ✅ Developer understands full codebase · ✅ 150+ nodes, 180+ edges · ✅ 26 documents · ✅ 10 sample tickets working |
| **Week 2** | Conversation history (B1) | Store last 5 messages per session, include in LLM prompt. Generate session UUID in frontend. Test multi-turn chats. |
| | Ticket classification (B2) | Auto-classify severity (P1-P4) + category (Voice/Chat/Routing/Copilot). Show badge in chat UI. |
| | Response feedback (B4) | POST `/api/feedback` endpoint for 👍/👎 ratings. Store in `feedback.json`. Add buttons to UI. |
| | Chat persistence (F1) | Save/restore chat from `localStorage`. Add "Clear Chat" button. |
| | Structured logging (B5) | Replace `print()` with Python `logging` module. Write to `server.log`. Log all requests. |
| | Graph hot-reload (B3) | POST `/api/reload-graph` endpoint to reload JSON without server restart. Add reload button. |
| | Graph validation script (G4) | Create `validate_graph.py` — check orphan nodes, missing properties, broken edges, duplicate IDs. |
| | Ticket template builder (F2) | Modal form with Service dropdown, Severity radio, Customer dropdown. Auto-compose ticket text. |
| | Error handling hardening (B6) | Try/catch all handlers. Return 500 with error JSON. Test: Ollama down, bad JSON, missing files. |
| | **Week 2 Deliverables** | ✅ Multi-turn conversations · ✅ Auto classification · ✅ Feedback system · ✅ Chat persistence · ✅ Logging · ✅ Graph reload + validation · ✅ Ticket form · ✅ Error handling |
| **Week 3** | Azure OpenAI integration (B7) | Create `llm_provider.py` with `OllamaProvider` + `AzureOpenAIProvider`. Toggle via `LLM_PROVIDER` env var. Use `openai` SDK. |
| | Azure provisioning | Create Resource Group, Azure OpenAI (GPT-4o-mini), App Service Plan (B1), App Service (Python 3.12). Configure env vars. |
| | Test Azure OpenAI locally | Set env vars, switch provider, verify chat works with Azure OpenAI. |
| | Migrate to Flask | Replace `http.server` with Flask. Create `requirements.txt`. SSE via `Response(stream_with_context(...))`. Create `.env.example`. |
| | Test locally with Flask | Verify all endpoints: `/api/chat-stream`, `/api/health`, `/api/graph-stats`, etc. |
| | Deploy to Azure | `az webapp up` or VS Code extension. Configure startup command. Test all tickets on Azure URL. Fix deployment issues. |
| | Security + monitoring | Enable Entra ID authentication. Set up Application Insights. Move keys to Key Vault. Create Monitor alerts. |
| | Deployment documentation | Write `DEPLOYMENT.md` with step-by-step deployment guide. |
| | **Week 3 Deliverables** | ✅ Azure OpenAI working · ✅ Flask migration · ✅ Deployed on Azure · ✅ SSE streaming on Azure · ✅ Entra ID auth · ✅ App Insights · ✅ DEPLOYMENT.md |
| **Week 4** | Graph context visualization (F3) | Mini D3.js graph in side panel showing traversed nodes/edges. Color-code matched (green) vs neighbor (blue). Click for details. |
| | End-to-end testing | Test all 10 tickets, conversation history, feedback flow, graph reload, Azure OpenAI provider. Fix all bugs. |
| | Performance optimization | Pre-index nodes by keyword for faster lookup. Add response caching with TTL. Basic load test (10 concurrent requests). |
| | Verify Azure performance | Benchmark streaming: Browser → Azure App Service → Azure OpenAI round-trip. |
| | Documentation | Write `README.md` (architecture, setup, API reference). Create demo script with 5 scenarios. Create architecture diagram. |
| | Code cleanup + handoff | Remove dead code, add docstrings. Run `validate_graph.py`. Deploy final version. Demo dry-run. Tag `v1.0-poc`. |
| | **Week 4 Deliverables** | ✅ Graph visualization · ✅ All scenarios tested · ✅ Performance optimized · ✅ README + demo script + diagram · ✅ Final Azure deploy · ✅ Release v1.0-poc |

---

## 6. Azure Deployment Plan

### Target Azure Architecture

```
┌──────────────────────────────────────────────────────┐
│                    Azure Cloud                        │
│                                                      │
│  ┌──────────────┐    ┌─────────────────────────┐     │
│  │ Azure App    │    │ Azure OpenAI Service     │     │
│  │ Service      │───▶│ (GPT-4o-mini)           │     │
│  │ (Python/Flask│    │                         │     │
│  │  + KG JSON)  │    └─────────────────────────┘     │
│  └──────┬───────┘                                    │
│         │            ┌─────────────────────────┐     │
│         │            │ Azure Key Vault          │     │
│         │            │ (API keys, secrets)      │     │
│         │            └─────────────────────────┘     │
│         │                                            │
│         │            ┌─────────────────────────┐     │
│         │            │ Application Insights     │     │
│         └───────────▶│ (Monitoring, traces)     │     │
│                      └─────────────────────────┘     │
│                                                      │
│  ┌─────────────────────────────────────────────┐     │
│  │ Entra ID (Authentication)                    │     │
│  └─────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────┘
```

### Azure Resources Required

| Resource | SKU/Tier | Estimated Monthly Cost |
|----------|----------|----------------------|
| App Service Plan | B1 (Basic) | ~$13/month |
| App Service | Python 3.12 | Included in plan |
| Azure OpenAI | GPT-4o-mini | ~$5-15/month (POC usage) |
| Key Vault | Standard | ~$0.03/month |
| Application Insights | Free tier | $0 (up to 5GB/month) |
| **Total** | | **~$20-30/month** |

### Environment Variables for Azure

```env
# LLM Provider (ollama or azure_openai)
LLM_PROVIDER=azure_openai

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_KEY=<your-key>  # Or use Key Vault reference
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Ollama (for local dev)
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=gemma3:4b

# App Config
PORT=8080
LOG_LEVEL=INFO
```

---

## 7. Future Roadmap (Post-POC)

These are features for **after the 4-week POC**, when the project graduates to a production pilot.

| Phase | Feature | Description |
|-------|---------|-------------|
| **Phase 2** | Neo4j Graph Database | Migrate from JSON to Neo4j for real-time graph queries, Cypher query language, and scalability beyond 1000 nodes |
| **Phase 2** | RAG with Azure AI Search | Index all documents in Azure AI Search. Use vector embeddings for semantic retrieval instead of keyword matching. |
| **Phase 2** | Real Ticket Integration | Connect to ServiceNow / Dynamics 365 via API to pull real support tickets instead of simulated ones |
| **Phase 2** | Agent Orchestration | Use Semantic Kernel or LangChain to orchestrate multi-step agent workflows (classify → search → retrieve → generate → validate) |
| **Phase 3** | Feedback Loop Training | Use stored feedback to fine-tune prompts or create few-shot examples for improved response quality |
| **Phase 3** | Multi-tenant Support | Isolate knowledge graphs per customer/project for multi-tenant SaaS deployment |
| **Phase 3** | Teams Integration | Embed the Support AI Agent as a Microsoft Teams bot for direct access from the support engineer's daily tool |
| **Phase 3** | Automated Runbook Execution | Instead of just suggesting runbook steps, actually execute safe automated remediation steps via Azure Automation |

---

## 8. Key Deliverables Summary

### 4-Week Outcome

| Week | Focus | Key Deliverable |
|------|-------|-----------------|
| **Week 1** | Learn + Data | Developer understands code; graph expanded to 150+ nodes; 10 sample tickets |
| **Week 2** | Features | Conversation history, ticket classification, feedback, chat persistence, logging, graph validation |
| **Week 3** | Azure | Azure OpenAI integration, Flask migration, deployed on Azure App Service, Entra ID auth |
| **Week 4** | Polish + Demo | Graph visualization, testing, caching, documentation, demo-ready, release tagged |

### Final POC Capabilities

At the end of 4 weeks, the POC will demonstrate:

1. ✅ **Knowledge Graph Traversal** — 150+ node graph covering services, known issues, runbooks, experts, incidents
2. ✅ **AI-Powered Ticket Resolution** — LLM generates step-by-step solutions grounded in graph data
3. ✅ **Streaming Responses** — Real-time token-by-token display (no waiting 30-90 seconds)
4. ✅ **Multi-Turn Conversations** — LLM remembers context from previous messages
5. ✅ **Auto Classification** — Severity and category auto-detected from ticket text
6. ✅ **Dual LLM Support** — Toggle between local Ollama and Azure OpenAI
7. ✅ **Interactive Graph Explorer** — D3.js visualization of the full knowledge graph
8. ✅ **Azure Deployed** — Accessible via Azure App Service with Entra ID authentication
9. ✅ **Monitored** — Application Insights for performance tracking
10. ✅ **Documented** — README, deployment guide, architecture diagram, demo script

---

> **Note for Developer:** Start with Week 1 Day 1. Don't skip the code reading phase — understanding the existing graph traversal and prompt construction is essential before adding features. Ask questions early. Commit daily. Test after every change.
