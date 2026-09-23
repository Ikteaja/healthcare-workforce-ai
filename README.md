## 📖 The Story

> *An HR officer at Helix Workforce Solutions GmbH receives a question from a nurse:*
> *"What is my annual leave entitlement?"*
> *She searches through 200 pages of German labour law documents.*
> *Fifteen minutes later she finds it: 30 days, TVöD-K Section 26.*
>
>
>
> ***With WorkforceIQ — the same answer appears in 30 seconds.***
> ***Cited. Verified. Grounded in the actual hospital policy document.***

---

## 🎯 What This Project Is

WorkforceIQ is a **production-grade prototype** of an Agentic RAG (Retrieval-Augmented Generation) platform built to demonstrate the full modern AI engineering stack — from raw PDF documents to a fully monitored, containerised, CI/CD-deployed AI system.

It solves a real enterprise problem: HR teams waste hours searching through policy documents, compliance texts, and labour law PDFs to answer questions that repeat every single day.

> **Prototype — but built to production standards:**
> CI/CD pipeline · 22 automated tests · MLOps observability ·
> Docker containerisation · Hallucination guard · Code quality enforcement

---

## ⚡ Quick Demo

```text
User asks:  "What is the annual leave for nurses?"

System:     1. Hybrid BM25 + Embedding search → 4 relevant chunks found
            2. Chunks + question → prompt → llama3.2 via Ollama
            3. Hallucination guard checks word overlap ≥ 30%
            4. Answer returned with citation

Response:   "According to SECTION 1: ANNUAL LEAVE (JAHRESURLAUB),
             section 1.2 — nurses are entitled to 30 days per year.
             Source: HR Policy v1.0, TVöD-K Section 26."

MLflow logs: retrieval=2.71s · llm=24.67s · total=27.49s · grounded=True
```

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────────────┐
│                         HR STAFF / USER                             │
│              Types question · Reads cited answer                    │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ browser
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                               │
│         localhost:8501 · Chat UI · PDF Upload · Quick Questions     │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTP POST /chat
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                                 │
│              localhost:8000 · uvicorn · CORS                        │
│   POST /chat  ·  GET /health  ·  POST /ingest  ·  GET /metrics      │
└───────┬───────────────────┬────────────────────────────┬────────────┘
        │                   │                            │
        ▼                   ▼                            ▼
┌───────────────┐  ┌────────────────────┐   ┌──────────────────────┐
│  INGESTION    │  │  HYBRID RETRIEVAL  │   │   LANGCHAIN AGENT    │
│  PIPELINE     │  │                    │   │                      │
│               │  │ BM25 (rank-bm25)   │   │  policy_tool    →    │
│  PyPDF        │  │ +                  │   │  ChromaDB search     │
│  → Chunker    │  │ Embedding search   │   │                      │
│  → Embedder   │  │ (nomic-embed-text) │   │  schedule_tool  →    │
│  → ChromaDB   │  │                    │   │  SQLite query        │
│               │  │ 50% + 50% combined │   │                      │
│  5 PDFs       │  │ → top 4 chunks     │   │  compliance_tool →   │
│  47 chunks    │  │   with all scores  │   │  DSGVO / AZG rules   │
└───────────────┘  └────────┬───────────┘   └──────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PROMPT BUILDER                                   │
│              chunks + question → structured prompt                  │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 OLLAMA — LOCAL LLM                                  │
│         localhost:11434 · llama3.2 3B · temperature=0              │
│         nomic-embed-text 768 dims · DSGVO compliant                │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ answer generated
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 HALLUCINATION GUARD                                 │
│         src/rag/hallucination_guard.py · Phase 15                  │
│                                                                     │
│  Word overlap check: answer words vs source chunk words            │
│  ≥ 30% match → GROUNDED  → return answer to user                   │
│  < 30% match → FALLBACK  → return safe message instead             │
│  Result logged to MLflow as grounded = True / False                │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
              ┌─────────────┴──────────────┐
              ▼                            ▼
