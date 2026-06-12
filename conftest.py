# =============================================================
# conftest.py
# =============================================================
# This file sits at the PROJECT ROOT (not inside src/).
# It tells pytest to add the project root to Python's path
# so imports like 'from src.ingestion.chunker import'
# work on both laptop and GitHub Actions.
# =============================================================

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath("."))