# Backend Dockerfile for FastAPI & LangGraph Agent
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and assessment data
COPY backend/app ./app
COPY data ./data

# Production paths
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DATA_DIR=/app/data
ENV CHROMA_PERSIST_DIR=/app/storage/chroma

# Build the RAG vector index during the image build
RUN python -m app.rag.ingestion

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]