"""
UTA Agent - Unified Troubleshooting Assistant

RAG-powered agent for CCaaS support engineers. Uses:
- ChromaDB + Azure AI Foundry embeddings for knowledge retrieval
- Azure OpenAI gpt-4o (or Ollama fallback) for intelligent response generation

This agent helps support engineers by:
1. Searching SOPs, playbooks, and known issues
2. Classifying ticket issues
3. Generating diagnostic workflows
4. Validating configurations
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from agents.base_agent import BaseAgent, AgentResponse, AgentStatus
from core.config_manager import ConfigManager
from core.state_manager import StateManager
from core.uta_vectorstore_base import VectorStore, SearchResult, DocumentType
from core.uta_ollama_client import OllamaClient, ChatMessage, GenerationConfig
from core.rag_service import RAGService
from core.rag_types import RAGContext, RAGConfig

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

class IssueCategory(Enum):
    """Categories for CCaaS issues."""
    ROUTING = "routing"
    LICENSING = "licensing"
    CONNECTIVITY = "connectivity"
    AGENT_EXPERIENCE = "agent_experience"
    VOICE = "voice"
    CHAT = "chat"
    EMAIL = "email"
    INTEGRATION = "integration"
    CONFIGURATION = "configuration"
    PERFORMANCE = "performance"
    UNKNOWN = "unknown"


@dataclass
class AnalysisResult:
    """Result from analyzing a support ticket."""
    ticket_summary: str
    category: IssueCategory
    severity: str  # "low", "medium", "high", "critical"
    relevant_docs: List[SearchResult]
    suggested_steps: List[str]
    known_issues: List[Dict[str, str]]
    configuration_checks: List[Dict[str, str]]
    escalation_needed: bool
    confidence: float
    raw_response: str


# =============================================================================
# UTA Agent - Combined RAG Logic + API Integration
# =============================================================================

class UTAAgent(BaseAgent):
    """
    Unified Troubleshooting Assistant Agent.
    
    A RAG-powered agent that helps CCaaS support engineers troubleshoot
    issues by combining knowledge retrieval with LLM reasoning.
    
    Extends BaseAgent for API integration while containing all RAG logic.
    
    Features:
    - RAG-powered knowledge search (SOPs, playbooks, known issues)
    - Ticket analysis and categorization
    - Diagnostic workflow generation
    - Configuration validation
    - Uses local Ollama models (llama3.1:8b + nomic-embed-text)
    
    Usage:
        from agents import UTAAgent
        
        agent = UTAAgent()
        await agent.initialize()
        
        # Via API
        response = await agent.process("Customer reports calls not routing...")
        
        # Direct methods
        result = agent.analyze_ticket_sync("Ticket description...")
        answer = agent.quick_answer_sync("What is queue timeout?")
    """
    
    # System prompts for different tasks
    SYSTEM_PROMPTS = {
        "analyze": """You are UTA (Unified Troubleshooting Assistant), an expert AI assistant for Microsoft CCaaS (Contact Center as a Service) support engineers.

Your role is to analyze support tickets and provide actionable troubleshooting guidance based on the knowledge base context provided.

When analyzing a ticket:
1. Identify the core issue and categorize it
2. Reference specific SOPs, playbooks, or known issues from the context
3. Provide step-by-step troubleshooting guidance
4. Highlight any configuration checks needed
5. Indicate if escalation might be required

Be concise, technical, and actionable. Reference document IDs when citing sources.""",

        "search": """You are UTA, helping search and summarize relevant knowledge for CCaaS troubleshooting.

Based on the retrieved documents, provide a clear summary of the most relevant information.
Cite document IDs and highlight key steps or solutions.""",

        "diagnose": """You are UTA, generating diagnostic workflows for CCaaS issues.

Create clear, numbered diagnostic steps that a support engineer can follow.
Include specific checks, commands, or configurations to verify.
Reference relevant documentation when available.""",

        "config_check": """You are UTA, validating CCaaS configurations.

