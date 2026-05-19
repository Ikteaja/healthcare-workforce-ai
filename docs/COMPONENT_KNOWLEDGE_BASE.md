# Healthcare Workforce AI — Component Knowledge Base

> Read this document to understand every component, what it does,
> how it connects, and why it exists in this project.

---

## Quick Reference Map

```
YOUR QUESTION
     │
     ▼
[Streamlit]  ←── you type here (browser UI)
     │ HTTP
     ▼
[FastAPI]    ←── receives your question (backend server)
     │
     ▼
[LangChain Agent]  ←── decides which tool to use (brain)
     │
     ├──▶ [policy_tool]    → searches ChromaDB (HR docs)
     ├──▶ [schedule_tool]  → queries SQLite (staff/shifts)
     └──▶ [compliance_tool]→ searches ChromaDB (compliance docs)
               │
               ▼
     [Retriever] → searches [ChromaDB Vector DB]
               │
               ▼
     [Prompt Builder] → combines chunks + question
               │
               ▼
     [Ollama LLM]  ←── generates the final answer
               │
               ▼
     Answer flows back → FastAPI → Streamlit → YOU
```

---

## Every Component Explained

---

### 1. Ollama

**What it is:**
A tool that runs AI models locally on your laptop.
No internet needed. No API cost. Everything stays private.

**What it does in this project:**
Runs two models for you:
- `llama3.2` — the LLM that reads and writes answers
- `nomic-embed-text` — the embedding model that converts text to numbers

**How it works:**
Ollama runs as a small server on your laptop on port 11434.
Your Python code talks to it like calling a web API.

**Workflow:**
```
Python code  →  HTTP request  →  Ollama (port 11434)  →  returns answer or numbers
```

**Where it lives:** Your laptop (runs natively, not in Docker)

**Commands:**
```powershell
ollama serve              # start the server
ollama pull llama3.2      # download LLM model
ollama pull nomic-embed-text  # download embedding model
ollama list               # see all downloaded models
```

**Config in .env:**
```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
EMBED_MODEL=nomic-embed-text
```

---

### 2. Embedding Model (nomic-embed-text)

**What it is:**
A special AI model that converts any text into a list of numbers
called a vector. Example: "nurse leave policy" → [0.82, 0.14, 0.67...]

**Why we need numbers:**
Computers cannot compare the meaning of words directly.
But they can compare numbers. Similar meaning = similar numbers.

**What it does in this project:**
Two jobs:

| Job | When | What happens |
|-----|------|--------------|
| Ingestion | Once at setup | Converts every document chunk → numbers → saves to ChromaDB |
| Query time | Every question | Converts user question → numbers → searches ChromaDB |

**Critical rule:**
The SAME model must do both jobs. If you change the model,
you must delete ChromaDB and re-run ingestion from scratch.

**Workflow:**
```
"Nurse leave policy"
        │
        ▼
nomic-embed-text
        │
        ▼
[0.82, 0.14, 0.67, 0.33, ...]  ← vector (list of numbers)
        │
        ▼
Saved into ChromaDB alongside the original text
```

**File:** `src/ingestion/embedder.py` and `src/rag/retriever.py`

---

### 3. ChromaDB (Vector Database)

**What it is:**
A special database that stores vectors (numbers) AND the original text
together. It can find the most similar vectors very fast.

**What it does in this project:**
Stores all your document chunks with their vectors.
When a question comes in, it finds the 4 most relevant chunks.

**What one record looks like inside ChromaDB:**
```
ID:       chunk_42
Vector:   [0.82, 0.14, 0.67, 0.33 ...]   ← used for searching
Text:     "Annual leave for nurses is 28 days per year..."  ← returned as result
Metadata: {source: "hr_policy.pdf", page: 3}
```

**How search works:**
```
User question → converted to numbers → compared to all vectors in DB
             → finds 4 closest matches → returns their TEXT (not numbers)
```

