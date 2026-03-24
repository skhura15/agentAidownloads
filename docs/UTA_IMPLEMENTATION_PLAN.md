# Unified Troubleshooting Assistant (UTA) - Implementation Plan

## Document Information
| Field | Value |
|-------|-------|
| Version | 1.0 |
| Created | January 20, 2026 |
| Status | Draft - Awaiting Approval |

---

## 1. Executive Summary

The Unified Troubleshooting Assistant (UTA) is an intelligent support agent designed for Microsoft CCaaS (Contact Center as a Service) support engineers. It addresses three critical gaps in the current DfM Copilot:

1. **Unified Knowledge Retrieval** - Consolidates scattered documentation into one surface
2. **Diagnostic Workflows** - Provides step-by-step guided troubleshooting
3. **Configuration Checks** - Validates routing, licensing, permissions, and versions

---

## 2. Problem Statement

### Current State
Support engineers today rely on scattered documentation:
- SOPs in SharePoint
- Knowledge bases in internal wikis
- CCaaS product documentation
- Slack/Teams notes
- Migration guides
- Internal expert emails
- Tribal knowledge shared verbally

### Pain Points
| Pain Point | Impact |
|------------|--------|
| Search fatigue | Engineers spend 30-60 mins searching |
| Diagnostic uncertainty | No structured "what to do next" guidance |
| Over-reliance on seniors | New engineers cannot self-serve |
| Missed configurations | Common root causes are overlooked |
| Variability in troubleshooting | Inconsistent resolution approaches |

### DfM Copilot Gaps
- Does NOT unify all support intelligence
- Does NOT provide step-by-step troubleshooting
- Does NOT perform configuration guidance or checks

---

## 3. Solution Overview

### 3.1 Three Pillars of UTA

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    UNIFIED TROUBLESHOOTING ASSISTANT                     │
├───────────────────────┬───────────────────────┬─────────────────────────┤
│  UNIFIED KNOWLEDGE    │  DIAGNOSTIC           │  CONFIGURATION          │
│  RETRIEVAL            │  WORKFLOWS            │  CHECKS                 │
├───────────────────────┼───────────────────────┼─────────────────────────┤
│ • SOPs                │ • Step-by-step guides │ • Queue/Routing         │
│ • Playbooks           │ • Branching trees     │ • Licensing validation  │
│ • Known issues        │ • Error code mapping  │ • Connectivity checks   │
│ • Migration guides    │ • Expected outcomes   │ • Version compatibility │
│ • Release notes       │ • Tool/URL references │ • Permissions review    │
│ • Expert heuristics   │ • Failure actions     │ • Feature availability  │
└───────────────────────┴───────────────────────┴─────────────────────────┘
```

### 3.2 User Journey

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────────────────┐
│   ENGINEER  │────▶│ PASTE TICKET│────▶│         UTA ANALYZES            │
│   OPENS UI  │     │ DESCRIPTION │     │  • Parses issue signals         │
└─────────────┘     └─────────────┘     │  • Retrieves knowledge          │
                                        │  • Generates workflow           │
                                        │  • Produces config checks       │
                                        └─────────────────────────────────┘
                                                        │
                                                        ▼
                    ┌─────────────────────────────────────────────────────┐
                    │               STRUCTURED OUTPUT                      │
                    ├─────────────────────────────────────────────────────┤
                    │ A. Issue Understanding                              │
                    │ B. Knowledge Summary (SOPs, KBs)                    │
                    │ C. Diagnostic Workflow (Step-by-step)               │
                    │ D. Configuration Checks                             │
                    │ E. Expert Notes & Common Pitfalls                   │
                    └─────────────────────────────────────────────────────┘
```

---

## 4. Technical Architecture

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                              │
│                    (React Web App + Optional Copilot Studio)            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         PYTHON BACKEND (FastAPI)                         │
│  POST /api/uta/analyze  │  POST /api/uta/config  │  GET /api/uta/search │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    AGENT ORCHESTRATOR (Agentic Framework)                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ RAG Agent   │  │ Diagnostic  │  │ Config      │  │ Formatter   │    │
│  │ (Knowledge) │  │ Workflow    │  │ Validator   │  │ Agent       │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          AZURE AI FOUNDRY                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ Vector Index    │  │ Embeddings      │  │ LLM (GPT-4)     │         │
│  │ (RAG Search)    │  │ Model           │  │ Reasoning       │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Component Breakdown