┌─────────────────────┐        ┌────────────────────────────────────┐
│     MLFLOW          │        │     PROMETHEUS + GRAFANA + LOKI    │
│  localhost:5000     │        │     localhost:9090/3000/3100       │
│                     │        │                                    │
│  Per-request:       │        │  Scrapes /metrics every 15s       │
│  · question         │        │  5 dashboard panels               │
│  · retrieval_time   │        │  · Total requests: 463            │
│  · llm_time         │        │  · Chat requests: 3               │
│  · total_time       │        │  · Avg response: 27.5s            │
│  · chunk BM25 score │        │  · Error rate: 0                  │
│  · chunk embed score│        │  Loki: log aggregation LogQL      │
│  · grounded tag     │        │                                   │
│  · 3 artifacts      │        │  Cross-validated with MLflow:     │
│    answer.txt       │        │  both show ~27.5s same request ✅  │
│    chunks.txt       │        │                                   │
│    prompt.txt       │        └────────────────────────────────────┘
└─────────────────────┘

CI/CD:
git push → flake8 + black → 22 pytest → Docker build → push GHCR
          GitHub Actions on every commit to develop branch
```

---

## 🔑 Key Finding from Observability

```text
MLflow measured for every /chat request:

  Retrieval (ChromaDB):   2.71s  =  10% of total time  ← fast
  LLM inference (CPU):   24.67s  =  90% of total time  ← bottleneck

Cross-validated: MLflow (27.49s) ≈ Grafana (27.5s) — same request,
two independent measurement systems. Both agree.

Production fix: GPU or cloud LLM → 5-7x faster immediately.
```

---

## 🛡️ Safety — Hallucination Guard

```text
Without guardrails:
  LLM confidently answers "nurses get gym membership"
  HR staff acts on wrong information — compliance risk

With hallucination guard:
  Word overlap check: 0% of "gym membership" words found in source chunks
  → BLOCKED → safe fallback returned instead
  → logged to MLflow as grounded=False

Test results:
  Grounded answer  → 100% word match → PASS ✅
  Hallucinated answer → 0% match → BLOCKED ✅
```

---

## 🔍 Hybrid Retrieval — Why Two Methods

```text
BM25 (keyword search):    finds exact terms — "TVöD-K", "Section 26"
Embedding (semantic):     finds meaning — "annual leave" finds "Urlaubsanspruch"

Combined: final_score = (0.5 × BM25) + (0.5 × embedding)
Result:   better chunk selection than either method alone

All 3 scores per chunk logged to MLflow for analysis.
```

---

## 🛠️ Tech Stack

LayerTechnologyPurpose**Frontend**StreamlitChat UI for HR staff**Backend**FastAPI + uvicornREST API — /chat /health /ingest /metrics**Orchestration**LangChainConnects LLM to tools and documents**LLM**Ollama + llama3.2Local inference — no cloud, no data leakage**Embeddings**nomic-embed-text768-dimensional vector encoding**Vector DB**ChromaDB 0.4.24Stores and searches 47 document chunks**Keyword Search**rank-bm25BM25Okapi exact keyword scoring**Staff DB**SQLiteStaff names, shifts, schedules**Guard**Custom word overlapBlocks ungrounded LLM answers**MLOps**MLflow 2.17.0Records every request with 14 metrics**Metrics**PrometheusHTTP request counts and response times**Dashboards**GrafanaLive 5-panel monitoring dashboard**Logs**LokiLog aggregation with LogQL**Container**DockerPackaged image pushed to GHCR**CI/CD**GitHub ActionsLint + test + build on every push**Language**Python 3.11Core language throughout

---

## 📁 Project Structure

```text
workforceiq/
├── streamlit_app.py              ← Frontend entry point (port 8501)
├── docker-compose.yml            ← Monitoring stack (Prometheus/Grafana/Loki)
├── Dockerfile                    ← Container definition
├── requirements.txt              ← All dependencies with pinned versions
├── pytest.ini                    ← Test configuration
│
├── src/
│   ├── api/
│   │   ├── main.py               ← FastAPI app + Prometheus instrumentation
│   │   └── routes.py             ← /chat /health /ingest endpoints + MLflow
│   ├── rag/
│   │   ├── retriever.py          ← Original ChromaDB embedding retrieval
│   │   ├── hybrid_retriever.py   ← BM25 + embedding combined (Phase 14)
│   │   ├── hallucination_guard.py← Word overlap guard (Phase 15)
│   │   ├── prompt.py             ← Builds prompt from chunks + question
│   │   └── chain.py              ← End-to-end RAG chain
│   ├── ingestion/
│   │   ├── loader.py             ← PyPDF document loader + normalisation
│   │   ├── chunker.py            ← 500-char chunks with 50-char overlap
│   │   └── embedder.py           ← Embeds chunks into ChromaDB
│   ├── database/
│   │   └── db.py                 ← SQLite staff/shift/schedule queries
│   └── agents/
│       └── orchestrator.py       ← LangChain agent with 3 tools
│
├── data/
│   ├── documents/                ← Source PDF files (5 documents)
│   ├── chroma_db/                ← Vector database on disk (47 chunks)
│   └── workforce.db              ← SQLite database
│
├── monitoring/
│   ├── prometheus.yml            ← Scrape config (15s interval)
│   └── grafana/datasources/      ← Auto-configured Prometheus + Loki
│
├── tests/
│   └── test_rag_quality.py       ← 22 automated tests across 5 layers
│
└── docs/
    ├── images/                   ← Architecture diagrams
    └── *.md                      ← Phase documentation
