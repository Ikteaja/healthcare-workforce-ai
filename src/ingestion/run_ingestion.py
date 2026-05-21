# =============================================================
# src/ingestion/run_ingestion.py
# =============================================================
# PURPOSE:
#   Master script that runs the full ingestion pipeline.
#   Calls loader → chunker → embedder in the correct order.
#
# THIS IS THE ONLY FILE YOU RUN DIRECTLY.
# Never run loader.py, chunker.py, or embedder.py alone.
#
# HOW TO RUN:
#   python src/ingestion/run_ingestion.py
#
# WHEN TO RUN:
#   - Once at project setup
#   - When you add new PDFs to data/documents/
#   - When you update existing PDFs
#   - When you change the embedding model
#     (delete data/chroma_db/ first if changing model)
#
# WHAT IT DOES:
#   Step 1: loader.py   reads all PDFs → Document objects
#   Step 2: chunker.py  splits pages  → chunk objects
#   Step 3: embedder.py converts      → vectors + saves to ChromaDB
# =============================================================

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath("."))

from src.ingestion.loader import load_documents
from src.ingestion.chunker import split_documents
from src.ingestion.embedder import embed_and_store


def run_ingestion():
    """
    Runs the full ingestion pipeline end to end.
    """

    print("=" * 50)
    print("INGESTION PIPELINE STARTED")
    print("=" * 50)

    # ── Step 1: Load documents ──────────────────────────
    print("\nStep 1: Loading documents from data/documents/...")
    documents = load_documents("./data/documents")

    if not documents:
        print("No documents found. Add PDFs to data/documents/ and try again.")
        return

    # ── Step 2: Split into chunks ───────────────────────
    print("\nStep 2: Splitting documents into chunks...")
    chunks = split_documents(documents)

    if not chunks:
        print("No chunks created. Check your documents.")
        return

    # ── Step 3: Embed and store in ChromaDB ─────────────
    print("\nStep 3: Embedding chunks and saving to ChromaDB...")
    embed_and_store(chunks)

    # ── Done ────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("INGESTION COMPLETE")
    print(f"  Documents loaded: {len(documents)} pages")
    print(f"  Chunks created:   {len(chunks)}")
    print("  ChromaDB is ready for searching")
    print("=" * 50)


if __name__ == "__main__":
    run_ingestion()
