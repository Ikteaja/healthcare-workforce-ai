# =============================================================
# src/agents/tools/policy_tool.py
# =============================================================
# PURPOSE:
#   A LangChain tool that searches ChromaDB for answers
#   about HR policies, leave rules, onboarding, and conduct.
#
# HOW IT WORKS:
#   Wraps chain.py from Phase 5.
#   Agent calls this when question is about HR policy.
#   Tool calls answer_question() which searches ChromaDB.
#
# CALLED BY: orchestrator.py when agent picks this tool
# CALLS:     src/rag/chain.py answer_question()
# SEARCHES:  ChromaDB — all document chunks
# =============================================================

from langchain.tools import tool
from src.rag.chain import answer_question


@tool
def policy_tool(question: str) -> str:
    """
    Use this tool for questions about:
    - Annual leave and holiday entitlements
    - Sick leave rules and procedures
    - Staff onboarding and probation
    - Conduct and disciplinary rules
    - Working hours and AZG regulations
    - TVoeD-K collective agreement questions
    - Staff HR policies and guidelines
    - Termination and notice periods

    Input: the HR policy question as a string
    Output: answer based on hospital HR documents
    """
    return answer_question(question)
