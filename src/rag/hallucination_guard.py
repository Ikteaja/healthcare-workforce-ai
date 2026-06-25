# =============================================================
# src/rag/hallucination_guard.py
# =============================================================
# PURPOSE:
#   Checks if the LLM answer is grounded in the source chunks.
#   If the answer has low overlap with retrieved chunks —
#   it may be hallucinated — return a fallback message instead.
#
# HOW IT WORKS:
#   Takes key words from the answer.
#   Checks how many appear in the retrieved chunks.
#   If overlap < threshold → hallucination likely → fallback.
#
# THRESHOLD:
#   0.15 = at least 15% of answer words must appear in chunks
#   Tune this up or down based on your documents.
# =============================================================

FALLBACK_MESSAGE = (
    "I could not find sufficient information in the hospital "
    "documents to answer this question confidently. "
    "Please consult your HR department or refer to the "
    "relevant policy document directly."
)

HALLUCINATION_THRESHOLD = 0.30
# Words shorter than this are ignored in the check
# "the", "is", "a" etc add noise — we only check real words
MIN_WORD_LENGTH = 4


def is_grounded(answer: str, chunks: list[str]) -> bool:
    """
    Returns True if answer appears grounded in chunks.
    Returns False if answer is likely hallucinated.
    """
    if not chunks or not answer:
        return True

    all_chunk_text = " ".join(chunks).lower()

    # Extract meaningful words from answer
    # Skip short common words — they appear everywhere
    answer_words = [
        word.lower().strip(".,;:?!()")
        for word in answer.split()
        if len(word) > MIN_WORD_LENGTH
    ]

    if not answer_words:
        return True

    # Skip words that are common nouns unlikely to indicate grounding
    # These appear in many contexts and should not count as evidence
    common_skip_words = {
        "nurses", "staff", "hospital", "patient", "doctor",
        "their", "that", "this", "with", "from", "have",
        "will", "been", "they", "were", "which", "also"
    }

    # Only check content-specific words
    content_words = [
        w for w in answer_words
        if w not in common_skip_words
    ]
    # If no content words remain — cannot verify — assume grounded
    if not content_words:
        return True
    # Count matches
    matched = sum(
        1 for word in content_words
        if word in all_chunk_text
    )
    overlap = matched / len(content_words)
    print(
        f"Hallucination check: "
        f"{matched}/{len(content_words)} content words matched "
        f"({overlap:.0%}) — "
        f"{'GROUNDED' if overlap >= HALLUCINATION_THRESHOLD else 'FALLBACK'}"
    )
    return overlap >= HALLUCINATION_THRESHOLD


def check_and_guard(answer: str, chunks: list[str]) -> str:
    """
    Returns the original answer if grounded,
    or FALLBACK_MESSAGE if hallucination detected.
    """
    if is_grounded(answer, chunks):
        return answer
    return FALLBACK_MESSAGE
