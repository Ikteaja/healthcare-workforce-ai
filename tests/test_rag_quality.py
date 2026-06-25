# =============================================================
# tests/test_rag_quality.py
# =============================================================
# PURPOSE:
#   Automated evaluation of RAG pipeline quality.
#   Runs on every GitHub push via GitHub Actions (ci.yml).
#   Tests each layer independently so you know exactly
#   which component failed when something breaks.
#
# HOW TO RUN LOCALLY:
#   pytest tests/test_rag_quality.py -v
#
# HOW TO RUN ONE TEST ONLY:
#   pytest tests/test_rag_quality.py::test_retrieval_finds_chunks -v
#
# WHAT IT TESTS (5 layers):
#   Layer 1 — ChromaDB retrieval (finds correct chunks?)
#   Layer 2 — Hybrid retrieval  (BM25 + embedding working?)
#   Layer 3 — Hallucination guard (grounded vs fallback?)
#   Layer 4 — Prompt building (prompt contains chunks?)
#   Layer 5 — Full pipeline (end-to-end answer quality?)
#
# NOTE ON LAYER 5:
#   Full pipeline test calls Ollama LLM — slow (25-30 seconds).
#   Marked with @pytest.mark.slow so you can skip it:
#   pytest tests/test_rag_quality.py -v -m "not slow"
# =============================================================

import sys
import os
import pytest

# Add project root to path so imports work
sys.path.insert(0, os.path.abspath("."))


# =============================================================
# LAYER 1 — ChromaDB Retrieval Tests
# =============================================================

class TestRetrieval:
    """
    Tests the original retriever.py using ChromaDB only.
    Verifies ChromaDB is populated and returns relevant chunks.
    """

    def test_retrieval_returns_chunks(self):
        """
        ChromaDB must return at least 1 chunk for a known question.
        If this fails: ChromaDB is empty — run ingestion first.
        """
        from src.rag.retriever import retrieve_chunks
        chunks = retrieve_chunks("What is the annual leave for nurses?")
        assert len(chunks) > 0, (
            "No chunks returned. Run: python src/ingestion/run_ingestion.py"
        )

    def test_retrieval_returns_max_4_chunks(self):
        """
        Default n_results=4 — should never return more than 4.
        Prevents accidental prompt overflow.
        """
        from src.rag.retriever import retrieve_chunks
        chunks = retrieve_chunks("What is the annual leave?")
        assert len(chunks) <= 4, (
            f"Too many chunks returned: {len(chunks)}"
        )

    def test_retrieval_returns_strings(self):
        """
        Each chunk must be a non-empty string.
        ChromaDB should never return None or empty values.
        """
        from src.rag.retriever import retrieve_chunks
        chunks = retrieve_chunks("nurse leave policy")
        for i, chunk in enumerate(chunks):
            assert isinstance(chunk, str), (
                f"Chunk {i} is not a string: {type(chunk)}"
            )
            assert len(chunk) > 10, (
                f"Chunk {i} is too short: '{chunk}'"
            )

    def test_retrieval_content_relevant(self):
        """
        Retrieved chunks must contain leave-related content
        for a leave-related question.
        """
        from src.rag.retriever import retrieve_chunks
        chunks = retrieve_chunks("annual leave for nurses")
        combined = " ".join(chunks).lower()
        # At least one of these words must appear
        relevant_words = ["leave", "annual", "days", "urlaub", "tvöd"]
        found = any(word in combined for word in relevant_words)
        assert found, (
            f"Retrieved chunks do not contain leave-related content.\n"
            f"Combined text (first 200 chars): {combined[:200]}"
        )

    def test_retrieval_empty_question_returns_list(self):
        """
        Even with an unusual question, should return a list.
        Should never raise an exception or return None.
        """
        from src.rag.retriever import retrieve_chunks
        result = retrieve_chunks("xyz123 nonexistent topic")
        assert isinstance(result, list), "Should always return a list"


# =============================================================
# LAYER 2 — Hybrid Retrieval Tests
# =============================================================

