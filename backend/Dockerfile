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

# Production paths & PyTorch memory/thread optimizations
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DATA_DIR=/app/data
ENV CHROMA_PERSIST_DIR=/app/storage/chroma
ENV HF_HOME=/app/.cache/huggingface
ENV TORCH_NUM_THREADS=1
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

# Build and verify the RAG vector index during image build
RUN python -m app.rag.ingestion && \
    python -c "import chromadb; from app.core.config import settings; client=chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR); collection=client.get_collection(settings.CHROMA_COLLECTION_NAME); print('RAG chunks:', collection.count()); assert collection.count() > 0, 'RAG collection is empty'"

# Enforce offline HF mode at runtime after model is baked into image
ENV HF_HUB_OFFLINE=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]