| Layer | Component | Technology | Purpose |
|-------|-----------|------------|---------|
| UI | Web Application | React + TypeScript | Ticket input, result display |
| UI | Copilot Studio | Microsoft Copilot Studio | Teams/D365 integration (optional) |
| API | REST Endpoints | FastAPI (Python) | Request handling, routing |
| Agent | UTA Agent | Agentic Framework | Orchestration, tool execution |
| Agent | RAG Agent | Agentic Framework | Knowledge retrieval |
| Agent | Diagnostic Agent | Agentic Framework | Workflow generation |
| Agent | Config Agent | Agentic Framework | Configuration validation |
| AI | Vector Search | Azure AI Search | Semantic document retrieval |
| AI | Embeddings | Azure OpenAI | Text vectorization |
| AI | LLM | Azure OpenAI GPT-4 | Reasoning, generation |

### 4.3 Existing Codebase Leverage

The current workspace already has reusable components:

| Component | Existing File | Reuse Strategy |
|-----------|---------------|----------------|
| Base Agent | `agents/base_agent.py` | Extend for UTA agents |
| API Layer | `api/main.py` | Add UTA routes |
| Orchestrator | `orchestration/agent_orchestrator.py` | Register UTA agents |
| Azure OpenAI | `core/azure_openai_client.py` | Use for LLM calls |
| Config | `core/config_manager.py` | Add UTA config |
| Tools | `tools/tool_registry.py` | Register UTA tools |
| Prompts | `prompts/prompt_manager.py` | Add UTA prompts |
| Frontend | `ui/frontend/` | Add UTA page |

---

## 5. Implementation Phases

### Phase 1: Foundation (Week 1-2)

#### 1.1 Data Preparation & Ingestion
- [ ] Collect sample knowledge sources (SOPs, playbooks, KBs)
- [ ] Normalize documents to Markdown/text format
- [ ] Define metadata schema (category, version, feature_area, severity)
- [ ] Create chunking strategy (size: 512 tokens, overlap: 50 tokens)

#### 1.2 Azure AI Foundry Setup
- [ ] Create Azure AI Foundry project
- [ ] Deploy embedding model (text-embedding-ada-002)
- [ ] Create vector index
- [ ] Upload and index sample documents
- [ ] Test semantic search queries

#### 1.3 UTA Agent Core
- [ ] Create `uta/agents/uta_agent.py`
- [ ] Define agent capabilities and skills
- [ ] Implement issue signal extraction
- [ ] Implement scenario classification

### Phase 2: Backend Development (Week 2-3)

#### 2.1 UTA Tools
- [ ] `search_knowledge_base` - RAG retrieval tool
- [ ] `classify_issue` - Issue categorization tool
- [ ] `generate_diagnostics` - Workflow generation tool
- [ ] `validate_configuration` - Config check tool
- [ ] `interpret_error_code` - Error code mapping tool

#### 2.2 API Endpoints
- [ ] `POST /api/uta/analyze` - Main ticket analysis
- [ ] `POST /api/uta/config-check` - Configuration validation
- [ ] `GET /api/uta/knowledge/{query}` - Direct knowledge search
- [ ] `GET /api/uta/workflows/{category}` - Get workflow templates
- [ ] `GET /api/uta/error-codes/{code}` - Error code lookup

#### 2.3 Response Structure
```python
class UTAResponse:
    issue_understanding: IssueUnderstanding
    knowledge_summary: List[KnowledgeItem]
    diagnostic_workflow: DiagnosticWorkflow
    configuration_checks: List[ConfigCheck]
    expert_notes: List[ExpertNote]
    metadata: ResponseMetadata
```

### Phase 3: Diagnostic Workflows (Week 3-4)

#### 3.1 Workflow Templates by Category
- [ ] Routing Issues (queue flows, skills, overflow)
- [ ] Licensing Issues (SKU, feature access, tenant config)
- [ ] Migration Issues (version compatibility, upgrade steps)
- [ ] Connectivity Issues (network, health checks)
- [ ] UI/Feature Issues (session logs, browser, feature flags)

#### 3.2 Workflow Structure
```yaml
workflow:
  id: "routing-001"
  name: "Queue Routing Troubleshooting"
  category: "routing"
  steps:
    - step: 1
      action: "Validate customer environment details"
      description: "Confirm tenant, region, and product version"
      expected_outcome: "Environment details documented"
      tools: ["Admin Portal", "Tenant Info API"]
      on_failure: "Escalate to Tier 2 if environment cannot be verified"
    - step: 2
      action: "Check licensing constraints"
      # ... additional steps
```