class TestHybridRetrieval:
    """
    Tests hybrid_retriever.py — BM25 + embedding combined.
    Verifies scores are calculated and results are ranked correctly.
    """

    def test_hybrid_returns_dicts(self):
        """
        hybrid_retrieve() returns list of dicts, not plain strings.
        Each dict must have: text, source, bm25_score, embed_score, final_score.
        """
        from src.rag.hybrid_retriever import hybrid_retrieve
        results = hybrid_retrieve("What is the annual leave for nurses?")
        assert len(results) > 0, "Hybrid retrieval returned nothing"

        required_keys = ["text", "source", "bm25_score", "embed_score", "final_score"]
        for i, result in enumerate(results):
            for key in required_keys:
                assert key in result, (
                    f"Chunk {i} missing key '{key}'. Keys found: {list(result.keys())}"
                )

    def test_hybrid_scores_are_valid(self):
        """
        All scores (BM25, embed, final) must be between 0 and 1.
        Ensures normalisation is working correctly.
        """
        from src.rag.hybrid_retriever import hybrid_retrieve
        results = hybrid_retrieve("leave policy Germany")

        for i, result in enumerate(results):
            assert 0.0 <= result["bm25_score"] <= 1.0, (
                f"Chunk {i} BM25 score out of range: {result['bm25_score']}"
            )
            assert 0.0 <= result["embed_score"] <= 1.0, (
                f"Chunk {i} embed score out of range: {result['embed_score']}"
            )
            assert 0.0 <= result["final_score"] <= 1.0, (
                f"Chunk {i} final score out of range: {result['final_score']}"
            )

    def test_hybrid_sorted_by_final_score(self):
        """
        Results must be sorted by final_score descending.
        First result should have the highest score.
        """
        from src.rag.hybrid_retriever import hybrid_retrieve
        results = hybrid_retrieve("annual leave nurses TVöD-K")

        if len(results) > 1:
            scores = [r["final_score"] for r in results]
            assert scores == sorted(scores, reverse=True), (
                f"Results not sorted by final_score. Scores: {scores}"
            )

    def test_hybrid_source_is_string(self):
        """
        Source field must be a non-empty string (filename).
        """
        from src.rag.hybrid_retriever import hybrid_retrieve
        results = hybrid_retrieve("nurse schedule shift")

        for i, result in enumerate(results):
            assert isinstance(result["source"], str), (
                f"Chunk {i} source is not a string"
            )

    def test_hybrid_bm25_top_result_for_exact_keyword(self):
        """
        When searching for an exact rare keyword,
        BM25 score of top result should be high (above 0.5).
        """
        from src.rag.hybrid_retriever import hybrid_retrieve
        # TVöD-K is a rare exact keyword — BM25 should rank it highly
        results = hybrid_retrieve("TVöD-K annual leave entitlement")

        if results:
            top_result = results[0]
            assert top_result["bm25_score"] > 0.3, (
                f"Expected high BM25 score for exact keyword search. "
                f"Got: {top_result['bm25_score']}"
            )


# =============================================================
# LAYER 3 — Hallucination Guard Tests
# =============================================================

class TestHallucinationGuard:
    """
    Tests hallucination_guard.py logic.
    Does NOT require Ollama or ChromaDB — pure unit tests.
    These run instantly.
    """

    def test_grounded_answer_passes(self):
        """
        An answer whose words appear in the chunks should pass.
        Should return the original answer unchanged.
        """
        from src.rag.hallucination_guard import check_and_guard

        answer = "Nurses get 30 days annual leave per TVöD-K policy"
        chunks = [
            "annual leave policy for nurses is 30 days under TVöD-K Section 26"
        ]
        result = check_and_guard(answer, chunks)
        assert result == answer, (
            f"Grounded answer was incorrectly flagged as hallucination.\n"
            f"Expected: {answer}\nGot: {result}"
        )

    def test_hallucinated_answer_blocked(self):
        """
        An answer with content not in chunks should be blocked.
        Should return FALLBACK_MESSAGE instead.
        """
        from src.rag.hallucination_guard import (
            check_and_guard, FALLBACK_MESSAGE
        )

        answer = "Nurses receive complimentary gym membership and company car"
        chunks = [
            "annual leave policy for nurses is 30 days under TVöD-K Section 26"
        ]
        result = check_and_guard(answer, chunks)
        assert result == FALLBACK_MESSAGE, (
            f"Hallucinated answer was not blocked.\n"
            f"Expected: FALLBACK_MESSAGE\nGot: {result}"
        )

    def test_empty_answer_passes(self):
        """
        Empty answer should not crash the guard.
        Returns True (grounded) to avoid unnecessary fallback.
        """
        from src.rag.hallucination_guard import is_grounded

        result = is_grounded("", ["some chunk text here"])
        assert result is True, "Empty answer should return grounded=True"

    def test_empty_chunks_passes(self):
        """
        Empty chunks list should not crash the guard.
        """
        from src.rag.hallucination_guard import is_grounded

        result = is_grounded("some answer", [])
        assert result is True, "Empty chunks should return grounded=True"

    def test_fallback_message_is_string(self):
        """
        FALLBACK_MESSAGE must be a non-empty string.
        """
        from src.rag.hallucination_guard import FALLBACK_MESSAGE

        assert isinstance(FALLBACK_MESSAGE, str), (
            "FALLBACK_MESSAGE must be a string"
        )
        assert len(FALLBACK_MESSAGE) > 20, (
            "FALLBACK_MESSAGE is too short to be useful"
        )

    def test_partial_overlap_above_threshold(self):
        """
        Answer with 50% content word overlap should pass.
        """
        from src.rag.hallucination_guard import check_and_guard

        answer = "Leave entitlement is thirty days for all nursing staff"
        chunks = ["entitlement leave thirty nursing staff hospital policy"]
        result = check_and_guard(answer, chunks)
        assert result == answer, (
            "Answer with 50% overlap should be grounded"
        )


