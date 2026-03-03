/**
 * AI Agents Data Configuration
 * 
 * Real-world production AI agents deployed across Microsoft & Enterprise customers.
 * Built with Microsoft Agent Framework, AutoGen, and Azure AI.
 * 
 * Categories: Content, Planning, Documentation, Operations, Support, Testing, 
 *             Marketing, Legal, Engineering, SRE, Release Management
 */

export interface AgentCapability {
  id: string;
  label: string;
  color: string;
}

export interface Agent {
  id: string;
  name: string;
  tagline: string;
  description: string;
  detailedDescription: string;
  icon: string; // Lucide icon name
  status: 'live' | 'beta' | 'coming-soon';
  capabilities: AgentCapability[];
  category: 'content' | 'planning' | 'documentation' | 'operations' | 'support' | 'testing' | 'marketing' | 'legal' | 'engineering' | 'sre' | 'release-management' | 'training';
  features: string[];
  useCases: string[];
  metrics?: {
    label: string;
    value: string;
  }[];
  demoAvailable: boolean;
  popularity: number; // 1-5 rating
  isNew: boolean;
  releaseDate?: string;
  track?: string;
  impact?: string[];
  agenticHighlights?: string[];
}

export const agentCapabilities: Record<string, AgentCapability> = {
  rag: {
    id: 'rag',
    label: 'RAG Enabled',
    color: '#0070AD',
  },
  toolUse: {
    id: 'tool-use',
    label: 'Tool Use',
    color: '#00A3E0',
  },
  multiModal: {
    id: 'multi-modal',
    label: 'Multi-Modal',
    color: '#FF6B35',
  },
  realTime: {
    id: 'real-time',
    label: 'Real-time',
    color: '#28A745',
  },
  streaming: {
    id: 'streaming',
    label: 'Streaming',
    color: '#17A2B8',
  },
  contextAware: {
    id: 'context-aware',
    label: 'Context Aware',
    color: '#6F42C1',
  },
  autonomous: {
    id: 'autonomous',
    label: 'Autonomous',
    color: '#FD7E14',
  },
  collaborative: {
    id: 'collaborative',
    label: 'Collaborative',
    color: '#20C997',
  },
  orchestration: {
    id: 'orchestration',
    label: 'Orchestration',
    color: '#E83E8C',
  },
  policyAware: {
    id: 'policy-aware',
    label: 'Policy Aware',
    color: '#6610F2',
  },
};