#### 3.3 Decision Tree Logic
- [ ] Implement branching based on issue signals
- [ ] Create condition evaluators
- [ ] Build dynamic step sequencing

### Phase 4: Configuration Checks (Week 4-5)

#### 4.1 Configuration Categories
| Category | Checks |
|----------|--------|
| Queue & Routing | Queue membership, routing rules, overflow, working hours, skills |
| Licensing | Tenant SKU, feature access, feature flags |
| Connectivity | Browser, firewall, Azure region, service health |
| Version | Known bugs, feature availability, deprecated params |
| Environment | RBAC, DLP/Compliance, permissions |

#### 4.2 Rule Engine
- [ ] Define rule schema
- [ ] Implement rule evaluation logic
- [ ] Create rule-to-check mapping
- [ ] Build check result formatting

### Phase 5: Frontend Development (Week 5-6)

#### 5.1 UI Components
- [ ] Ticket input textarea with metadata fields
- [ ] Analysis trigger button
- [ ] Collapsible result sections
- [ ] Workflow step display with progress
- [ ] Configuration check cards
- [ ] Copy-to-clipboard functionality
- [ ] Regenerate/rephrase option

#### 5.2 UI Pages
- [ ] `/uta` - Main UTA page
- [ ] `/uta/knowledge` - Knowledge browser (optional)
- [ ] `/uta/workflows` - Workflow templates (optional)

### Phase 6: Integration & Testing (Week 6-7)

#### 6.1 Integration
- [ ] End-to-end flow testing
- [ ] API contract validation
- [ ] Agent orchestration testing
- [ ] RAG quality evaluation

#### 6.2 User Testing
- [ ] Internal dogfooding
- [ ] Feedback collection
- [ ] Iteration on workflows

### Phase 7: Deployment (Week 7-8)

#### 7.1 Infrastructure
- [ ] Deploy backend to Azure App Service / Container Apps
- [ ] Deploy frontend to Azure Static Web Apps
- [ ] Configure Azure AI Foundry endpoints
- [ ] Set up monitoring and logging

#### 7.2 Security
- [ ] Azure AD authentication
- [ ] API key management
- [ ] Access control configuration

---

## 6. Directory Structure

```
uta/
├── docs/
│   └── IMPLEMENTATION_PLAN.md          # This document
├── agents/
│   ├── __init__.py
│   ├── uta_agent.py                    # Main UTA agent
│   ├── rag_agent.py                    # Knowledge retrieval agent
│   ├── diagnostic_agent.py             # Workflow generation agent
│   └── config_agent.py                 # Configuration validation agent
├── tools/
│   ├── __init__.py
│   ├── knowledge_search.py             # RAG search tool
│   ├── issue_classifier.py             # Issue classification tool
│   ├── diagnostic_generator.py         # Workflow generator tool
│   ├── config_validator.py             # Config validation tool
│   └── error_code_interpreter.py       # Error code lookup tool
├── api/
│   ├── __init__.py
│   ├── routes.py                       # UTA API endpoints
│   └── models.py                       # Request/response models
├── workflows/
│   ├── routing.yaml                    # Routing issue workflows
│   ├── licensing.yaml                  # Licensing issue workflows
│   ├── migration.yaml                  # Migration issue workflows
│   ├── connectivity.yaml               # Connectivity issue workflows
│   └── ui_features.yaml                # UI/Feature issue workflows
├── config_rules/
│   ├── routing_rules.yaml              # Routing config checks
│   ├── licensing_rules.yaml            # Licensing config checks
│   ├── connectivity_rules.yaml         # Connectivity config checks
│   └── version_rules.yaml              # Version config checks
├── prompts/
│   ├── issue_understanding.yaml        # Issue parsing prompt
│   ├── knowledge_summary.yaml          # Knowledge synthesis prompt
│   ├── diagnostic_generation.yaml      # Workflow generation prompt
│   └── config_check.yaml               # Config validation prompt
├── knowledge/
│   ├── sample_sops/                    # Sample SOP documents
│   ├── sample_playbooks/               # Sample playbooks
│   └── error_codes.json                # Error code mappings
└── tests/
    ├── __init__.py
    ├── test_uta_agent.py
    ├── test_tools.py
    └── test_api.py
```

---

## 7. API Specification

### 7.1 Analyze Ticket

**Endpoint:** `POST /api/uta/analyze`

**Request:**
```json
{
  "ticket_description": "Customer reports calls not routing to agents. Queue shows 15 calls waiting but agents are available. Started after upgrade to v2.5.3.",
  "product_area": "routing",
  "version": "2.5.3",
  "environment": "production",
  "priority": "high"
}
```

