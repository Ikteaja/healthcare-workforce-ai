''''''''''''''''''''''''
You write:  "if I send question X, I expect answer Y"
Test runs:  sends question X
Test checks: did I get answer Y?
Test result: ✅ PASS or ❌ FAIL
The tests/ folder
What is tests/?
This folder contains code that automatically checks your code works correctly. Instead of manually testing every time, you write test files once and run them with one command.
Simple example of what a test does:
You write:  "if I send question X, I expect answer Y"
Test runs:  sends question X
Test checks: did I get answer Y?
Test result: ✅ PASS or ❌ FAIL
Why it matters:
Every time you push code to GitHub, GitHub Actions automatically runs all tests. If something is broken, it catches it before it reaches your main branch.

What tests we will write for this project
FileTests WhatExample Checktest_ingestion.pyChunker works correctly500-word chunks created properlytest_retriever.pyChromaDB search worksReturns relevant chunks for a querytest_api.pyFastAPI endpoints work/health returns {"status":"ok"}

Step 1 — Create tests/ folder
powershellcd C:\Users\Ikteaja.Hasan\Projects\healthcare-workforce-ai
mkdir tests

Step 2 — Create tests/__init__.py
Same as src/__init__.py — tells Python this folder is a package.
powershellNew-Item tests\__init__.py -type file
Verify it is 0 bytes:
powershelldir tests
If it shows anything other than 0 bytes — clear it:
powershellClear-Content tests\__init__.py

Step 3 — Create test_ingestion.py
powershellcode tests\test_ingestion.py
Paste this inside:
python# =============================================================
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
Save it (Ctrl+S).

Step 4 — Create test_api.py
powershellcode tests\test_api.py
Paste this inside:
python# =============================================================
# test_api.py
# =============================================================
# Tests the FastAPI endpoints.
# We use TestClient — it pretends to be a browser sending
# HTTP requests to our API without needing the server running.
# NOTE: /chat tests will be added in Phase 7 when we build
# the actual API. For now we test what we can.
# =============================================================

# This file is ready but tests will be activated in Phase 7
# when src/api/main.py is built.

# Placeholder so pytest does not complain about empty file.
def test_placeholder():
    """
    Placeholder test — always passes.
    Real API tests will be added in Phase 7.
    """
    assert True
    print("✅ Placeholder test passed — API tests coming in Phase 7")
Save it.

Step 5 — Create test_retriever.py
powershellcode tests\test_retriever.py
Paste this inside:
python# =============================================================
# test_retriever.py
# =============================================================
# Tests the ChromaDB retriever.
# We use a mock (fake) ChromaDB so we do not need the real
# database running during tests.
# NOTE: Full retriever tests will be activated in Phase 5
# when src/rag/retriever.py is built.
# =============================================================

# Placeholder so pytest does not complain about empty file.
def test_placeholder():
    """
    Placeholder test — always passes.
    Real retriever tests will be added in Phase 5.
    """
    assert True
    print("✅ Placeholder test passed — Retriever tests coming in Phase 5")
Save it.

Step 6 — Verify all files exist
powershelldir tests
You should see:
Length   Name
------   ----
0        __init__.py
...      test_api.py
...      test_ingestion.py
...      test_retriever.py

Step 7 — Install pytest and run tests
powershellpip install pytest
Run all tests:
powershellpytest tests/ -v
You should see:
tests/test_api.py::test_placeholder PASSED
tests/test_retriever.py::test_placeholder PASSED
tests/test_ingestion.py::test_chunker_splits_long_text PASSED
tests/test_ingestion.py::test_chunker_preserves_text PASSED
tests/test_ingestion.py::test_chunker_empty_document PASSED

5 passed in 0.5s

Step 8 — Commit
powershellgit add tests\
git commit -m "feat: add tests folder with ingestion tests"
git push origin develop

What we have now
healthcare-workforce-ai/
├── src/
│   └── __init__.py              ✅
├── data/
│   ├── documents/               ✅
│   └── chroma_db/               ✅
├── docs/                        ✅
├── tests/
│   ├── __init__.py              ✅ empty — marks as Python package
│   ├── test_ingestion.py        ✅ tests chunker
│   ├── test_api.py              ✅ placeholder — active in Phase 7
│   └── test_retriever.py        ✅ placeholder — active in Phase 5
├── .env                         ✅
├── .env.example                 ✅
└── README.md                    ✅

Tell me what pytest tests/ -v shows and we move to the next folder —



Perfect question. You are thinking like a real developer. Let me explain clearly.

Your confusion is completely valid
You are right to question this. Let me answer directly:
What are we actually testing?
We are NOT testing your healthcare data. We are testing the chunker function itself — does it work correctly as a piece of code?
Think of it like this:

  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) {
    animation-duration: 0.25s;
    animation-timing-function: cubic-bezier(0.19, 1, 0.22, 1);
  }
VvisualizeVvisualize show_widget
The simple answer
We are testing the chunker function — not your healthcare data.
The chunker does one job: take text in → produce chunks out. We need to verify that job works correctly. The content of the text does not matter — what matters is that the function behaves correctly.

