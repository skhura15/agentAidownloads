"""
Standalone Self-Service Support Agent Demo using Ollama

This is a simplified standalone version that doesn't require the full framework.
Perfect for quick testing and demonstrations.

Requirements:
- Python 3.8+
- requests library: pip install requests
- Ollama running locally with llama3 model
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from enum import Enum


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class AgentResponse:
    """Standardized agent response"""
    def __init__(self, content: str, agent_id: str, agent_name: str, 
                 status: AgentStatus = AgentStatus.COMPLETED,
                 metadata: Optional[Dict] = None, tools_used: Optional[List[str]] = None,
                 handoff_to: Optional[str] = None, error: Optional[str] = None):
        self.content = content
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.status = status
        self.metadata = metadata or {}
        self.tools_used = tools_used or []
        self.handoff_to = handoff_to
        self.error = error


class StandaloneSupportAgent:
    """Simplified Self-Service Support Agent using Ollama"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.agent_id = "self-service-support"
        self.agent_name = "Self-Service Support Agent"
        self.ollama_url = ollama_url
        
        # Model tier configuration
        self.models = {
            "tier1": "llama3:latest",  # Using llama3 for all tiers in demo
            "tier2": "llama3:latest",
            "tier3": "llama3:latest"
        }
        
        # Knowledge base
        self.knowledge_base = [
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
                "category": "integration",
                "question": "How do I connect to Microsoft Teams?",
                "answer": "Teams integration: 1) Settings > Integrations > Microsoft Teams, 2) Click 'Connect', 3) Sign in with Microsoft account, 4) Grant permissions, 5) Select channels to sync. Integration may take 5-10 minutes to activate."
            },
        ]
        
        # Metrics
        self.metrics = {
            "total_queries": 0,
            "tier1_resolved": 0,
            "tier2_resolved": 0,
            "escalated": 0,
            "cost_savings": 0.0
        }
    
    def _search_knowledge_base(self, query: str) -> List[Dict]:
        """Search knowledge base for relevant articles"""
        query_lower = query.lower()
        results = []
        
        for article in self.knowledge_base:
            if (query_lower in article["question"].lower() or 
                query_lower in article["answer"].lower() or
                query_lower in article["category"].lower()):
                results.append(article)
        
        return results[:3]
    
    def _call_ollama(self, model: str, prompt: str, system: Optional[str] = None) -> str:
        """Call Ollama API"""
        try:
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "top_p": 0.9}
            }
            
            if system:
                payload["system"] = system
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response", "")
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _classify_complexity(self, query: str) -> str:
        """Classify query complexity"""
        query_lower = query.lower()
        
        simple_keywords = ["password", "reset", "login", "forgot", "how do i"]
        technical_keywords = ["error", "bug", "crash", "slow", "performance", "api"]
        complex_keywords = ["enterprise", "custom", "architecture", "sso", "migration"]
        
        if any(k in query_lower for k in complex_keywords):
            return "tier3"
        elif any(k in query_lower for k in technical_keywords):
            return "tier2"
        return "tier1"
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Simple sentiment analysis"""
        negative = ["angry", "frustrated", "terrible", "horrible", "upset"]
        positive = ["great", "excellent", "thank", "appreciate", "happy"]
        
        text_lower = text.lower()
        neg_count = sum(1 for w in negative if w in text_lower)
        pos_count = sum(1 for w in positive if w in text_lower)
        
        if neg_count > pos_count:
            return {"sentiment": "negative", "score": 0.3}
        elif pos_count > neg_count:
            return {"sentiment": "positive", "score": 0.8}
        return {"sentiment": "neutral", "score": 0.5}
    
    async def execute(self, query: str, user_context: Dict = None) -> AgentResponse:
        """Execute support query"""
        try:
            start_time = datetime.now()
            self.metrics["total_queries"] += 1
            
            # Sentiment analysis
            sentiment = self._analyze_sentiment(query)
            
            # Search knowledge base
            kb_results = self._search_knowledge_base(query)
            kb_context = "\n\n".join([
                f"KB Article {r['id']}: {r['question']}\n{r['answer']}"
                for r in kb_results
            ]) if kb_results else "No relevant articles found."
            
            # Classify complexity
            tier = self._classify_complexity(query)
            model = self.models[tier]
            
            # Build prompt
            system_prompt = """You are a helpful customer support agent. Provide clear, concise answers.
