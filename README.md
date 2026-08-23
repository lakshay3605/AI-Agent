# ParcelPilot AI — Enterprise Logistics Support Platform

ParcelPilot AI is a production-ready AI support agent and RAG platform built for enterprise logistics, shipping policy navigation, parcel status resolution, and automated customer support workflows. Powered by Next.js, FastAPI, LangGraph, ChromaDB vector stores, and Google Gemini 2.5 Flash, ParcelPilot AI combines semantic search over enterprise contracts and SOPs with real-time operational database tools and strict human-in-the-loop action authorization.

---

## Architecture

```text
User / Browser (Next.js 14 + Tailwind CSS)
       │
       ▼ REST API / NEXT_PUBLIC_API_BASE_URL
FastAPI Backend (Python 3.11+)
       │
       ▼
LangGraph Agent Orchestrator
       │
       ├────► Google Gemini 2.5 Flash LLM (gemini-2.5-flash)
       │         └─ Tool Selection & Reasoning Loop
       │
       ├────► Real Operational Tools (app/agent/tools.py)
       │         ├─ search_documents  ──► ChromaDB Vector Store & PyMuPDF RAG
       │         ├─ get_order         ──► Pandas / Excel Operational Records
       │         ├─ get_customer      ──► Customer Account Records
       │         ├─ get_ticket        ──► Support Ticket Records
       │         ├─ calculate_service_credit  ──► SLA & Fault-Attribution Engine
       │         └─ create_escalation ──► Human-in-the-Loop Pending Actions
       │
       └────► Security & Scope Validator (account_scope enforcement)
```

---

## Key Features

- **AI Support Assistant**: Conversational agent answering operational questions grounded strictly in authentic source data.
- **RAG over Policies, SOPs & Agreements**: High-precision semantic search over PDFs with metadata-aware page citations.
- **Structured Operational Data Lookup**: Direct querying of live Excel orders, tickets, and customer account records.
- **Multi-Step Tool Calling**: Autonomous tool selection powered by Google Gemini 2.5 Flash and LangGraph state graphs.
- **Customer-Scoped Access Security**: Enforces account scope limits (`Northstar Logistics`, `LumenWorks`, etc.) preventing cross-customer data exposure.
- **Human-in-the-Loop Action Approval**: State-changing actions (`create_escalation`) return pending action state requiring explicit human REST confirmation (`/confirm` or `/reject`).
- **Source Precedence & Grounding**: Customer enterprise agreements take explicit precedence over general SOPs and deprecated policies.

---

## Local Development Guide

### 1. Install Dependencies

#### Backend Setup
```bash
cd backend
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

#### Frontend Setup
```bash
cd frontend
npm install
```

### 2. Environment Variables

Copy `.env.example` to `backend/.env` and set your Google Gemini API key:

```env
PROJECT_NAME="ParcelPilot AI Agent API"
ENVIRONMENT="development"
DEBUG=True
HOST="0.0.0.0"
PORT=8000
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"

LLM_PROVIDER="gemini"
GEMINI_MODEL="gemini-2.5-flash"
GEMINI_API_KEY="AIzaSyYourActualKeyHere"
```

### 3. Ingest Assessment Data into RAG Vector Store

Ensure source files (`*.pdf` and `ParcelPilot_Assessment_Data.xlsx`) are in the `data/` folder, then run:

```bash
cd backend
python -m app.rag.ingestion
```

### 4. Start the Backend API Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 5. Start the Next.js Frontend App

```bash
cd frontend
npm run dev
```
Open browser at: [http://localhost:3000](http://localhost:3000)

### 6. Run Automated Test Suite

```bash
# Run backend pytest suite
pytest tests/backend/

# Run frontend production build check
cd frontend
npm run build
```

---

## Production Deployment Guide

### Recommended Architecture

```text
Browser (Frontend Container: Port 3000)
    │
    ▼ REST API
FastAPI Backend Container (Port 8000)
    │
    ├─► Google Gemini API (External HTTPS)
    └─► Persistent Storage Volume (/app/data & /app/storage)
```

### 1. Required Files & Storage Volumes
- `data/`: Contains source PDF contracts/SOPs and `ParcelPilot_Assessment_Data.xlsx`.
- `storage/chroma/`: Contains pre-ingested vector database embeddings. Mount as a persistent volume in production.

### 2. Required Production Environment Variables

#### Backend Environment Variables (`backend/.env` or Container Environment)
- `ENVIRONMENT`: `"production"`
- `DEBUG`: `False`
- `HOST`: `"0.0.0.0"`
- `PORT`: `8000`
- `CORS_ORIGINS`: `["https://your-production-frontend-domain.com"]` (JSON list or comma-separated string)
- `LLM_PROVIDER`: `"gemini"`
- `GEMINI_MODEL`: `"gemini-2.5-flash"`
- `GEMINI_API_KEY`: `"AIzaSyYourProductionGeminiKey"` (Keep strictly backend-only)

#### Frontend Environment Variables (`frontend/.env.production` or Container Build Argument)
- `NEXT_PUBLIC_API_BASE_URL`: `"https://your-production-backend-domain.com"`

### 3. Containerized Deployment (Docker Compose)

Start backend and frontend services using Docker Compose:

```bash
# Build and launch production containers
docker-compose up -d --build
```

### 4. Direct Process Startup Commands

#### Backend Production Command
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend Production Command
```bash
cd frontend
npm run build
npm start
```

### 5. Production Health Check Endpoint
- `GET http://your-backend-domain/health`
- Response: `{"status": "ok", "project": "ParcelPilot AI Agent API", "version": "0.1.0", "environment": "production"}`
- *Note: The health check does not make outbound Gemini API calls, ensuring zero billing usage for basic liveness monitoring.*

---

## Security Guidelines

1. **Secret Isolation**: `GEMINI_API_KEY` is loaded strictly on the backend. It is never exposed in frontend code, `NEXT_PUBLIC_*` environment variables, Docker image layers, or git source control.
2. **CORS Enforcement**: Production CORS restricts cross-origin HTTP requests exclusively to configured frontend domains (`CORS_ORIGINS`).
3. **Data Scope Limits**: Customer context validation enforces strict tenant isolation preventing cross-account data leakage.
