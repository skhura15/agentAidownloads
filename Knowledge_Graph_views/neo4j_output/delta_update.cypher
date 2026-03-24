// ========================================
// Knowledge Graph DELTA Update - Cypher Queries
// Generated: 2026-03-06 19:22:19
// New Nodes: 47, Updated: 2, Deleted: 22
// New Edges: 81, Deleted: 0
// ========================================

// --- ADD NEW NODES ---

CREATE (n:Service {id: 'SVC-001', label: 'Omnichannel Voice', tags: ["Voice", "ACS", "IVR", "Recording"], service_id: 'CCaaS-VOICE', description: 'Inbound/outbound voice channel with Azure Communication Services integration, IVR, call recording, real-time transcription, and sentiment analysis.', status: 'Active', criticality: 'P1', sla_uptime: '99.99%', technology_stack: ["Azure Communication Services", "Azure Speech", "Teams"], port_requirements: 'UDP 3478-3481, TCP 443'});
CREATE (n:Service {id: 'SVC-002', label: 'Unified Routing', tags: ["Routing", "AI Classification", "Skills-Based"], service_id: 'CCaaS-ROUTING', description: 'AI-powered intelligent routing engine that classifies and routes work items (calls, chats, emails, cases) to the best-suited agent based on skills, capacity, presence, and sentiment.', status: 'Active', criticality: 'P1', sla_uptime: '99.95%', technology_stack: ["Dataverse", "Azure ML", "Power Platform"]});
CREATE (n:Service {id: 'SVC-003', label: 'Digital Messaging', tags: ["Chat", "SMS", "WhatsApp", "Messenger"], service_id: 'CCaaS-MESSAGING', description: 'Live chat, SMS, WhatsApp, Facebook Messenger, Apple Messages, and custom messaging channels for digital customer engagement.', status: 'Active', criticality: 'P2', sla_uptime: '99.95%', technology_stack: ["Azure Bot Service", "Dataverse", "WebSocket"]});
CREATE (n:Service {id: 'SVC-004', label: 'Copilot for Agents', tags: ["Copilot", "AI", "GPT", "Summarization"], service_id: 'CCaaS-COPILOT', description: 'AI-powered assistant embedded in the agent desktop. Provides real-time suggestions, knowledge article recommendations, case summarization, response drafting, and sentiment-informed guidance.', status: 'Active', criticality: 'P2', sla_uptime: '99.90%', technology_stack: ["Azure OpenAI", "Dataverse", "Knowledge Base"]});
CREATE (n:Service {id: 'SVC-005', label: 'Agent Desktop (Workspace)', tags: ["Agent Desktop", "Workspace", "Unified"], service_id: 'CCaaS-DESKTOP', description: 'Unified agent workspace built on Dynamics 365, providing a single pane of glass for handling conversations, customer context, knowledge search, and case management.', status: 'Active', criticality: 'P1', sla_uptime: '99.95%', technology_stack: ["Dynamics 365", "Power Apps", "Dataverse"]});
CREATE (n:Service {id: 'SVC-006', label: 'Real-Time Analytics', tags: ["Analytics", "Dashboards", "Power BI", "CSAT"], service_id: 'CCaaS-ANALYTICS', description: 'Real-time and historical dashboards for supervisors. Includes agent performance, queue metrics, sentiment trends, CSAT scores, and SLA adherence.', status: 'Active', criticality: 'P2', sla_uptime: '99.90%', technology_stack: ["Power BI", "Azure Data Lake", "Dataverse"]});
CREATE (n:Service {id: 'SVC-007', label: 'Knowledge Management', tags: ["Knowledge Base", "Articles", "Search"], service_id: 'CCaaS-KM', description: 'Centralized knowledge base with article authoring, version control, search, and AI-powered suggestions integrated into agent workspace and Copilot.', status: 'Active', criticality: 'P2', technology_stack: ["Dataverse", "Azure Search", "Dynamics 365"]});
CREATE (n:Service {id: 'SVC-008', label: 'Power Virtual Agents (Bot)', tags: ["Bot", "IVR", "Self-Service", "Copilot Studio"], service_id: 'CCaaS-BOT', description: 'Self-service IVR and chatbot built on Copilot Studio. Handles common queries, collects customer info before handoff, and escalates to live agent with full context.', status: 'Active', criticality: 'P2', technology_stack: ["Copilot Studio", "Azure Bot Service", "Power Automate"]});
CREATE (n:Service {id: 'SVC-009', label: 'Workforce Management', tags: ["WFM", "Scheduling", "Forecasting", "Adherence"], service_id: 'CCaaS-WFM', description: 'Comprehensive workforce management solution for contact centers. Provides forecasting, agent scheduling, intraday management, real-time adherence monitoring, and shift bidding. Integrates with unified routing and real-time analytics.', status: 'Active', criticality: 'P2', sla_uptime: '99.90%', technology_stack: ["Dataverse", "Power Platform", "Azure ML", "Power BI"]});
CREATE (n:SPO {id: 'SPO-001', label: 'CCaaS Enterprise License', tags: ["Enterprise", "Full Suite"], spo_code: 'MS-CCaaS-ENT-2025', description: 'Full Microsoft Dynamics 365 Contact Center Enterprise license with omnichannel voice+digital, Copilot, unified routing, analytics, and 24/7 premier support.', pricing_model: 'Per agent/month', price_usd: '$110/agent/month', included_channels: ["Voice", "Chat", "SMS", "WhatsApp", "Email", "Social"], sla_tier: 'Premier', document: 'data/SPO_CCaaS_Enterprise.txt'});
CREATE (n:SPO {id: 'SPO-002', label: 'CCaaS Digital Only License', tags: ["Digital", "No Voice"], spo_code: 'MS-CCaaS-DIG-2025', description: 'Digital-only license. Includes chat, SMS, social channels, unified routing for digital, and Copilot. Voice channel excluded.', pricing_model: 'Per agent/month', price_usd: '$65/agent/month', included_channels: ["Chat", "SMS", "WhatsApp", "Email", "Social"], sla_tier: 'Standard', document: 'data/SPO_CCaaS_Digital.txt'});
CREATE (n:ReleaseNote {id: 'RN-001', label: '2025 Wave 2 Release Notes', tags: ["2025W2", "Copilot", "Voice", "Translation"], version: '2025 Release Wave 2', release_date: '2025-10-01', highlights: ["Copilot autonomous actions", "Enhanced voice quality with ACS v2", "Real-time translation 50+ languages", "Supervisor Copilot", "Priority-based overflow queues"], document: 'data/ReleaseNotes_2025W2.txt'});
CREATE (n:ReleaseNote {id: 'RN-002', label: '2025 Wave 1 Release Notes', tags: ["2025W1", "Analytics", "WhatsApp"], version: '2025 Release Wave 1', release_date: '2025-04-01', highlights: ["Enhanced real-time analytics", "WhatsApp Business API v2", "Copilot case summarization GA", "Outbound dialer preview", "Sentiment-based routing"], document: 'data/ReleaseNotes_2025W1.txt'});
CREATE (n:UserGuide {id: 'UG-001', label: 'Agent Desktop User Guide', tags: ["Agent", "Desktop", "Guide"], title: 'Dynamics 365 Contact Center — Agent Desktop User Guide', audience: 'Contact Center Agents', pages: 45, topics: ["Login & Presence", "Handling Conversations", "Customer Context", "Knowledge Search", "Case Management", "Copilot Usage"], document: 'data/UserGuide_AgentDesktop.txt'});
CREATE (n:UserGuide {id: 'UG-002', label: 'Supervisor Dashboard Guide', tags: ["Supervisor", "Dashboard", "Analytics"], title: 'Dynamics 365 Contact Center — Supervisor Dashboard Guide', audience: 'Supervisors & Managers', pages: 28, topics: ["Real-Time Monitoring", "Agent Performance", "Queue Metrics", "Sentiment Dashboard", "Whisper & Monitor", "Reports Export"], document: 'data/UserGuide_Supervisor.txt'});
CREATE (n:UserGuide {id: 'UG-003', label: 'Unified Routing Admin Guide', tags: ["Admin", "Routing", "Configuration"], title: 'Dynamics 365 Contact Center — Unified Routing Configuration Guide', audience: 'Administrators', pages: 52, topics: ["Workstreams", "Queues", "Routing Rules", "Skills-Based Routing", "Capacity Profiles", "Overflow Rules", "Assignment Methods"], document: 'data/UserGuide_RoutingAdmin.txt'});
CREATE (n:UserGuide {id: 'UG-004', label: 'WFM Admin Guide', tags: ["WFM", "Admin", "Guide"], title: 'Dynamics 365 Contact Center — Workforce Management Guide', audience: 'WFM Administrators & Supervisors', pages: 38, topics: ["Forecasting Model Setup", "Schedule Generation", "Agent Shift Bidding", "Real-Time Adherence", "Intraday Management", "Reports"], document: 'data/UserGuide_WFM.txt'});
CREATE (n:KnownIssue {id: 'KI-001', label: 'Voice call drops during transfer', tags: ["Voice", "Transfer", "P1", "ACS"], issue_id: 'KI-2025-001', severity: 'P1', affected_versions: ["2025 Wave 1", "2025 Wave 2"], symptoms: ["Call drops when agent initiates warm transfer", "Customer hears dead air for 3-5 seconds before disconnect", "Transfer failure logged in ACS"], root_cause: 'Race condition in Azure Communication Services session handoff when both agents are in different Azure regions.', workaround: 'Ensure both agents are in the same Azure region. Use cold transfer instead of warm transfer until patch is applied.', status: 'Fix in Progress', eta_fix: '2026-03-15', document: 'data/KnownIssue_VoiceTransferDrop.txt'});
CREATE (n:KnownIssue {id: 'KI-002', label: 'Copilot suggestions delayed > 10s', tags: ["Copilot", "Latency", "P2", "Azure OpenAI"], issue_id: 'KI-2025-002', severity: 'P2', affected_versions: ["2025 Wave 2"], symptoms: ["Copilot response time exceeds 10 seconds", "Agent sees spinning indicator for extended period", "Intermittent timeouts during peak hours"], root_cause: 'Azure OpenAI throttling when tenant exceeds TPM quota during peak load.', workaround: 'Request Azure OpenAI quota increase via Azure Portal. Enable Copilot response caching for common queries.', status: 'Workaround Available', document: 'data/KnownIssue_CopilotDelay.txt'});
CREATE (n:KnownIssue {id: 'KI-003', label: 'Chat widget not loading on Safari', tags: ["Chat", "Safari", "Cookies", "ITP"], issue_id: 'KI-2025-003', severity: 'P2', affected_versions: ["2025 Wave 2"], symptoms: ["Live chat widget fails to render on Safari 17+", "Console shows SecurityError blocked frame", "Affects iOS and macOS Safari"], root_cause: 'Safari ITP blocks third-party cookies needed for chat session authentication.', workaround: 'Enable first-party cookie mode in chat widget config. Set cookieDomain to customer\'s own domain.', status: 'Workaround Available', document: 'data/KnownIssue_SafariChat.txt'});
CREATE (n:Runbook {id: 'RB-001', label: 'Voice Channel Outage Recovery', tags: ["Voice", "Outage", "ACS", "Recovery"], runbook_id: 'RB-VOICE-001', category: 'Incident Recovery', estimated_time: '30 minutes', steps: ["1. Check Azure Communication Services health at status.azure.com", "2. Verify ACS resource health in Azure Portal > Resource Health", "3. Check CCaaS Voice channel status in Dynamics 365 admin center > Channels", "4. Review call failure logs in Application Insights", "5. If ACS region outage \u2014 enable geo-redundant failover", "6. If CCaaS-side \u2014 restart Omnichannel provisioning from admin center", "7. Test with internal call, confirm call flow, recording, transcription", "8. Notify supervisors and update incident ticket"], document: 'data/Runbook_VoiceOutage.txt'});
CREATE (n:Runbook {id: 'RB-002', label: 'Routing Misconfiguration Fix', tags: ["Routing", "Config", "Workstream"], runbook_id: 'RB-ROUTE-001', category: 'Configuration Fix', estimated_time: '20 minutes', steps: ["1. Identify affected workstream in admin center > Workstreams", "2. Check routing rules \u2014 verify classification rulesets are published", "3. Confirm assignment method is set correctly", "4. Verify agent queue membership and skill assignments", "5. Check capacity profiles", "6. Review overflow rules", "7. Test with a sample work item via Routing diagnostics", "8. Publish pending changes and monitor for 15 minutes"], document: 'data/Runbook_RoutingFix.txt'});
CREATE (n:SOP {id: 'SOP-001', label: 'P1 Incident Escalation Process', tags: ["P1", "Escalation", "SLA"], sop_id: 'SOP-ESC-P1', category: 'Escalation', steps: ["1. L1 confirms P1 severity (voice outage, routing failure, or >50 agents affected)", "2. Create incident in ServiceNow with P1 and tag MS-CCaaS", "3. Page on-call L2 engineer via PagerDuty within 5 minutes", "4. L2 joins bridge call and begins triage using relevant runbook", "5. If not resolved in 30 min \u2014 escalate to Microsoft Premier Support", "6. Notify VP Support, CSM, and affected customer contacts", "7. Post-incident: RCA document within 48 hours"], document: 'data/SOP_P1_Escalation.txt'});
CREATE (n:Incident {id: 'INC-001', label: 'INC-20260115: Voice outage US-East', tags: ["Voice", "Outage", "US-East", "P1"], incident_id: 'INC-20260115-001', date: '2026-01-15', severity: 'P1', duration: '47 minutes', affected_service: 'Omnichannel Voice', affected_customers: ["Contoso Corp", "Fabrikam Inc"], root_cause: 'Azure Communication Services US East region had transient DNS resolution failure.', resolution: 'ACS auto-recovered. Applied geo-redundant failover configuration.', post_mortem: 'Implemented dual-region ACS provisioning. Added synthetic call monitoring every 5 minutes.'});
CREATE (n:Incident {id: 'INC-002', label: 'INC-20260203: Routing stuck in queue', tags: ["Routing", "Queue", "Circular Rule"], incident_id: 'INC-20260203-002', date: '2026-02-03', severity: 'P2', duration: '1 hour 15 minutes', affected_service: 'Unified Routing', affected_customers: ["Contoso Corp"], root_cause: 'Admin published classification ruleset with circular dependency causing routing engine to loop.', resolution: 'Removed circular rule. Flushed stuck work items via OData API.', post_mortem: 'Implemented pre-publish validation for classification rules.'});
CREATE (n:Expert {id: 'EXP-001', label: 'Priya Sharma', tags: ["Voice", "ACS", "On-Call"], employee_id: 'EMP-4521', role: 'Senior CCaaS Engineer', expertise: ["Omnichannel Voice", "Azure Communication Services", "Call Quality", "Network Troubleshooting"], email: 'priya.sharma@hcltech.com', on_call: True, location: 'Noida, India', certifications: ["MS Dynamics 365 Customer Service Functional Consultant", "Azure Solutions Architect"]});
CREATE (n:Expert {id: 'EXP-002', label: 'James Wilson', tags: ["Routing", "Copilot", "Architect"], employee_id: 'EMP-7834', role: 'CCaaS Platform Architect', expertise: ["Unified Routing", "Copilot Configuration", "Power Platform", "Dataverse"], email: 'james.wilson@hcltech.com', on_call: False, location: 'Dallas, USA', certifications: ["MS Power Platform Solution Architect", "Dynamics 365 CE Developer"]});
CREATE (n:Expert {id: 'EXP-003', label: 'Ananya Gupta', tags: ["Chat", "Digital", "Bots"], employee_id: 'EMP-3298', role: 'Digital Channels Specialist', expertise: ["Live Chat", "SMS", "WhatsApp Integration", "Bot Framework", "Copilot Studio"], email: 'ananya.gupta@hcltech.com', on_call: True, location: 'Bangalore, India', certifications: ["Azure AI Engineer", "Copilot Studio Specialist"]});
CREATE (n:Expert {id: 'EXP-004', label: 'Maria Rodriguez', tags: ["WFM", "Scheduling", "Operations"], employee_id: 'EMP-5612', role: 'WFM Operations Lead', expertise: ["Workforce Management", "Forecasting", "Schedule Optimization", "Capacity Planning", "Adherence Management"], email: 'maria.rodriguez@hcltech.com', on_call: False, location: 'Mexico City, Mexico', certifications: ["MS Dynamics 365 Customer Service Functional Consultant", "Workforce Management Professional"]});
CREATE (n:Team {id: 'TEAM-001', label: 'CCaaS Voice Platform Team', tags: ["Voice", "ACS"], team_id: 'T-VOICE', members: 8, lead: 'Priya Sharma', responsibilities: ["Voice channel health", "ACS integration", "Call quality monitoring", "IVR flows"], on_call_rotation: 'Weekly', escalation_channel: '#ccaas-voice-oncall (Teams)'});
CREATE (n:Team {id: 'TEAM-002', label: 'CCaaS Digital & Routing Team', tags: ["Digital", "Routing"], team_id: 'T-DIGITAL', members: 6, lead: 'James Wilson', responsibilities: ["Routing engine", "Chat/SMS channels", "Bot integrations", "Copilot config"], on_call_rotation: 'Bi-weekly', escalation_channel: '#ccaas-digital-oncall (Teams)'});
CREATE (n:Team {id: 'TEAM-003', label: 'CCaaS WFM & Planning Team', tags: ["WFM", "Planning"], team_id: 'T-WFM', members: 4, lead: 'Maria Rodriguez', responsibilities: ["WFM system health", "Forecasting accuracy", "Schedule optimization", "Adherence monitoring"], on_call_rotation: 'Monthly', escalation_channel: '#ccaas-wfm-support (Teams)'});
CREATE (n:Customer {id: 'CUST-001', label: 'Contoso Corp', tags: ["Enterprise", "Finance", "Premier"], customer_id: 'C-CONTOSO', industry: 'Financial Services', agents_licensed: 250, license_type: 'Enterprise', sla_tier: 'Premier', channels: ["Voice", "Chat", "Email", "WhatsApp"], region: 'US East', csm: 'Rebecca Torres'});
CREATE (n:Customer {id: 'CUST-002', label: 'Fabrikam Inc', tags: ["Enterprise", "Retail"], customer_id: 'C-FABRIKAM', industry: 'Retail', agents_licensed: 120, license_type: 'Enterprise', sla_tier: 'Standard', channels: ["Voice", "Chat", "SMS"], region: 'US West', csm: 'David Kim'});
CREATE (n:Customer {id: 'CUST-003', label: 'Northwind Traders', tags: ["Digital", "Logistics"], customer_id: 'C-NORTHWIND', industry: 'Logistics', agents_licensed: 45, license_type: 'Digital Only', sla_tier: 'Standard', channels: ["Chat", "SMS", "Email"], region: 'EU West', csm: 'Hans Mueller'});
CREATE (n:Infrastructure {id: 'INFRA-001', label: 'Azure Communication Services', tags: ["ACS", "Azure", "Voice"], resource_type: 'ACS', regions: ["US East", "US West", "EU West"], provisioning: 'Multi-region with geo-failover', monitoring: 'Application Insights + Azure Monitor', health_url: 'https://status.azure.com'});
CREATE (n:Infrastructure {id: 'INFRA-002', label: 'Dataverse (CDS)', tags: ["Dataverse", "Data", "Power Platform"], resource_type: 'Dataverse', regions: ["US East", "EU West"], capacity: '10 GB per environment', monitoring: 'Power Platform Admin Center', description: 'Core data platform storing all CCaaS entities.'});
CREATE (n:Infrastructure {id: 'INFRA-003', label: 'Azure OpenAI Service', tags: ["OpenAI", "GPT", "Copilot"], resource_type: 'Azure OpenAI', model: 'GPT-4o', regions: ["US East", "EU West"], tpm_quota: '120K tokens/min', description: 'Powers Copilot for agents — case summarization, response drafting, knowledge article recommendations.'});
CREATE (n:Configuration {id: 'CFG-001', label: 'Voice Channel Config', tags: ["Voice", "Config"], config_area: 'Voice', key_settings: ["Phone number assignment via ACS", "IVR greeting and menu", "Call recording policy", "Transcription language", "Post-call survey trigger"], admin_path: 'Dynamics 365 admin center > Customer Service > Channels > Voice'});
CREATE (n:Configuration {id: 'CFG-002', label: 'Copilot Feature Flags', tags: ["Copilot", "Config", "Feature Flags"], config_area: 'Copilot', key_settings: ["Enable/disable Copilot", "Case summarization toggle", "Response suggestion toggle", "Knowledge article suggestion toggle", "Analytics and feedback"], admin_path: 'Dynamics 365 admin center > Productivity > Copilot'});
CREATE (n:Configuration {id: 'CFG-003', label: 'WFM Configuration', tags: ["WFM", "Config", "Scheduling"], config_area: 'Workforce Management', key_settings: ["Forecast models", "Schedule templates", "Shift patterns", "Break rules", "Adherence thresholds", "Time-off requests"], admin_path: 'Dynamics 365 admin center > Workforce Management > Configuration'});
CREATE (n:FAQ {id: 'FAQ-001', label: 'How to reset agent presence?', tags: ["Presence", "Agent", "Reset"], question: 'An agent is stuck in Busy status and cannot receive new work items. How to reset?', answer: '1. Sign out of Dynamics 365 and close all tabs. 2. Wait 2 minutes. 3. Sign back in and set Available. 4. Admin can reset via Omnichannel admin > Agents > Reset presence. 5. Last resort: OData API PATCH msdyn_omnichannelpresences.'});
CREATE (n:FAQ {id: 'FAQ-002', label: 'How to add a new chat channel?', tags: ["Chat", "Widget", "Setup"], question: 'How do I configure a new live chat widget for a customer website?', answer: '1. Admin center > Channels > Chat > Add Chat Widget. 2. Configure name, language, operating hours, pre-chat survey. 3. Set routing workstream and queue. 4. Customize appearance. 5. Copy JS snippet. 6. Paste into customer website. 7. Test in incognito.'});
CREATE (n:FAQ {id: 'FAQ-003', label: 'Why is Copilot not showing suggestions?', tags: ["Copilot", "Troubleshooting"], question: 'Copilot panel shows No suggestions available for an active conversation. Why?', answer: '1. Copilot feature flag disabled — check admin center > Productivity > Copilot. 2. No published knowledge articles matching topic. 3. Azure OpenAI quota exhausted. 4. Agent missing Copilot User security role. 5. Need at least 2 customer messages before Copilot activates.'});
CREATE (n:FAQ {id: 'FAQ-004', label: 'How to generate agent schedules?', tags: ["WFM", "Scheduling", "Forecasting"], question: 'How do I generate optimized agent schedules based on forecasted volume?', answer: '1. Admin center > Workforce Management > Forecasting. 2. Import historical data or use AI forecasting. 3. Review forecast accuracy. 4. Navigate to Scheduling > Generate Schedule. 5. Set date range, shift patterns, and staffing requirements. 6. Run optimizer. 7. Review draft schedule. 8. Publish to agents. 9. Allow shift bidding if enabled.'});
CREATE (n:Feature {id: 'FEAT-001', label: 'Real-Time Translation', tags: ["Translation", "Multilingual", "Chat"], feature_name: 'Real-Time Message Translation', description: 'Automatically translates messages between customer and agent languages in real-time. Supports 50+ languages.', availability: '2025 Wave 2', channels: ["Chat", "SMS", "WhatsApp"], prerequisite: 'Azure AI Translator resource connected'});
CREATE (n:Feature {id: 'FEAT-002', label: 'Sentiment-Based Routing', tags: ["Sentiment", "Routing", "AI"], feature_name: 'Sentiment-Based Intelligent Routing', description: 'Routes conversations to specialized agents when customer sentiment is Very Negative. Uses real-time sentiment analysis to reclassify and reroute.', availability: '2025 Wave 1', channels: ["Voice", "Chat"], prerequisite: 'Sentiment analysis enabled in workstream settings'});