```

---

## 🚀 Complete Startup Guide

### Prerequisites

```text
✅ Python 3.11 installed
✅ Docker Desktop running
✅ Ollama installed and running
✅ Git repository cloned
```

### One-time setup

```powershell
# Clone the repo
git clone https://github.com/Ikteaja/healthcare-workforce-ai.git
cd healthcare-workforce-ai

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate      # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Pull Ollama models
ollama pull llama3.2
ollama pull nomic-embed-text

# Run ingestion (builds ChromaDB from PDFs)
python src/ingestion/run_ingestion.py
```

### Daily startup — 4 terminals

**Terminal 1 — FastAPI Backend**

```powershell
venv\Scripts\activate
uvicorn src.api.main:app --port 8000
```

✅ Verify: `http://localhost:8000/health` → `{"status":"ok"}`

**Terminal 2 — Streamlit Frontend**

```powershell
venv\Scripts\activate
streamlit run streamlit_app.py
```

✅ Verify: `http://localhost:8501` → chat UI loads

**Terminal 3 — MLflow Dashboard**

```powershell
venv\Scripts\activate
mlflow ui --port 5000
```

✅ Verify: `http://localhost:5000` → experiments list

**Terminal 4 — Monitoring Stack**

```powershell
docker compose up -d
```

✅ Verify: `http://localhost:3000` → Grafana (admin/admin)

### All service URLs

| Service | URL | Credentials |
| --- | --- | --- |
| Streamlit UI | http://localhost:8501 | none |
| FastAPI docs | http://localhost:8000/docs | none |
| MLflow | http://localhost:5000 | none |
| Prometheus | http://localhost:9090 | none |
| Grafana | http://localhost:3000 | admin / admin |
| Ollama | http://localhost:11434 | none |

### Shutdown

```powershell
# Ctrl+C in terminals 1, 2, 3
docker compose down    # stops Prometheus, Grafana, Loki
```

---

## 🧪 Run the Tests

```powershell
# Fast — 20 tests, no Ollama needed (~34 seconds)
pytest tests\test_rag_quality.py -v -m "not slow"

# Full — 22 tests including LLM calls (~68 seconds)
pytest tests\test_rag_quality.py -v
```

### What is tested

| Layer | Tests | What it checks |
| --- | --- | --- |
| ChromaDB retrieval | 5 | Chunks returned, count ≤4, strings, relevant content |
| Hybrid retrieval | 5 | Returns dicts, scores 0-1, sorted correctly |
| Hallucination guard | 6 | Grounded passes, hallucinated blocked, edge cases |
| Prompt building | 4 | Question in prompt, chunks in prompt, not empty |
| Full pipeline (slow) | 2 | End-to-end LLM answer quality |