If you don't know, admit it and suggest escalation. Be empathetic and professional."""
            
            user_prompt = f"""Customer Query: {query}

Relevant Knowledge Base:
{kb_context}

Please provide a helpful response. Keep it under 200 words unless detailed steps are needed."""
            
            # Call Ollama
            print(f"   🤖 Using {tier} model: {model}")
            response_text = self._call_ollama(model, user_prompt, system_prompt)
            
            # Check escalation
            needs_escalation = any(word in response_text.lower() 
                                  for word in ["escalate", "human", "don't know", "uncertain"])
            
            # Update metrics
            if tier == "tier1":
                self.metrics["tier1_resolved"] += 1
                cost_saved = 0.10
            elif tier == "tier2":
                self.metrics["tier2_resolved"] += 1
                cost_saved = 0.05
            else:
                cost_saved = 0.0
            
            if needs_escalation:
                self.metrics["escalated"] += 1
                response_text += "\n\n⚠️ This query has been escalated to human support."
            
            self.metrics["cost_savings"] += cost_saved
            
            resolution_time = (datetime.now() - start_time).total_seconds()
            
            metadata = {
                "model_tier": tier,
                "model_used": model,
                "sentiment": sentiment,
                "kb_articles_found": len(kb_results),
                "needs_escalation": needs_escalation,
                "resolution_time_seconds": resolution_time,
                "cost_saved_usd": cost_saved
            }
            
            return AgentResponse(
                content=response_text,
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                status=AgentStatus.COMPLETED,
                metadata=metadata,
                tools_used=["knowledge_base", "sentiment_analysis", f"ollama_{model}"],
                handoff_to="human_support" if needs_escalation else None
            )
            
        except Exception as e:
            return AgentResponse(
                content=f"Error processing request: {str(e)}",
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                status=AgentStatus.ERROR,
                error=str(e)
            )
    
    def get_metrics(self) -> Dict:
        """Get performance metrics"""
        total = self.metrics["tier1_resolved"] + self.metrics["tier2_resolved"]
        return {
            "total_queries": self.metrics["total_queries"],
            "total_resolved": total,
            "escalated": self.metrics["escalated"],
            "escalation_rate": f"{(self.metrics['escalated'] / max(self.metrics['total_queries'], 1)) * 100:.1f}%",
            "cost_savings_usd": f"${self.metrics['cost_savings']:.2f}"
        }


# Sample queries
SAMPLE_QUERIES = [
    "I forgot my password and can't log in. How do I reset it?",
    "My dashboard is loading extremely slow and I'm getting errors!",
    "How do I export my data to CSV format?",
    "I'm trying to connect Microsoft Teams but getting authentication errors",
]


async def run_demo():
    """Run the demo"""
    print("\n" + "=" * 80)
    print("  🤖 HCLTech Self-Service Support Agent Demo (Standalone)")
    print("=" * 80 + "\n")
    
    # Check Ollama
    print("🔍 Checking Ollama connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama connected! Available models: {len(models)}")
            if models:
                print(f"   Models: {', '.join([m['name'] for m in models[:3]])}")
        else:
            print("❌ Ollama not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("\nPlease start Ollama: ollama serve")
        return
    
    agent = StandaloneSupportAgent()
    
    print("\n" + "=" * 80)
    print("  📝 Running Sample Support Queries")
    print("=" * 80)
    
    for idx, query in enumerate(SAMPLE_QUERIES, 1):
        print(f"\n\n{'─' * 80}")
        print(f"Query {idx}/{len(SAMPLE_QUERIES)}")
        print(f"{'─' * 80}")
        print(f"\n❓ User: {query}")
        print(f"\n⏳ Processing...")
        
        response = await agent.execute(query)
        
        print(f"\n📋 Response:\n{response.content}\n")
        
        if response.metadata:
            print(f"📊 Metadata:")
            print(f"   • Tier: {response.metadata.get('model_tier')}")
            print(f"   • Sentiment: {response.metadata.get('sentiment', {}).get('sentiment')}")
            print(f"   • KB Articles: {response.metadata.get('kb_articles_found')}")
            print(f"   • Time: {response.metadata.get('resolution_time_seconds', 0):.2f}s")
            print(f"   • Cost Saved: ${response.metadata.get('cost_saved_usd', 0):.2f}")
        
        if response.handoff_to:
            print(f"\n👤 Escalated to: {response.handoff_to}")
    
    # Show metrics
    print("\n\n" + "=" * 80)
    print("  📊 Final Metrics")
    print("=" * 80 + "\n")
    
    metrics = agent.get_metrics()
    for key, value in metrics.items():
        print(f"   • {key.replace('_', ' ').title()}: {value}")
    
    print("\n✅ Demo completed successfully!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
