# Backend Dockerfile for FastAPI & LangGraph Agent
FROM python:3.11-slim

WORKDIR /app

# Install build essentials for PyMuPDF / ChromaDB if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code, assessment data, and persistent storage
COPY backend/app ./app
COPY data ./data
COPY storage ./storage

EXPOSE 8000

ENV HOST=0.0.0.0
ENV PORT=8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