```text
Results: 22/22 PASSED
Fast run:  34 seconds  (no Ollama needed)
Full run:  68 seconds  (requires Ollama running)
```

---

## ♻️ Re-ingest Documents

Add new PDFs to `data/documents/` then run:

```powershell
python src\ingestion\run_ingestion.py
```

---

## 📊 MLflow Metrics — What Is Logged

Every `/chat` request logs:

- `question` — text asked (first 250 chars)
- `model` — llama3.2
- `embed_model` — nomic-embed-text
- `chunk_N_sources` — source filename per chunk
- `retrieval_time_seconds` — 2.71s
- `llm_time_seconds` — 24.67s
- `total_response_time_seconds` — 27.49s
- `chunks_retrieved` — 4
- `chunk_N_bm25` — 0–1 per chunk
- `chunk_N_embed` — 0–1 per chunk
- `chunk_N_final` — 0–1 per chunk
- `grounded` — True / False
- `retrieval_type` — hybrid_bm25_embedding
- `answer.txt` — full LLM response
- `retrieved_chunks.txt` — 4 source chunks used
- `prompt.txt` — exact prompt sent to LLM

---

## 🔒 Why On-Premise — Compliance

```text
German law (DSGVO) requires patient and staff personal data
to stay within controlled infrastructure.

Architectural decision: Ollama runs locally.
  ✅ No personal data leaves the hospital server
  ✅ No cloud API calls for patient queries
  ✅ Full audit trail via MLflow
  ✅ DSGVO compliant by design

Production path: Azure/AWS with private VPC endpoints
                 or dedicated on-premise GPU server
```

---

## 🔮 Known Limitations and Next Steps

This is a production-grade prototype. Known limitations:

| Limitation | Production Fix |
| --- | --- |
| 27s response (CPU only) | Cloud GPU or AWS Bedrock → 4s |
| No response caching | Redis cache → repeated questions <1s |
| No streaming | LLM streaming → words appear live |
| No RBAC | Cognito / IAM → role-based access |
| Basic hallucination check | NLI model → more accurate grounding |
| No PII redaction | AWS Comprehend → scrub personal data |

---

## ✅ Project Phases

```text
Phase 1  ✅  Laptop + GitHub Setup
Phase 2  ✅  Folder Structure + Requirements
Phase 3  ✅  SQLite Database Layer
Phase 4  ✅  Ingestion Pipeline
Phase 5  ✅  RAG Core (retriever, prompt, chain)
Phase 6  ✅  LangChain Agent Layer
Phase 7  ✅  FastAPI Backend
Phase 8  ✅  Streamlit Frontend
Phase 9  ✅  MLflow Experiment Tracking
Phase 10 ✅  Docker Containerisation
Phase 11 ✅  GitHub Actions CI/CD
Phase 12 ✅  Prometheus + Grafana + Loki Monitoring
Phase 14 ✅  Hybrid BM25 + Embedding Retrieval
Phase 15 ✅  Hallucination Fallback Guard
Phase 16 ✅  Citation Backing (automatic)
Phase 17 ✅  Continuous Evals — 22 automated tests
```

---

## 🐳 Docker

```powershell
# Build image
docker build -t workforceiq .

# Run container
docker run -p 8000:8000 workforceiq

# Pull from GitHub Container Registry
docker pull ghcr.io/ikteaja/healthcare-workforce-ai:latest
```

---

## 👤 Author

**Ikteaja Hasan**
Cloud & DevOps Engineer | AI Engineering
Köln, Deutschland

[LinkedIn](https://linkedin.com/in/ikteaja-hasan-27a529166)
[GitHub](https://github.com/Ikteaja)

> 📩 **Repository access:** This repo is private.
> DM on LinkedIn or email to request access for review.

---

## 📄 Licence

Private repository — all rights reserved.
Contact the author for access or collaboration.

---

*WorkforceIQ — Agentic RAG Platform for Workforce Intelligence*
*Built with Python · LangChain · ChromaDB · FastAPI · MLflow · Docker*
