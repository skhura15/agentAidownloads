"""
FastAPI endpoint for Self-Service Support Agent

This API exposes the support agent functionality to the frontend UI.
Run with: uvicorn api.support_api:app --reload --port 8000
"""

# Load .env file FIRST before any other imports
from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import simulation routes
from api.routes.simulation import router as simulation_router, set_orchestrator
from agents.skilling import SimulationOrchestrator
from core.config_manager import ConfigManager

# Import standalone agent (doesn't require full framework dependencies)
import asyncio
import json
from datetime import datetime
import requests
from enum import Enum


# Recreate minimal classes needed
class AgentStatus(Enum):
    IDLE = "idle"
    COMPLETED = "completed"
    ERROR = "error"


class StandaloneSupportAgent:
    """Simplified Support Agent for API use"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.knowledge_base = [
            {
                "id": "kb001",
                "category": "account",
                "question": "How do I reset my password?",
                "answer": "To reset your password: 1) Click 'Forgot Password' on login page, 2) Enter your email, 3) Check inbox for reset link, 4) Create new password (min 8 chars with uppercase, number, special character)."
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
                "answer": "Dashboard performance: 1) Clear browser cache and cookies, 2) Try incognito mode, 3) Check network connection, 4) Disable browser extensions. If persists, contact support with browser version."
            },
            {
                "id": "kb004",
                "category": "features",
                "question": "How do I export my data?",
                "answer": "Data export: 1) Settings > Data Management, 2) Click 'Export Data', 3) Select format (CSV/JSON/Excel), 4) Choose date range, 5) Click 'Generate Export'. Download link via email in 15 mins."
            },
            {
                "id": "kb005",
                "category": "integration",
                "question": "How do I connect to Microsoft Teams?",
                "answer": "Teams integration: 1) Settings > Integrations > Teams, 2) Click 'Connect', 3) Sign in with Microsoft account, 4) Grant permissions, 5) Select channels. Takes 5-10 mins to activate."
            }
        ]
    
    def _search_kb(self, query: str):
        query_lower = query.lower()
        results = []
        for article in self.knowledge_base:
            if (query_lower in article["question"].lower() or 
                query_lower in article["answer"].lower() or
                query_lower in article["category"].lower()):
                results.append(article)
        return results[:3]
    
    def _call_ollama(self, prompt: str, system: str) -> str:
        try:
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": "llama3:latest",
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {"temperature": 0.7, "top_p": 0.9}
            }
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _analyze_sentiment(self, text: str) -> Dict:
        negative = ["angry", "frustrated", "terrible", "horrible", "upset"]
        positive = ["great", "excellent", "thank", "appreciate", "happy"]
        text_lower = text.lower()
        neg = sum(1 for w in negative if w in text_lower)
        pos = sum(1 for w in positive if w in text_lower)
        
        if neg > pos:
            return {"sentiment": "negative", "score": 0.3}
        elif pos > neg:
            return {"sentiment": "positive", "score": 0.8}
        return {"sentiment": "neutral", "score": 0.5}
    
    async def execute(self, query: str) -> Dict[str, Any]:
        try:
            start_time = datetime.now()
            
            # Search KB
            kb_results = self._search_kb(query)
            kb_context = "\n\n".join([
                f"KB Article {r['id']}: {r['question']}\n{r['answer']}"
                for r in kb_results
            ]) if kb_results else "No relevant articles found."
            
            # Sentiment
            sentiment = self._analyze_sentiment(query)
            
            # Build prompt
            system_prompt = """You are a helpful customer support agent. Provide clear, concise answers.
If you don't know, admit it and suggest escalation. Be empathetic and professional. Keep responses under 200 words."""
            
            user_prompt = f"""Customer Query: {query}

Relevant Knowledge Base:
{kb_context}

Provide a helpful response."""
            
            # Call Ollama
            response_text = self._call_ollama(user_prompt, system_prompt)
            
            # Check escalation
            needs_escalation = any(word in response_text.lower() 
                                  for word in ["escalate", "human", "don't know", "uncertain"])
            
            if needs_escalation:
                response_text += "\n\n⚠️ This has been escalated to human support."
            
            resolution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "response": response_text,
                "sentiment": sentiment,
                "kb_articles_found": len(kb_results),
                "needs_escalation": needs_escalation,
                "resolution_time_seconds": resolution_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}. Please try again or contact human support.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# FastAPI app
app = FastAPI(
    title="HCLTech Self-Service Support API",
    description="AI-powered support agent using Ollama",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator for simulation routes
app.include_router(simulation_router)

# Try to initialize orchestrator
try:
    # First try with config manager
    try:
        config_manager = ConfigManager()
        orchestrator = SimulationOrchestrator(config_manager=config_manager)
    except Exception as e:
        # If ConfigManager fails, create minimal orchestrator for file-based cases only
        print(f"  ConfigManager initialization failed: {e}")
        print("  Creating minimal orchestrator for file-based cases...")
        from pathlib import Path
        cases_dir = Path(__file__).parent.parent / "data" / "cases"
        # Pass None for config_manager - orchestrator should handle this gracefully
        orchestrator = SimulationOrchestrator(config_manager=None)
    
    set_orchestrator(orchestrator)
    print("✓ SimulationOrchestrator initialized")
except Exception as e:
    print(f"⚠ Warning: Failed to initialize SimulationOrchestrator: {e}")
    print("  Simulation endpoints may not work properly")

# Initialize agent
support_agent = StandaloneSupportAgent()


# Request/Response models
class SupportQuery(BaseModel):
    query: str
    user_id: Optional[str] = "anonymous"
    user_context: Optional[Dict[str, Any]] = None


class SupportResponse(BaseModel):
    response: str
    sentiment: Optional[Dict[str, Any]] = None
    kb_articles_found: Optional[int] = 0
    needs_escalation: Optional[bool] = False
    resolution_time_seconds: Optional[float] = 0.0
    timestamp: str


# Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "HCLTech Self-Service Support API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Check if Ollama is available"""
    try:
        response = requests.get(f"{support_agent.ollama_url}/api/tags", timeout=5)
        ollama_status = "online" if response.status_code == 200 else "offline"
    except:
        ollama_status = "offline"
    
    return {
        "api_status": "online",
        "ollama_status": ollama_status,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/support/query", response_model=SupportResponse)
async def handle_support_query(query: SupportQuery):
    """
    Process a support query using the AI agent
    
    Example:
    ```
    POST /api/support/query
    {
        "query": "How do I reset my password?",
        "user_id": "user123"
    }
    ```
    """
    try:
        result = await support_agent.execute(query.query)
        return SupportResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/support/knowledge-base")
async def get_knowledge_base():
    """Get all knowledge base articles"""
    return {
        "articles": support_agent.knowledge_base,
        "total": len(support_agent.knowledge_base)
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting HCLTech Support API on http://localhost:8000")
    print("📚 API docs available at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
