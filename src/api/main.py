# =============================================================
# src/api/main.py
# =============================================================
# PURPOSE:
#   Creates the FastAPI application.
#   Configures CORS so Streamlit can call it.
#   Registers all routes from routes.py.
#   This is the entry point — uvicorn runs this file.
#
# HOW TO RUN:
#   uvicorn src.api.main:app --reload --port 8000
#
# HOW TO TEST:
#   Open browser: http://localhost:8000/docs
#   This shows auto-generated interactive test page.
#
# WHAT IS CORS:
#   Streamlit runs on port 8501.
#   FastAPI runs on port 8000.
#   Browser blocks requests between different ports
#   unless FastAPI explicitly allows it.
#   CORSMiddleware tells the browser: allow port 8501.
# =============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router

# Create the FastAPI application
# title and description appear on the /docs page
app = FastAPI(
    title="Healthcare Workforce AI",
    description=(
        "RAG Agentic AI for Healthcare Workforce Management. "
        "German labour law compliant. "
        "Powered by LangChain + ChromaDB + Ollama."
    ),
    version="1.0.0",
)

# =============================================================
# CORS MIDDLEWARE
# =============================================================
# Allows Streamlit (port 8501) to send requests to
# FastAPI (port 8000) without the browser blocking them.
#
# allow_origins=["*"] means any origin is allowed.
# In production you would restrict this to your exact domain.
# Example: allow_origins=["https://your-hospital.com"]
# =============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes from routes.py
# All endpoints (/health, /chat, /ingest) become active here
app.include_router(router)


# =============================================================
# ROOT ROUTE
# =============================================================
# When someone opens http://localhost:8000 in browser
# they see this welcome message instead of an error.
# =============================================================


@app.get("/")
def root():
    """
    Root endpoint.
    Shows welcome message and links to documentation.
    """
    return {
        "message": "Healthcare Workforce AI is running",
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/health",
    }