**Where it lives:** `data/chroma_db/` folder on your laptop disk

**Important:** Never delete this folder unless you plan to re-run ingestion.

**Config in .env:**
```
CHROMA_PATH=./data/chroma_db
```

**File:** Used in `src/ingestion/embedder.py` and `src/rag/retriever.py`

---

### 4. Documents (data/documents/)

**What it is:**
The folder where you put all your healthcare documents.
These are the source of truth for the AI's answers.

**What goes here:**

| File | Content |
|------|---------|
| hr_policy.pdf | Leave rules, conduct, onboarding |
| shift_rotation_policy.pdf | How shifts are assigned |
| compliance_hipaa.pdf | HIPAA and data handling rules |
| onboarding_guide.pdf | New staff steps |
| role_descriptions.pdf | Nurse, doctor, admin roles |
| emergency_protocol.pdf | Emergency staffing procedures |

**Workflow:**
```
You drop PDFs here
       │
       ▼
Ingestion pipeline reads them (loader.py)
       │
       ▼
Splits into chunks (chunker.py)
       │
       ▼
Converts chunks to numbers (embedder.py)
       │
       ▼
Saves to ChromaDB (done — AI can now answer from these docs)
```

**Important:** After adding new documents, re-run:
```powershell
python src/ingestion/run_ingestion.py
```

---

### 5. Ingestion Pipeline

**What it is:**
A one-time process that reads your documents, cuts them into pieces,
converts them to numbers, and saves them into ChromaDB.

**Three files, three jobs:**

**loader.py — reads files**
```
data/documents/hr_policy.pdf  →  full raw text
```

**chunker.py — splits text into small pieces**
```
Full document (50 pages)
        │
        ▼
Chunk 1: "Annual leave for nurses is 28 days..." (500 words)
Chunk 2: "Sick leave requires a doctor's note..." (500 words)
Chunk 3: "Overtime must be approved 48 hours..." (500 words)
...and so on
```
Why 500 words? Big enough to have meaning, small enough to be precise.
Overlap of 50 words means chunks share context at the edges.

**embedder.py — converts chunks to numbers and saves**
```
Chunk text  →  nomic-embed-text  →  vector  →  ChromaDB
```

**Run ingestion:**
```powershell
python src/ingestion/run_ingestion.py
```

**When to re-run:**
- When you add new documents
- When you update existing documents
- When you change the embedding model

---

### 6. SQLite Database (workforce.db)

**What it is:**
A simple database file that stores structured data about your staff,
shifts, and schedules. Lives in `data/workforce.db`.

**Why separate from ChromaDB:**
ChromaDB is for searching documents (unstructured text).
SQLite is for querying structured data like tables and dates.

**Three tables:**

**Staff table:**
```
id | name          | role   | department | email
1  | Sarah Johnson | Nurse  | ICU        | s.johnson@hospital.com
2  | Ahmed Ali     | Doctor | ER         | a.ali@hospital.com
```

**Shifts table:**
```
id | staff_id | date       | start_time | end_time | ward
1  | 1        | 2026-05-20 | 07:00      | 15:00    | Ward A
2  | 2        | 2026-05-20 | 08:00      | 16:00    | ER
```

**Schedules table:**
```
id | department | week_start | min_staff_required
1  | ICU        | 2026-05-18 | 5
2  | ER         | 2026-05-18 | 8
```

**File:** `src/database/models.py` and `src/database/db.py`

**Config in .env:**
```
DB_PATH=./data/workforce.db
```

---

### 7. LangChain

**What it is:**
A Python framework that connects all the AI pieces together.
It provides the tools, agent, prompt templates, and pipeline connectors.

**What it does in this project — four jobs:**

| Job | File | What it does |
|-----|------|--------------|
| Document loading | loader.py | Reads PDFs and Word files |
| Text splitting | chunker.py | Splits documents into chunks |
| Agent | orchestrator.py | Decides which tool to call |
| Prompt templates | prompt.py | Builds the prompt for the LLM |

