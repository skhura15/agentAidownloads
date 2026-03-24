# Backend Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Explicitly copy pre-ingested vector data (in case .dockerignore has issues)
COPY data/chroma_azure/ ./data/chroma_azure/

# Create logs directory
RUN mkdir -p logs

# Note: Knowledge ingestion happens at runtime since it requires Azure credentials
# The data/uta_knowledge folder is included for runtime ingestion

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
