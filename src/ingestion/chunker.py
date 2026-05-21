# =============================================================
# src/ingestion/chunker.py
# =============================================================
# PURPOSE:
#   Takes the list of Document objects from loader.py
#   and splits each page into smaller 500-word pieces
#   called chunks.
#
# WHY WE SPLIT:
#   A full PDF page is too large for precise searching.
#   Smaller chunks give the AI more accurate results.
#   The AI only reads the 4 most relevant chunks —
#   not the whole document.
#
# INPUT:  list of Document objects (from loader.py)
# OUTPUT: list of smaller Document objects (chunks)
#
# THIS FILE NEVER CHANGES when you switch data source.
# It does not care where the text came from.
# =============================================================

from langchain.text_splitter import RecursiveCharacterTextSplitter


def split_documents(documents: list) -> list:
    """
    Splits a list of Document objects into smaller chunks.

    Args:
        documents: list of Document objects from loader.py

    Returns:
        list of smaller Document objects (chunks)
    """

    if not documents:
        print("No documents to split.")
        return []

    # RecursiveCharacterTextSplitter splits text by trying
    # these separators in order: paragraph, line, sentence, word
    # It stops when the chunk is small enough
    splitter = RecursiveCharacterTextSplitter(
        # each chunk is maximum 500 characters
        chunk_size=500,
        # 50 characters are shared between neighbouring chunks
        # so context is not lost at the boundary
        chunk_overlap=50,
        # try splitting at these points in this order
        separators=["\n\n", "\n", ".", " "],
    )

    chunks = splitter.split_documents(documents)

    print(f"Split {len(documents)} pages into {len(chunks)} chunks")
    return chunks
