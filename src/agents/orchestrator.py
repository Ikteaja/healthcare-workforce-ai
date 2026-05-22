# =============================================================
# src/agents/orchestrator.py
# =============================================================
# PURPOSE:
#   The brain of the system. Receives a question, decides
#   which tool to use, calls it, and returns the answer.
#
# HOW IT WORKS — ReAct pattern:
#   1. Receives user question
#   2. Reads tool descriptions
#   3. Reasons: which tool has this answer?
#   4. Acts: calls that tool
#   5. Reads result
#   6. Returns final answer
#
# CALLED BY: src/api/routes.py in Phase 7
# CALLS:     policy_tool, schedule_tool, compliance_tool
# USES:      LangChain ReAct agent + Ollama LLM
# =============================================================
import os
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from src.agents.tools.policy_tool import policy_tool
from src.agents.tools.schedule_tool import schedule_tool
from src.agents.tools.compliance_tool import compliance_tool
from dotenv import load_dotenv

load_dotenv()
# The LLM that drives the agent decisions
llm = OllamaLLM(
    model=os.getenv("OLLAMA_MODEL", "llama3.2"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
)
# All tools the agent can use
tools = [policy_tool, schedule_tool, compliance_tool]

# ReAct prompt template — tells agent how to think and act
AGENT_PROMPT = PromptTemplate.from_template(
    """You are a healthcare workforce management AI assistant
for a German hospital.

IMPORTANT RULES:
- Always pass questions to tools in ENGLISH only
- Never translate questions to German before using a tool
- Use the exact question wording as given
- Always use a tool — never answer from your own memory
- Once you have a clear answer — STOP and write Final Answer immediately
- NEVER call the same tool twice with the same input
- If a tool gives you an answer — use it immediately as Final Answer

You have access to these tools:
{tools}

Use this EXACT format — no variations:
Question: the question you must answer
Thought: which tool should I use?
Action: tool name (one of [{tool_names}])
Action Input: the question in ENGLISH
Observation: the result from the tool
Final Answer: the complete answer

STOP after writing Final Answer. Do not call any more tools.

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
)
# Create the ReAct agent
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=AGENT_PROMPT,
)
# AgentExecutor runs the agent loop
# max_iterations prevents infinite loops
# handle_parsing_errors prevents crashes on bad LLM output
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True,
)


def run_agent(question: str) -> str:
    """
    Runs the agent with the given question.
    Returns the final answer as a string.
    Args:
        question: the user question string
    Returns:
        answer string from the agent
    """
    try:
        result = executor.invoke({"input": question})
        return result.get("output", "No answer generated.")
    except Exception as e:
        # Fallback to direct RAG if agent fails
        print(f"Agent error: {e}")
        print("Falling back to direct RAG...")
        from src.rag.chain import answer_question
        return answer_question(question)
