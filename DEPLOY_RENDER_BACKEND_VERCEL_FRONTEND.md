# Deploy Guide: Render Backend + Vercel Frontend

This is the recommended setup for this project:

- Backend (FastAPI + AI processing) on **Render**
- Frontend (Vite/React static app) on **Vercel**

---

## 1) Backend on Render

### Option A: Use `render.yaml` (already configured)

This repo now includes a backend-only `render.yaml` with:

- `runtime: python`
- `buildCommand: pip install -r requirements.txt`
- `startCommand: gunicorn api.main:app -k uvicorn.workers.UvicornWorker --workers 1 --threads 2 --timeout 120`
- `healthCheckPath: /api/health`

### Option B: Configure in Render dashboard manually

Use the same commands and health path above.

### Required environment variables on Render

Add all backend env vars used by `core/config.py`, including:

- `GROQ_API_KEY`
- `NEWS_API_KEY`
- any other keys from your local `.env`

### Verify backend

After deploy:

- `https://<render-backend>.onrender.com/api/health` -> should return status `ok`

---

## 2) Frontend on Vercel

Create a separate Vercel project from this same repository.

- Root Directory: `web`
- Framework Preset: `Vite`
- Build Command: `npm run build`
- Output Directory: `dist`

Set frontend environment variable:

- `VITE_API_BASE_URL=https://<render-backend>.onrender.com`

(`web/.env.example` already documents this variable.)

### Verify frontend

After deploy:

- Open `https://<vercel-frontend>.vercel.app`
- Click Analyze
- Requests should go to `https://<render-backend>.onrender.com/api/...`

---

## 3) Notes

- CORS is currently permissive in backend (`allow_origins=["*"]`), so cross-domain calls will work.
- For production hardening later, restrict CORS to your Vercel frontend domain.
