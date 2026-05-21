# =============================================================
# src/rag/chain.py
# =============================================================
# PURPOSE:
#   Connects all three RAG steps into one function.
#   Give it a question, get back an answer.
#
# FLOW:
#   question
#     -> retriever.py  search ChromaDB for chunks
#     -> prompt.py     build prompt from chunks + question
#     -> Ollama LLM    read prompt, write answer
#     -> answer returned
#
# FastAPI will call answer_question() in Phase 7.
# =============================================================

import os
from langchain_ollama import OllamaLLM
from src.rag.retriever import retrieve_chunks
from src.rag.prompt import build_prompt
from dotenv import load_dotenv

load_dotenv()

# Connect to Ollama LLM
llm = OllamaLLM(
    model=os.getenv("OLLAMA_MODEL", "llama3.2"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
)


def answer_question(question: str) -> str:
    """
    Takes a question, searches documents, returns an answer.

    Args:
        question: the user question string

    Returns:
        answer string from the LLM
    """

    print(f"\nQuestion: {question}")
    print("-" * 40)

    # Step 1 - retrieve relevant chunks
    chunks = retrieve_chunks(question)

    # Step 2 - build the prompt
    prompt = build_prompt(chunks, question)

    # Step 3 - send to LLM and get answer
    print("Sending to LLM...")
    answer = llm.invoke(prompt)

    return answer
