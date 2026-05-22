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
# =============================================================

import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from src.rag.chain import answer_question
from src.ingestion.loader import load_documents
from src.ingestion.chunker import split_documents
from src.ingestion.embedder import embed_and_store

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
# ROUTE 2: POST /chat
# =============================================================
# SOURCE:      Streamlit UI (port 8501)
# SENDS:       {"question": "What is the annual leave?"}
# RETURNS:     {"answer": "Nurses get 30 days per TVöD-K..."}
# PURPOSE:     receives question, returns AI answer
# TEST IT:     http://localhost:8000/docs → POST /chat
# =============================================================


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Receives a question from Streamlit.
    Passes it to the RAG chain.
    Returns the AI generated answer.
    """

    # Validate question is not empty
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        # Call RAG chain — this is where the AI work happens
        # retriever finds chunks → prompt builds message
        # → LLM generates answer
        answer = answer_question(request.question)
        return ChatResponse(answer=answer)

    except Exception as e:
        # If something goes wrong — return clear error
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
# =============================================================


@router.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    """
    Document ingestion endpoint.
    Receives a PDF file uploaded from Streamlit sidebar.
    Saves it to data/documents/.
    Runs the ingestion pipeline to add it to ChromaDB.
    """

    # Check it is a PDF file
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        # Save the uploaded file to data/documents/
        save_path = f"./data/documents/{file.filename}"
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Run ingestion pipeline on just this new file
        documents = load_documents("./data/documents")
        chunks = split_documents(documents)
        embed_and_store(chunks)

        return IngestResponse(
            message=f"{file.filename} uploaded and ingested successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting file: {str(e)}")
