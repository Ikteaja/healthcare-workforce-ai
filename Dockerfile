# =============================================================
# Dockerfile
# =============================================================
# This file packages the FastAPI backend into a Docker container.
#
# HOW IT WORKS:
# 1. Starts with a clean Python 3.11 Linux machine
# 2. Copies your code into it
# 3. Installs all libraries
# 4. Starts the FastAPI server when container runs
#
# BUILD:  docker build -t healthcare-ai .
# RUN:    docker compose up
# =============================================================

# Step 1 — Start with Python 3.11 slim (small Linux + Python)
FROM python:3.11-slim

# Step 2 — Set the working directory inside the container
# All commands after this run from /app
WORKDIR /app

# Step 3 — Copy requirements first (Docker caches this layer)
# If requirements.txt did not change, Docker skips reinstalling
COPY requirements.txt .

# Step 4 — Install all Python libraries
# --no-cache-dir keeps the image size smaller
RUN pip install --no-cache-dir -r requirements.txt

# Step 5 — Copy all source code into the container
COPY src/ ./src/

# Step 6 — Copy env example as default config
# Real .env is mounted at runtime via docker-compose
COPY .env.example .env

# Step 7 — Tell Docker this container uses port 8000
EXPOSE 8000

# Step 8 — Command that runs when container starts
# Starts FastAPI server on all network interfaces
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]