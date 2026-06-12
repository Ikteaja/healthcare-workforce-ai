# =============================================================
# src/rag/prompt.py
# =============================================================
# PURPOSE:
#   Builds the final message sent to the LLM.
#   Combines retrieved chunks + user question.
#
# WHY "USE ONLY CONTEXT BELOW":
#   Stops LLM making up answers not in your documents.
#   Forces answers based only on your healthcare policies.
# =============================================================

from langchain.prompts import PromptTemplate

RAG_PROMPT_TEMPLATE = """You are a helpful healthcare workforce \
management assistant for a German hospital.

You help with questions about:
- HR policies and leave entitlements
- Staff schedules and shift assignments
- German labour law (AZG, TVoeD-K, DSGVO)
- Role descriptions and qualifications
- Emergency protocols

Use ONLY the information in the context below.
If the answer is not there, say:
"I don't have that information in my documents."
Never guess. Always mention the source document.

Context:
{context}

Question: {question}

Answer:"""

RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=RAG_PROMPT_TEMPLATE,
)


def build_prompt(chunks: list, question: str) -> str:
    """
    Combines chunks and question into a prompt for the LLM.

    Args:
        chunks:   list of text strings from retriever.py
        question: the user question string

    Returns:
        formatted prompt string ready to send to LLM
    """

    if not chunks:
        context = "No relevant information found in documents."
    else:
        context = "\n\n---\n\n".join(chunks)

    return RAG_PROMPT.format(
        context=context,
        question=question,
    )