**Think of LangChain as the glue** — it connects Ollama, ChromaDB,
SQLite, and your custom tools into one working system.

---

### 8. LangChain Agent (Orchestrator)

**What it is:**
The brain of the system. It reads the user's question and decides
which tool to call to find the answer.

**How it decides:**

```
Question: "What is the annual leave policy?"
  → Agent thinks: this is about HR policy
  → Calls: policy_tool (searches ChromaDB)

Question: "Who is working in Ward A on Friday?"
  → Agent thinks: this is about schedules
  → Calls: schedule_tool (queries SQLite)

Question: "Is our shift rotation HIPAA compliant?"
  → Agent thinks: this needs compliance info
  → Calls: compliance_tool (searches ChromaDB)
```

**Three tools available:**

| Tool | Searches | Best for |
|------|----------|---------|
| policy_tool | ChromaDB | HR rules, leave, onboarding |
| schedule_tool | SQLite | Who works when and where |
| compliance_tool | ChromaDB | HIPAA, regulations, audits |

**File:** `src/agents/orchestrator.py`

---

### 9. Retriever

**What it is:**
The search function. It takes a question, converts it to numbers,
searches ChromaDB, and returns the 4 most relevant text chunks.

**Workflow:**
```
Question: "What is the nurse leave policy?"
        │
        ▼
Convert question to numbers: [0.81, 0.13, 0.66...]
        │
        ▼
Compare with all vectors in ChromaDB
        │
        ▼
Find 4 closest matches
        │
        ▼
Return their TEXT:
  - "Annual leave for nurses is 28 days..."
  - "Leave requests must be submitted 2 weeks..."
  - "Sick leave policy states that..."
  - "Public holidays are in addition to..."
```

**File:** `src/rag/retriever.py`

---

### 10. Prompt Builder

**What it is:**
Assembles the final message that gets sent to the LLM.
It combines the retrieved chunks + the original question into one
structured prompt.

**What the prompt looks like:**
```
You are a healthcare workforce management assistant.
Use ONLY the information below to answer. Do not guess.

Context:
[Chunk 1 text]
[Chunk 2 text]
[Chunk 3 text]
[Chunk 4 text]

Question: What is the nurse leave policy?

Answer:
```

**Why this structure matters:**
- "Use ONLY the information below" — stops the AI from making things up
- Chunks give the AI real facts from your actual documents
- The AI reads the chunks and writes a clear answer

**File:** `src/rag/prompt.py`

---

### 11. LLM — llama3.2 (via Ollama)

**What it is:**
The language model that reads the prompt (chunks + question)
and writes the final answer in plain English.

**What it does NOT do:**
- It does not search anything
- It does not access the internet
- It does not remember previous conversations
- It only reads what is in the current prompt

**Why local LLM (Ollama) instead of OpenAI:**

| | Ollama (local) | OpenAI (cloud) |
|--|----------------|----------------|
| Cost | Free | Pay per use |
| Privacy | Data stays on laptop | Data sent to cloud |
| Internet | Not needed | Required |
| Speed | Depends on laptop | Fast |
| Setup | Pull model once | Need API key |

**File:** Used in `src/rag/chain.py` and `src/agents/orchestrator.py`

---

### 12. FastAPI (Backend)

**What it is:**
A Python web server that receives questions from the frontend,
passes them to the agent, and returns answers as JSON.

**Three endpoints:**

| Endpoint | Method | What it does |
|----------|--------|-------------|
| /chat | POST | Receives question → runs agent → returns answer |
| /ingest | POST | Receives a new PDF → runs ingestion pipeline |
| /health | GET | Returns {"status":"ok"} — used by CI/CD to check if app is running |