// --- UPDATE EXISTING NODES ---

MATCH (n:Product {id: 'PROD-001'}) SET n.label = 'MS Dynamics 365 Contact Center', n.tags = ["CCaaS", "Omnichannel", "Copilot", "Azure"], full_name: 'Microsoft Dynamics 365 Contact Center (CCaaS)', vendor: 'Microsoft', version: '2025 Release Wave 2', category: 'Contact Center as a Service', deployment: 'Cloud (Azure)', product_url: 'https://learn.microsoft.com/en-us/dynamics365/contact-center/', description: 'Cloud-based omnichannel contact center platform with AI-powered routing, Copilot assistance, real-time analytics, and unified agent desktop.', support_tier: 'Enterprise';
MATCH (n:KnownIssue {id: 'KI-004'}) SET n.label = 'WFM schedule not syncing with agent presence', n.tags = ["WFM", "Presence", "Sync", "P2"], issue_id: 'KI-2026-004', severity: 'P2', affected_versions: ["2025 Wave 2"], symptoms: ["Agent scheduled but shows as offline", "Presence status not updating when shift starts", "Manual presence override required"], root_cause: 'Delayed sync between WFM service and Dataverse presence table when schedule changes occur within 5 minutes of shift start.', workaround: 'Agent manually sets presence to Available at shift start. Admin can force sync via WFM settings > Sync Presence Now.', status: 'Workaround Available', document: 'data/KnownIssue_WFM_PresenceSync.txt';

