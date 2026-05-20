# =============================================================
# conftest.py
# =============================================================
# This file sits at the project root.
# It tells pytest to add the project root folder to Python's
# path so that imports like 'from src.ingestion.chunker import'
# work correctly both on your laptop AND on GitHub Actions.
# =============================================================

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath("."))