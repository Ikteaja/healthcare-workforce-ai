# healthcare-workforce-ai
RAG Agentic AI for Healthcare Workforce Management
## 🚀 Complete Startup Reference

> Every command needed to start the full system, in order.
> Run each block in a separate terminal (5 terminals total).
> Always activate venv first in every terminal.

### Quick Reference Table

| # | Terminal | Service | Port | Command | URL |
|---|----------|---------|------|---------|-----|
| 0 | any | Activate venv | - | `venv\Scripts\activate` | - |
| 0 | any | Docker Desktop | - | open manually (GUI app) | - |
| 1 | T1 | FastAPI Backend | 8000 | `uvicorn src.api.main:app --port 8000` | http://localhost:8000/docs |
| 2 | T2 | Streamlit UI | 8501 | `streamlit run streamlit_app.py` | http://localhost:8501 |
| 3 | T3 | MLflow Dashboard | 5000 | `mlflow ui --port 5000` | http://localhost:5000 |
| 4 | T4 | Monitoring Stack | 9090/3000/3100 | `docker compose up -d` | see below |
| - | - | Ollama | 11434 | starts automatically | http://localhost:11434 |

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
cd C:\Users\Ikteaja.Hasan\Projects\healthcare-workforce-ai
venv\Scripts\activate
streamlit run streamlit_app.py
```
Verify: `http://localhost:8501` → sidebar shows "✅ API is running"

**Terminal 3 — MLflow Dashboard**
```powershell
cd C:\Users\Ikteaja.Hasan\Projects\healthcare-workforce-ai
venv\Scripts\activate
mlflow ui --port 5000
```
Verify: `http://localhost:5000` → Experiments → healthcare-workforce-ai

**Terminal 4 — Monitoring Stack (Prometheus + Grafana + Loki)**
```powershell
cd C:\Users\Ikteaja.Hasan\Projects\healthcare-workforce-ai
docker compose up -d
```
Verify:
```
http://localhost:9090       → Prometheus → Status → Targets (UP)
http://localhost:3000       → Grafana login (admin/admin)
http://localhost:3100/ready → Loki ready
```

### Daily Use

```
1. http://localhost:8501          → ask questions
2. http://localhost:5000          → check MLflow run timings
3. http://localhost:3000          → check Grafana dashboard
4. http://localhost:9090/targets  → confirm Prometheus scraping
```

### Shutdown

```powershell
# Terminal 1, 2, 3 — press Ctrl+C in each
# Terminal 4:
docker compose down
```

### Port Reference

| Port | Service | Started by | Used for |
|------|---------|-----------|----------|
| 8000 | FastAPI | uvicorn | API, /chat, /health, /ingest, /metrics |
| 8501 | Streamlit | streamlit run | Chat UI |
| 5000 | MLflow | mlflow ui | AI experiment tracking dashboard |
| 9090 | Prometheus | docker compose | Metrics scraping + storage |
| 3000 | Grafana | docker compose | Dashboards (admin/admin) |
| 3100 | Loki | docker compose | Log storage |
| 11434| Ollama | auto-start | LLM (llama3.2) + embeddings (nomic-embed-text) |
