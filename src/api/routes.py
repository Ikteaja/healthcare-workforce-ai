# =============================================================
# src/api/routes.py
# =============================================================
# PURPOSE:
#   Defines the three API endpoints.
#   Each endpoint is one URL that accepts requests.
#
# THREE ROUTES:
#   GET  /health  → checks FastAPI is alive
#   POST /chat    → receives question, returns AI answer
#                   + MLflow tracking added in Phase 9
#   POST /ingest  → receives PDF file, adds to ChromaDB
#
# WHO CALLS EACH:
#   /health → Docker, GitHub Actions, browser
#   /chat   → Streamlit (every time user asks question)
#   /ingest → Streamlit sidebar (when HR uploads PDF)
#
# HOW DATA FLOWS:
#   /chat:   Streamlit → FastAPI → chain.py → LLM → answer
#   /ingest: Streamlit → FastAPI → save file → ingestion
#
# MLFLOW TRACKING (Phase 9):
#   Every /chat request is recorded to MLflow dashboard.
#   View at: http://localhost:5000
#   Records: question, model, retrieval time, LLM time,
#            total time, chunks found, answer artifact
# =============================================================

import os
import shutil
import time  # ← Phase 9: for timing

import mlflow  # ← Phase 9: experiment tracking
from dotenv import load_dotenv  # ← Phase 9: reads .env
from fastapi import APIRouter, File, HTTPException, UploadFile
from langchain_ollama import OllamaLLM  # ← Phase 9: direct LLM call
from pydantic import BaseModel

load_dotenv()

# =============================================================
# MLFLOW CONFIGURATION (Phase 9)
# =============================================================
# set_tracking_uri tells MLflow where to send data.
# Points to MLflow server running at localhost:5000.
# Start the server with: mlflow ui
#
# set_experiment groups all runs under one experiment name.
# Like a folder name — all /chat runs go here.
# View at: http://localhost:5000
# =============================================================

# Use local file tracking — saves to mlruns/ folder on disk
# No server needed — FastAPI starts without MLflow running
mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("healthcare-workforce-ai")

# APIRouter groups all routes together
# main.py imports this router and registers it with the app
router = APIRouter()


# =============================================================
# REQUEST AND RESPONSE MODELS
# =============================================================
# Pydantic models define the shape of data coming in and out.
# FastAPI uses these to automatically validate every request.
# If Streamlit sends wrong data — FastAPI returns 422 error.


class ChatRequest(BaseModel):
    # The question the user typed in Streamlit
    # Must be a non-empty string
    question: str


class ChatResponse(BaseModel):
    # The answer the LLM generated
    answer: str


class IngestResponse(BaseModel):
    # Confirmation message after file upload
    message: str


# =============================================================
# ROUTE 1: GET /health
# =============================================================
# SOURCE:      Docker, GitHub Actions, or your browser
# SENDS:       nothing
# RETURNS:     {"status": "ok"}
# PURPOSE:     confirms FastAPI is running correctly
# TEST IT:     open browser → http://localhost:8000/health
# NO CHANGE — MLflow not needed for health checks
# =============================================================


@router.get("/health")
def health_check():
    """
    Health check endpoint.
    Returns ok if the server is running.
    Used by Docker and CI/CD to verify deployment.
    """
    return {"status": "ok"}


