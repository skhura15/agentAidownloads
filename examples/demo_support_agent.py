"""
Demo script for Self-Service Support Agent using Ollama

This script demonstrates the cost-optimized support agent with:
- Tiered model selection (phi3-mini -> mistral -> llama3)
- Knowledge base RAG integration
- Sentiment analysis
- Context preservation
- Simulated support queries

Requirements:
- Ollama installed and running (ollama.ai)
- Models pulled: ollama pull phi3:mini && ollama pull mistral && ollama pull llama3
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.self_service_support_agent import SelfServiceSupportAgent, SAMPLE_SUPPORT_QUERIES
import json
from datetime import datetime


def print_header(text: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_response(response, query_num: int, total: int):
    """Print formatted agent response"""
    print(f"\n{'─' * 80}")
    print(f"Query {query_num}/{total}")
    print(f"{'─' * 80}")
    print(f"\n📋 Response:\n{response.content}\n")
    
    if response.metadata:
        print("📊 Metadata:")
        print(f"  • Model Tier: {response.metadata.get('model_tier', 'N/A')}")
        print(f"  • Model Used: {response.metadata.get('model_used', 'N/A')}")
        print(f"  • Sentiment: {response.metadata.get('sentiment', {}).get('sentiment', 'N/A')} "
              f"(score: {response.metadata.get('sentiment', {}).get('score', 0):.2f})")
        print(f"  • KB Articles Found: {response.metadata.get('kb_articles_found', 0)}")
        print(f"  • Resolution Time: {response.metadata.get('resolution_time_seconds', 0):.2f}s")
        print(f"  • Cost Saved: ${response.metadata.get('cost_saved_usd', 0):.2f}")
        
        if response.metadata.get('needs_escalation'):
            print("  • ⚠️  ESCALATED TO HUMAN SUPPORT")
    
    if response.tools_used:
        print(f"\n🔧 Tools Used: {', '.join(response.tools_used)}")
    
    if response.handoff_to:
        print(f"\n👤 Handoff To: {response.handoff_to}")
    
    print(f"\n{'─' * 80}\n")


async def run_demo():
    """Run interactive demo of support agent"""
    
    print_header("🤖 HCLTech Self-Service Support Agent Demo")
    print("Cost-optimized AI support using local Ollama models\n")
    print("Features:")
    print("  ✓ Tiered model selection (phi3-mini → mistral → llama3)")
    print("  ✓ Knowledge base RAG integration")
    print("  ✓ Sentiment analysis")
    print("  ✓ Context preservation")
    print("  ✓ Human escalation when needed")
    print("\n" + "─" * 80)
    
    # Check Ollama connection
    print("\n🔍 Checking Ollama connection...")
    agent = SelfServiceSupportAgent()
    
    try:
        import requests
        response = requests.get(f"{agent.ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama connected successfully!")
            print(f"   Available models: {len(models)}")
        else:
            print("❌ Ollama is not responding correctly")
            print("   Please ensure Ollama is running: ollama serve")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {str(e)}")
        print("\nPlease:")
        print("  1. Install Ollama from https://ollama.ai")
        print("  2. Start Ollama: ollama serve")
        print("  3. Pull required models:")
        print("     ollama pull phi3:mini")
        print("     ollama pull mistral")
        print("     ollama pull llama3")
        return
    
    # Run simulated queries
    print_header("📝 Running Simulated Support Queries")
    
    total_queries = len(SAMPLE_SUPPORT_QUERIES)
    
    for idx, sample in enumerate(SAMPLE_SUPPORT_QUERIES, 1):
        print(f"\n🎯 Query {idx}/{total_queries}")
        print(f"User: {sample['query']}")
        print(f"Expected Tier: {sample['expected_tier']}")
        print(f"Context: {json.dumps(sample['user_context'])}")
        
        # Execute query
        task = {
            "query": sample["query"],
            "user_context": sample["user_context"],
            "escalation_allowed": True
        }
        
        print("\n⏳ Processing with AI agent...")
        response = await agent.execute(task)
        
        print_response(response, idx, total_queries)
        
        # Small delay between queries
        if idx < total_queries:
            await asyncio.sleep(1)
    
    # Show final metrics
    print_header("📊 Agent Performance Metrics")
    metrics = agent.get_metrics()
    
    print("Performance Summary:")
    for key, value in metrics.items():
        key_formatted = key.replace("_", " ").title()
        print(f"  • {key_formatted}: {value}")
    
    print("\n💡 Cost Optimization Impact:")
    print(f"  • Using tier1 model (phi3-mini) for {metrics['avg_tier1_percentage']} of queries")
    print(f"  • Total cost savings: {metrics['cost_savings_usd']}")
    print(f"  • Escalation rate: {metrics['escalation_rate']}")
    
    # Interactive mode
    print_header("💬 Interactive Mode")
    print("Try your own support queries! (Type 'exit' to quit)\n")
    
    while True:
        try:
            user_query = input("Your question: ").strip()
            
            if user_query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Thank you for using HCLTech Self-Service Support Agent!")
                break
            
            if not user_query:
                continue
            
            task = {
                "query": user_query,
                "user_context": {"user_id": "demo_user", "account_type": "demo"},
                "escalation_allowed": True
            }
            
            print("\n⏳ Processing...")
            response = await agent.execute(task)
            
            print(f"\n🤖 Agent Response:\n{response.content}\n")
            
            if response.metadata:
                print(f"📊 Tier: {response.metadata.get('model_tier')} | "
                      f"Sentiment: {response.metadata.get('sentiment', {}).get('sentiment')} | "
                      f"Time: {response.metadata.get('resolution_time_seconds', 0):.2f}s")
            
            if response.handoff_to:
                print(f"\n👤 Escalated to: {response.handoff_to}")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
