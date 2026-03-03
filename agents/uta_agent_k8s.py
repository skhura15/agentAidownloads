"""
UTA Agent - Kubernetes-Ready Version

Modified version of UTAAgent that uses the remote RAG service
when deployed in Kubernetes, or falls back to local RAG when running standalone.

This enables:
- Independent scaling of RAG and Agent workloads
- Shared knowledge base across multiple agents
- Better resource utilization

Usage:
    # In Kubernetes (uses remote RAG service)
    agent = UTAAgentK8s(rag_service_url="http://rag-service:8001")
    
    # Local development (auto-fallback to local RAG)
    agent = UTAAgentK8s()  # Will check RAG_SERVICE_URL env var
"""

import asyncio
import logging
import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from agents.base_agent import BaseAgent, AgentResponse, AgentStatus
from core.config_manager import ConfigManager
from core.state_manager import StateManager

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes (same as original)
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
    severity: str
    relevant_docs: List[Any]
    suggested_steps: List[str]
    known_issues: List[Dict[str, str]]
    configuration_checks: List[Dict[str, str]]
    escalation_needed: bool
    confidence: float
    raw_response: str


# =============================================================================
# UTA Agent - Kubernetes Version
# =============================================================================

class UTAAgentK8s(BaseAgent):
    """
    Unified Troubleshooting Assistant Agent - Kubernetes Ready.
    
    This version of UTAAgent can operate in two modes:
    
    1. **Remote Mode** (Kubernetes): Uses RAG Service client to communicate
       with the standalone RAG service deployed in Kubernetes.
       
    2. **Local Mode** (Development): Falls back to local RAGService when
       no remote service is available.
    
    The mode is automatically detected based on:
    - RAG_SERVICE_URL environment variable
    - Health check of remote service
    
    Example:
        # Kubernetes deployment
        agent = UTAAgentK8s(rag_service_url="http://rag-service:8001")
        
        # Local development (auto-detect)
        agent = UTAAgentK8s()
    """
    
    SYSTEM_PROMPTS = {
        "analyze": """You are UTA (Unified Troubleshooting Assistant), an expert AI assistant for Microsoft CCaaS support engineers.

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
        rag_service_url: Optional[str] = None,
        config_manager: Optional[ConfigManager] = None,
        state_manager: Optional[StateManager] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        if config_manager is None:
            config_manager = ConfigManager(config_dir="configs")
        if state_manager is None:
            state_manager = StateManager(use_redis=False)
            
        super().__init__(
            agent_id="uta-troubleshooting-k8s",
            agent_name="Unified Troubleshooting Assistant (UTA)",
            description="RAG-powered troubleshooting assistant for CCaaS support engineers (K8s-ready)",
            capabilities=[
                "knowledge_search",
                "ticket_analysis",
                "diagnostic_generation",
                "config_validation",
                "rag_enabled",
                "kubernetes_ready",
            ],
            config_manager=config_manager,
            state_manager=state_manager,
        )
        
        self.config = config or {}
        
        # RAG Service URL (remote or local)
        self.rag_service_url = rag_service_url or os.getenv(
            "RAG_SERVICE_URL",
            "http://localhost:8001"
        )
        
        # Clients (lazy initialized)
        self._rag_client = None  # Remote RAG service client
        self._local_rag_service = None  # Fallback local RAG service
        self._llm = None  # For local mode
        
        # Mode detection
        self._use_remote = False
        
        # Metrics
        self.uta_metrics = {
            "tickets_analyzed": 0,
            "knowledge_searches": 0,
            "diagnostics_generated": 0,
            "avg_response_time_ms": 0,
            "mode": "unknown",
        }
    
    # =========================================================================
    # BaseAgent Lifecycle
    # =========================================================================
    
    async def _load_configuration(self) -> None:
        """Load configuration."""
        self.logger.info("Loading UTA K8s configuration...")
    
    async def _setup_tools(self) -> None:
        """Initialize RAG client (remote or local fallback)."""
        self.logger.info("Initializing UTA K8s agent...")
        
        # Try remote RAG service first
        if await self._try_remote_rag():
            self._use_remote = True
            self.uta_metrics["mode"] = "remote"
            self.logger.info(f"Using remote RAG service at {self.rag_service_url}")
        else:
            # Fall back to local RAG
            self._use_remote = False
            self.uta_metrics["mode"] = "local"
            await self._setup_local_rag()
            self.logger.info("Using local RAG service (fallback)")
    
    async def _try_remote_rag(self) -> bool:
        """Try to connect to remote RAG service."""
        try:
            from rag_service.client import RAGServiceClient
            
            self._rag_client = RAGServiceClient(base_url=self.rag_service_url)
            
            # Health check with timeout
            is_ready = await asyncio.wait_for(
                self._rag_client.is_ready(),
                timeout=5.0
            )
            
            if is_ready:
                self.logger.info("Remote RAG service is ready")
                return True
            else:
                self.logger.warning("Remote RAG service not ready")
                await self._rag_client.close()
                self._rag_client = None
                return False
                
        except Exception as e:
            self.logger.warning(f"Cannot connect to remote RAG service: {e}")
            if self._rag_client:
                await self._rag_client.close()
                self._rag_client = None
            return False
    
    async def _setup_local_rag(self) -> None:
        """Set up local RAG service (fallback)."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        try:
            from core import VectorStoreFactory
            from core.rag_service import RAGService
            from core.rag_types import RAGConfig
            
            use_foundry = os.getenv("USE_FOUNDRY", "").lower() == "true"
            foundry_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
            foundry_api_key = os.getenv("FOUNDRY_API_KEY")
            
            # Vector store
            if use_foundry and foundry_endpoint:
                vector_config = {
                    "collection_name": "uta_knowledge_azure",
                    "persist_directory": "./data/chroma_azure",
                    "embedding_provider": "azure_openai",
                    "embedding_model": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
                    "azure_openai_endpoint": foundry_endpoint,
                    "azure_openai_key": foundry_api_key,
                    "use_foundry": True,
                }
            else:
                vector_config = {
                    "collection_name": "uta_knowledge",
                    "persist_directory": "./data/chroma",
                    "embedding_provider": "ollama",
                    "embedding_model": os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
                    "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                }
            
            vector_store = VectorStoreFactory.create(provider="chroma", config=vector_config)
            
            # LLM client
            if use_foundry and foundry_endpoint:
                from core.uta_azure_openai_llm import AzureOpenAIClient
                from core.uta_azure_openai_llm import GenerationConfig as AzureGenConfig
                
                self._llm = AzureOpenAIClient(
                    model=os.getenv("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4o"),
                    endpoint=foundry_endpoint,
                    api_key=foundry_api_key,
                    config=AzureGenConfig(temperature=0.7, max_tokens=2048),
                    use_foundry=True,
                )
            else:
                from core.uta_ollama_client import OllamaClient, GenerationConfig
                
                self._llm = OllamaClient(
                    model=os.getenv("OLLAMA_LLM_MODEL", "llama3.1:8b-instruct-q8_0"),
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                    config=GenerationConfig(temperature=0.7, max_tokens=2048),
                )
            
            self._local_rag_service = RAGService(
                vector_store=vector_store,
                llm_client=self._llm,
                config=RAGConfig(top_k=5, min_score=0.05),
            )
            
            self.logger.info(f"Local RAG initialized with {vector_store.count()} documents")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize local RAG: {e}")
    
    async def _execute_logic(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        """Execute the UTA agent's main logic."""
        start_time = datetime.utcnow()
        request_type = context.get("request_type", "auto")
        
        # Check if we have any RAG capability
        if not self._is_rag_ready():
            return await self._fallback_response(user_input, context)
        
        try:
            if request_type == "ticket_analysis" or self._looks_like_ticket(user_input):
                return await self._handle_ticket_analysis(user_input, context)
            elif request_type == "diagnostic":
                return await self._handle_diagnostics(user_input, context)
            elif request_type == "config_check":
                return await self._handle_config_check(user_input, context)
            else:
                return await self._handle_quick_answer(user_input, context)
                
        except Exception as e:
            self.logger.error(f"Error in UTA execution: {e}", exc_info=True)
            return AgentResponse(
                content=f"I encountered an error while processing your request: {str(e)}",
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                status=AgentStatus.ERROR,
                error=str(e),
            )
        finally:
            elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_avg_response_time(elapsed)
    
    def _is_rag_ready(self) -> bool:
        """Check if RAG is available (remote or local)."""
        if self._use_remote:
            return self._rag_client is not None
        return self._local_rag_service is not None and self._local_rag_service.is_ready
    
    def _looks_like_ticket(self, text: str) -> bool:
        """Detect if input looks like a support ticket."""
        indicators = [
            "customer:", "tenant:", "issue:", "error:", "impact:",
            "ticket", "case", "incident", "problem:", "symptoms:"
        ]
        text_lower = text.lower()
        return any(ind in text_lower for ind in indicators)
    
    # =========================================================================
    # Request Handlers
    # =========================================================================
    
    async def _handle_quick_answer(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        """Handle quick answer using remote or local RAG."""
        self.uta_metrics["knowledge_searches"] += 1
        
        if self._use_remote:
            # Use remote RAG service
            response = await self._rag_client.generate(
                query=user_input,
                system_prompt=self.SYSTEM_PROMPTS["search"],
            )
            content = response.response
        else:
            # Use local RAG
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(
                None,
                lambda: self._quick_answer_local(user_input)
            )
        
        return AgentResponse(
            content=content,
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status=AgentStatus.COMPLETED,
            tools_used=["knowledge_search"],
            metadata={"mode": "remote" if self._use_remote else "local"},
        )
    
    def _quick_answer_local(self, question: str) -> str:
        """Local quick answer implementation."""
        from core.uta_ollama_client import ChatMessage
        
        context = self._local_rag_service.build_context(question)
        
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
    
    async def _handle_ticket_analysis(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        """Handle ticket analysis."""
        self.uta_metrics["tickets_analyzed"] += 1
        
        if self._use_remote:
            # Remote: Get context and generate
            ctx_response = await self._rag_client.build_context(user_input)
            gen_response = await self._rag_client.generate(
                query=user_input,
                system_prompt=self.SYSTEM_PROMPTS["analyze"],
            )
            content = f"## Ticket Analysis\n\n{gen_response.response}"
            
            return AgentResponse(
                content=content,
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                status=AgentStatus.COMPLETED,
                tools_used=["knowledge_search", "ticket_analysis"],
                metadata={
                    "mode": "remote",
                    "docs_found": ctx_response.document_count,
                },
            )
        else:
            # Local: Use existing logic
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._analyze_ticket_local(user_input, context.get("customer_info"))
            )
            return self._format_analysis_response(result)
    
    def _analyze_ticket_local(self, ticket: str, customer_info: Optional[Dict] = None) -> AnalysisResult:
        """Local ticket analysis implementation."""
        from core.uta_ollama_client import ChatMessage
        
        context = self._local_rag_service.build_context(ticket)
        
        customer_context = ""
        if customer_info:
            customer_context = f"\nCustomer: {customer_info.get('tenant', 'Unknown')}"
        
        user_prompt = f"""Analyze this support ticket.

TICKET: {ticket}{customer_context}

CONTEXT: {context.formatted_context}

Provide SUMMARY, CATEGORY, SEVERITY, STEPS, and ESCALATION recommendation."""

        messages = [
            ChatMessage(role="system", content=self.SYSTEM_PROMPTS["analyze"]),
            ChatMessage(role="user", content=user_prompt),
        ]
        
        response = self._llm.chat(messages)
        
        return AnalysisResult(
            ticket_summary=ticket[:100],
            category=IssueCategory.UNKNOWN,
            severity="medium",
            relevant_docs=[],
            suggested_steps=["Review the analysis above"],
            known_issues=[],
            configuration_checks=[],
            escalation_needed=False,
            confidence=0.7,
            raw_response=response,
        )
    
    def _format_analysis_response(self, result: AnalysisResult) -> AgentResponse:
        """Format analysis result into AgentResponse."""
        return AgentResponse(
            content=f"## Ticket Analysis\n\n{result.raw_response}",
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status=AgentStatus.COMPLETED,
            tools_used=["knowledge_search", "ticket_analysis"],
            metadata={
                "mode": "local",
                "category": result.category.value,
                "severity": result.severity,
            },
        )
    
    async def _handle_diagnostics(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        """Handle diagnostic generation."""
        self.uta_metrics["diagnostics_generated"] += 1
        
        if self._use_remote:
            response = await self._rag_client.generate(
                query=user_input,
                system_prompt=self.SYSTEM_PROMPTS["diagnose"],
            )
            content = response.response
        else:
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(
                None,
                lambda: self._generate_diagnostics_local(user_input, context.get("category"))
            )
        
        return AgentResponse(
            content=f"## Diagnostic Workflow\n\n{content}",
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status=AgentStatus.COMPLETED,
            tools_used=["knowledge_search", "diagnostic_generation"],
        )
    
    def _generate_diagnostics_local(self, issue: str, category: Optional[str] = None) -> str:
        """Local diagnostics generation."""
        from core.uta_ollama_client import ChatMessage
        from core.uta_vectorstore_base import DocumentType
        
        doc_types = [DocumentType.PLAYBOOK, DocumentType.SOP]
        context = self._local_rag_service.build_context(issue, doc_types=doc_types)
        
        user_prompt = f"""Generate diagnostic workflow for: {issue}

CONTEXT: {context.formatted_context}"""

        messages = [
            ChatMessage(role="system", content=self.SYSTEM_PROMPTS["diagnose"]),
            ChatMessage(role="user", content=user_prompt),
        ]
        
        return self._llm.chat(messages)
    
    async def _handle_config_check(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        """Handle configuration check."""
        if self._use_remote:
            response = await self._rag_client.generate(
                query=user_input,
                system_prompt=self.SYSTEM_PROMPTS["config_check"],
            )
            content = response.response
        else:
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(
                None,
                lambda: self._check_config_local(user_input, context.get("config_type"))
            )
        
        return AgentResponse(
            content=f"## Configuration Analysis\n\n{content}",
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status=AgentStatus.COMPLETED,
            tools_used=["knowledge_search", "config_validation"],
        )
    
    def _check_config_local(self, config: str, config_type: Optional[str] = None) -> str:
        """Local config check."""
        from core.uta_ollama_client import ChatMessage
        
        context = self._local_rag_service.build_context(f"{config_type or ''} config {config[:200]}")
        
        user_prompt = f"""Analyze this configuration:

TYPE: {config_type or 'General'}
CONFIG: {config}

REFERENCE: {context.formatted_context}"""

        messages = [
            ChatMessage(role="system", content=self.SYSTEM_PROMPTS["config_check"]),
            ChatMessage(role="user", content=user_prompt),
        ]
        
        return self._llm.chat(messages)
    
    async def _fallback_response(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        """Fallback when RAG is not available."""
        return AgentResponse(
            content=(
                "I'm the Unified Troubleshooting Assistant (UTA), but my knowledge base "
                "is currently unavailable.\n\n"
                f"**Mode:** {'Remote' if self._use_remote else 'Local'}\n"
                f"**RAG Service URL:** {self.rag_service_url}\n\n"
                "Please ensure the RAG service is running and accessible."
            ),
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status=AgentStatus.COMPLETED,
            metadata={"fallback": True},
        )
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def _update_avg_response_time(self, elapsed_ms: float) -> None:
        """Update average response time."""
        current_avg = self.uta_metrics.get("avg_response_time_ms", 0)
        total = self.metadata.get("total_requests", 1)
        new_avg = ((current_avg * (total - 1)) + elapsed_ms) / total
        self.uta_metrics["avg_response_time_ms"] = round(new_avg, 2)
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        info = super().get_info()
        
        info["uta_status"] = {
            "mode": "remote" if self._use_remote else "local",
            "rag_service_url": self.rag_service_url if self._use_remote else None,
            "rag_ready": self._is_rag_ready(),
        }
        info["uta_metrics"] = self.uta_metrics
        
        return info
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self._rag_client:
            await self._rag_client.close()
        await super().cleanup()