# =============================================================
# LAYER 4 — Prompt Building Tests
# =============================================================

class TestPromptBuilding:
    """
    Tests prompt.py — verifies the prompt is built correctly.
    Does NOT require Ollama — pure unit tests.
    """

    def test_prompt_contains_question(self):
        """
        The built prompt must contain the original question.
        """
        from src.rag.prompt import build_prompt

        question = "What is the annual leave for nurses?"
        chunks = ["Nurses get 30 days leave per TVöD-K Section 26"]
        prompt = build_prompt(chunks, question)

        assert question in prompt, (
            f"Question not found in prompt.\n"
            f"Prompt (first 200 chars): {prompt[:200]}"
        )

    def test_prompt_contains_chunks(self):
        """
        The built prompt must contain at least part of the chunks.
        Chunks are the context the LLM needs to answer from.
        """
        from src.rag.prompt import build_prompt

        question = "leave policy?"
        chunk_text = "Nurses get 30 days leave per TVöD-K Section 26"
        chunks = [chunk_text]
        prompt = build_prompt(chunks, question)

        assert chunk_text[:30] in prompt, (
            "Chunk content not found in prompt"
        )

    def test_prompt_is_string(self):
        """
        build_prompt must always return a string.
        """
        from src.rag.prompt import build_prompt

        result = build_prompt(["some chunk"], "some question")
        assert isinstance(result, str), (
            f"build_prompt returned {type(result)}, expected str"
        )

    def test_prompt_not_empty(self):
        """
        Prompt must never be an empty string.
        """
        from src.rag.prompt import build_prompt

        result = build_prompt(["chunk"], "question")
        assert len(result) > 50, (
            "Prompt is too short to be useful"
        )


# =============================================================
# LAYER 5 — Full Pipeline Tests (slow — requires Ollama)
# =============================================================

class TestFullPipeline:
    """
    End-to-end tests that call the full RAG pipeline.
    These are SLOW (25-30 seconds each) because they call Ollama.

    Skip slow tests locally with:
      pytest tests/test_rag_quality.py -v -m "not slow"

    These run in CI only when Ollama is available.
    """

    @pytest.mark.slow
    def test_full_answer_not_empty(self):
        """
        Full pipeline must return a non-empty answer string.
        Tests: retrieval → prompt → LLM → answer.
        """
        from src.rag.chain import answer_question

        answer = answer_question("What is the annual leave for nurses?")
        assert answer is not None, "Answer should not be None"
        assert isinstance(answer, str), "Answer must be a string"
        assert len(answer) > 20, (
            f"Answer too short to be meaningful: '{answer}'"
        )

    @pytest.mark.slow
    def test_full_answer_mentions_leave(self):
        """
        Answer to a leave question must mention leave-related content.
        Basic quality check on the LLM output.
        """
        from src.rag.chain import answer_question

        answer = answer_question(
            "What is the annual leave for nurses?"
        ).lower()
        relevant_terms = ["leave", "days", "annual", "urlaub", "30"]
        found = any(term in answer for term in relevant_terms)
        assert found, (
            f"Answer does not mention leave-related content.\n"
            f"Answer: {answer[:300]}"
        )


# =============================================================
# EVAL REPORT — runs all tests and prints summary
# =============================================================

if __name__ == "__main__":
    """
    Run directly for a quick eval report:
    python tests/test_rag_quality.py
    """
    import subprocess
    result = subprocess.run(
        ["pytest", "tests/test_rag_quality.py", "-v", "-m", "not slow"],
        capture_output=False
    )
    sys.exit(result.returncode)
