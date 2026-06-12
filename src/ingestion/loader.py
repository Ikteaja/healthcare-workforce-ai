# =============================================================
# src/ingestion/loader.py
# =============================================================
# PURPOSE:
#   Reads every PDF file from data/documents/ folder
#   and returns the raw text as Document objects.
#
# INPUT:  folder path string  e.g. "./data/documents"
# OUTPUT: list of LangChain Document objects
#
# Each Document contains:
#   page_content: text of one page
#   metadata:     source filename + page number
#
# TO SWITCH DATA SOURCE (AWS S3 / Azure / SharePoint):
#   Only change this file — chunker and embedder stay the same.
#   See src/ingestion/README.md for full examples.
# =============================================================
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


def load_documents(folder_path: str) -> list:
    """
    Reads all PDF files from the given folder.
    Returns a list of Document objects.

    Args:
        folder_path: path to folder containing PDF files

    Returns:
        list of LangChain Document objects
    """
    documents = []
    folder = Path(folder_path)

    # Check folder exists
    if not folder.exists():
        print(f"Folder not found: {folder_path}")
        return []

    # Find all PDF files
    pdf_files = list(folder.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {folder_path}")
        return []

    print(f"Found {len(pdf_files)} PDF files...")

    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf_file))
            pages = loader.load()
            documents.extend(pages)
            print(f"  Loaded: {pdf_file.name} ({len(pages)} pages)")

        except Exception as e:
            print(f"  Failed to load {pdf_file.name}: {e}")

    print(f"\nTotal pages loaded: {len(documents)}")
    return documents
