import sys
import os
import traceback
from pathlib import Path

print("[TEST] test_kg_agent.py loaded", flush=True)

# Ensure project root is importable
ROOT = Path(__file__).resolve().parents[1]  # scripts/.. = kg/
sys.path.insert(0, str(ROOT))
print(f"[TEST] ROOT={ROOT}", flush=True)
print(f"[TEST] sys.path[0]={sys.path[0]}", flush=True)

# Load env from repo root (optional but recommended)
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    print("[TEST] .env loaded (if present)", flush=True)
except Exception as e:
    print(f"[TEST] dotenv not available or failed to load .env: {e}", flush=True)

# Print provider env sanity
print("[TEST] AZURE_OPENAI_ENDPOINT:", os.getenv("AZURE_OPENAI_ENDPOINT"), flush=True)
print("[TEST] AZURE_OPENAI_API_KEY set:", bool(os.getenv("AZURE_OPENAI_API_KEY")), flush=True)
print("[TEST] AZURE_OPENAI_API_VERSION:", os.getenv("AZURE_OPENAI_API_VERSION"), flush=True)
print("[TEST] KG_AGENT_MODEL:", os.getenv("KG_AGENT_MODEL"), flush=True)
print("[TEST] OPENAI_API_KEY set:", bool(os.getenv("OPENAI_API_KEY")), flush=True)

import asyncio

try:
    from agents.knowledge_graph.knowledge_graph_agent import KnowledgeGraphAgent
    print("[TEST] Imported KnowledgeGraphAgent OK", flush=True)
except Exception:
    print("[TEST] Failed importing KnowledgeGraphAgent:", flush=True)
    traceback.print_exc()
    raise


class DummyConfig:
    def get(self, *args, **kwargs):
        return None


class DummyState:
    async def update_agent_state(self, agent_id, state):
        return None

    async def clear_agent_state(self, agent_id):
        return None


async def main():
    print("[TEST] Entered main()", flush=True)

    agent = KnowledgeGraphAgent(
        config_manager=DummyConfig(),
        state_manager=DummyState(),
        tenant_id="tenant_demo",
        default_service_id="svc_payment",
    )
    print("[TEST] Agent object created", flush=True)

    # Initialize with timeout so it can't hang forever
    print("[TEST] Initializing agent...", flush=True)
    await asyncio.wait_for(agent.initialize(), timeout=20)
    print("[TEST] Agent initialized ✅", flush=True)

    msg = "Payment is broken. Seeing 5xx and timeouts."
    print("[TEST]  Calling agent.execute()...", flush=True)

    # process() with timeout
    resp = await asyncio.wait_for(agent.execute(msg, context={}), timeout=30)

    print("[TEST] agent.process() returned ✅", flush=True)
    print("========================================", flush=True)
    print("USER:", msg, flush=True)
    print("AGENT:", resp.content, flush=True)


if __name__ == "__main__":
    try:
        print("[TEST] Starting asyncio.run(main())", flush=True)
        asyncio.run(main())
        print("[TEST] Finished ✅", flush=True)
    except Exception:
        print("[TEST] Unhandled exception:", flush=True)
        traceback.print_exc()
        raise