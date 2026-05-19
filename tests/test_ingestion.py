# =============================================================
# test_ingestion.py
# =============================================================
# Tests the chunking part of the ingestion pipeline.
# We do NOT need real PDF files to test this.
# We pass plain text directly and check the chunks come out right.
# =============================================================

from src.ingestion.chunker import split_documents
from langchain.schema import Document


def test_chunker_splits_long_text():
    """
    Test that a long document gets split into multiple chunks.
    We create a fake document with 1000 words and check
    that the chunker produces more than 1 chunk.
    """
    # Create a fake document (100 words repeated)
    fake_text = "This is a test sentence about healthcare policies. " * 100
    fake_doc = Document(page_content=fake_text, metadata={"source": "test.pdf"})

    # Run the chunker
    chunks = split_documents([fake_doc])

    # Check we got more than 1 chunk
    assert len(chunks) > 1, "Long text should produce multiple chunks"
    print(f"✅ Chunker produced {len(chunks)} chunks from long text")


def test_chunker_preserves_text():
    """
    Test that the chunker does not lose or change the text content.
    The combined chunks should contain all the original words.
    """
    fake_text = "Annual leave policy for nurses is twenty eight days per year."
    fake_doc = Document(page_content=fake_text, metadata={"source": "test.pdf"})

    chunks = split_documents([fake_doc])

    # Combine all chunk text
    combined = " ".join([c.page_content for c in chunks])

    # Check the key words are still there
    assert "Annual leave" in combined, "Text content should be preserved"
    assert "nurses" in combined, "Text content should be preserved"
    print("✅ Chunker preserved original text content")


def test_chunker_empty_document():
    """
    Test that the chunker handles an empty document without crashing.
    """
    fake_doc = Document(page_content="", metadata={"source": "empty.pdf"})
    chunks = split_documents([fake_doc])

    # Empty document should produce 0 chunks
    assert len(chunks) == 0, "Empty document should produce no chunks"
    print("✅ Chunker handled empty document correctly")