# 🤖  WorkforceIQ — Agentic RAG Platform for Workforce Intelligence

> *"A nurse walks up to the HR desk and asks: What is my annual leave entitlement?"*
> *The HR officer searches through 200 pages of German labour law documents.*
> *Fifteen minutes later, she finds the answer: 30 days, TVöD-K Section 26.*
>
> *With this system, the same answer appears in 30 seconds.*
> *Cited. Verified. Grounded in the actual hospital policy document.*

---

## The Problem This Solves

Helix Workforce Solutions GmbH — a German hospital — employs hundreds of nurses,
doctors, and administrative staff. Every day, HR staff answer the same questions
repeatedly:

- *"How many days of annual leave do I get?"*
- *"What is the night shift supplement rate?"*
- *"Who is working in ICU this Monday?"*
- *"What are our DSGVO patient data rights?"*

The answers exist — buried inside PDF policy documents, labour law texts, and
shift schedule spreadsheets. Finding them takes time, expertise in German law,
and patience. Human error happens. Compliance risks arise.

This project builds an AI assistant that answers these questions instantly,
citing the exact source document and section — running entirely on-premise
to comply with German data protection law (DSGVO).

---

## What Was Built

A **complete, production-grade RAG Agentic AI system** built from scratch —
from raw PDF documents to a monitored, containerised, CI/CD-deployed application.

```
HR staff types a question
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              Streamlit Chat Interface                │
│         "What is the annual leave for nurses?"       │
└───────────────────────┬─────────────────────────────┘
                        │ HTTP POST
                        ▼
┌─────────────────────────────────────────────────────┐
│                 FastAPI Backend                      │
│         /chat  /health  /ingest  /metrics            │
└───────────────────────┬─────────────────────────────┘
                        │
              ┌─────────┴──────────┐
              ▼                    ▼
┌─────────────────────┐  ┌─────────────────────────┐
│   ChromaDB          │  │   SQLite Database        │
│   47 document chunks│  │   Staff · Shifts         │
│   Vector search     │  │   Schedules              │
│   BM25 + Embedding  │  └─────────────────────────┘
└──────────┬──────────┘
           │ top 4 relevant chunks
           ▼
┌─────────────────────────────────────────────────────┐
│              Ollama — llama3.2                       │
│   Reads context → writes answer → cites source       │
└───────────────────────┬─────────────────────────────┘
                        │
           ┌────────────┼────────────┐
           ▼            ▼            ▼
      MLflow         Prometheus    Grafana
   tracks every     scrapes       live
   AI request       /metrics      dashboard
```

**The answer returned:**
> *"According to SECTION 1: ANNUAL LEAVE (JAHRESURLAUB), section 1.2 —
> Nurses (Pflegepersonal) are entitled to 30 days per year.
> Source: HEALTHCARE WORKFORCE HR POLICY, Helix Workforce Solutions GmbH,
> Version 1.0, May 2026."*

Cited. Grounded. Verified against the actual document.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit | Chat UI for HR staff |
| Backend | FastAPI + uvicorn | REST API — /chat /health /ingest /metrics |
| AI Orchestration | LangChain | Connects LLM to tools and documents |
| LLM | Ollama + llama3.2 | Local inference — no cloud, no data leakage |
| Embeddings | nomic-embed-text | Converts text to searchable vectors |
| Vector Database | ChromaDB 0.4.24 | Stores and searches document chunks |
| Staff Database | SQLite | Staff names, shifts, schedules |
| Retrieval | Hybrid BM25 + Embedding | Better chunk finding than embeddings alone |
| Hallucination Guard | Custom word overlap | Blocks ungrounded LLM answers |
| Experiment Tracking | MLflow 2.17.0 | Records every question, timing, answer |
| Metrics | Prometheus | HTTP request counts, response times |
| Dashboards | Grafana | Live monitoring dashboard |
| Log Aggregation | Loki | Log storage and search |
| Containerisation | Docker | Packaged and portable |
| Container Registry | GHCR | ghcr.io/ikteaja/healthcare-workforce-ai |
| CI/CD | GitHub Actions | Lint + test + build on every push |
| Language | Python 3.11 | Core language throughout |

---

## The Journey — 17 Phases

This system was not built in one step. Each phase added one layer,
verified it worked, and committed it to GitHub.

```
Phase 1  ✅  Laptop setup, GitHub repo, Python environment
Phase 2  ✅  Folder structure, requirements, .env configuration
Phase 3  ✅  SQLite database — 6 staff, 6 shifts, 3 schedules
Phase 4  ✅  Ingestion pipeline — 5 PDFs → 47 ChromaDB chunks
Phase 5  ✅  RAG core — retriever, prompt builder, chain
Phase 6  ✅  Agent layer — policy, schedule, compliance tools
Phase 7  ✅  FastAPI backend — /chat /health /ingest /metrics
Phase 8  ✅  Streamlit frontend — chat UI with quick questions
Phase 9  ✅  MLflow tracking — every request logged with timing
Phase 10 ✅  Docker — image built, pushed to GHCR
Phase 11 ✅  CI/CD — GitHub Actions test + build on every push
Phase 12 ✅  Monitoring — Prometheus + Grafana + Loki stack
Phase 14 ✅  Hybrid retrieval — BM25 + embedding combined
Phase 15 ✅  Hallucination guard — ungrounded answers blocked
Phase 16 ✅  Citation backing — source document cited in answer
Phase 17 ✅  Continuous evals — 22 automated RAG quality tests
```