**How it communicates:**
```
Streamlit  →  POST /chat {"question": "..."}  →  FastAPI
FastAPI    →  calls LangChain agent
FastAPI    ←  gets answer back
Streamlit  ←  {"answer": "..."}  ←  FastAPI
```

**Run it:**
```powershell
uvicorn src.api.main:app --reload --port 8000
```

**Test it:**
Open http://localhost:8000/docs — auto-generated test page

**File:** `src/api/main.py` and `src/api/routes.py`

---

### 13. Streamlit (Frontend)

**What it is:**
A Python library that creates a simple chat web interface.
HR staff and employees use this to ask questions.

**What the user sees:**
- A chat window (like WhatsApp)
- Type a question → get an answer
- Sidebar to upload new documents

**How it communicates:**
```
User types question
       │
       ▼
Streamlit sends HTTP POST to FastAPI at localhost:8000/chat
       │
       ▼
Gets JSON answer back
       │
       ▼
Displays answer in chat bubble
```

**Run it:**
```powershell
streamlit run streamlit_app.py
```

**Opens at:** http://localhost:8501

**File:** `streamlit_app.py`

---

### 14. MLflow (Experiment Tracking)

**What it is:**
A tool that records every AI interaction — what question was asked,
how long the answer took, which model was used.

**What it tracks in this project:**

| What | Example |
|------|---------|
| Question asked | "What is the leave policy?" |
| Answer given | "Annual leave is 28 days..." |
| Response time | 2.3 seconds |
| Model used | llama3.2 |
| Chunks retrieved | 4 |
| Ingestion runs | 127 chunks from 5 documents |

**Why it matters:**
- See if the AI is getting slower over time
- Compare different models
- Debug bad answers by seeing exactly what chunks were retrieved
- Track when new documents were added

**Run it:**
```powershell
mlflow ui
```
**Opens at:** http://localhost:5000

**Config in .env:**
```
MLFLOW_TRACKING_URI=http://localhost:5000
```

**File:** Used in `src/api/routes.py`

---

### 15. Docker

**What it is:**
A tool that packages your entire application into a container —
a box that has Python, all libraries, and your code inside.
This container runs the same way on any computer.

**Why we need it:**
"It works on my laptop" problem. Docker makes sure it works everywhere.

**Two files:**

**Dockerfile** — recipe to build the container:
```
Start with Python 3.11
Install all requirements
Copy source code
Run FastAPI on port 8000
```

**docker-compose.yml** — runs multiple services together:
```
Service 1: FastAPI app (port 8000)
Service 2: Streamlit frontend (port 8501)
Future: Prometheus, Grafana, Loki
```

**Commands:**
```powershell
docker compose up --build   # build and start everything
docker compose down         # stop everything
docker compose logs         # see what is happening
```

---

### 16. GitHub Actions (CI/CD)

**What it is:**
Automated pipeline that runs every time you push code to GitHub.
CI = Continuous Integration. CD = Continuous Delivery.

**What happens automatically on every git push:**

```
You run: git push origin develop
              │
              ▼
GitHub Actions starts automatically
              │
         ┌────┴────┐
         ▼         ▼
    Run tests   Check code style
    (pytest)    (flake8, black)
         │         │
         └────┬────┘
              │ if all pass
              ▼
        Build Docker image
              │
              ▼
        Push to GHCR
        (GitHub Container Registry)
```

**File:** `.github/workflows/ci.yml`

**What it catches:**
- Broken code before it reaches main branch
- Style errors
- Failed tests

---

### 17. GitHub Container Registry (GHCR)

**What it is:**
GitHub's storage for Docker images. Like GitHub for code,
but for containers.

**Address of your image:**
```
ghcr.io/ikteaja/healthcare-workforce-ai:latest
```

**Why it matters:**
Anyone (or any server) can pull your Docker image and run
the application without needing your source code.

---

### 18. Prometheus + Grafana + Loki (Future Phase)

**What they are:**