Analyze the provided configuration against best practices and known requirements.
Identify any misconfigurations, missing settings, or potential issues.
Provide specific remediation steps for each issue found.""",
    }
    
    def __init__(
        self, 
        config_manager: Optional[ConfigManager] = None,
        state_manager: Optional[StateManager] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        # Create default managers if not provided
        if config_manager is None:
            config_manager = ConfigManager(config_dir="configs")
        if state_manager is None:
            state_manager = StateManager(use_redis=False)
            
        super().__init__(
            agent_id="uta-troubleshooting",
            agent_name="Unified Troubleshooting Assistant (UTA)",
            description="RAG-powered troubleshooting assistant for CCaaS support engineers",
            capabilities=[
                "knowledge_search",
                "ticket_analysis", 
                "diagnostic_generation",
                "config_validation",
                "rag_enabled"
            ],
            config_manager=config_manager,
            state_manager=state_manager
        )
        
        self.config = config or {}
        
        # Load environment variables
        import os
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        # Embedding configuration - prefer Azure AI Foundry
        self.use_foundry = os.getenv("USE_FOUNDRY", "").lower() == "true"
        self.foundry_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
        self.foundry_api_key = os.getenv("FOUNDRY_API_KEY")
        self.embedding_model = self.config.get("embedding_model", os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"))
        
        # Ollama configuration (for LLM - separate from embedding provider)
        self.ollama_url = self.config.get("ollama_url", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
        # Use Ollama model for local LLM (not the Foundry deployment name)
        self.llm_model = self.config.get("llm_model", os.getenv("OLLAMA_LLM_MODEL", "llama3.1:8b-instruct-q8_0"))
        
        # RAG configuration
        self.top_k = self.config.get("top_k", 5)
        self.min_score = self.config.get("min_score", 0.05)  # Lowered for ChromaDB distance-based scoring
        
        # RAG Service (initialized in _setup_tools)
        self._rag_service: Optional[RAGService] = None
        
        # Components (lazy initialized) - kept for backward compatibility
        self._vector_store: Optional[VectorStore] = None
        self._llm: Optional[OllamaClient] = None
        
        # UTA-specific metrics
        self.uta_metrics = {
            "tickets_analyzed": 0,
            "knowledge_searches": 0,
            "diagnostics_generated": 0,
            "avg_response_time_ms": 0
        }
    
    # =========================================================================
    # BaseAgent Lifecycle Methods
    # =========================================================================
    
    async def _load_configuration(self) -> None:
        """Load agent-specific configuration"""
        self.logger.info("Loading UTA configuration...")
    
    async def _setup_tools(self) -> None:
        """Set up the UTA RAG components"""
        self.logger.info("Initializing UTA RAG components...")
        
        try:
            # Initialize vector store
            from core import VectorStoreFactory
            import os
            
            # Use Azure AI Foundry embeddings if configured, otherwise fallback to Ollama
            if self.use_foundry and self.foundry_endpoint:
                self.logger.info("Using Azure AI Foundry for embeddings")
                vector_config = {
                    "collection_name": "uta_knowledge_azure",
                    "persist_directory": "./data/chroma_azure",
                    "embedding_provider": "azure_openai",
                    "embedding_model": self.embedding_model,
                    "azure_openai_endpoint": self.foundry_endpoint,
                    "azure_openai_key": self.foundry_api_key,
                    "use_foundry": True,
                }
            else:
                self.logger.info("Using Ollama for embeddings")
                vector_config = {
                    "collection_name": "uta_knowledge",
                    "persist_directory": "./data/chroma",
                    "embedding_provider": "ollama",
                    "embedding_model": os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
                    "ollama_base_url": self.ollama_url,
                }
            
            self._vector_store = VectorStoreFactory.create(
                provider="chroma",
                config=vector_config,
            )
            
            doc_count = self._vector_store.count()
            self.logger.info(f"Vector store initialized with {doc_count} documents")
            
            # Initialize LLM client - use Azure OpenAI if Foundry is enabled
            if self.use_foundry and self.foundry_endpoint:
                from core.uta_azure_openai_llm import AzureOpenAIClient
                from core.uta_azure_openai_llm import ChatMessage as AzureChatMessage
                from core.uta_azure_openai_llm import GenerationConfig as AzureGenConfig
                
                self._llm = AzureOpenAIClient(
                    model=os.getenv("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4o"),
                    endpoint=self.foundry_endpoint,
                    api_key=self.foundry_api_key,
                    config=AzureGenConfig(
                        temperature=0.7,
                        max_tokens=2048,
                    ),
                    use_foundry=True,
                )
                self.logger.info(f"LLM initialized with Azure AI Foundry: {os.getenv('FOUNDRY_MODEL_DEPLOYMENT', 'gpt-4o')}")
            else:
                # Fallback to Ollama
                self._llm = OllamaClient(
                    model=self.llm_model,
                    base_url=self.ollama_url,
                    config=GenerationConfig(
                        temperature=0.7,
                        max_tokens=2048,
                    ),
                )
                self.logger.info(f"LLM initialized with Ollama: {self.llm_model}")
            
            # Initialize RAG Service with vector store and LLM
            self._rag_service = RAGService(
                vector_store=self._vector_store,
                llm_client=self._llm,
                config=RAGConfig(
                    top_k=self.top_k,
                    min_score=self.min_score,
                    use_query_expansion=True,
                ),
            )
            self.logger.info("RAG Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize UTA components: {e}")
            # Don't raise - we'll use fallback responses
    
    async def _execute_logic(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        """Execute the UTA agent's main logic"""
        start_time = datetime.utcnow()
        
        # Determine the type of request
        request_type = context.get("request_type", "auto")
        
        if self._rag_service is None or not self._rag_service.is_ready:
            return await self._fallback_response(user_input, context)
        
        try:
            # Route to appropriate handler
            if request_type == "ticket_analysis" or self._looks_like_ticket(user_input):
                return await self._handle_ticket_analysis(user_input, context)
            elif request_type == "diagnostic":
                return await self._handle_diagnostics(user_input, context)
            elif request_type == "config_check":
                return await self._handle_config_check(user_input, context)
            else:
                # Default: quick answer / knowledge search
                return await self._handle_quick_answer(user_input, context)
                
        except Exception as e:
            self.logger.error(f"Error in UTA execution: {e}", exc_info=True)
            return AgentResponse(
                content=f"I encountered an error while processing your request. Please try again or contact support.",
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                status=AgentStatus.ERROR,
                error=str(e)
            )
        finally:
            # Update metrics
            elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_avg_response_time(elapsed)
    
    # =========================================================================
    # Request Handlers (Async wrappers for API)
    # =========================================================================
    
    def _looks_like_ticket(self, text: str) -> bool:
        """Heuristic to detect if input looks like a support ticket"""
        ticket_indicators = [
            "customer:", "tenant:", "issue:", "error:", "impact:",
            "ticket", "case", "incident", "problem:", "symptoms:"
        ]
        text_lower = text.lower()
        return any(ind in text_lower for ind in ticket_indicators)
    
    async def _handle_ticket_analysis(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        """Handle ticket analysis request"""
        self.uta_metrics["tickets_analyzed"] += 1
        
        # Run in executor since core methods are synchronous
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.analyze_ticket_sync(user_input, context.get("customer_info"))
        )
        
        # Format response
        response_parts = [
            f"## Ticket Analysis\n",
            f"**Summary:** {result.ticket_summary}\n",
            f"**Category:** {result.category.value.replace('_', ' ').title()}\n",
            f"**Severity:** {result.severity.upper()}\n",
            f"**Confidence:** {result.confidence:.0%}\n",
            f"**Escalation Needed:** {'Yes' if result.escalation_needed else 'No'}\n",
        ]
        
        if result.relevant_docs:
            response_parts.append(f"\n### Relevant Documentation\n")
            for doc in result.relevant_docs[:3]:
                response_parts.append(f"- [{doc.document.id}] (relevance: {doc.score:.0%})\n")
        
        if result.suggested_steps:
            response_parts.append(f"\n### Troubleshooting Steps\n")
            for i, step in enumerate(result.suggested_steps[:7], 1):
                response_parts.append(f"{i}. {step}\n")
        
        if result.known_issues:
            response_parts.append(f"\n### Related Known Issues\n")
            for ki in result.known_issues[:3]:
                response_parts.append(f"- {ki.get('issue', 'N/A')}\n")
        
        if result.configuration_checks:
            response_parts.append(f"\n### Configuration Checks\n")
            for check in result.configuration_checks[:3]:
                response_parts.append(f"- {check.get('check', 'N/A')}\n")
        
        return AgentResponse(
            content="".join(response_parts),
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status=AgentStatus.COMPLETED,
            tools_used=["knowledge_search", "ticket_analysis"],
            metadata={
                "category": result.category.value,
                "severity": result.severity,
                "confidence": result.confidence,
                "escalation_needed": result.escalation_needed,
                "docs_found": len(result.relevant_docs),
            }
        )
    
    async def _handle_diagnostics(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        """Handle diagnostic workflow request"""
        self.uta_metrics["diagnostics_generated"] += 1
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.generate_diagnostics_sync(user_input, context.get("category"))
        )
        
        return AgentResponse(
            content=f"## Diagnostic Workflow\n\n{result}",
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status=AgentStatus.COMPLETED,
            tools_used=["knowledge_search", "diagnostic_generation"],
        )
    
    async def _handle_config_check(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        """Handle configuration validation request"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.check_configuration_sync(user_input, context.get("config_type"))
        )
        
        return AgentResponse(
            content=f"## Configuration Analysis\n\n{result}",
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status=AgentStatus.COMPLETED,
            tools_used=["knowledge_search", "config_validation"],
        )
    
    async def _handle_quick_answer(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        """Handle quick answer request"""
        self.uta_metrics["knowledge_searches"] += 1
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.quick_answer_sync(user_input)
        )
        
        return AgentResponse(
            content=result,
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status=AgentStatus.COMPLETED,
            tools_used=["knowledge_search"],
        )
    
    async def _fallback_response(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        """Fallback when components aren't initialized"""
        import os
        use_foundry = os.getenv("USE_FOUNDRY", "").lower() == "true"
        
        if use_foundry:
            setup_instructions = (
                "1. Ensure Azure AI Foundry credentials are configured in `.env`\n"
                "2. Run knowledge base ingestion: `python -m examples.uta_ingest_knowledge --clear`\n"
                "3. Restart the API server"
            )
        else:
            setup_instructions = (
                "1. Ollama is running (`ollama serve`)\n"
                "2. Models are pulled (`ollama pull nomic-embed-text` and `ollama pull llama3.1:8b-instruct-q8_0`)\n"
                "3. Knowledge base is ingested (`python -m examples.uta_ingest_knowledge`)"
            )
        
        return AgentResponse(
            content=(
                "I'm the Unified Troubleshooting Assistant (UTA), but my knowledge base "
                "components are still initializing. Please ensure:\n\n"
                f"{setup_instructions}\n\n"
                "Once ready, I can help you with:\n"
                "- Analyzing support tickets\n"
                "- Searching SOPs and playbooks\n"
                "- Generating diagnostic workflows\n"
                "- Validating configurations"
            ),
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status=AgentStatus.COMPLETED,
            metadata={"fallback": True}
        )
    
    # =========================================================================
    # Core RAG Methods (Synchronous) - Delegates to RAGService
    # =========================================================================
    
    def search_knowledge(
        self,
        query: str,
        doc_types: Optional[List[DocumentType]] = None,
        top_k: Optional[int] = None,
        use_query_expansion: bool = True,
    ) -> List[SearchResult]:
        """
        Search the knowledge base for relevant documents.
        
        Delegates to RAGService for actual search functionality.
        
        Args:
            query: Search query
            doc_types: Filter by document types
            top_k: Number of results (default: self.top_k)
            use_query_expansion: Whether to expand query into variations
            
        Returns:
            List of SearchResult objects
        """
        if self._rag_service is None or not self._rag_service.is_ready:
            return []
        
        return self._rag_service.search(
            query=query,
            doc_types=doc_types,
            top_k=top_k,
            use_query_expansion=use_query_expansion,
        )
    
    def _build_rag_context(
        self,
        query: str,
        doc_types: Optional[List[DocumentType]] = None,
    ) -> RAGContext:
        """
        Build RAG context by retrieving and formatting relevant documents.
        
        Delegates to RAGService for context building.
        """
        if self._rag_service is None or not self._rag_service.is_ready:
            return RAGContext(
                documents=[],
                formatted_context="RAG service not initialized.",
                doc_types_found=[],
                query=query,
            )
        
        return self._rag_service.build_context(query, doc_types=doc_types)
    
    def analyze_ticket_sync(
        self,
        ticket_description: str,
        customer_info: Optional[Dict[str, Any]] = None,
    ) -> AnalysisResult:
        """
        Analyze a support ticket and provide troubleshooting guidance.
        
        Args:
            ticket_description: The ticket text/description
            customer_info: Optional customer context (tenant, product, etc.)
            
        Returns:
            AnalysisResult with categorization and recommendations
        """
        logger.info(f"Analyzing ticket: {ticket_description[:100]}...")
        
        # Build RAG context
        context = self._build_rag_context(ticket_description)
        
        # Build the prompt
        customer_context = ""
        if customer_info:
            customer_context = f"""
Customer Information:
- Tenant: {customer_info.get('tenant', 'Unknown')}
- Product: {customer_info.get('product', 'CCaaS')}
- Environment: {customer_info.get('environment', 'Production')}
"""
        
        user_prompt = f"""Analyze this support ticket and provide troubleshooting guidance.

TICKET DESCRIPTION:
{ticket_description}
{customer_context}

KNOWLEDGE BASE CONTEXT:
{context.formatted_context}

Please provide:
1. SUMMARY: Brief summary of the issue (1-2 sentences)
2. CATEGORY: Issue category (routing/licensing/connectivity/agent_experience/voice/chat/email/integration/configuration/performance/unknown)
3. SEVERITY: low/medium/high/critical
4. RELEVANT DOCUMENTS: List document IDs that are most relevant
5. TROUBLESHOOTING STEPS: Numbered steps to resolve
6. KNOWN ISSUES: Any matching known issues from context
7. CONFIG CHECKS: Specific configurations to verify
8. ESCALATION: Yes/No - whether this might need escalation
9. CONFIDENCE: Your confidence level (0.0-1.0) in this analysis"""

        # Generate response
        messages = [
            ChatMessage(role="system", content=self.SYSTEM_PROMPTS["analyze"]),
            ChatMessage(role="user", content=user_prompt),
        ]
        
        response = self._llm.chat(messages)
        
        # Parse response into structured result
        return self._parse_analysis_response(response, context)
    
    def _parse_analysis_response(
        self,
        response: str,
        context: RAGContext,
    ) -> AnalysisResult:
        """Parse LLM response into structured AnalysisResult."""
        lines = response.strip().split("\n")
        
        # Defaults
        summary = ""
        category = IssueCategory.UNKNOWN
        severity = "medium"
        steps = []
        known_issues = []
        config_checks = []
        escalation = False
        confidence = 0.5
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            if "summary:" in line_lower:
                current_section = "summary"
                summary = line.split(":", 1)[-1].strip()
            elif "category:" in line_lower:
                current_section = "category"
                cat_str = line.split(":", 1)[-1].strip().lower()
                try:
                    category = IssueCategory(cat_str)
                except ValueError:
                    category = IssueCategory.UNKNOWN
            elif "severity:" in line_lower:
                current_section = "severity"
                severity = line.split(":", 1)[-1].strip().lower()
            elif "troubleshooting" in line_lower or "steps:" in line_lower:
                current_section = "steps"
            elif "known issue" in line_lower:
                current_section = "known_issues"
            elif "config" in line_lower and "check" in line_lower:
                current_section = "config_checks"
            elif "escalation:" in line_lower:
                current_section = "escalation"
                escalation = "yes" in line_lower
            elif "confidence:" in line_lower:
                current_section = "confidence"
                try:
                    conf_str = line.split(":", 1)[-1].strip()
                    confidence = float(conf_str.replace("%", "").strip())
                    if confidence > 1:
                        confidence = confidence / 100
                except ValueError:
                    confidence = 0.5
            elif current_section == "steps" and (line.startswith(("-", "•")) or line[0].isdigit()):
                steps.append(line.lstrip("-•0123456789. "))
            elif current_section == "known_issues" and (line.startswith(("-", "•")) or "KI-" in line):
                known_issues.append({"issue": line.lstrip("-• ")})
            elif current_section == "config_checks" and (line.startswith(("-", "•")) or line[0].isdigit()):
                config_checks.append({"check": line.lstrip("-•0123456789. ")})
        
        return AnalysisResult(
            ticket_summary=summary or "Unable to summarize",
            category=category,
            severity=severity if severity in ["low", "medium", "high", "critical"] else "medium",
            relevant_docs=context.documents,
            suggested_steps=steps or ["Review ticket details", "Check system status", "Contact customer for more info"],
            known_issues=known_issues,
            configuration_checks=config_checks,
            escalation_needed=escalation,
            confidence=confidence,
            raw_response=response,
        )
    
    def generate_diagnostics_sync(
        self,
        issue_description: str,
        category: Optional[str] = None,
    ) -> str:
        """
        Generate diagnostic workflow for an issue.
        
        Args:
            issue_description: Description of the issue
            category: Optional issue category for focused diagnostics
            
        Returns:
            Formatted diagnostic steps
        """
        # Get relevant playbooks and SOPs
        doc_types = [DocumentType.PLAYBOOK, DocumentType.SOP]
        context = self._build_rag_context(issue_description, doc_types)
        
        category_hint = f"Issue Category: {category}" if category else ""
        
        user_prompt = f"""Generate a diagnostic workflow for this issue.

ISSUE: {issue_description}
{category_hint}

RELEVANT DOCUMENTATION:
{context.formatted_context}

Provide numbered diagnostic steps that a support engineer can follow.
Include specific checks, commands, or configurations to verify."""

        messages = [
            ChatMessage(role="system", content=self.SYSTEM_PROMPTS["diagnose"]),
            ChatMessage(role="user", content=user_prompt),
        ]
        
        return self._llm.chat(messages)
    
    def check_configuration_sync(
        self,
        config_description: str,
        config_type: Optional[str] = None,
    ) -> str:
        """
        Validate a configuration against best practices.
        
        Args:
            config_description: Description or dump of configuration
            config_type: Type of config (e.g., "routing", "queue", "capacity")
            
        Returns:
            Configuration analysis and recommendations
        """
        doc_types = [DocumentType.CONFIG_CHECK, DocumentType.SOP]
        context = self._build_rag_context(
            f"{config_type or ''} configuration {config_description[:200]}", 
            doc_types
        )
        
        user_prompt = f"""Analyze this CCaaS configuration and identify any issues.

CONFIGURATION TYPE: {config_type or 'General'}

CONFIGURATION:
{config_description}

CONFIGURATION RULES AND BEST PRACTICES:
{context.formatted_context}

Identify any misconfigurations, missing settings, or potential issues.
Provide specific remediation steps for each issue found."""

        messages = [
            ChatMessage(role="system", content=self.SYSTEM_PROMPTS["config_check"]),
            ChatMessage(role="user", content=user_prompt),
        ]
        
        return self._llm.chat(messages)
    
    def quick_answer_sync(self, question: str) -> str:
        """
        Get a quick answer to a troubleshooting question.
        
        Args:
            question: The question to answer
            
        Returns:
            Concise answer based on knowledge base
        """
        context = self._build_rag_context(question)
        
        user_prompt = f"""Answer this troubleshooting question concisely.

QUESTION: {question}

CONTEXT:
{context.formatted_context}

Provide a direct, actionable answer. Cite sources if relevant."""

        messages = [
            ChatMessage(role="system", content=self.SYSTEM_PROMPTS["search"]),
            ChatMessage(role="user", content=user_prompt),
        ]
        
        return self._llm.chat(messages)
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def _update_avg_response_time(self, elapsed_ms: float) -> None:
        """Update average response time metric"""
        current_avg = self.uta_metrics.get("avg_response_time_ms", 0)
        total = self.metadata.get("total_requests", 1)
        new_avg = ((current_avg * (total - 1)) + elapsed_ms) / total
        self.uta_metrics["avg_response_time_ms"] = round(new_avg, 2)
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information with UTA-specific details"""
        info = super().get_info()
        
        info["uta_status"] = {
            "rag_service_ready": self._rag_service is not None and self._rag_service.is_ready,
            "vector_store_ready": self._vector_store is not None,
            "llm_ready": self._llm is not None,
            "documents_indexed": self._rag_service.document_count if self._rag_service else 0,
            "llm_model": self.llm_model,
            "embedding_model": self.embedding_model,
        }
        info["uta_metrics"] = self.uta_metrics
        
        # Include RAG service metrics if available
        if self._rag_service:
            info["rag_metrics"] = self._rag_service.metrics
        
        return info
