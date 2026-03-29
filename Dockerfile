# ── Stage 1: Build the React Frontend ──────────────────────────────
FROM node:20-slim AS build-stage

WORKDIR /app/web

# Copy package files and install dependencies
COPY web/package*.json ./
RUN npm install

# Copy source and build (Vite defaults to /app/web/dist)
COPY web/ ./
RUN npm run build

# ── Stage 2: Prepare the FastAPI Backend ────────────────────────────
FROM python:3.11-slim AS run-stage

WORKDIR /app

# Install system dependencies (libgomp1 for faiss-cpu)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn  # Ensure gunicorn is present

# Copy backend source
COPY agents/ ./agents/
COPY api/ ./api/
COPY core/ ./core/
COPY data/ ./data/

# Copy the built frontend from the previous stage
COPY --from=build-stage /app/web/dist ./web/dist

# Pre-download the embedding model during build (avoids runtime HF Hub issues)
ENV TRANSFORMERS_CACHE=/app/data/hf_cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L3-v2')"

# Expose the default Render port
EXPOSE 10000

# Start the application using Gunicorn with Uvicorn workers
CMD ["gunicorn", "api.main:app", \
     "--bind", "0.0.0.0:10000", \
     "--workers", "1", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--timeout", "300"]
