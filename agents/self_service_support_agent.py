"""
Self-Service Support Agent Implementation

Delivers frictionless support with AI-human hybrid approach using Ollama.
Focuses on cost optimization by using lightweight local models for initial triage
and escalating to more capable models only when needed.

Features:
- Cost-optimized model selection (small model -> large model)
- Context preservation across escalation
- Knowledge base RAG integration
- Sentiment analysis
- Human-in-the-loop for complex issues
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests

from agents.base_agent import BaseAgent, AgentResponse, AgentStatus
from core.config_manager import ConfigManager
from core.state_manager import StateManager


class SelfServiceSupportAgent(BaseAgent):
    """
    Self-Service Support Agent using Ollama for local AI inference.
    
    Uses tiered model approach:
    - Level 1: Lightweight model (phi3-mini) for simple queries
    - Level 2: Medium model (mistral) for technical issues
    - Level 3: Large model (llama3) + human escalation for complex problems
    """
    
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
            agent_id="self-service-support",
            agent_name="Self-Service Support Agent",
            description="AI-powered customer support with tiered model approach",
            capabilities=["customer_support", "knowledge_base_search", "sentiment_analysis", "escalation"],
            config_manager=config_manager,
            state_manager=state_manager
        )
        
        self.config = config or {}
        
        # Ollama configuration
        self.ollama_url = self.config.get("ollama_url", "http://localhost:11434")
        
        # Model tier configuration (cost-optimized)
        self.models = {
            "tier1": "phi3:mini",      # Lightweight - simple queries
            "tier2": "mistral:latest",  # Medium - technical issues
            "tier3": "llama3:latest"    # Advanced - complex problems
        }
        
        # Knowledge base (simulated)
        self.knowledge_base = self._load_knowledge_base()
        
        # Support metrics
        self.metrics = {
            "total_queries": 0,
            "tier1_resolved": 0,
            "tier2_resolved": 0,
            "escalated": 0,
            "avg_resolution_time": 0,
            "cost_savings": 0.0
        }
    
    async def _load_configuration(self) -> None:
        """Load agent-specific configuration"""
        # Configuration is already loaded in __init__
        self.logger.info("Configuration loaded for Self-Service Support Agent")
    
    async def _setup_tools(self) -> None:
        """Set up agent-specific tools"""
        # Tools are built-in methods for this agent
        self.logger.info("Tools configured for Self-Service Support Agent")
    
    async def _execute_logic(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        """Execute the agent's main logic"""
        task = {
            "query": user_input,
            "user_context": context,
            "escalation_allowed": True
        }
        return await self.execute_support_query(task)
    
    async def execute_support_query(self, task: Dict[str, Any]) -> AgentResponse:
        """
        Execute support query with tiered model approach (renamed from execute)
        """
        try:
            start_time = datetime.now()
            query = task.get("query", "")
            user_context = task.get("user_context", {})
            escalation_allowed = task.get("escalation_allowed", True)
            
            self.metrics["total_queries"] += 1
            
            # Step 1: Sentiment analysis
            sentiment = self._analyze_sentiment(query)
            self.logger.info(f"Query sentiment: {sentiment['sentiment']} (score: {sentiment['score']})")
            
            # Step 2: Search knowledge base (RAG)
            kb_results = self._search_knowledge_base(query)
            kb_context = "\n\n".join([
                f"KB Article {r['id']}: {r['question']}\n{r['answer']}"
                for r in kb_results
            ]) if kb_results else "No relevant knowledge base articles found."
            
            # Step 3: Classify complexity
            tier = self._classify_query_complexity(query)
            model = self.models[tier]
            
            self.logger.info(f"Using {tier} model: {model}")
            
            # Step 4: Construct prompt with RAG context
            system_prompt = """You are a helpful customer support agent. Provide clear, concise answers.
If you don't know the answer, admit it and suggest escalation to human support.
Be empathetic and professional. Keep responses under 200 words unless detailed steps are needed."""
            
            user_prompt = f"""Customer Query: {query}

Relevant Knowledge Base Information:
{kb_context}

User Context: {json.dumps(user_context) if user_context else 'No additional context'}

Please provide a helpful response. If this requires human assistance or is outside your knowledge, clearly state that."""
            
            # Step 5: Call appropriate model tier
            response_text = self._call_ollama(model, user_prompt, system_prompt)
            
            # Step 6: Determine if escalation needed
            escalation_keywords = [
                "escalate", "human", "specialist", "complex", 
                "don't know", "uncertain", "cannot help"
            ]
            needs_escalation = any(keyword in response_text.lower() for keyword in escalation_keywords)
            
            # Update metrics
            if tier == "tier1":
                self.metrics["tier1_resolved"] += 1
                cost_saved = 0.10  # Simulated cost savings
            elif tier == "tier2":
                self.metrics["tier2_resolved"] += 1
                cost_saved = 0.05
            else:
                cost_saved = 0.0
            
            if needs_escalation and escalation_allowed:
                self.metrics["escalated"] += 1
                response_text += "\n\n⚠️ This query has been escalated to human support for further assistance."
            
            self.metrics["cost_savings"] += cost_saved
            
            # Calculate resolution time
            resolution_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare metadata
            metadata = {
                "model_tier": tier,
                "model_used": model,
                "sentiment": sentiment,
                "kb_articles_found": len(kb_results),
                "needs_escalation": needs_escalation,
                "resolution_time_seconds": resolution_time,
                "cost_saved_usd": cost_saved,
                "timestamp": datetime.now().isoformat()
            }
            
            return AgentResponse(
                content=response_text,
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                status=AgentStatus.COMPLETED,
                metadata=metadata,
                tools_used=["knowledge_base_search", "sentiment_analysis", f"ollama_{model}"],
                handoff_to="human_support" if needs_escalation else None
            )
            
        except Exception as e:
            self.logger.error(f"Error in support agent: {str(e)}")
            return AgentResponse(
                content=f"I apologize, but I encountered an error processing your request. Please try again or contact human support.",
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                status=AgentStatus.ERROR,
                error=str(e)
            )
    
    def _load_knowledge_base(self) -> List[Dict[str, str]]:
        """Load simulated knowledge base for RAG"""
        return [
            {
                "id": "kb001",
                "category": "account",
                "question": "How do I reset my password?",
                "answer": "To reset your password: 1) Click 'Forgot Password' on login page, 2) Enter your email, 3) Check your inbox for reset link, 4) Create new password (min 8 chars, must include uppercase, number, and special character)."
            },
            {
                "id": "kb002",
                "category": "billing",
                "question": "How do I update my payment method?",
                "answer": "Update payment: 1) Go to Account Settings > Billing, 2) Click 'Update Payment Method', 3) Enter new card details, 4) Click 'Save'. Changes take effect immediately."
            },
            {
                "id": "kb003",
                "category": "technical",
                "question": "Why is my dashboard loading slowly?",
                "answer": "Dashboard performance: 1) Clear browser cache and cookies, 2) Try incognito/private mode, 3) Check network connection, 4) Disable browser extensions. If issue persists, contact support with browser version and error console logs."
            },
            {
                "id": "kb004",
                "category": "features",
                "question": "How do I export my data?",
                "answer": "Data export: 1) Navigate to Settings > Data Management, 2) Click 'Export Data', 3) Select format (CSV/JSON/Excel), 4) Choose date range, 5) Click 'Generate Export'. You'll receive download link via email within 15 minutes."
            },
            {
                "id": "kb005",
                "category": "account",
                "question": "How do I delete my account?",
                "answer": "Account deletion: 1) Go to Settings > Account, 2) Scroll to 'Delete Account' section, 3) Click 'Request Deletion', 4) Confirm via email link. Account will be permanently deleted after 30-day grace period. This action cannot be undone."
            },
            {
                "id": "kb006",
                "category": "integration",
                "question": "How do I connect to Microsoft Teams?",
                "answer": "Teams integration: 1) Settings > Integrations > Microsoft Teams, 2) Click 'Connect', 3) Sign in with Microsoft account, 4) Grant permissions, 5) Select channels to sync. Integration may take 5-10 minutes to activate."
            },
            {
                "id": "kb007",
                "category": "security",
                "question": "How do I enable two-factor authentication?",
                "answer": "Enable 2FA: 1) Settings > Security > Two-Factor Authentication, 2) Choose method (SMS/App), 3) If using app, scan QR code with authenticator app, 4) Enter verification code, 5) Save backup codes. Recommended for all accounts."
            },
            {
                "id": "kb008",
                "category": "troubleshooting",
                "question": "Error: 'Session expired' keeps appearing",
                "answer": "Session expiry fix: 1) Log out completely, 2) Clear all cookies for our domain, 3) Close browser entirely, 4) Restart browser and log in again. If persistent, check system clock is accurate and try different browser."
            }
        ]
    
    def _search_knowledge_base(self, query: str) -> List[Dict[str, str]]:
        """Simple keyword-based knowledge base search"""
        query_lower = query.lower()
        results = []
        
        for article in self.knowledge_base:
            if (query_lower in article["question"].lower() or 
                query_lower in article["answer"].lower() or
                query_lower in article["category"].lower()):
                results.append(article)
        
        return results[:3]  # Top 3 matches
    
    def _call_ollama(self, model: str, prompt: str, system: Optional[str] = None) -> str:
        """Call Ollama API for inference"""
        try:
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            if system:
                payload["system"] = system
            
            self.logger.info(f"Calling Ollama with model: {model}")
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ollama API error: {str(e)}")
            return f"Error connecting to local AI: {str(e)}"
    
    def _classify_query_complexity(self, query: str) -> str:
        """Classify query to determine which model tier to use"""
        query_lower = query.lower()
        
        # Simple keywords that tier1 can handle
        simple_keywords = [
            "password", "reset", "login", "forgot", "email",
            "how do i", "where is", "find", "access"
        ]
        
        # Technical keywords requiring tier2
        technical_keywords = [
            "error", "bug", "crash", "slow", "performance",
            "api", "integration", "webhook", "authentication"
        ]
        
        # Complex keywords requiring tier3
        complex_keywords = [
            "migration", "enterprise", "custom", "architecture",
            "security policy", "compliance", "gdpr", "sso"
        ]
        
        if any(keyword in query_lower for keyword in complex_keywords):
            return "tier3"
        elif any(keyword in query_lower for keyword in technical_keywords):
            return "tier2"
        else:
            return "tier1"
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Simple sentiment analysis"""
        negative_words = ["angry", "frustrated", "terrible", "horrible", "upset", "disappointed"]
        positive_words = ["great", "excellent", "thank", "appreciate", "happy", "satisfied"]
        
        text_lower = text.lower()
        negative_count = sum(1 for word in negative_words if word in text_lower)
        positive_count = sum(1 for word in positive_words if word in text_lower)
        
        if negative_count > positive_count:
            sentiment = "negative"
            score = 0.3
        elif positive_count > negative_count:
            sentiment = "positive"
            score = 0.8
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {
            "sentiment": sentiment,
            "score": score,
            "requires_priority": sentiment == "negative" and negative_count > 1
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        total_resolved = self.metrics["tier1_resolved"] + self.metrics["tier2_resolved"]
        
        return {
            "total_queries": self.metrics["total_queries"],
            "total_resolved": total_resolved,
            "tier1_resolved": self.metrics["tier1_resolved"],
            "tier2_resolved": self.metrics["tier2_resolved"],
            "escalated": self.metrics["escalated"],
            "escalation_rate": f"{(self.metrics['escalated'] / max(self.metrics['total_queries'], 1)) * 100:.1f}%",
            "cost_savings_usd": f"${self.metrics['cost_savings']:.2f}",
            "avg_tier1_percentage": f"{(self.metrics['tier1_resolved'] / max(total_resolved, 1)) * 100:.1f}%"
        }


# Simulated test data
SAMPLE_SUPPORT_QUERIES = [
    {
        "query": "I forgot my password and can't log in. How do I reset it?",
        "user_context": {"user_id": "user123", "account_type": "basic"},
        "expected_tier": "tier1"
    },
    {
        "query": "My dashboard is loading extremely slow and I'm getting a 504 error. This is affecting my work!",
        "user_context": {"user_id": "user456", "account_type": "premium"},
        "expected_tier": "tier2"
    },
    {
        "query": "I need to integrate your API with our enterprise SSO system using SAML 2.0. Can you provide documentation for custom enterprise architecture?",
        "user_context": {"user_id": "enterprise789", "account_type": "enterprise"},
        "expected_tier": "tier3"
    },
    {
        "query": "How do I export my data to CSV format?",
        "user_context": {"user_id": "user101", "account_type": "pro"},
        "expected_tier": "tier1"
    },
    {
        "query": "I'm trying to connect Microsoft Teams but keep getting authentication errors. Error code: AUTH_502",
        "user_context": {"user_id": "user202", "account_type": "business"},
        "expected_tier": "tier2"
    }
]
