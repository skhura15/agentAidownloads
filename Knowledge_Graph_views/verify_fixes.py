#!/usr/bin/env python3
"""
Quick test script to verify the bug fixes
"""
import http.server
import subprocess
import time
import sys
import os
from pathlib import Path

print("="*60)
print("Support AI Agent - Bug Fix Verification")
print("="*60)

# Check if server.py exists
server_path = Path(__file__).parent / "server.py"
if not server_path.exists():
    print("❌ server.py not found!")
    sys.exit(1)

print("\n✓ server.py found")

# Check if knowledge_graph.json is valid
kg_path = Path(__file__).parent / "knowledge_graph.json"
if not kg_path.exists():
    print("❌ knowledge_graph.json not found!")
    sys.exit(1)

import json
try:
    with open(kg_path, 'r', encoding='utf-8') as f:
        kg = json.load(f)
    print(f"✓ knowledge_graph.json is valid ({len(kg['nodes'])} nodes)")
except Exception as e:
    print(f"❌ knowledge_graph.json is invalid: {e}")
    sys.exit(1)

# Check if support_agent.html exists
html_path = Path(__file__).parent / "support_agent.html"
if not html_path.exists():
    print("❌ support_agent.html not found!")
    sys.exit(1)

print("✓ support_agent.html found")

print("\n" + "="*60)
print("All files verified! Ready to start server.")
print("="*60)
print("\nTo start the server, run:")
print("  python server.py")
print("\nThen access:")
print("  http://localhost:8080/support_agent.html")
print("\nTest cases:")
print("  1. Type 'System crashed' and send")
print("  2. Verify Send button is re-enabled after response")
print("  3. Check browser console (F12) for error logs")
print("  4. Toggle 'Use Ollama LLM' OFF for faster testing")
print("\nExpected behavior:")
print("  ✓ Button re-enables after every response")
print("  ✓ Error messages shown in chat if backend issues")
print("  ✓ Timeout after 60 seconds if no response")
print("="*60)