---

## The Monitoring Story

One of the most valuable findings came from MLflow tracking.

After asking *"What is the annual leave for nurses?"*, MLflow recorded:

```
retrieval_time_seconds:       2.71s   (10% of total)
llm_time_seconds:            24.67s   (90% of total)
total_response_time_seconds: 27.49s
chunks_retrieved:             4
status:                       success
grounded:                     True
```

Two independent monitoring systems — MLflow and Grafana — both measured
~27.5 seconds for the same request. When two completely different
measurement methods agree, you can trust the number.

The conclusion: **90% of response time is LLM inference on CPU**.
ChromaDB retrieval is fast. The bottleneck is the local model.
The fix in production: switch to GPU-backed cloud inference.
This insight is only possible because of proper observability.

---

## The Safety Story

A RAG system without guardrails is dangerous for a compliance use case.
The LLM has its own training knowledge — it can confidently make up
answers that sound correct but have no basis in the hospital's actual
policies.

This system has a hallucination guard. After the LLM generates an answer,
it is checked against the retrieved source chunks. If less than 30% of
the meaningful content words in the answer appear in the source documents,
the answer is replaced with a safe fallback:

> *"I could not find sufficient information in the hospital documents
> to answer this question confidently. Please consult your HR department
> or refer to the relevant policy document directly."*

Two tests confirm this works every time:
```
Grounded answer:     "Nurses get 30 days annual leave per TVöD-K"
  → 100% word match → returned to user ✅

Hallucinated answer: "Nurses receive complimentary gym membership"
  → 0% word match → blocked, fallback returned ✅
```

---

## The Retrieval Story

The original system used embedding-only search. Embeddings understand
meaning — "annual leave" finds "Urlaubsanspruch". But they miss exact
terminology like "TVöD-K Section 26" when the semantic meaning is
slightly off.

Hybrid retrieval combines two methods:

```
BM25 (keyword search):
  Finds chunks with exact words "TVöD-K", "Section 26", "Pflegepersonal"
  BM25 scores per chunk logged to MLflow

Embedding (semantic search):
  Finds chunks meaning "leave entitlement for nursing staff"
  Embedding scores per chunk logged to MLflow

Final score = 50% BM25 + 50% Embedding
Result: better chunk selection than either method alone
```

MLflow now records 14 metrics per request — including BM25 score,
embedding score, and final combined score for each of the 4 retrieved chunks.

---

## The Quality Assurance Story

22 automated tests cover every layer of the pipeline:

```
Layer 1 — ChromaDB retrieval     (5 tests)  — finds relevant chunks?
Layer 2 — Hybrid retrieval       (5 tests)  — BM25 + embed scores valid?
Layer 3 — Hallucination guard    (6 tests)  — blocks bad answers?
Layer 4 — Prompt building        (4 tests)  — prompt contains context?
Layer 5 — Full pipeline          (2 tests)  — LLM answers correctly? [slow]
```

```
Fast run (no Ollama):   20/20 passed in 33 seconds
Full run (with Ollama): 22/22 passed in 68 seconds
```

GitHub Actions runs the fast 20 tests automatically on every push.
If anything breaks — a red X appears within 33 seconds of pushing code.

---

## Compliance by Design

This system was designed for German healthcare from the ground up:

```
DSGVO  → all data stays on-premise, no cloud calls, no data leakage
TVöD-K → German collective labour agreement for hospital staff
AZG    → German working hours law
DSGVO  → patient data rights baked into compliance tool
```

The choice of Ollama (local LLM) over OpenAI (cloud LLM) was deliberate.
Patient and staff data never leaves the hospital server.

---

## 🚀 Complete Startup Reference

> Run each block in a separate terminal. Always activate venv first.

### Quick Reference Table

| # | Terminal | Service | Command | URL |
|---|----------|---------|---------|-----|
| 0 | — | Docker Desktop | open manually | — |
| 1 | T1 | FastAPI Backend | `uvicorn src.api.main:app --port 8000` | localhost:8000/docs |
| 2 | T2 | Streamlit UI | `streamlit run streamlit_app.py` | localhost:8501 |
| 3 | T3 | MLflow Dashboard | `mlflow ui --port 5000` | localhost:5000 |
| 4 | T4 | Monitoring Stack | `docker compose up -d` | see below |

### Step by Step

