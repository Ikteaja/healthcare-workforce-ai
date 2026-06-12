# =============================================================
# src/rag/retriever.py
# =============================================================
#
# WHAT IT DOES:
#   Searches ChromaDB and finds the most relevant document
#   chunks for a given user question.
#
# SIMPLE ANALOGY:
#   Think of a librarian. You ask "what is nurse leave policy?"
#   The librarian searches all 47 document pieces and brings
#   back the 4 most relevant ones for you to read.
#
# HOW IT WORKS STEP BY STEP:
#   1. User types a question
#   2. Question is converted to numbers (same embedding model
#      used during ingestion — MUST be identical)
#   3. Those numbers are compared against all 47 vectors
#      stored in ChromaDB
#   4. ChromaDB finds the 4 closest matches
#   5. Returns the original TEXT of those 4 chunks
#      (not the numbers — numbers were only for searching)
#
# CRITICAL RULE:
#   The embedding model here MUST match embedder.py.
#   Both use: nomic-embed-text via Ollama port 11434
#   If they differ, search results will be wrong.
#
# INPUT:  question string   e.g. "What is nurse leave policy?"
# OUTPUT: list of 4 text strings — the most relevant chunks
#
# CONNECTS TO:
#   - ChromaDB (data/chroma_db/) to search vectors
#   - Ollama (port 11434) to embed the question
#   - prompt.py receives the returned chunks
# =============================================================

import sys
from unittest.mock import MagicMock

# Patch onnxruntime before ChromaDB loads
sys.modules["onnxruntime"] = MagicMock()
sys.modules["onnxruntime.capi"] = MagicMock()
sys.modules["onnxruntime.capi._pybind_state"] = MagicMock()

import os
import chromadb
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv

# Load values from .env file
# CHROMA_PATH, EMBED_MODEL, OLLAMA_BASE_URL
load_dotenv()


def retrieve_chunks(query: str, n_results: int = 4) -> list:
    """
    Searches ChromaDB for the most relevant chunks.

    WHY n_results=4?
        4 chunks gives the LLM enough context to answer
        accurately without overloading the prompt.
        More chunks = slower + less focused answers.

    Args:
        query:     the user's question as a plain string
        n_results: number of chunks to return (default 4)

    Returns:
        list of strings — text content of matching chunks
        empty list if ChromaDB is empty or not found
    """

    # ── Step 1: Connect to ChromaDB ──────────────────────────
    # PersistentClient reads from the folder on disk
    # This is the same folder embedder.py wrote to
    chroma_path = os.getenv("CHROMA_PATH", "./data/chroma_db")
    client = chromadb.PersistentClient(path=chroma_path)

    # ── Step 2: Get the collection ───────────────────────────
    # Collection = a named group of vectors (like a table)
    # "healthcare_docs" was the name used in embedder.py
    # If it does not exist, ingestion has not been run yet
    try:
        # embedding_function=None tells ChromaDB we provide
        # our own embeddings — do NOT load onnxruntime default
        collection = client.get_collection(
            name="healthcare_docs", embedding_function=None
        )
    except Exception:
        print("ChromaDB collection not found.")
        print("Run ingestion first:")
        print("  python src/ingestion/run_ingestion.py")
        return []

    # ── Step 3: Check collection has data ────────────────────
    if collection.count() == 0:
        print("ChromaDB is empty. Run ingestion first.")
        return []

    # ── Step 4: Embed the question ───────────────────────────
    # Convert question text → numbers (vector)
    # MUST use the same model as embedder.py
    # Because: if you use different models, the numbers
    # will not be comparable and search will give wrong results
    embeddings = OllamaEmbeddings(
        model=os.getenv("EMBED_MODEL", "nomic-embed-text"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )

    # This sends the question to Ollama and gets back
    # a list of ~768 numbers representing the question meaning
    query_vector = embeddings.embed_query(query)

    # ── Step 5: Search ChromaDB ──────────────────────────────
    # Compare query_vector against all 47 stored vectors
    # ChromaDB calculates the distance between each vector
    # Lower distance = more similar = more relevant
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results,
        # include all three so we can show useful debug info
        include=["documents", "metadatas", "distances"],
    )

    # ── Step 6: Extract results ──────────────────────────────
    # results["documents"][0] = list of chunk texts
    # results["metadatas"][0]  = list of source info per chunk
    # results["distances"][0]  = list of similarity scores
    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    # ── Step 7: Print what was found ─────────────────────────
    # This helps you see which documents the AI is reading
    # Similarity: 100% = identical, 0% = completely different
    print(f"Found {len(chunks)} relevant chunks:")
    for i, (chunk, meta, dist) in enumerate(zip(chunks, metadatas, distances)):
        source = meta.get("source", "unknown")
        page = meta.get("page", "?")
        # Convert distance to percentage similarity
        # ChromaDB uses cosine distance: 0=identical, 2=opposite
        similarity = round((1 - dist) * 100, 1)
        print(
            f"  Chunk {i + 1}: {source} " f"page {page} " f"(similarity: {similarity}%)"
        )
    # ── Step 8: Return only the text ─────────────────────────
    # We return just the text strings, not vectors or metadata
    # The text is what gets passed to prompt.py
    return chunks