# =============================================================
# ROUTE 2: POST /chat  ← UPDATED IN PHASE 9
# =============================================================
# SOURCE:      Streamlit UI (port 8501)
# SENDS:       {"question": "What is the annual leave?"}
# RETURNS:     {"answer": "Nurses get 30 days per TVöD-K..."}
# PURPOSE:     receives question, returns AI answer
# TEST IT:     http://localhost:8000/docs → POST /chat
#
# PHASE 9 ADDITION — MLflow tracking:
#   Every request opens a MLflow run (like pressing record).
#   Times retrieval and LLM separately so you can see
#   exactly where the slowness comes from.
#   Saves full answer, chunks, and prompt as artifacts.
# =============================================================


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Imports moved here — only load when /chat is called
    from src.rag.retriever import retrieve_chunks
    from src.rag.prompt import build_prompt

    start_time = time.time()

    # ── Phase 9: open MLflow run — everything inside recorded
    # with block automatically closes and saves run at the end
    with mlflow.start_run():

        # ── Phase 9: log what was asked and which model ──────
        # log_param = fixed values that describe this request
        mlflow.log_param("question", request.question[:250])
        mlflow.log_param("model", os.getenv("OLLAMA_MODEL", "llama3.2"))
        mlflow.log_param("embed_model", os.getenv("EMBED_MODEL", "nomic-embed-text"))
        # Tags are labels — help filter runs in dashboard
        mlflow.set_tag("environment", "development")
        mlflow.set_tag("route", "/chat")

        try:
            # ── Phase 9: time retrieval step separately ──────
            # This tells you: how long did ChromaDB search take?
            retrieval_start = time.time()
            chunks = retrieve_chunks(request.question)
            retrieval_time = round(time.time() - retrieval_start, 2)

            # log_metric = numbers you measured during the run
            mlflow.log_metric("retrieval_time_seconds", retrieval_time)
            mlflow.log_metric("chunks_retrieved", len(chunks))

            # ── Phase 9: build prompt ─────────────────────────
            # Same prompt.py from Phase 5 — no change
            prompt = build_prompt(chunks, request.question)

            # ── Phase 9: time LLM step separately ────────────
            # This tells you: how long did the LLM take?
            # Usually 80-95% of total time on laptop CPU
            llm_start = time.time()
            llm = OllamaLLM(
                model=os.getenv("OLLAMA_MODEL", "llama3.2"),
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            )
            answer = llm.invoke(prompt)
            llm_time = round(time.time() - llm_start, 2)

            mlflow.log_metric("llm_time_seconds", llm_time)

            # ── Phase 9: log total time ───────────────────────
            total_time = round(time.time() - start_time, 2)
            mlflow.log_metric("total_response_time_seconds", total_time)

            # ── Phase 9: save artifacts ───────────────────────
            # Artifacts = files saved alongside the run
            # Open any run in dashboard and download these files
            mlflow.log_text(answer, "answer.txt")
            mlflow.log_text("\n\n---\n\n".join(chunks), "retrieved_chunks.txt")
            mlflow.log_text(prompt, "prompt.txt")

            # ── Phase 9: mark this run as successful ──────────
            mlflow.set_tag("status", "success")

            # Print timing summary to FastAPI terminal
            print(
                f"MLflow logged | "
                f"retrieval={retrieval_time}s | "
                f"llm={llm_time}s | "
                f"total={total_time}s"
            )

            return ChatResponse(answer=answer)

        except Exception as e:
            # ── Phase 9: log errors to MLflow too ────────────
            # Failed runs appear in dashboard with status=error
            # Click the failed run to see error_message param
            mlflow.set_tag("status", "error")
            mlflow.log_param("error_message", str(e)[:250])
            total_time = round(time.time() - start_time, 2)
            mlflow.log_metric("total_response_time_seconds", total_time)
            raise HTTPException(
                status_code=500, detail=f"Error generating answer: {str(e)}"
            )


# =============================================================
# ROUTE 3: POST /ingest
# =============================================================
# SOURCE:      Streamlit sidebar file uploader
# SENDS:       a PDF file (binary data)
# RETURNS:     {"message": "file.pdf uploaded successfully"}
# PURPOSE:     adds new document to ChromaDB
# TEST IT:     http://localhost:8000/docs → POST /ingest
# NO CHANGE — MLflow not added here (ingestion is one-time)
# =============================================================


@router.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    """
    Document ingestion endpoint.
    Receives a PDF file uploaded from Streamlit sidebar.
    Saves it to data/documents/.
    Runs the ingestion pipeline to add it to ChromaDB.
    """

    # Imports moved here — only load when /ingest is called
    # Prevents ChromaDB loading at FastAPI startup
    from src.ingestion.loader import load_documents
    from src.ingestion.chunker import split_documents
    from src.ingestion.embedder import embed_and_store

    # Check it is a PDF file
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        save_path = f"./data/documents/{file.filename}"
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        documents = load_documents("./data/documents")
        chunks = split_documents(documents)
        embed_and_store(chunks)

        return IngestResponse(
            message=(f"{file.filename} uploaded and " f"ingested successfully")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting file: {str(e)}")