// --- DELETE REMOVED NODES ---

MATCH (n {id: 'FAQ-005'}) DETACH DELETE n;
MATCH (n {id: 'KI-2025-002'}) DETACH DELETE n;
MATCH (n {id: 'KI-005'}) DETACH DELETE n;
MATCH (n {id: 'KI-2025-003'}) DETACH DELETE n;
MATCH (n {id: 'KI-2025-001'}) DETACH DELETE n;
MATCH (n {id: 'NODE-2025W1'}) DETACH DELETE n;
MATCH (n {id: 'NODE-2025W2'}) DETACH DELETE n;
MATCH (n {id: 'NODE-2025W2-QM'}) DETACH DELETE n;
MATCH (n {id: 'NODE-2025W2-WFM'}) DETACH DELETE n;
MATCH (n {id: 'RB-005'}) DETACH DELETE n;
MATCH (n {id: 'RB-ROUTE-001'}) DETACH DELETE n;
MATCH (n {id: 'RB-VOICE-001'}) DETACH DELETE n;
MATCH (n {id: 'RB-004'}) DETACH DELETE n;
MATCH (n {id: 'SOP-ESC-P1'}) DETACH DELETE n;
MATCH (n {id: 'SOP-003'}) DETACH DELETE n;
MATCH (n {id: 'SPO-CCAAS-DIGITAL'}) DETACH DELETE n;
MATCH (n {id: 'SPO-CCAAS-ENTERPRISE'}) DETACH DELETE n;
MATCH (n {id: 'UG-AGENTDESKTOP'}) DETACH DELETE n;
MATCH (n {id: 'UG-QM-ADMIN'}) DETACH DELETE n;
MATCH (n {id: 'UG-ROUTINGADMIN'}) DETACH DELETE n;
MATCH (n {id: 'UG-SUPERVISOR'}) DETACH DELETE n;
MATCH (n {id: 'UG-WFM-ADMIN'}) DETACH DELETE n;

