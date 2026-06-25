# =============================================================
# src/rag/hybrid_retriever.py
# =============================================================
#
# WHAT IT DOES:
#   Improved version of retriever.py.
#   Uses TWO search methods combined:
#
#   Method 1 — BM25 (keyword search)
#     Finds chunks containing the exact words in the question.
#     Good for: specific terms like "TVöD-K", "Urlaubsgeld"
#
#   Method 2 — Embedding search (semantic search)
#     Finds chunks with similar MEANING, not just same words.
#     Good for: "annual leave" finding "Urlaubsanspruch"
#
#   Final score = 50% BM25 + 50% Embedding
#   Returns top 4 chunks sorted by combined score.
#
# WHY BETTER THAN retriever.py:
#   retriever.py uses embeddings only.
#   hybrid uses both → catches more relevant chunks.
#
# CONNECTS TO:
#   - ChromaDB (data/chroma_db/) to search vectors
#   - Ollama (port 11434) to embed the question
#   - rank_bm25 library for keyword scoring
#   - routes.py calls hybrid_retrieve() instead of retrieve_chunks()
#
# INSTALL:
#   pip install rank-bm25
# =============================================================

import sys
from unittest.mock import MagicMock

# Patch onnxruntime before ChromaDB loads (same fix as retriever.py)
sys.modules["onnxruntime"] = MagicMock()
sys.modules["onnxruntime.capi"] = MagicMock()
sys.modules["onnxruntime.capi._pybind_state"] = MagicMock()

import os  # noqa: E402
import chromadb  # noqa: E402
from rank_bm25 import BM25Okapi  # noqa: E402
from langchain_ollama import OllamaEmbeddings  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

load_dotenv()


def hybrid_retrieve(query: str, n_results: int = 4) -> list[dict]:
    """
    Retrieves chunks using BM25 + embedding similarity combined.

    Args:
        query:     user question as plain string
        n_results: number of chunks to return (default 4)

    Returns:
        list of dicts — each dict has:
          "text"        → the chunk text (same as retriever.py)
          "source"      → filename e.g. hr_policy_germany.pdf
          "page"        → page number
          "bm25_score"  → keyword match score (0-1)
          "embed_score" → semantic similarity score (0-1)
          "final_score" → combined score (0-1)
    """

    # ── Step 1: Connect to ChromaDB ──────────────────────────
    chroma_path = os.getenv("CHROMA_PATH", "./data/chroma_db")
    client = chromadb.PersistentClient(path=chroma_path)

    try:
        collection = client.get_collection(
            name="healthcare_docs",
            embedding_function=None
        )
    except Exception:
        print("ChromaDB collection not found.")
        print("Run ingestion first:")
        print("  python src/ingestion/run_ingestion.py")
        return []

    if collection.count() == 0:
        print("ChromaDB is empty. Run ingestion first.")
        return []

    # ── Step 2: Get ALL chunks from ChromaDB ─────────────────
    # We need all chunks to run BM25 across the full set
    # (BM25 scores every document, not just top N)
    all_data = collection.get(
        include=["documents", "metadatas"]
    )
    all_texts = all_data["documents"]
    all_metadatas = all_data["metadatas"]

    if not all_texts:
        return []

    # ── Step 3: BM25 keyword scoring ─────────────────────────
    # Split each chunk into words for BM25
    # BM25 gives higher scores to chunks with more
    # query words and rarer words (like TF-IDF)
    tokenized_corpus = [
        doc.lower().split() for doc in all_texts
    ]
    bm25 = BM25Okapi(tokenized_corpus)
    query_tokens = query.lower().split()
    bm25_scores = bm25.get_scores(query_tokens)

    # Normalise BM25 scores to 0-1 range
    # (BM25 scores have no fixed range — normalise for combining)
    bm25_max = max(bm25_scores) if max(bm25_scores) > 0 else 1
    bm25_norm = [float(s) / bm25_max for s in bm25_scores]

    # ── Step 4: Embedding semantic scoring ───────────────────
    # Convert question to vector using same model as ingestion
    embeddings = OllamaEmbeddings(
        model=os.getenv("EMBED_MODEL", "nomic-embed-text"),
        base_url=os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        ),
    )
    query_vector = embeddings.embed_query(query)

    # Query ChromaDB for ALL chunks sorted by embedding distance
    embed_results = collection.query(
        query_embeddings=[query_vector],
        n_results=len(all_texts),  # get all, we rerank ourselves
        include=["documents", "distances", "metadatas"]
    )

    result_docs = embed_results["documents"][0]
    distances = embed_results["distances"][0]

    # Convert distances to similarity scores (0-1)
    # ChromaDB returns cosine distance: 0=identical, 2=opposite
    # So similarity = 1 - (distance / max_distance)
    max_dist = max(distances) if distances else 1
    embed_scores_list = [1 - (d / max_dist) for d in distances]

    # Build lookup: chunk text → embedding score
    embed_score_map = {
        doc: score
        for doc, score in zip(result_docs, embed_scores_list)
    }

    # ── Step 5: Combine BM25 + Embedding scores ───────────────
    # Equal weighting: 50% BM25 + 50% Embedding
    # Can tune: 0.3 BM25 + 0.7 Embed for more semantic focus
    combined = []
    for i, text in enumerate(all_texts):
        embed_score = embed_score_map.get(text, 0.0)
        bm25_score = bm25_norm[i]
        final_score = (0.5 * bm25_score) + (0.5 * embed_score)

        meta = all_metadatas[i] if all_metadatas else {}

        combined.append({
            "text": text,
            "source": meta.get("source", "unknown"),
            "page": meta.get("page", "?"),
            "bm25_score": round(bm25_score, 3),
            "embed_score": round(embed_score, 3),
            "final_score": round(final_score, 3),
        })

    # ── Step 6: Sort by final score, return top N ─────────────
    combined.sort(key=lambda x: x["final_score"], reverse=True)
    top_chunks = combined[:n_results]

    # ── Step 7: Print what was found ──────────────────────────
    print(f"Hybrid retrieval — found {len(top_chunks)} chunks:")
    for i, c in enumerate(top_chunks):
        print(
            f"  Chunk {i+1}: {c['source']} page {c['page']} "
            f"| BM25={c['bm25_score']} "
            f"| Embed={c['embed_score']} "
            f"| Final={c['final_score']}"
        )

    return top_chunks
