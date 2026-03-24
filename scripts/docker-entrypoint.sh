#!/bin/bash
set -e

echo "Starting Agentic CoE API..."

# Check if knowledge base needs ingestion
if [ ! -f "/app/data/chroma_azure/.ingested" ]; then
    echo "Ingesting knowledge base..."
    python -m examples.uta_ingest_knowledge --clear --persist-dir "./data/chroma_azure" || echo "Ingestion failed, continuing anyway..."
    touch /app/data/chroma_azure/.ingested
    echo "Knowledge base ingestion complete"
else
    echo "Knowledge base already ingested"
fi

# Start the API server
exec uvicorn api.main:app --host 0.0.0.0 --port 8000
