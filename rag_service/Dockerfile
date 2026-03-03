# RAG Service Dockerfile
# Standalone microservice for RAG operations

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY core/ ./core/
COPY rag_service/ ./rag_service/
COPY configs/ ./configs/

# Create data directories
RUN mkdir -p /app/data/chroma /app/data/chroma_azure /app/logs

# Environment variables with defaults
ENV RAG_SERVICE_HOST=0.0.0.0
ENV RAG_SERVICE_PORT=8001
ENV VECTOR_PROVIDER=chroma
ENV VECTOR_COLLECTION=uta_knowledge
ENV VECTOR_PERSIST_DIR=/app/data/chroma
ENV RAG_TOP_K=5
ENV RAG_MIN_SCORE=0.05
ENV RAG_QUERY_EXPANSION=true
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${RAG_SERVICE_PORT}/health || exit 1

# Expose port
EXPOSE 8001

# Run the service
CMD ["python", "-m", "rag_service.app"]
