# =============================================================
# src/agents/tools/compliance_tool.py
# =============================================================
# PURPOSE:
#   A LangChain tool that searches ChromaDB specifically
#   for compliance and regulatory information.
#
# HOW IT WORKS:
#   Same as policy_tool but with a compliance-focused
#   question prefix to get more relevant results.
#
# CALLED BY: orchestrator.py when agent picks this tool
# SEARCHES:  ChromaDB — compliance document chunks
# =============================================================

from langchain.tools import tool
from src.rag.chain import answer_question


@tool
def compliance_tool(question: str) -> str:
    """
    Use this tool for questions about:
    - DSGVO and data protection rules
    - Patient rights and confidentiality
    - HIPAA compliance requirements
    - Infection control and IfSG regulations
    - Occupational health and safety (ArbSchG)
    - Vaccination requirements for staff
    - Mandatory reporting obligations
    - Quality management requirements
    - IT security and data breach procedures

    Input: the compliance or regulatory question
    Output: answer based on compliance documents
    """

    # Add compliance context to the question
    # to help the retriever find compliance-specific chunks
    compliance_question = f"compliance regulation law: {question}"
    return answer_question(compliance_question)
