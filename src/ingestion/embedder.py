# =============================================================
# src/ingestion/embedder.py
# =============================================================
# PURPOSE:
#   Takes each text chunk from chunker.py, sends it to the
#   Ollama embedding model, gets back a list of numbers
#   (vector), and saves both the numbers AND the original
#   text into ChromaDB.
#
# THIS IS THE MOST IMPORTANT FILE in the ingestion pipeline.
# After this runs, ChromaDB is filled and the AI can search.
#
# TWO THINGS SAVED PER CHUNK:
#   vector:  [0.82, 0.14, 0.67, ...]  ← used for searching
#   text:    "Annual leave is 28..."   ← returned as result
#
# CRITICAL RULE:
#   The embedding model used here MUST be the same model
#   used in retriever.py when searching.
#   If you change the model → delete data/chroma_db/ first
#   and re-run this script.
#
# INPUT:  list of chunk Document objects (from chunker.py)
# OUTPUT: nothing returned — saves directly to ChromaDB
#
# THIS FILE NEVER CHANGES when you switch data source.
# =============================================================

import os
import chromadb
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv

load_dotenv()


def embed_and_store(chunks: list) -> None:
    """
    Converts each chunk to a vector and saves to ChromaDB.

    Args:
        chunks: list of Document objects from chunker.py

    Returns:
        None — saves directly to ChromaDB on disk
    """

    if not chunks:
        print("No chunks to embed.")
        return

    # Connect to ChromaDB
    # PersistentClient saves data to disk at CHROMA_PATH
    # If the folder does not exist, ChromaDB creates it
    chroma_path = os.getenv("CHROMA_PATH", "./data/chroma_db")
    client = chromadb.PersistentClient(path=chroma_path)

    # Get or create the collection
    # A collection is like a table in a normal database
    # All healthcare document chunks go into one collection
    collection = client.get_or_create_collection(
        name="healthcare_docs",
        metadata={"description": "Healthcare workforce documents"},
    )

    # Connect to the Ollama embedding model
    # This model converts text to numbers (vectors)
    # MUST be the same model used in retriever.py
    embeddings = OllamaEmbeddings(
        model=os.getenv("EMBED_MODEL", "nomic-embed-text"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )

    print(f"Embedding {len(chunks)} chunks into ChromaDB...")
    print("This may take a few minutes — each chunk is sent to Ollama...")

    # Process each chunk one by one
    success_count = 0
    error_count = 0

    for i, chunk in enumerate(chunks):

        try:
            # Convert chunk text to a vector (list of numbers)
            # This calls Ollama API at localhost:11434
            vector = embeddings.embed_query(chunk.page_content)

            # Create a unique ID for this chunk
            # Using index + source filename to ensure uniqueness
            source = chunk.metadata.get("source", "unknown")
            page = chunk.metadata.get("page", 0)
            chunk_id = f"chunk_{i}_{source}_{page}"

            # Save to ChromaDB — three things together:
            # 1. The unique ID
            # 2. The original text
            # 3. The vector (numbers)
            # 4. The metadata (source file, page number)
            collection.add(
                ids=[chunk_id],
                documents=[chunk.page_content],
                embeddings=[vector],
                metadatas=[
                    {
                        "source": source,
                        "page": str(page),
                        "chunk_index": str(i),
                    }
                ],
            )

            success_count += 1

            # Print progress every 10 chunks
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{len(chunks)} chunks done...")

        except Exception as e:
            print(f"  Failed on chunk {i}: {e}")
            error_count += 1

    print(f"\nEmbedding complete:")
    print(f"  Saved:  {success_count} chunks")
    print(f"  Failed: {error_count} chunks")
    print(f"  Location: {chroma_path}")
