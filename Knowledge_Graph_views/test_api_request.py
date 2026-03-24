import requests
import json

# Test the /api/chat-stream endpoint with "System crashed"
url = "http://localhost:8080/api/chat-stream"
payload = {
    "message": "System crashed",
    "use_llm": False  # Use fallback mode to avoid Ollama dependency
}

try:
    print("Sending POST request to /api/chat-stream...")
    print(f"Payload: {payload}")
    
    response = requests.post(url, json=payload, stream=True, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print("\n" + "="*60)
    print("Response (SSE stream):")
    print("="*60)
    
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            print(decoded)
            if decoded.startswith('data: '):
                try:
                    evt = json.loads(decoded[6:])
                    print(f"  Parsed: {evt.get('type', 'unknown')}")
                except:
                    pass
    
    print("\n✓ Request completed successfully!")
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
