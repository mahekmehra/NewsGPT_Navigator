# Deploy Guide: Render Backend + Vercel Frontend

This is the recommended setup for this project:

- Backend (FastAPI + AI processing) on **Render**
- Frontend (Vite/React static app) on **Vercel**

---

## 1) Backend on Render

### Option A: Use `render.yaml` (Optimized for Free Tier)

This repo includes a backend-only `render.yaml` optimized for **512MB RAM**:

- `runtime: python`
- `buildCommand: pip install -r requirements.txt`
- `startCommand: gunicorn api.main:app -w 1 -k uvicorn.workers.UvicornWorker --threads 1 --timeout 180`
- `healthCheckPath: /api/health`

### Required environment variables on Render

Add these to your Render service:

- `GROQ_API_KEY`: Your Groq API key.
- `NEWS_API_KEY`: Your NewsAPI key.
- `WEB_CONCURRENCY`: `1` (Crucial for memory).
- `MALLOC_ARENA_MAX`: `2` (Prevents memory fragmentation).
- `PYTHONUNBUFFERED`: `1`

---

## 2) Frontend on Vercel

Create a project on Vercel named **News_GPT**.

- Root Directory: `web`
- Framework Preset: `Vite`
- Build Command: `npm run build`
- Output Directory: `dist`

Set environment variable:

- `VITE_API_BASE_URL=https://<render-backend>.onrender.com`

---

## 3) Deployment Notes

- **Initial Load**: The first analysis may take longer as the embedding model (~45MB) is downloaded.
- **Memory**: The system is capped at 1 active job to prevent Render from killing the process due to RAM limits.
- **CORS**: Currently set to `allow_origins=["*"]`. Restricted for production in `api/main.py` if needed.
- **Cleanup**: The `tests/` directory and `venv/` have been removed to reduce package size.
