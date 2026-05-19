# Healthcare Workforce AI — Project Documentation

**Project:** RAG Agentic AI for Healthcare Workforce Management
**Developer:** Ikteaja Hasan
**Repo:** https://github.com/Ikteaja/healthcare-workforce-ai
**Started:** May 2026

---

## What This Project Does

An AI assistant for healthcare workforce management.
HR staff and employees can ask questions in plain English and get
accurate answers from real company documents and staff data.

Example questions the AI can answer:
- "What is the nurse annual leave policy?"
- "Who is working in ICU on Monday?"
- "What are the HIPAA compliance rules for data handling?"
- "How many staff are required in the ER this week?"

---

## How To Set Up (New Developer)

### Step 1 — Clone the repo
```bash
git clone https://github.com/Ikteaja/healthcare-workforce-ai.git
cd healthcare-workforce-ai
```

### Step 2 — Install Python 3.11
Download from: https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

### Step 3 — Create virtual environment
```bash
py -3.11 -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4 — Set up environment variables
```bash
copy .env.example .env
# Open .env and fill in your values
```

### Step 5 — Install and start Ollama
Download from: https://ollama.com/download
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### Step 6 — Run ingestion (first time only)
```bash
python src/ingestion/run_ingestion.py
```

### Step 7 — Start the application
```bash
# Terminal 1 — Backend
uvicorn src.api.main:app --reload --port 8000

# Terminal 2 — Frontend
streamlit run streamlit_app.py
```

Open browser at: http://localhost:8501

---

## Project Folder Structure
healthcare-workforce-ai/
│
├── data/
│   ├── documents/          ← PUT YOUR PDF FILES HERE
│   ├── chroma_db/          ← auto-created by ChromaDB
│   └── workforce.db        ← auto-created by SQLAlchemy
│
├── src/
│   ├── ingestion/          ← reads docs, chunks, embeds, saves to ChromaDB
│   ├── rag/                ← retriever, prompt builder, LLM chain
│   ├── agents/             ← LangChain agent and tools
│   ├── api/                ← FastAPI backend
│   └── database/           ← SQLite models and connection
│
├── docs/                   ← all documentation
├── tests/                  ← all test files
├── .github/workflows/      ← GitHub Actions CI/CD
├── streamlit_app.py        ← frontend chat UI
├── Dockerfile              ← container recipe
├── docker-compose.yml      ← runs all services
├── requirements.txt        ← Python libraries
├── .env                    ← secrets (never push to GitHub)
└── .env.example            ← safe template (pushed to GitHub)

---

## Build Phases

| Phase | What | Status |
|-------|------|--------|
| 1 | Laptop + GitHub setup | ✅ Done |
| 2 | Folder structure + requirements | 🔄 In progress |
| 3 | Data layer — documents + SQLite | ⬜ Next |
| 4 | Ingestion pipeline | ⬜ Pending |
| 5 | RAG core — retriever + prompt | ⬜ Pending |
| 6 | Agent layer — orchestrator + tools | ⬜ Pending |
| 7 | FastAPI backend | ⬜ Pending |
| 8 | Streamlit frontend | ⬜ Pending |
| 9 | MLflow tracking | ⬜ Pending |
| 10 | Docker | ⬜ Pending |
| 11 | GitHub Actions CI/CD | ⬜ Pending |
| 12 | Monitoring — future | ⬜ Future |

---

## Daily Developer Workflow

```powershell
# 1. Go to project folder
cd C:\Users\Ikteaja.Hasan\Projects\healthcare-workforce-ai

# 2. Activate venv
venv\Scripts\activate

# 3. Switch to develop branch
git checkout develop
git pull origin develop

# 4. Start Ollama
ollama serve

# 5. Start backend (Terminal 1)
uvicorn src.api.main:app --reload --port 8000

# 6. Start frontend (Terminal 2)
streamlit run streamlit_app.py

# 7. After coding — commit and push
git add .
git commit -m "feat: describe what you built"
git push origin develop
```

---

## Port Reference

| Service | Port | URL |
|---------|------|-----|
| FastAPI | 8000 | http://localhost:8000 |
| FastAPI docs | 8000 | http://localhost:8000/docs |
| Streamlit | 8501 | http://localhost:8501 |
| Ollama | 11434 | http://localhost:11434 |
| MLflow | 5000 | http://localhost:5000 |

---

## Troubleshooting Log

| Date | Problem | Cause | Fix |
|------|---------|-------|-----|
| May 2026 | git clone — repo not found | Repo not created on GitHub yet | Created repo first |
| May 2026 | git clone 403 error | PAT token missing repo scope | New token with repo scope |
| May 2026 | Wrong folder .vscode | Working in wrong directory | Used Projects folder |
| May 2026 | Python 3.14 installed | Too new for libraries | Installed Python 3.11 |
| May 2026 | copy command failed | Wrong working directory | cd into project first |