export const agents: Agent[] = [
  // =========================================================================
  // TRAINING / SKILLING TRACK (Featured)
  // =========================================================================
  {
    id: 'in-flow-simulation-coach',
    name: 'In-Flow Simulation Coach',
    tagline: 'AI-Powered Contact Center Training Simulator',
    description: 'Multi-agent training simulator that lets support agents practice real customer scenarios with an AI customer and a real-time shadow coach providing guidance.',
    detailedDescription: 'The In-Flow Simulation Coach uses a "Fourth Wall" multi-agent architecture: a CustomerSim agent role-plays realistic customer personas while a ShadowCoach agent observes the conversation and provides real-time coaching hints, warnings, and praise — all invisible to the simulated customer. Trainees practice de-escalation, billing disputes, technical troubleshooting, retention calls, and more. Each session ends with a detailed performance report including skill scores, checkpoint completion, key moments analysis, and manager-ready watch-out warnings.',
    icon: 'GraduationCap',
    status: 'live',
    capabilities: [
      agentCapabilities.contextAware,
      agentCapabilities.collaborative,
      agentCapabilities.orchestration,
      agentCapabilities.realTime,
    ],
    category: 'training',
    track: 'Training & Skilling',
    features: [
      'Fourth Wall architecture — coach is invisible to customer',
      'AI-generated customer personas with emotional states',
      'Real-time shadow coaching (hints, praise, warnings)',
      'Checkpoint-based progress tracking',
      'Detailed post-session performance reports',
      'Skill scoring across empathy, resolution, communication',
      'Manager-ready watch-out warnings and recommendations',
      'Session expiry protection with keepalive',
    ],
    useCases: [
      'New agent onboarding & ramp-up',
      'De-escalation practice with angry customers',
      'Billing dispute resolution training',
      'Technical troubleshooting skill building',
      'Retention & cancellation handling',
      'Fraud & chargeback scenario practice',
      'Sales discovery call simulation',
      'HR & people management conversations',
    ],
    impact: [
      'Faster agent ramp-up time',
      'Risk-free practice environment',
      'Consistent coaching quality at scale',
      'Data-driven training gap identification',
      'Reduced live-call coaching dependency',
    ],
    agenticHighlights: [
      'Multi-agent orchestration (CustomerSim + ShadowCoach)',
      'Fourth Wall — agents never see each other\'s messages',
      'AI Scenario Architect generates configs from case data',
      'Checkpoint rubric with auto-detection of completion',
      'Comprehensive post-session report with key moments',
    ],
    metrics: [
      { label: 'Training Scenarios', value: '30+' },
      { label: 'Skill Categories', value: '8' },
      { label: 'Avg Session Time', value: '10 min' },
    ],
    demoAvailable: true,
    popularity: 5,
    isNew: true,
    releaseDate: '2026-02-10',
  },

  // PRIORITY AGENTS (Top 4 - HCLTech Focus)
  // SUPPORT TRACK
  {
    id: 'self-service-support',
    name: 'Self-Service Support Agent',
    tagline: 'Frictionless AI-Human Hybrid Support',
    description: 'Delivers fast, low-cost self-service support with seamless AI-to-human escalation, maintaining context throughout. Highly focused on AI cost optimization.',
    detailedDescription: 'Provides a frictionless support experience where end-users start with fast, low-cost self-service. When needed, seamlessly transitions to AI-assisted resolution with human oversight—all without losing context. Lower-cost agents handle initial troubleshooting; higher-compute agents used only for escalation.',
    icon: 'Headset',
    status: 'live',
    capabilities: [
      agentCapabilities.contextAware,
      agentCapabilities.streaming,
      agentCapabilities.rag,
      agentCapabilities.collaborative,
    ],
    category: 'support',
    track: 'Support',
    features: [
      'Cost-optimized AI model selection',
      'Tiered agent complexity (low to high cost)',
      'Context preservation across escalation',
      'Human-in-the-loop for complex issues',
      'Knowledge base integration',
      'Real-time sentiment analysis',
    ],
    useCases: [
      'Technical troubleshooting',
      'Account and billing inquiries',
      'Product feature questions',
      'Bug report collection',
      'Service request management',
    ],
    impact: [
      'Significant reduction in support costs',
      'Faster resolution for simple issues',
      'No context loss during escalation',
      'Optimal AI resource allocation',
    ],
    agenticHighlights: [
      'High focus on AI cost optimization',
      'Lower cost agents for initial troubleshooting',
      'Higher compute agents used only for escalation',
    ],
    metrics: [
      { label: 'Cost Reduction', value: '65%' },
      { label: 'First Contact Resolution', value: '82%' },
      { label: 'Escalation Rate', value: '18%' },
    ],
    demoAvailable: true,
    popularity: 5,
    isNew: false,
  },

  // UTA - Unified Troubleshooting Assistant
  {
    id: 'uta-troubleshooting',
    name: 'Unified Troubleshooting Assistant (UTA)',
    tagline: 'RAG-Powered CCaaS Support Intelligence',
    description: 'AI-powered troubleshooting assistant for Microsoft CCaaS support engineers. Uses RAG to search SOPs, playbooks, and known issues for instant resolution guidance.',
    detailedDescription: 'UTA is a Retrieval-Augmented Generation (RAG) powered assistant designed specifically for CCaaS (Contact Center as a Service) support engineers. It unifies knowledge from SOPs, playbooks, known issues, error codes, and expert insights into a single searchable interface. The agent analyzes support tickets, generates diagnostic workflows, validates configurations, and provides step-by-step troubleshooting guidance with citations to source documents.',
    icon: 'SearchCheck',
    status: 'live',
    capabilities: [
      agentCapabilities.rag,
      agentCapabilities.contextAware,
      agentCapabilities.toolUse,
      agentCapabilities.streaming,
    ],
    category: 'support',
    track: 'Support',
    features: [
      'Unified knowledge base search (SOPs, playbooks, known issues)',
      'Automatic ticket analysis and categorization',
      'Diagnostic workflow generation',
      'Configuration validation against best practices',
      'Error code lookup with resolution steps',
      'Expert insights and tribal knowledge access',
      'Citation of source documents',
      'Local LLM support via Ollama (llama3.1:8b)',
    ],
    useCases: [
      'CCaaS ticket troubleshooting',
      'Routing and queue configuration issues',
      'License activation and validation',
      'Connectivity and timeout problems',
      'Agent experience issues',
      'Voice quality troubleshooting',
      'Known issue identification',
    ],
    impact: [
      '60% faster ticket resolution',
      'Reduced knowledge search time',
      'Consistent troubleshooting approach',
      'Better knowledge utilization',
      'Reduced escalation rate',
    ],
    agenticHighlights: [
      'ChromaDB vector store with Ollama embeddings',
      'Local LLM inference (no cloud dependency)',
      'Switchable to Azure AI Search for production',
      'Structured analysis with confidence scoring',
    ],
    metrics: [
      { label: 'Knowledge Sources', value: '100+' },
      { label: 'Avg Response Time', value: '<30s' },
      { label: 'Resolution Accuracy', value: '85%' },
    ],
    demoAvailable: true,
    popularity: 5,
    isNew: true,
    releaseDate: '2026-01-21',
  },

  // LEGAL TRACK
  {
    id: 'compliance-review',
    name: 'Compliance Review Agent',
    tagline: 'Automated Legal & Regulatory Compliance',
    description: 'Microsoft Legal (CELA) agent trained on compliance and regulatory policies. Provides clarification and reviews material to ensure policy compliance.',
    detailedDescription: 'Microsoft\'s legal team has extensive compliance and regulatory documents outlining required policies. This agent is deeply trained on these policies and can provide authoritative clarification and/or review any material to ensure full compliance before publication or deployment.',
    icon: 'Scale',
    status: 'live',
    capabilities: [
      agentCapabilities.rag,
      agentCapabilities.policyAware,
      agentCapabilities.contextAware,
      agentCapabilities.autonomous,
    ],
    category: 'legal',
    track: 'Legal',
    features: [
      'Deep policy knowledge training',
      'Automated compliance checking',
      'Regulatory requirement mapping',
      'Risk assessment and scoring',
      'Policy clarification on-demand',
      'Audit trail generation',
    ],
    useCases: [
      'Pre-publication compliance review',
      'Contract clause verification',
      'Marketing material approval',
      'Data privacy assessment',
      'Export control compliance',
    ],
    impact: [
      'Faster compliance verification',
      'Reduced legal review bottlenecks',
      'Consistent policy interpretation',
      'Proactive risk identification',
    ],
    agenticHighlights: [
      'Trained on Microsoft Legal (CELA) compliance and regulatory policies',
      'Provides clarification and reviews material for compliance',
    ],
    metrics: [
      { label: 'Review Time', value: '-85%' },
      { label: 'Compliance Rate', value: '99.8%' },
      { label: 'Reviews/Month', value: '5,000+' },
    ],
    demoAvailable: true,
    popularity: 5,
    isNew: false,
  },

  // SRE TRACK
  {
    id: 'smart-ticket-triage',
    name: 'Smart Ticket Triage Agent',
    tagline: 'Intelligent Incident Classification & Routing',
    description: 'Reads every incoming alert/ticket, classifies priority, category, impacted service, and urgency. Maps incidents to past resolved tickets and suggests resolution paths.',
    detailedDescription: 'Functions like a human L1 engineer, understanding context and eliminating manual queue sorting. Learns from past tickets to continuously improve accuracy. Reduces ticket acknowledgment time to under 1 minute, ensuring rapid response to critical issues.',
    icon: 'ListTodo',
    status: 'live',
    capabilities: [
      agentCapabilities.realTime,
      agentCapabilities.autonomous,
      agentCapabilities.rag,
      agentCapabilities.contextAware,
    ],
    category: 'sre',
    track: 'SRE',
    features: [
      'Automated priority classification',
      'Historical ticket mapping',
      'Resolution path suggestions',
      'Service impact analysis',
      'Urgency-based routing',
      'Continuous learning from resolutions',
    ],
    useCases: [
      'Incident ticket triage',
      'Alert classification',
      'Service outage routing',
      'Support queue optimization',
      'On-call engineer assistance',
    ],
    impact: [
      'Understands context like human L1 engineer',
      'Eliminates manual queue sorting',
      'Learns from past tickets',
      'Gets better over time',
    ],
    agenticHighlights: [
      'Classifies priority, category, impacted service, urgency automatically',
      'Maps incidents to past resolved tickets',
      'Reduces ticket "ack" time to <1 minute',
    ],
    metrics: [
      { label: 'Ack Time', value: '< 1min' },
      { label: 'Classification Accuracy', value: '94%' },
      { label: 'Manual Work', value: '-90%' },
    ],
    demoAvailable: true,
    popularity: 5,
    isNew: false,
  },

  // RELEASE MANAGEMENT TRACK
  {
    id: 'gate-orchestrator',
    name: 'Gate Orchestrator Agent',
    tagline: 'End-to-End Deployment Gating Pipeline',
    description: 'Runs full gating pipeline: triggers tests, collects evidence, compiles Go/No-Go decisions. Coordinates parallel checks for security, evals, cost, and ops readiness.',
    detailedDescription: 'Provides adaptive gating that tightens criteria for high-risk changes. Uses evidence-based decisioning with full explainability and learns which checks best predict post-production incidents. Produces a signed Deployment Readiness Report.',
    icon: 'GitBranch',
    status: 'live',
    capabilities: [
      agentCapabilities.orchestration,
      agentCapabilities.autonomous,
      agentCapabilities.toolUse,
      agentCapabilities.contextAware,
    ],
    category: 'release-management',
    track: 'Release Management',
    features: [
      'End-to-end pipeline execution',
      'Parallel check coordination',
      'Adaptive gating criteria',
      'Evidence collection',
      'Go/No-Go decision compilation',
      'Deployment Readiness Report generation',
    ],
    useCases: [
      'Production deployment gating',
      'Release approval automation',
      'Quality gate enforcement',
      'Risk assessment before deployment',
      'Multi-stakeholder approval',
    ],
    impact: [
      'Adaptive gating for high-risk changes',
      'Evidence-based decisions with explainability',
      'Learns which checks predict incidents',
    ],
    agenticHighlights: [
      'Runs full gating pipeline end-to-end',
      'Coordinates parallel checks (security, evals, cost, ops readiness)',
      'Produces signed Deployment Readiness Report',
    ],
    metrics: [
      { label: 'Deployment Success', value: '99.2%' },
      { label: 'Incidents Prevented', value: '350+' },
      { label: 'Gate Time', value: '-55%' },
    ],
    demoAvailable: true,
    popularity: 5,
    isNew: false,
  },

  // CONTENT TRACK
  {
    id: 'digital-content',
    name: 'Digital Content Agents',
    tagline: 'Automated Brand-Compliant Content Creation',
    description: 'AI agents that build digital store content, apply Microsoft branding & policy rules, handle translations, and publish content with full orchestration.',
    detailedDescription: 'Specialized agents trained in Microsoft-specific branding, tone, and regulatory policies work collaboratively to create, review, and publish content. The orchestration agent oversees the entire content creation pipeline and determines the next needed agent based on workflow state.',
    icon: 'FileEdit',
    status: 'live',
    capabilities: [
      agentCapabilities.multiModal,
      agentCapabilities.orchestration,
      agentCapabilities.policyAware,
      agentCapabilities.collaborative,
    ],
    category: 'content',
    track: 'Content',
    features: [
      'Microsoft branding enforcement',
      'Multi-language translation and localization',
      'Regulatory policy compliance checking',
      'Automated content publishing workflows',
      'Agent-to-agent collaboration via orchestration',
      'Content quality and tone validation',
    ],
    useCases: [
      'Digital storefront content generation',
      'Marketing material creation',
      'Product documentation',
      'Multi-market content localization',
      'Brand-compliant social media posts',
    ],
    impact: [
      '70% reduction in content creation time',
      'Consistent brand voice across all channels',
      'Zero compliance violations',
      'Automated publishing eliminates manual errors',
    ],
    agenticHighlights: [
      'Specialized agents trained in Microsoft branding, tone, and regulatory policies',
      'Orchestration agent oversees content creation and evaluates next needed agent',
    ],
    metrics: [
      { label: 'Time Savings', value: '70%' },
      { label: 'Brand Compliance', value: '100%' },
      { label: 'Content Published', value: '10K+/mo' },
    ],
    demoAvailable: true,
    popularity: 5,
    isNew: false,
  },

  // PLANNING TRACK
  {
    id: 'experimentation-planner',
    name: 'Experimentation Planner',
    tagline: 'AI-Driven A/B Test Design & Optimization',
    description: 'Automates marketing experiment design and planning using historical data. Agents design experiments, predict outcomes, and determine when exit criteria are met.',
    detailedDescription: 'Large effort for teams to manage the design and planning of A/B testing is eliminated. Agents receive guidelines & goals, then design & optimize experiments while cross-referencing extensive datasets from past experiments. Orchestration determines when experiments meet exit criteria or need additional processing.',
    icon: 'Beaker',
    status: 'live',
    capabilities: [
      agentCapabilities.autonomous,
      agentCapabilities.rag,
      agentCapabilities.orchestration,
      agentCapabilities.contextAware,
    ],
    category: 'planning',
    track: 'Planning',
    features: [
      'Historical experiment analysis and learning',
      'Predictive outcome modeling',
      'Automated test design based on goals',
      'Statistical significance detection',
      'Multi-variate test optimization',
      'Real-time experiment monitoring',
    ],
    useCases: [
      'Marketing campaign A/B testing',
      'Website conversion optimization',
      'Product feature rollout experiments',
      'Pricing strategy testing',
      'User experience optimization',
    ],
    impact: [
      '85% faster experiment design',
      'Higher statistical confidence in results',
      'Reduced experiment cycle time by 60%',
      'Data-driven optimization recommendations',
    ],
    agenticHighlights: [
      'Specialized agents trained with extensive dataset of past experiments',
      'Predict measurable outcomes before running tests',
      'Orchestration agent determines exit criteria and additional processing needs',
    ],
    metrics: [
      { label: 'Design Time', value: '-85%' },
      { label: 'Success Rate', value: '+45%' },
      { label: 'Experiments/Month', value: '500+' },
    ],
    demoAvailable: true,
    popularity: 5,
    isNew: false,
  },

  {
    id: 'learning-schedule',
    name: 'Learning Schedule Agents',
    tagline: 'Intelligent Training & Event Management',
    description: 'AI agents process learning/training requests using VMs, adjust content based on user permissions, and handle event scheduling in SAP on behalf of ops teams.',
    detailedDescription: 'Automates the entire learning and training workflow from request intake to event scheduling. Agents intelligently adjust content visibility and access based on end-user permissions and handle complex SAP integration for event management.',
    icon: 'GraduationCap',
    status: 'live',
    capabilities: [
      agentCapabilities.contextAware,
      agentCapabilities.toolUse,
      agentCapabilities.autonomous,
    ],
    category: 'planning',
    track: 'Planning',
    features: [
      'Permission-based content filtering',
      'SAP event scheduling integration',
      'VM-based training delivery',
      'Automated calendar management',
      'Multi-timezone scheduling',
      'Training material personalization',
    ],
    useCases: [
      'Employee onboarding training',
      'Technical certification programs',
      'Leadership development courses',
      'Compliance training distribution',
      'Product knowledge sessions',
    ],
    impact: [
      'Ops team freed from manual scheduling',
      '24/7 training request processing',
      'Automatic content access control',
      'Seamless SAP integration',
    ],
    agenticHighlights: [
      'Agents adjust content based on end-user permissions',
      'Handle event scheduling (SAP) on behalf of ops team',
    ],
    metrics: [
      { label: 'Manual Work', value: '-90%' },
      { label: 'Scheduling Accuracy', value: '99.8%' },
      { label: 'Events/Month', value: '1,200+' },
    ],
    demoAvailable: true,
    popularity: 4,
    isNew: false,
  },

  {
    id: 'compsense',
    name: 'CompSense Agents',
    tagline: 'Automated Compensation Guidance at Scale',
    description: 'Generates structured, role-specific compensation guidance for 40,000+ Microsoft sellers. Aggregates data from multiple sources, eliminating manual errors.',
    detailedDescription: 'Revolutionizes compensation planning by automating the generation of accurate, personalized compensation guidance for tens of thousands of sales professionals. Agents aggregate data from multiple CRM and HR systems, producing multimodal outputs including video and podcast formats.',
    icon: 'DollarSign',
    status: 'live',
    capabilities: [
      agentCapabilities.multiModal,
      agentCapabilities.toolUse,
      agentCapabilities.autonomous,
      agentCapabilities.contextAware,
    ],
    category: 'planning',
    track: 'Planning',
    features: [
      'Multi-source data aggregation (CRM, HR, Finance)',
      'Role-specific compensation calculations',
      'Video and podcast generation',
      'Compliance with compensation policies',
      'Personalized guidance for 40K+ users',
      'Real-time data synchronization',
    ],
    useCases: [
      'Sales compensation planning',
      'Quarterly compensation reviews',
      'New hire compensation briefings',
      'Territory-based comp adjustments',
      'Performance-based incentive calculations',
    ],
    impact: [
      'Eliminated error-prone manual process',
      'Serves 40,000+ sellers accurately',
      'Multimodal delivery (video, podcast, documents)',
      'Real-time compensation insights',
    ],
    agenticHighlights: [
      'Automated generation of accurate, role-specific compensation guidance',
      'Multimodal outputs: video and podcast formats',
    ],
    metrics: [
      { label: 'Users Served', value: '40K+' },
      { label: 'Error Reduction', value: '99.5%' },
      { label: 'Time Saved', value: '95%' },
    ],
    demoAvailable: true,
    popularity: 5,
    isNew: false,
  },

  // DOCUMENTATION TRACK
  {
    id: 'content-agent-guides',
    name: 'Content Agent for User Guides',
    tagline: 'Automated Product Documentation Updates',
    description: 'Maintains large-scale user guides for M365 product line. Agents receive product update feeds and automatically generate revised documentation.',
    detailedDescription: 'The team maintains thousands of user guides covering the entire M365 ecosystem. This agent system receives continuous feeds of product updates and converts them into professionally revised user guides, with specialized agents handling specific products, graphics/layout, and documentation best practices.',
    icon: 'BookOpenText',
    status: 'live',
    capabilities: [
      agentCapabilities.rag,
      agentCapabilities.multiModal,
      agentCapabilities.collaborative,
      agentCapabilities.autonomous,
    ],
    category: 'documentation',
    track: 'Documentation',
    features: [
      'Product update feed integration',
      'Automated documentation generation',
      'Graphics and layout optimization',
      'Multi-product expertise',
      'Best practices enforcement',
      'Version control and tracking',
    ],
    useCases: [
      'M365 product documentation',
      'Release notes generation',
      'Admin guide updates',
      'User onboarding materials',
      'Feature announcement docs',
    ],
    impact: [
      'Massive reduction in manual documentation effort',
      'Always up-to-date with product changes',
      'Consistent documentation quality',
      'Specialized expertise per product area',
    ],
    agenticHighlights: [
      'Agents specialize in specific product knowledge, graphics/layout, and guide best practices',
    ],
    metrics: [
      { label: 'Guides Maintained', value: '5,000+' },
      { label: 'Update Speed', value: '-80%' },
      { label: 'Quality Score', value: '98%' },
    ],
    demoAvailable: true,
    popularity: 4,
    isNew: false,
  },

  // OPERATIONS TRACK
  {
    id: 'customer360',
    name: 'Customer360 Agent',
    tagline: 'Holistic Enterprise Customer Intelligence',
    description: 'Scans multiple CRMs to build comprehensive customer profiles, highlighting the most relevant and urgent data for team members who interact with enterprise customers daily.',
    detailedDescription: 'Solves the problem of fragmented customer data across multiple CRM systems. Agents integrate with many MCP CRM interfaces and perform real-time evaluation to surface the most relevant, timely customer information in unified profiles.',
    icon: 'Users2',
    status: 'live',
    capabilities: [
      agentCapabilities.toolUse,
      agentCapabilities.realTime,
      agentCapabilities.rag,
      agentCapabilities.contextAware,
    ],
    category: 'operations',
    track: 'Operations',
    features: [
      'Multi-CRM data aggregation',
      'MCP CRM interface integration',
      'Real-time data relevance scoring',
      'Urgency-based prioritization',
      'Unified customer view',
      '360-degree relationship mapping',
    ],
    useCases: [
      'Sales team customer preparation',
      'Account manager briefings',
      'Executive customer meetings',
      'Support escalation context',
      'Renewal planning',
    ],
    impact: [
      'Holistic view eliminates information silos',
      'Real-time prioritization of urgent data',
      'Faster customer interaction prep',
      'Better informed decision making',
    ],
    agenticHighlights: [
      'Integrations to many MCP CRM interfaces',
      'Real-time evaluation on most relevant, timely customer data in profile',
    ],
    metrics: [
      { label: 'CRM Sources', value: '12+' },
      { label: 'Prep Time', value: '-75%' },
      { label: 'Data Accuracy', value: '99%' },
    ],
    demoAvailable: true,
    popularity: 5,
    isNew: false,
  },

  // TESTING TRACK
  {
    id: 'cert-testing-delegate',
    name: 'Cert Testing Delegate',
    tagline: 'Intelligent Game Certification Workflow',
    description: 'Manages game certification testing lifecycle. Reviews game images from 3rd party companies, enriches tickets, and manages triage/routing/assignment automatically.',
    detailedDescription: 'Work items (game images) arrive from 3rd party game companies requiring a complex testing lifecycle. AI agents review material, enrich tickets with metadata, and manage the entire triage/routing/assignment process, streamlining workflows and reducing cycle time significantly.',
    icon: 'TestTube2',
    status: 'live',
    capabilities: [
      agentCapabilities.multiModal,
      agentCapabilities.autonomous,
      agentCapabilities.toolUse,
      agentCapabilities.contextAware,
    ],
    category: 'testing',
    track: 'Test',
    features: [
      'Automated game image analysis',
      'Intelligent ticket enrichment',
      'Smart triage and routing',
      'Assignment optimization',
      '24/7 availability',
      'Workflow tracking and reporting',
    ],
    useCases: [
      'Xbox game certification',
      '3rd party game testing',
      'Compliance verification',
      'Quality assurance workflows',
      'Release readiness assessment',
    ],
    impact: [
      'Streamlined certification process',
      'Reduced cycle time significantly',
      '24/7 availability vs. business hours',
      'Faster response and routing',
    ],
    agenticHighlights: [
      'Agents streamline the process and reduce cycle time',
      'Improved time to respond/route as agent available 24x7',
    ],
    metrics: [
      { label: 'Cycle Time', value: '-55%' },
      { label: 'Response Time', value: '< 1hr' },
      { label: 'Accuracy', value: '96%' },
    ],
    demoAvailable: true,
    popularity: 4,
    isNew: false,
  },

  // MARKETING TRACK
  {
    id: 'xbox-indie-suite',
    name: 'XBOX Indie Gamer Suite',
    tagline: 'Empowering Independent Game Studios',
    description: 'Comprehensive suite helping indie developers with certification and marketing. Addresses gaming industry shift to small/independent studios.',
    detailedDescription: 'The gaming industry is shifting to small and independent dev studios. This suite brings indie studios into the XBOX platform with focused support in areas where small studios struggle: certification processes and effective marketing strategies.',
    icon: 'Gamepad2',
    status: 'beta',
    capabilities: [
      agentCapabilities.multiModal,
      agentCapabilities.toolUse,
      agentCapabilities.collaborative,
      agentCapabilities.contextAware,
    ],
    category: 'marketing',
    track: 'Marketing',
    features: [
      'Certification process guidance',
      'Marketing campaign automation',
      'Store presence optimization',
      'Community engagement tools',
      'Analytics and insights',
      'Platform integration support',
    ],
    useCases: [
      'Indie game certification',
      'Launch campaign planning',
      'Store listing optimization',
      'Social media marketing',
      'Community building',
    ],
    impact: [
      'Lowers barrier to entry for indie studios',
      'Faster time to market',
      'Better marketing effectiveness',
      'Increased indie presence on XBOX',
    ],
    agenticHighlights: [
      'Focus on areas where indie studios struggle most',
      'Combines certification and marketing support',
    ],
    metrics: [
      { label: 'Studios Supported', value: '500+' },
      { label: 'Time to Launch', value: '-40%' },
      { label: 'Marketing ROI', value: '+60%' },
    ],
    demoAvailable: true,
    popularity: 4,
    isNew: true,
    releaseDate: '2025-11-15',
  },

  // ENGINEERING TRACK
  {
    id: 'bic-agentic',
    name: 'BIC Agentic Solution',
    tagline: 'Enterprise Build & Integration Automation',
    description: 'Comprehensive build, integration, and continuous delivery solution leveraging agentic AI for complex enterprise engineering workflows.',
    detailedDescription: 'Advanced agentic system designed for complex build, integration, and CI/CD workflows in large-scale enterprise environments. Automates build orchestration, dependency management, integration testing, and deployment pipelines.',
    icon: 'Workflow',
    status: 'beta',
    capabilities: [
      agentCapabilities.autonomous,
      agentCapabilities.orchestration,
      agentCapabilities.toolUse,
      agentCapabilities.contextAware,
    ],
    category: 'engineering',
    track: 'Engineering',
    features: [
      'Automated build orchestration',
      'Intelligent dependency resolution',
      'CI/CD pipeline optimization',
      'Integration testing automation',
      'Deployment validation',
      'Rollback management',
    ],
    useCases: [
      'Large-scale build automation',
      'Microservices integration',
      'Multi-repo dependency management',
      'Continuous deployment pipelines',
      'Release orchestration',
    ],
    impact: [
      'Streamlined build processes',
      'Faster integration cycles',
      'Reduced deployment failures',
      'Better dependency management',
    ],
    agenticHighlights: [
      'Autonomous build and integration orchestration',
      'Context-aware deployment decisions',
    ],
    metrics: [
      { label: 'Build Time', value: '-45%' },
      { label: 'Deployment Success', value: '98%' },
      { label: 'MTTR', value: '-60%' },
    ],
    demoAvailable: false,
    popularity: 3,
    isNew: true,
    releaseDate: '2025-12-01',
  },

  // SRE TRACK (continued)
  {
    id: 'root-cause-analysis',
    name: 'Root-Cause Analysis Agent',
    tagline: 'AI-Powered RCA in Under 2 Minutes',
    description: 'Reads logs, service maps, dependencies, and recent changes. Runs RCA reasoning to identify likely causes with confidence scores and recommended fixes.',
    detailedDescription: 'Performs multi-source reasoning across logs, configuration, metrics, and code changes to generate human-level RCA summaries in under 2 minutes. Links issues to code commits, config drifts, and recent deployments for comprehensive root cause analysis.',
    icon: 'Search',
    status: 'live',
    capabilities: [
      agentCapabilities.rag,
      agentCapabilities.autonomous,
      agentCapabilities.contextAware,
      agentCapabilities.realTime,
    ],
    category: 'sre',
    track: 'SRE',
    features: [
      'Multi-source log analysis',
      'Service dependency mapping',
      'Configuration drift detection',
      'Code commit correlation',
      'Confidence score calculation',
      'Automated fix recommendations',
    ],
    useCases: [
      'Production incident RCA',
      'Performance degradation analysis',
      'Service outage investigation',
      'Deployment issue diagnosis',
      'Configuration problem detection',
    ],
    impact: [
      'Multi-source reasoning (logs + config + metrics + code)',
      'Generates human-level RCA in <2 mins',
      'Links to commits, config drifts, deployments',
    ],
    agenticHighlights: [
      'Reads logs, service maps, dependencies, recent changes',
      'Provides confidence score + recommended fix',
      'Generates RCA summary in <2 minutes',
    ],
    metrics: [
      { label: 'RCA Time', value: '< 2min' },
      { label: 'Accuracy', value: '91%' },
      { label: 'MTTR Reduction', value: '70%' },
    ],
    demoAvailable: true,
    popularity: 5,
    isNew: false,
  },

  {
    id: 'auto-runbook',
    name: 'Auto-Runbook Execution Agent',
    tagline: 'Autonomous Incident Remediation',
    description: 'Executes runbooks for standard incidents (restart pods, clear cache, failover, rollback) with validation. Escalates only when automated remediation fails.',
    detailedDescription: 'Provides autonomous execution with comprehensive safeguard checks. Handles standard operational tasks like pod restarts, cache clearing, failovers, and rollbacks. Validates post-execution health and learns which runbooks deliver the highest success rates.',
    icon: 'Play',
    status: 'live',
    capabilities: [
      agentCapabilities.autonomous,
      agentCapabilities.toolUse,
      agentCapabilities.realTime,
      agentCapabilities.contextAware,
    ],
    category: 'sre',
    track: 'SRE',
    features: [
      'Automated runbook execution',
      'Pre-execution safety checks',
      'Post-execution validation',
      'Health monitoring',
      'Intelligent escalation',
      'Success rate tracking',
    ],
    useCases: [
      'Service restart automation',
      'Cache clearing operations',
      'Failover execution',
      'Deployment rollbacks',
      'Resource cleanup',
    ],
    impact: [
      'Autonomous execution with safeguards',
      'Escalates only on failure',
      'Learns highest success rate runbooks',
    ],
    agenticHighlights: [
      'Executes standard incident runbooks autonomously',
      'Validates post-execution health',
      'Learns which runbook gives highest success rate',
    ],
    metrics: [
      { label: 'Automation Rate', value: '78%' },
      { label: 'Success Rate', value: '96%' },
      { label: 'MTTR', value: '-65%' },
    ],
    demoAvailable: true,
    popularity: 5,
    isNew: false,
  },

  {
    id: 'knowledge-troubleshooting',
    name: 'Knowledge & Troubleshooting Agent',
    tagline: 'Internal SRE Knowledge Base Intelligence',
    description: 'Queries all SRE knowledge sources (Confluence, SharePoint, Git, Postmortems) and generates tailored troubleshooting steps and fix instructions.',
    detailedDescription: 'Searches across structured and unstructured content to generate step-by-step fix instructions tailored to specific incidents. Acts as the internal SRE "brains," providing L1/L2 teams with exact troubleshooting guidance based on comprehensive knowledge base analysis.',
    icon: 'BookKey',
    status: 'live',
    capabilities: [
      agentCapabilities.rag,
      agentCapabilities.contextAware,
      agentCapabilities.streaming,
    ],
    category: 'sre',
    track: 'SRE',
    features: [
      'Multi-source knowledge search',
      'Structured + unstructured content analysis',
      'Step-by-step instruction generation',
      'Incident-tailored guidance',
      'Postmortem integration',
      'Quick "How to fix" summaries',
    ],
    useCases: [
      'L1/L2 engineer support',
      'Incident response guidance',
      'New team member onboarding',
      'Complex troubleshooting scenarios',
      'Knowledge discovery',
    ],
    impact: [
      'Searches across all knowledge sources',
      'Generates tailored fix instructions',
      'Acts as internal SRE "brains"',
    ],
    agenticHighlights: [
      'Queries Confluence, SharePoint, Git, Postmortems',
      'Suggests exact troubleshooting steps',
      'Generates quick "How to fix" summaries for L1/L2 teams',
    ],
    metrics: [
      { label: 'Knowledge Sources', value: '15+' },
      { label: 'Query Time', value: '< 5sec' },
      { label: 'Resolution Rate', value: '88%' },
    ],
    demoAvailable: true,
    popularity: 4,
    isNew: false,
  },

  {
    id: 'knowledge-graph-builder',
    name: 'Knowledge Graph Builder Agent',
    tagline: 'Living Memory for SRE & Support Ecosystem',
    description: 'Continuously ingests enterprise operational data to build a dynamic knowledge graph linking alerts, root causes, tickets, fixes, deployments, and dependencies.',
    detailedDescription: 'Ingests data from ICM/ServiceNow, Azure Monitor, App Insights, logs, traces, deployment pipelines, and RCAs. Extracts entities and builds an evolving knowledge graph that makes the entire operational landscape searchable and reason-ready. Learns relationships automatically and connects multi-format data to produce a living memory that gets smarter with every incident.',
    icon: 'Network',
    status: 'beta',
    capabilities: [
      agentCapabilities.rag,
      agentCapabilities.autonomous,
      agentCapabilities.contextAware,
      agentCapabilities.realTime,
    ],
    category: 'sre',
    track: 'SRE',
    features: [
      'Continuous data ingestion',
      'Entity extraction and linking',
      'Relationship learning',
      'Pattern identification',
      'Semantic understanding',
      'Predictive capabilities',
    ],
    useCases: [
      'Historical incident analysis',
      'Pattern detection',
      'Predictive alerting',
      'Knowledge discovery',
      'Root cause correlation',
    ],
    impact: [
      'Learns relationships automatically',
      'Understands meaning, not keywords',
      'Enables reasoning for other agents',
      'Produces living memory vs. static KB',
    ],
    agenticHighlights: [
      'Builds dynamic knowledge graph linking: Alerts ↔ Root causes, Tickets ↔ Fix steps, Deployments ↔ Incidents',
      'Understands meaning (e.g., "503", "service unavailable", "API timeout" → same root issue)',
      'Self-updates with new incidents, reducing stale documentation',
      'Unlocks predictive capabilities by identifying patterns humans miss',
    ],
    metrics: [
      { label: 'Entities Tracked', value: '500K+' },
      { label: 'Relationships', value: '2M+' },
      { label: 'Pattern Detection', value: '+85%' },
    ],
    demoAvailable: false,
    popularity: 5,
    isNew: true,
    releaseDate: '2025-10-15',
  },

  // RELEASE MANAGEMENT TRACK (continued)
  {
    id: 'rai-compliance-gate',
    name: 'Policy & RAI Compliance Gate',
    tagline: 'Responsible AI & Policy Enforcement',
    description: 'Validates RAI principles: safety, fairness, privacy, inclusiveness. Checks PII/PCI/PHI handling, content safety, consent, and retention policies.',
    detailedDescription: 'Performs scenario reasoning to simulate risky user journeys and auto-generates mitigations and guardrails. Verifies Entra ID scoping, Purview DLP rules, and data access boundaries. Provides continuous policy drift detection post-deployment.',
    icon: 'ShieldCheck',
    status: 'live',
    capabilities: [
      agentCapabilities.policyAware,
      agentCapabilities.contextAware,
      agentCapabilities.autonomous,
      agentCapabilities.rag,
    ],
    category: 'release-management',
    track: 'Release Management',
    features: [
      'RAI principle validation',
      'PII/PCI/PHI compliance checking',
      'Content safety assessment',
      'Scenario-based risk simulation',
      'Auto-generated guardrails',
      'Policy drift detection',
    ],
    useCases: [
      'AI model deployment validation',
      'Data privacy compliance',
      'Content safety verification',
      'Responsible AI assessment',
      'Regulatory compliance checks',
    ],
    impact: [
      'Scenario reasoning (simulates risky journeys)',
      'Auto-generates mitigations and guardrails',
      'Continuous policy drift detection post-deployment',
    ],
    agenticHighlights: [
      'Validates RAI principles: safety, fairness, privacy, inclusiveness',
      'Checks PII/PCI/PHI handling, content safety, consent, retention',
      'Verifies Entra ID scoping, Purview DLP rules, data access boundaries',
    ],
    metrics: [
      { label: 'Policy Violations', value: '0' },
      { label: 'Risk Scenarios', value: '1,000+' },
      { label: 'Compliance Rate', value: '100%' },
    ],
    demoAvailable: true,
    popularity: 5,
    isNew: false,
  },

  {
    id: 'legal-licensing-gate',
    name: 'Legal & Licensing Compliance Gate',
    tagline: 'Third-Party License & Export Control',
    description: 'Checks third-party models, datasets, and library licenses. Validates usage terms, export controls, and geo policies. Recommends alternative dependencies.',
    detailedDescription: 'Performs license reasoning and conflict detection. Ensures compliance with redistribution, commercial use, and attribution requirements. Validates export controls and geographical restrictions. Generates compliance statements for audit trails.',
    icon: 'FileCheck',
    status: 'live',
    capabilities: [
      agentCapabilities.rag,
      agentCapabilities.policyAware,
      agentCapabilities.contextAware,
      agentCapabilities.autonomous,
    ],
    category: 'release-management',
    track: 'Release Management',
    features: [
      'License compliance checking',
      'Conflict detection',
      'Alternative dependency recommendations',
      'Export control validation',
      'Geo-policy enforcement',
      'Audit statement generation',
    ],
    useCases: [
      'Third-party library validation',
      'Open source compliance',
      'Model license verification',
      'Dataset usage validation',
      'Export control compliance',
    ],
    impact: [
      'License reasoning and conflict detection',
      'Alternative dependency recommendations',
      'Generates compliance statements for audit',
    ],
    agenticHighlights: [
      'Checks third-party models, datasets, and libraries licenses',
      'Validates usage terms (redistribution, commercial use, attribution)',
      'Ensures export controls and geo policies',
    ],
    metrics: [
      { label: 'License Violations', value: '0' },
      { label: 'Dependencies Scanned', value: '50K+' },
      { label: 'Audit Readiness', value: '100%' },
    ],
    demoAvailable: true,
    popularity: 4,
    isNew: false,
  },

  {
    id: 'documentation-readiness-gate',
    name: 'Documentation & KB Readiness Gate',
    tagline: 'Automated Documentation Completeness',
    description: 'Confirms SOPs, FAQs, troubleshooting, and customer comms are ready. Ensures Knowledge Graph links and validates onboarding guides for SRE/Support teams.',
    detailedDescription: 'Auto-generates missing documentation from telemetry and tests. Measures documentation completeness and freshness. Blocks releases if critical documentation is missing, ensuring operational readiness.',
    icon: 'BookCheck',
    status: 'live',
    capabilities: [
      agentCapabilities.rag,
      agentCapabilities.autonomous,
      agentCapabilities.contextAware,
    ],
    category: 'release-management',
    track: 'Release Management',
    features: [
      'Documentation completeness checking',
      'Auto-generation from telemetry',
      'Freshness validation',
      'Knowledge Graph link verification',
      'Onboarding guide validation',
      'Critical doc requirement enforcement',
    ],
    useCases: [
      'Release documentation validation',
      'Runbook completeness checking',
      'Customer communication readiness',
      'Team onboarding preparation',
      'Knowledge base updates',
    ],
    impact: [
      'Auto-generates missing docs from telemetry/tests',
      'Measures doc completeness & freshness',
      'Blocks release if critical docs missing',
    ],
    agenticHighlights: [
      'Confirms SOPs, FAQs, troubleshooting, customer comms ready',
      'Ensures Knowledge Graph links (runbooks, RCA, configs)',
      'Validates onboarding guides for SRE/Support teams',
    ],
    metrics: [
      { label: 'Doc Coverage', value: '100%' },
      { label: 'Auto-Generated Docs', value: '2,500+' },
      { label: 'Freshness', value: '< 7 days' },
    ],
    demoAvailable: true,
    popularity: 4,
    isNew: false,
  },

  {
    id: 'safety-redteaming-gate',
    name: 'Safety Red-Teaming & Jailbreak Gate',
    tagline: 'Adversarial AI Safety Testing',
    description: 'Performs adversarial testing: jailbreaks, prompt injections, data exfiltration. Tests content safety in multilingual, code, and document contexts.',
    detailedDescription: 'Self-play adversary creates novel attack prompts and learns from community and internal incident patterns. Validates refusal behaviors and safety responses. Produces hardening diffs including system prompts, tool guards, and filters.',
    icon: 'Shield',
    status: 'beta',
    capabilities: [
      agentCapabilities.autonomous,
      agentCapabilities.multiModal,
      agentCapabilities.contextAware,
    ],
    category: 'release-management',
    track: 'Release Management',
    features: [
      'Jailbreak attack simulation',
      'Prompt injection testing',
      'Data exfiltration detection',
      'Multilingual safety testing',
      'Refusal behavior validation',
      'Automated hardening recommendations',
    ],
    useCases: [
      'AI model safety testing',
      'LLM security validation',
      'Content filter testing',
      'Adversarial robustness',
      'Safety mechanism verification',
    ],
    impact: [
      'Self-play adversary creates novel attacks',
      'Learns from community and incident patterns',
      'Produces hardening diffs (prompts, guards, filters)',
    ],
    agenticHighlights: [
      'Performs adversarial testing: jailbreaks, prompt injections, data exfil',
      'Tests content safety in multilingual, code, and document contexts',
      'Validates refusal behaviors and safety responses',
    ],
    metrics: [
      { label: 'Attack Scenarios', value: '10K+' },
      { label: 'Vulnerabilities Found', value: '250+' },
      { label: 'Hardening Success', value: '97%' },
    ],
    demoAvailable: false,
    popularity: 5,
    isNew: true,
    releaseDate: '2025-11-01',
  },

  {
    id: 'observability-ops-readiness-gate',
    name: 'Observability & Ops Readiness Gate',
    tagline: 'Comprehensive Production Readiness Validation',
    description: 'Ensures logs, metrics, traces, quality signals, and audit trails are wired. Checks alert rules, runbooks, escalation paths, and on-call rotations.',
    detailedDescription: 'Auto-generates runbooks from failure patterns and creates synthetic monitors and health checks. Validates dashboards for MTTR, accuracy, cost, and compliance. Blocks releases if monitoring coverage is less than 100%.',
    icon: 'Activity',
    status: 'live',
    capabilities: [
      agentCapabilities.autonomous,
      agentCapabilities.toolUse,
      agentCapabilities.contextAware,
      agentCapabilities.orchestration,
    ],
    category: 'release-management',
    track: 'Release Management',
    features: [
      'Telemetry validation',
      'Alert rule verification',
      'Runbook auto-generation',
      'Synthetic monitor creation',
      'Dashboard validation',
      'Coverage enforcement',
    ],
    useCases: [
      'Production deployment readiness',
      'Monitoring coverage validation',
      'Operational preparedness',
      'SRE readiness assessment',
      'Observability compliance',
    ],
    impact: [
      'Auto-generates runbooks from failure patterns',
      'Creates synthetic monitors and health checks',
      'Blocks release if monitoring coverage < 100%',
    ],
    agenticHighlights: [
      'Ensures logs, metrics, traces, quality signals, audit trails wired',
      'Checks alert rules, runbooks, escalation paths, on-call rotations',
      'Validates dashboards (MTTR, accuracy, cost, compliance)',
    ],
    metrics: [
      { label: 'Coverage', value: '100%' },
      { label: 'Auto-Generated Runbooks', value: '500+' },
      { label: 'Deployment Blocks', value: '45' },
    ],
    demoAvailable: true,
    popularity: 5,
    isNew: false,
  },
];

