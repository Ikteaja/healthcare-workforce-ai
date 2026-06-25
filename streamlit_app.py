# =============================================================
# streamlit_app.py
# =============================================================
# PURPOSE:
#   The chat interface that HR staff and employees use.
#   Runs on port 8501.
#   Sends questions to FastAPI (port 8000).
#   Displays answers in a chat bubble interface.
#
# HOW TO RUN:
#   streamlit run streamlit_app.py
#
# REQUIRES:
#   FastAPI must be running on port 8000 first.
#   Start FastAPI: uvicorn src.api.main:app --reload --port 8000
#
# WHAT IT DOES:
#   1. Shows a chat window (like WhatsApp)
#   2. User types question → sends POST to /chat
#   3. Displays AI answer in chat bubble
#   4. Sidebar: upload new PDF documents via /ingest
#   5. Sidebar: shows system status and quick questions
# =============================================================

import requests
import streamlit as st

# =============================================================
# PAGE CONFIGURATION
# =============================================================
# Must be the very first Streamlit command
st.set_page_config(
    page_title="WorkforceIQ",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# FastAPI backend URL
# Change this when deploying to production server
API_URL = "http://localhost:8000"


# =============================================================
# HELPER FUNCTIONS
# =============================================================


def check_api_health() -> bool:
    """
    Checks if FastAPI backend is running.
    Returns True if running, False if not.
    """
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        return response.status_code == 200
    except Exception:
        return False


def ask_question(question: str) -> str:
    """
    Sends question to FastAPI /chat endpoint.
    Returns the AI answer as a string.
    """
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"question": question},
            timeout=120,  # LLM can take up to 2 minutes
        )
        if response.status_code == 200:
            return response.json()["answer"]
        else:
            return f"Error: {response.json().get('detail', 'Unknown error')}"
    except requests.exceptions.Timeout:
        return "The AI is taking too long to respond. Please try again."
    except requests.exceptions.ConnectionError:
        return "Cannot connect to FastAPI. Make sure it is running on port 8000."
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def upload_document(file) -> str:
    """
    Uploads a PDF file to FastAPI /ingest endpoint.
    Returns success or error message.
    """
    try:
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        response = requests.post(
            f"{API_URL}/ingest",
            files=files,
            timeout=300,  # ingestion can take a few minutes
        )
        if response.status_code == 200:
            return response.json()["message"]
        else:
            return f"Error: {response.json().get('detail', 'Upload failed')}"
    except Exception as e:
        return f"Upload error: {str(e)}"


# =============================================================
# SIDEBAR
# =============================================================

with st.sidebar:
    st.title("🤖 WorkforceIQ")
    st.caption("Agentic RAG Platform for Workforce Intelligence")
    # ── System Status ──────────────────────────────────────
    st.divider()
    st.subheader("System Status")

    if check_api_health():
        st.success("✅ API is running")
    else:
        st.error("❌ API is offline — start FastAPI first")
        st.code(
            "uvicorn src.api.main:app --reload --port 8000",
            language="bash",
        )

    # ── Document Upload ────────────────────────────────────
    st.divider()
    st.subheader("Upload Document")
    st.caption("Add new PDF to the knowledge base")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload HR policies, compliance docs, or any PDF",
    )

    if uploaded_file is not None:
        if st.button("Upload and Process", type="primary"):
            with st.spinner("Uploading and processing document..."):
                message = upload_document(uploaded_file)
                if "successfully" in message.lower():
                    st.success(message)
                else:
                    st.error(message)

    # ── Quick Questions ────────────────────────────────────
    st.divider()
    st.subheader("Quick Questions")
    st.caption("Click to ask common questions")

    quick_questions = [
        "What is the annual leave for nurses?",
        "What is the night shift supplement?",
        "Who works in ICU today?",
        "What are the DSGVO patient rights?",
        "What is the minimum staffing for ICU?",
        "What vaccinations do staff need?",
    ]

    for q in quick_questions:
        if st.button(q, use_container_width=True):
            st.session_state.quick_question = q

    # ── About ──────────────────────────────────────────────
    st.divider()
    st.caption("Powered by LangChain + ChromaDB + Ollama")
    st.caption("German labour law compliant")
    st.caption("Helix Workforce Solutions GmbH")


# =============================================================
# MAIN CHAT AREA
# =============================================================

# Title and description
st.title("🤖 WorkforceIQ")
st.caption(
    "Agentic RAG Platform for Workforce Intelligence — "
    "HR policies, schedules, labour law and compliance."
)

# ── Initialise chat history ────────────────────────────────
# session_state persists data between Streamlit reruns
# Without this — chat history disappears on every interaction
if "messages" not in st.session_state:
    st.session_state.messages = []

# Add welcome message on first load
if len(st.session_state.messages) == 0:
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": (
                "Hello! I am WorkforceIQ — your Agentic AI Assistant. "
                "I can help you with workforce intelligence:\n\n"
                "- **HR policies** — leave, sick pay, working hours\n"
                "- **Staff schedules** — who works when and where\n"
                "- **German labour law** — AZG, TVöD-K, DSGVO\n"
                "- **Compliance** — HIPAA, infection control\n\n"
                "What would you like to know?"
            ),
        }
    )

# ── Display chat history ───────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Handle quick question from sidebar ────────────────────
if "quick_question" in st.session_state:
    question = st.session_state.quick_question
    del st.session_state.quick_question

    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Get and display answer
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = ask_question(question)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()

# ── Chat input ─────────────────────────────────────────────
if question := st.chat_input("Ask about HR policies, schedules, or compliance..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": question})

    # Display user message
    with st.chat_message("user"):
        st.markdown(question)

    # Get answer from FastAPI and display
    with st.chat_message("assistant"):
        with st.spinner("Searching documents and thinking..."):
            answer = ask_question(question)
        st.markdown(answer)

    # Add assistant answer to history
    st.session_state.messages.append({"role": "assistant", "content": answer})