| Tool | Job | Think of it as |
|------|-----|----------------|
| Prometheus | Collects numbers (metrics) | A counter that watches your app |
| Grafana | Displays charts and dashboards | A TV showing your app's health |
| Loki | Collects log messages | A diary of everything your app does |

**What you will see in Grafana:**
- How many questions asked per hour
- Average response time
- Error rate
- Which tools the agent calls most

**These run as Docker services — added in a future phase.**

---

## How Everything Connects — Full Flow

### Ingestion Flow (run once)

```
1. You put PDFs in  →  data/documents/
2. loader.py        →  reads the PDF text
3. chunker.py       →  splits into 500-word chunks
4. embedder.py      →  converts each chunk to numbers (nomic-embed-text via Ollama)
5. ChromaDB         →  saves numbers + text to data/chroma_db/
   Done — documents are ready to be searched
```

### Query Flow (every question)

```
1. User types       →  "Who works in ICU on Monday?"
2. Streamlit        →  sends HTTP POST to FastAPI /chat
3. FastAPI          →  passes question to LangChain Agent
4. Agent            →  decides to call schedule_tool
5. schedule_tool    →  queries SQLite workforce.db
6. Agent            →  gets results, builds context
7. Prompt builder   →  combines context + question into prompt
8. Ollama LLM       →  reads prompt, writes answer
9. FastAPI          →  sends answer back as JSON
10. Streamlit       →  displays answer in chat bubble
11. MLflow          →  records the question, answer, and timing
```

---

## Port Reference

| Service | Port | URL |
|---------|------|-----|
| FastAPI backend | 8000 | http://localhost:8000 |
| FastAPI docs (test page) | 8000 | http://localhost:8000/docs |
| Streamlit frontend | 8501 | http://localhost:8501 |
| Ollama server | 11434 | http://localhost:11434 |
| MLflow UI | 5000 | http://localhost:5000 |
| Prometheus (future) | 9090 | http://localhost:9090 |
| Grafana (future) | 3000 | http://localhost:3000 |

---

## File-to-Component Map

| File | Component | What it does |
|------|-----------|-------------|
| src/ingestion/loader.py | Ingestion | Reads PDFs and Word files |
| src/ingestion/chunker.py | Ingestion | Splits text into 500-word chunks |
| src/ingestion/embedder.py | Embedding + ChromaDB | Converts chunks to vectors, saves to ChromaDB |
| src/ingestion/run_ingestion.py | Ingestion | Runs the full ingestion pipeline |
| src/rag/retriever.py | Retriever | Searches ChromaDB for relevant chunks |
| src/rag/prompt.py | Prompt Builder | Assembles chunks + question into prompt |
| src/rag/chain.py | RAG chain | Connects retriever → prompt → LLM |
| src/agents/orchestrator.py | LangChain Agent | Decides which tool to use |
| src/agents/tools/policy_tool.py | Agent Tool | Searches HR policy documents |
| src/agents/tools/schedule_tool.py | Agent Tool | Queries staff shift database |
| src/agents/tools/compliance_tool.py | Agent Tool | Searches compliance documents |
| src/api/main.py | FastAPI | App entry point, CORS setup |
| src/api/routes.py | FastAPI | /chat /ingest /health endpoints |
| src/database/models.py | SQLite | Staff, Shift, Schedule table definitions |
| src/database/db.py | SQLite | Database connection and session |
| streamlit_app.py | Streamlit | Chat UI frontend |
| Dockerfile | Docker | Recipe to build the container |
| docker-compose.yml | Docker | Runs all services together |
| .github/workflows/ci.yml | GitHub Actions | Auto test and build on every push |
| .env | Config | Secret values — never pushed to GitHub |
| .env.example | Config | Safe template — pushed to GitHub |
| requirements.txt | Python | All library dependencies |

---

*Document version: 1.0 — May 2026*
*Project: Healthcare Workforce AI — RAG Agentic System*
*Developer: Ikteaja Hasan*