// Helper functions
export const getAgentById = (id: string): Agent | undefined => {
  return agents.find(agent => agent.id === id);
};

export const getAgentsByCategory = (category: Agent['category']): Agent[] => {
  return agents.filter(agent => agent.category === category);
};

export const getAgentsByStatus = (status: Agent['status']): Agent[] => {
  return agents.filter(agent => agent.status === status);
};

export const getLiveAgents = (): Agent[] => {
  return agents.filter(agent => agent.status === 'live');
};

export const getNewAgents = (): Agent[] => {
  return agents.filter(agent => agent.isNew);
};

export const getPopularAgents = (limit: number = 6): Agent[] => {
  return [...agents]
    .sort((a, b) => b.popularity - a.popularity)
    .slice(0, limit);
};

export const categories = [
  { id: 'content', label: 'Content', icon: 'FileEdit' },
  { id: 'planning', label: 'Planning', icon: 'Beaker' },
  { id: 'documentation', label: 'Documentation', icon: 'BookOpenText' },
  { id: 'operations', label: 'Operations', icon: 'Settings' },
  { id: 'support', label: 'Support', icon: 'Headset' },
  { id: 'testing', label: 'Testing', icon: 'TestTube2' },
  { id: 'marketing', label: 'Marketing', icon: 'Megaphone' },
  { id: 'legal', label: 'Legal', icon: 'Scale' },
  { id: 'engineering', label: 'Engineering', icon: 'Wrench' },
  { id: 'sre', label: 'SRE', icon: 'Server' },
  { id: 'release-management', label: 'Release Management', icon: 'Rocket' },
  { id: 'training', label: 'Training & Skilling', icon: 'GraduationCap' },
] as const;