// --- ADD NEW EDGES ---

MATCH (a {id: 'PROD-001'}), (b {id: 'SVC-001'}) MERGE (a)-[:HAS_SERVICE]->(b);
MATCH (a {id: 'PROD-001'}), (b {id: 'SVC-002'}) MERGE (a)-[:HAS_SERVICE]->(b);
MATCH (a {id: 'PROD-001'}), (b {id: 'SVC-003'}) MERGE (a)-[:HAS_SERVICE]->(b);
MATCH (a {id: 'PROD-001'}), (b {id: 'SVC-004'}) MERGE (a)-[:HAS_SERVICE]->(b);
MATCH (a {id: 'PROD-001'}), (b {id: 'SVC-005'}) MERGE (a)-[:HAS_SERVICE]->(b);
MATCH (a {id: 'PROD-001'}), (b {id: 'SVC-006'}) MERGE (a)-[:HAS_SERVICE]->(b);
MATCH (a {id: 'PROD-001'}), (b {id: 'SVC-007'}) MERGE (a)-[:HAS_SERVICE]->(b);
MATCH (a {id: 'PROD-001'}), (b {id: 'SVC-008'}) MERGE (a)-[:HAS_SERVICE]->(b);
MATCH (a {id: 'SVC-001'}), (b {id: 'INFRA-001'}) MERGE (a)-[:RUNS_ON]->(b);
MATCH (a {id: 'SVC-002'}), (b {id: 'INFRA-002'}) MERGE (a)-[:RUNS_ON]->(b);
MATCH (a {id: 'SVC-003'}), (b {id: 'INFRA-002'}) MERGE (a)-[:RUNS_ON]->(b);
MATCH (a {id: 'SVC-004'}), (b {id: 'INFRA-003'}) MERGE (a)-[:RUNS_ON]->(b);
MATCH (a {id: 'SVC-005'}), (b {id: 'INFRA-002'}) MERGE (a)-[:RUNS_ON]->(b);
MATCH (a {id: 'SVC-006'}), (b {id: 'INFRA-002'}) MERGE (a)-[:RUNS_ON]->(b);
MATCH (a {id: 'SVC-007'}), (b {id: 'INFRA-002'}) MERGE (a)-[:RUNS_ON]->(b);
MATCH (a {id: 'SVC-008'}), (b {id: 'INFRA-002'}) MERGE (a)-[:RUNS_ON]->(b);
MATCH (a {id: 'SVC-004'}), (b {id: 'SVC-007'}) MERGE (a)-[:DEPENDS_ON]->(b);
MATCH (a {id: 'SVC-004'}), (b {id: 'INFRA-003'}) MERGE (a)-[:DEPENDS_ON]->(b);
MATCH (a {id: 'SVC-005'}), (b {id: 'SVC-002'}) MERGE (a)-[:DEPENDS_ON]->(b);
MATCH (a {id: 'SVC-005'}), (b {id: 'SVC-004'}) MERGE (a)-[:DEPENDS_ON]->(b);
MATCH (a {id: 'SVC-008'}), (b {id: 'SVC-002'}) MERGE (a)-[:DEPENDS_ON]->(b);
MATCH (a {id: 'SVC-008'}), (b {id: 'SVC-003'}) MERGE (a)-[:DEPENDS_ON]->(b);
MATCH (a {id: 'SVC-001'}), (b {id: 'SVC-002'}) MERGE (a)-[:DEPENDS_ON]->(b);
MATCH (a {id: 'PROD-001'}), (b {id: 'SPO-001'}) MERGE (a)-[:BELONGS_TO_SPO]->(b);
MATCH (a {id: 'PROD-001'}), (b {id: 'SPO-002'}) MERGE (a)-[:BELONGS_TO_SPO]->(b);
MATCH (a {id: 'PROD-001'}), (b {id: 'RN-001'}) MERGE (a)-[:HAS_RELEASE_NOTE]->(b);
MATCH (a {id: 'PROD-001'}), (b {id: 'RN-002'}) MERGE (a)-[:HAS_RELEASE_NOTE]->(b);
MATCH (a {id: 'SVC-005'}), (b {id: 'UG-001'}) MERGE (a)-[:DOCUMENTED_IN]->(b);
MATCH (a {id: 'SVC-006'}), (b {id: 'UG-002'}) MERGE (a)-[:DOCUMENTED_IN]->(b);
MATCH (a {id: 'SVC-002'}), (b {id: 'UG-003'}) MERGE (a)-[:DOCUMENTED_IN]->(b);
MATCH (a {id: 'SVC-001'}), (b {id: 'KI-001'}) MERGE (a)-[:HAS_KNOWN_ISSUE]->(b);
MATCH (a {id: 'SVC-004'}), (b {id: 'KI-002'}) MERGE (a)-[:HAS_KNOWN_ISSUE]->(b);
MATCH (a {id: 'SVC-003'}), (b {id: 'KI-003'}) MERGE (a)-[:HAS_KNOWN_ISSUE]->(b);
MATCH (a {id: 'SVC-001'}), (b {id: 'RB-001'}) MERGE (a)-[:HAS_RUNBOOK]->(b);
MATCH (a {id: 'SVC-002'}), (b {id: 'RB-002'}) MERGE (a)-[:HAS_RUNBOOK]->(b);
MATCH (a {id: 'PROD-001'}), (b {id: 'SOP-001'}) MERGE (a)-[:HAS_SOP]->(b);
MATCH (a {id: 'CUST-001'}), (b {id: 'INC-001'}) MERGE (a)-[:REPORTED_INCIDENT]->(b);
MATCH (a {id: 'CUST-002'}), (b {id: 'INC-001'}) MERGE (a)-[:REPORTED_INCIDENT]->(b);
MATCH (a {id: 'CUST-001'}), (b {id: 'INC-002'}) MERGE (a)-[:REPORTED_INCIDENT]->(b);
MATCH (a {id: 'INC-001'}), (b {id: 'SVC-001'}) MERGE (a)-[:IMPACTED_BY]->(b);
MATCH (a {id: 'INC-002'}), (b {id: 'SVC-002'}) MERGE (a)-[:IMPACTED_BY]->(b);
MATCH (a {id: 'INC-001'}), (b {id: 'RB-001'}) MERGE (a)-[:RESOLVED_BY]->(b);
MATCH (a {id: 'INC-002'}), (b {id: 'RB-002'}) MERGE (a)-[:RESOLVED_BY]->(b);
MATCH (a {id: 'INC-001'}), (b {id: 'EXP-001'}) MERGE (a)-[:ASSIGNED_TO]->(b);
MATCH (a {id: 'INC-002'}), (b {id: 'EXP-002'}) MERGE (a)-[:ASSIGNED_TO]->(b);
MATCH (a {id: 'TEAM-001'}), (b {id: 'SVC-001'}) MERGE (a)-[:OWNS]->(b);
MATCH (a {id: 'TEAM-002'}), (b {id: 'SVC-002'}) MERGE (a)-[:OWNS]->(b);
MATCH (a {id: 'TEAM-002'}), (b {id: 'SVC-003'}) MERGE (a)-[:OWNS]->(b);
MATCH (a {id: 'TEAM-002'}), (b {id: 'SVC-004'}) MERGE (a)-[:OWNS]->(b);
MATCH (a {id: 'TEAM-001'}), (b {id: 'EXP-001'}) MERGE (a)-[:ASSIGNED_TO]->(b);
MATCH (a {id: 'TEAM-002'}), (b {id: 'EXP-002'}) MERGE (a)-[:ASSIGNED_TO]->(b);
MATCH (a {id: 'TEAM-002'}), (b {id: 'EXP-003'}) MERGE (a)-[:ASSIGNED_TO]->(b);
MATCH (a {id: 'CUST-001'}), (b {id: 'SPO-001'}) MERGE (a)-[:SUBSCRIBES_TO]->(b);
MATCH (a {id: 'CUST-002'}), (b {id: 'SPO-001'}) MERGE (a)-[:SUBSCRIBES_TO]->(b);
MATCH (a {id: 'CUST-003'}), (b {id: 'SPO-002'}) MERGE (a)-[:SUBSCRIBES_TO]->(b);
MATCH (a {id: 'SVC-001'}), (b {id: 'CFG-001'}) MERGE (a)-[:CONFIGURED_BY]->(b);
MATCH (a {id: 'SVC-004'}), (b {id: 'CFG-002'}) MERGE (a)-[:CONFIGURED_BY]->(b);
MATCH (a {id: 'KI-001'}), (b {id: 'RN-001'}) MERGE (a)-[:FIXED_IN]->(b);
MATCH (a {id: 'KI-002'}), (b {id: 'CFG-002'}) MERGE (a)-[:WORKAROUND_IN]->(b);
MATCH (a {id: 'KI-003'}), (b {id: 'CFG-001'}) MERGE (a)-[:WORKAROUND_IN]->(b);
MATCH (a {id: 'SVC-005'}), (b {id: 'FAQ-001'}) MERGE (a)-[:HAS_FAQ]->(b);
MATCH (a {id: 'SVC-003'}), (b {id: 'FAQ-002'}) MERGE (a)-[:HAS_FAQ]->(b);
MATCH (a {id: 'SVC-004'}), (b {id: 'FAQ-003'}) MERGE (a)-[:HAS_FAQ]->(b);
MATCH (a {id: 'SVC-003'}), (b {id: 'FEAT-001'}) MERGE (a)-[:HAS_FEATURE]->(b);
MATCH (a {id: 'SVC-002'}), (b {id: 'FEAT-002'}) MERGE (a)-[:HAS_FEATURE]->(b);
MATCH (a {id: 'SOP-001'}), (b {id: 'TEAM-001'}) MERGE (a)-[:ESCALATES_TO]->(b);
MATCH (a {id: 'SOP-001'}), (b {id: 'TEAM-002'}) MERGE (a)-[:ESCALATES_TO]->(b);
MATCH (a {id: 'KI-001'}), (b {id: 'INC-001'}) MERGE (a)-[:RELATED_TO]->(b);
MATCH (a {id: 'RB-001'}), (b {id: 'CFG-001'}) MERGE (a)-[:RELATED_TO]->(b);
MATCH (a {id: 'RB-002'}), (b {id: 'UG-003'}) MERGE (a)-[:RELATED_TO]->(b);
MATCH (a {id: 'PROD-001'}), (b {id: 'SVC-009'}) MERGE (a)-[:HAS_SERVICE]->(b);
MATCH (a {id: 'SVC-009'}), (b {id: 'INFRA-002'}) MERGE (a)-[:RUNS_ON]->(b);
MATCH (a {id: 'SVC-009'}), (b {id: 'SVC-006'}) MERGE (a)-[:DEPENDS_ON]->(b);
MATCH (a {id: 'SVC-009'}), (b {id: 'SVC-002'}) MERGE (a)-[:DEPENDS_ON]->(b);
MATCH (a {id: 'SVC-009'}), (b {id: 'CFG-003'}) MERGE (a)-[:CONFIGURED_BY]->(b);
MATCH (a {id: 'SVC-009'}), (b {id: 'UG-004'}) MERGE (a)-[:DOCUMENTED_IN]->(b);
MATCH (a {id: 'SVC-009'}), (b {id: 'KI-004'}) MERGE (a)-[:HAS_KNOWN_ISSUE]->(b);
MATCH (a {id: 'SVC-009'}), (b {id: 'FAQ-004'}) MERGE (a)-[:HAS_FAQ]->(b);
MATCH (a {id: 'TEAM-003'}), (b {id: 'SVC-009'}) MERGE (a)-[:OWNS]->(b);
MATCH (a {id: 'TEAM-003'}), (b {id: 'EXP-004'}) MERGE (a)-[:ASSIGNED_TO]->(b);
MATCH (a {id: 'SPO-001'}), (b {id: 'SVC-009'}) MERGE (a)-[:HAS_SERVICE]->(b);

// --- DONE ---
// Delta update completed