**Terminal 1 — FastAPI Backend**
```powershell
cd C:\Users\Ikteaja.Hasan\Projects\healthcare-workforce-ai
venv\Scripts\activate
uvicorn src.api.main:app --port 8000
```
Verify: `http://localhost:8000/health` → `{"status":"ok"}`

**Terminal 2 — Streamlit Frontend**
```powershell
venv\Scripts\activate
streamlit run streamlit_app.py
```
Verify: `http://localhost:8501` → sidebar shows "✅ API is running"

**Terminal 3 — MLflow Dashboard**
```powershell
venv\Scripts\activate
mlflow ui --port 5000
```
Verify: `http://localhost:5000` → Experiments → healthcare-workforce-ai

**Terminal 4 — Monitoring Stack**
```powershell
docker compose up -d
```
Verify:
- `http://localhost:9090` → Prometheus → Status → Targets → UP
- `http://localhost:3000` → Grafana (admin/admin)
- `http://localhost:3100/ready` → Loki ready

### Port Reference

| Port | Service | Purpose |
|------|---------|---------|
| 8000 | FastAPI | API — /chat /health /ingest /metrics |
| 8501 | Streamlit | Chat UI |
| 5000 | MLflow | AI experiment tracking |
| 9090 | Prometheus | Metrics collection |
| 3000 | Grafana | Live dashboards (admin/admin) |
| 3100 | Loki | Log aggregation |
| 11434 | Ollama | Local LLM + embeddings |

### Shutdown
```powershell
# Ctrl+C in terminals 1, 2, 3
docker compose down    # terminal 4
```

---

## Run the Tests

```powershell
# Fast — 20 tests, no Ollama needed (~34 seconds)
pytest tests\test_rag_quality.py -v -m "not slow"

# Full — 22 tests including LLM (~68 seconds)
pytest tests\test_rag_quality.py -v
```

---

## Re-ingest Documents

Add new PDFs to `data/documents/` then:
```powershell
python src\ingestion\run_ingestion.py
```

---

## Container Registry

```
ghcr.io/ikteaja/healthcare-workforce-ai
```

Built and pushed automatically by GitHub Actions on every push to develop.

---

## Key Performance Numbers

```
Response time (local CPU):    27 - 30 seconds
LLM inference share:          90% of total time
ChromaDB retrieval share:     10% of total time
Documents ingested:           5 PDFs
Chunks in ChromaDB:           47
Staff records in SQLite:      6
Automated tests:              22 (20 fast + 2 slow)
CI/CD jobs on every push:     lint → test → docker build → push
```

---

## What Could Be Next

```
⬜ Caching            → repeated questions answered in < 1 second
⬜ Streaming responses → words appear as LLM generates them
⬜ Cloud LLM          → 5-7x faster with GPU inference
⬜ RBAC               → role-based access (HR vs doctor vs admin)
⬜ Kubernetes         → production-grade orchestration
⬜ ArgoCD             → GitOps deployment
⬜ LLM-as-judge evals → automated answer quality scoring
⬜ Guardrails         → PII redaction, prompt injection protection
```

---

## Project Structure

```
healthcare-workforce-ai/
├── src/
│   ├── api/
│   │   ├── main.py              ← FastAPI app + Prometheus
│   │   └── routes.py            ← /chat /health /ingest endpoints
│   ├── rag/
│   │   ├── retriever.py         ← ChromaDB embedding search
│   │   ├── hybrid_retriever.py  ← BM25 + embedding combined
│   │   ├── hallucination_guard.py ← grounded answer check
│   │   ├── prompt.py            ← builds prompt from chunks
│   │   └── chain.py             ← end-to-end RAG chain
│   ├── ingestion/
│   │   ├── loader.py            ← reads PDFs
│   │   ├── chunker.py           ← splits text into chunks
│   │   └── embedder.py          ← stores vectors in ChromaDB
│   ├── database/
│   │   └── db.py                ← SQLite staff/shift queries
│   └── agents/
│       └── orchestrator.py      ← LangChain agent tools
├── data/
│   ├── documents/               ← source PDFs
│   ├── chroma_db/               ← vector database on disk
│   └── workforce.db             ← SQLite database
├── monitoring/
│   ├── prometheus.yml           ← scrape config
│   └── grafana/datasources/     ← auto-configured datasources
├── tests/
│   └── test_rag_quality.py      ← 22 automated RAG tests
├── docs/                        ← all documentation
├── streamlit_app.py             ← frontend entry point
├── docker-compose.yml           ← monitoring stack
├── Dockerfile                   ← container definition
├── requirements.txt             ← all dependencies
└── .github/workflows/ci.yml     ← CI/CD pipeline
```

---

*Built by Ikteaja Hasan*
*German healthcare scenario — Helix Workforce Solutions GmbH*
*Stack: Python · LangChain · ChromaDB · Ollama · FastAPI · Streamlit*
*MLOps: MLflow · Prometheus · Grafana · Docker · GitHub Actions*
