"""
Test script to reproduce "System crashed" error
"""
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import server functions
KG_PATH = os.path.join(os.path.dirname(__file__), "knowledge_graph.json")

try:
    print("Loading knowledge_graph.json...")
    with open(KG_PATH, "r", encoding="utf-8") as f:
        KG = json.load(f)
    
    NODES = {n["id"]: n for n in KG["nodes"]}
    EDGES = KG["edges"]
    
    print(f"✓ Loaded {len(NODES)} nodes, {len(EDGES)} edges")
    
    # Test extract_keywords
    def extract_keywords(ticket_text):
        keyword_map = {
            "voice": ["voice", "call", "phone", "inbound", "outbound", "ivr", "dial"],
            "routing": ["routing", "route", "queue", "assignment", "workstream", "skill"],
            "chat": ["chat", "messaging", "whatsapp", "sms", "widget", "digital"],
            "copilot": ["copilot", "ai", "suggestion", "summarization", "draft"],
            "transfer": ["transfer", "warm transfer", "cold transfer", "consult"],
            "agent": ["agent", "desktop", "workspace", "presence", "login", "session"],
            "analytics": ["analytics", "dashboard", "report", "metrics", "supervisor"],
            "bot": ["bot", "virtual agent", "self-service", "copilot studio", "pva"],
            "safari": ["safari", "browser", "widget", "cookie", "itp"],
            "latency": ["slow", "delay", "latency", "timeout", "spinning"],
            "outage": ["outage", "down", "unavailable", "error", "failure", "drop"],
            "recording": ["recording", "transcription", "transcript"],
            "knowledge": ["knowledge", "article", "kb", "documentation"],
            "configuration": ["config", "configuration", "setting", "setup", "admin"],
            "escalation": ["escalation", "escalate", "p1", "critical", "urgent", "sev1"],
            "customer": ["contoso", "fabrikam", "northwind"],
            "system": ["system", "crashed", "crash", "hang", "freeze"],
        }

        text_lower = ticket_text.lower()
        found_keywords = set()

        for category, terms in keyword_map.items():
            for term in terms:
                if term in text_lower:
                    found_keywords.add(category)
                    found_keywords.add(term)

        # Extract individual words
        words = text_lower.split()
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at",
                      "to", "for", "of", "with", "and", "or", "not", "from", "by"}

        for word in words:
            cleaned = word.strip(".,!?;:\"'()[]{}").lower()
            if len(cleaned) > 2 and cleaned not in stop_words:
                found_keywords.add(cleaned)

        return list(found_keywords)
    
    # Test search_nodes_by_keywords
    def search_nodes_by_keywords(keywords):
        keywords_lower = [k.lower() for k in keywords]
        scored = []
        for nid, node in NODES.items():
            score = 0
            label_lower = node["label"].lower()
            tags_lower = [t.lower() for t in node.get("tags", [])]
            props_str = json.dumps(node.get("properties", {})).lower()

            for kw in keywords_lower:
                if kw in label_lower:
                    score += 10
                for tag in tags_lower:
                    if kw in tag:
                        score += 5
                if kw in props_str:
                    score += 2
            if score > 0:
                scored.append((score, node))

        scored.sort(key=lambda x: -x[0])
        return [item[1] for item in scored[:10]]
    
    print("\n" + "="*60)
    print("Testing with input: 'System crashed'")
    print("="*60)
    
    test_input = "System crashed"
    keywords = extract_keywords(test_input)
    print(f"\nExtracted keywords: {keywords}")
    
    matched_nodes = search_nodes_by_keywords(keywords)
    print(f"\nMatched {len(matched_nodes)} nodes:")
    for node in matched_nodes:
        print(f"  - [{node['type']}] {node['label']}")
    
    print("\n✓ Test completed successfully - no errors!")

except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