Real example — why this catches real bugs
Imagine you accidentally change chunker.py like this:
python# BEFORE — correct
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

# AFTER — you accidentally change it
splitter = RecursiveCharacterTextSplitter(
    chunk_size=0,      ← accidental change
    chunk_overlap=50
)
With chunk_size=0 your chunker breaks — it produces zero chunks and the whole RAG system stops working. Without tests you would not notice until a user gets a wrong answer.
With the test:
pytest tests/test_ingestion.py

test_chunker_splits_long_text  ❌ FAILED
Expected: more than 1 chunk
Got: 0 chunks

→ GitHub Actions blocks your push
→ You fix the bug immediately

Three things each test actually verifies
Test 1 — test_chunker_splits_long_text
Question it answers: Does the chunker actually split text?
Input:  1000 words of fake text
Checks: did we get more than 1 chunk back?
Why:    If this fails, chunker is completely broken
Test 2 — test_chunker_preserves_text
Question it answers: Does the chunker lose any words?
Input:  "Annual leave policy for nurses is twenty eight days"
Checks: are those exact words still in the chunks?
Why:    If words disappear, AI gives wrong answers
Test 3 — test_chunker_empty_document
Question it answers: Does the chunker crash on empty files?
Input:  empty document ""
Checks: did we get 0 chunks without any error or crash?
Why:    Someone might upload an empty PDF by mistake

Where it integrates in your project
You write code
     │
     ▼
git push origin develop
     │
     ▼
GitHub Actions triggers automatically
     │
     ▼
runs: pytest tests/
     │
     ├── test_ingestion.py  ← runs RIGHT NOW (chunker exists)
     ├── test_api.py        ← placeholder until Phase 7
     └── test_retriever.py  ← placeholder until Phase 5
     │
     ▼
All pass ✅ → build continues → Docker image built
Any fail ❌ → build stops → you must fix before merging

When do we add REAL data tests?
In Phase 4 when ingestion is built — we will add a test that:

Uses a real small PDF (a test PDF we create just for testing)
Runs the full ingestion pipeline
Checks that ChromaDB actually received the chunks

That will be an integration test — testing multiple components together with real data. What we have now are unit tests — testing one function in isolation.

Unit test (now)Integration test (Phase 4)Uses real data❌ fake text✅ real test PDFTestsone functionmultiple components togetherSpeedvery fastslowerRuns in CI✅ always✅ always

Does this make sense now? Tell me and we continue to the .github/workflows/ folder.You said: where actually this function are written adn how it is relate with the test .where actually this function are written adn how it is relate with the test . ho it catch bugs5:01 PMClaude responded: Great question.Great question. Let me show you exactly where the function lives, how the test connects to it, and how it catches bugs.

  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) {
    animation-duration: 0.25s;
    animation-timing-function: cubic-bezier(0.19, 1, 0.22, 1);
  }
VvisualizeVvisualize show_widget
The connection in plain words
There are two files. They are connected by one line — import.
File 1 — the real function lives here:
src/ingestion/chunker.py
pythondef split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500)
    return splitter.split_documents(documents)
This is the actual working code your project uses.

File 2 — the test lives here:
tests/test_ingestion.py
python# this one line connects the test to the real function
from src.ingestion.chunker import split_documents

def test_chunker_splits_long_text():
    chunks = split_documents([fake_doc])  # calls the REAL function
    assert len(chunks) > 1               # checks the result
The test does NOT have its own version of split_documents. It imports and calls the exact same real function your project uses. So when the function breaks — the test breaks too. That is how bugs are caught.

Step by step — how a bug gets caught
Step 1 — you change chunker.py by accident
         chunk_size=500  →  chunk_size=0

Step 2 — you run: git push origin develop

Step 3 — GitHub Actions starts automatically
         runs: pytest tests/

Step 4 — test_ingestion.py imports split_documents
         calls it with fake text
         gets back 0 chunks

Step 5 — assert len(chunks) > 1
         0 > 1 is FALSE
         test FAILS

Step 6 — GitHub Actions sees the failure
         blocks the push
         sends you an email saying what failed

Step 7 — you open chunker.py
         see chunk_size=0
         fix it back to 500
         push again — all tests pass

Right now — the function does not exist yet
This is important to understand. Right now chunker.py is an empty file. We created it but did not write the function yet. So if you run the test right now it will fail with:
ImportError: cannot import name 'split_documents' from 'src.ingestion.chunker'
That is expected and correct. The test is written and waiting. The function gets written in Phase 4. The moment you write the function in chunker.py — the test automatically works because it imports from the real file.

Summary
QuestionAnswerWhere is the function written?src/ingestion/chunker.pyWhere is the test written?tests/test_ingestion.pyHow are they connected?from src.ingestion.chunker import split_documentsDoes the test copy the function?No — it imports and calls the real oneHow does it catch bugs?If function breaks, assert fails, push is blockedDoes it work right now?No — function not written yet. Works after Phase 4

''''''''''''''''''''''''