**Response:**
```json
{
  "issue_understanding": {
    "summary": "Call routing failure post-upgrade",
    "signals": ["calls not routing", "queue waiting", "agents available", "post-upgrade"],
    "category": "routing",
    "severity": "high",
    "confidence": 0.92
  },
  "knowledge_summary": [
    {
      "source": "SOP-ROUTING-045",
      "title": "Queue Routing Troubleshooting",
      "relevance": 0.95,
      "key_points": ["Check queue membership", "Validate routing rules", "Review overflow settings"],
      "link": "https://internal.wiki/sop-routing-045"
    }
  ],
  "diagnostic_workflow": {
    "id": "routing-001",
    "name": "Queue Routing Troubleshooting",
    "steps": [
      {
        "step": 1,
        "action": "Verify queue configuration",
        "description": "Check if queue is enabled and agents are assigned",
        "expected_outcome": "Queue active with assigned agents",
        "tools": ["Admin Portal > Queues"],
        "on_failure": "Proceed to step 2"
      }
    ]
  },
  "configuration_checks": [
    {
      "category": "routing",
      "check": "Queue membership validation",
      "description": "Verify agents are assigned to the queue",
      "priority": "high",
      "how_to_check": "Admin Portal > Queues > [Queue Name] > Members"
    }
  ],
  "expert_notes": [
    {
      "note": "v2.5.3 has a known issue with skill-based routing. Check KB-2023-1145.",
      "source": "SME Advisory"
    }
  ],
  "metadata": {
    "processing_time_ms": 1250,
    "model_version": "gpt-4",
    "rag_sources_consulted": 12
  }
}
```

---

## 8. Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Agent Pattern | Multi-agent | Separation of concerns, easier testing |
| RAG Backend | Azure AI Search | Production-ready, scalable, integrated with Azure |
| Diagnostic Logic | Hybrid (LLM + Rules) | LLM for reasoning, rules for deterministic checks |
| UI Framework | React (existing) | Leverage existing frontend codebase |
| Copilot Studio | Phase 2 | Focus on web UI first, add Teams later |
| Knowledge Format | YAML + Markdown | Human-readable, version-controllable |

---

## 9. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to first actionable step | < 30 seconds | API response time |
| Knowledge retrieval accuracy | > 85% | User feedback ratings |
| Workflow completion rate | > 70% | Step completion tracking |
| Config check relevance | > 80% | User confirmation |
| Engineer satisfaction | > 4.0/5.0 | Survey scores |
| Resolution time reduction | 20% | Before/after comparison |

---

## 10. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Poor RAG quality | High | Medium | Iterative tuning, feedback loop |
| Workflow gaps | Medium | Medium | Start with top 5 categories, expand |
| LLM hallucination | High | Low | Guardrails, confidence thresholds |
| Azure AI Foundry setup delays | Medium | Low | Fallback to local vector store |
| User adoption | Medium | Medium | Training, documentation, champions |

---

## 11. Next Steps

1. **Review and approve this plan**
2. **Set up Azure AI Foundry project** (if not already done)
3. **Collect sample knowledge documents** for POC
4. **Begin Phase 1 implementation**

---

## 12. Appendix

### A. Sample Issue Categories

| Category | Example Signals |
|----------|-----------------|
| Routing | "calls not routing", "queue not picking", "overflow issues" |
| Licensing | "feature not available", "license error", "SKU mismatch" |
| Migration | "after upgrade", "version compatibility", "missing feature" |
| Connectivity | "network error", "timeout", "cannot connect" |
| UI/Feature | "button not working", "page not loading", "preview feature" |

### B. Error Code Format

```json
{
  "error_codes": {
    "ERR-QUEUE-001": {
      "meaning": "Queue capacity exceeded",
      "common_causes": ["High call volume", "Agents unavailable"],
      "recommended_actions": ["Check queue capacity settings", "Add agents to queue"],
      "kb_article": "KB-2023-0567"
    }
  }
}
```

### C. Configuration Check Schema

```yaml
check:
  id: "CHK-ROUTING-001"
  category: "routing"
  name: "Queue Membership Validation"
  description: "Verify agents are assigned to the queue"
  priority: "high"
  applicable_when:
    - signal: "calls not routing"
    - signal: "queue issues"
  how_to_check: "Admin Portal > Queues > [Queue Name] > Members"
  expected_result: "At least one agent assigned and available"
  common_failures:
    - "No agents assigned"
    - "Agents assigned but offline"
```

---

*End of Implementation Plan*
