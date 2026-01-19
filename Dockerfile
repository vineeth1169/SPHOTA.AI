# Multi-stage build for Sphota Engine FastAPI microservice
# Stage 1: Builder - Download and cache AI models
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies for building and model downloads
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements early for layer caching
COPY requirements.txt .

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies (skip chromadb temporarily to avoid build issues)
RUN pip install --upgrade pip setuptools wheel && \
    grep -v "chromadb" requirements.txt > requirements_docker.txt && \
    pip install --no-cache-dir -r requirements_docker.txt

# Pre-download the Sentence-Transformers model to avoid runtime download
# This prevents the first run from waiting for a 300MB+ download
RUN python -c "from sentence_transformers import SentenceTransformer; \
    print('Downloading all-MiniLM-L6-v2 model...'); \
    model = SentenceTransformer('all-MiniLM-L6-v2'); \
    print(f'Model cached at: {model.modules[0].auto_model.config.model_type}')"

# Stage 2: Runtime - Slim production image
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose API port
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
