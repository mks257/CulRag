# CulRAG Deployment Guide

Two pieces deploy independently:

| Piece | Platform | Config |
|---|---|---|
| Backend (FastAPI) | Railway | `deployment/railway.json` + `deployment/Dockerfile` |
| Frontend (React/Vite) | Vercel | `deployment/vercel.json` |

Deploy the **backend first** — the frontend needs its URL at build time.

## 1. Backend on Railway

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo** → select `CulRag`.
2. In the service settings, set **Config file path** to `deployment/railway.json` (Settings → Config-as-code). Railway will build with `deployment/Dockerfile`.
3. Add environment variables (Settings → Variables):
   - `OPENAI_API_KEY` — required for real embeddings + LLM. Without it the API runs in **demo mode** (local hash embeddings, retrieval-only recommendations) — fine for UI testing, not for the paper's user study.
   - `ANTHROPIC_API_KEY` — optional, only if `LLM_MODEL` is a Claude model.
   - `LLM_MODEL` — optional, defaults to `gpt-4`.
   - `FRONTEND_ORIGIN` — set after step 2 below, e.g. `https://culrag.vercel.app` (needed for CORS).
4. Deploy. Railway assigns a public URL like `https://culrag-api-production.up.railway.app`.
5. Verify: `curl https://<railway-url>/api/health` → `{"status": "ok", "mode": "full", ...}`.

Notes:
- The vector index is built **in memory at startup** from `data/sample_foods.csv` (~1s for 50 foods). With the full IFCT dataset, switch to a persistent Chroma volume or Pinecone (`VECTOR_DB_TYPE=pinecone` + `PINECONE_API_KEY`).
- Feedback is appended to `data/feedback.json` **inside the container** — it does not survive redeploys. Attach a Railway volume mounted at `/app/data`, or move to Postgres before the user study.

## 2. Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New Project** → import the `CulRag` repo.
2. Set **Root Directory** to `culrag-frontend`.
3. Vercel auto-detects Vite. If not, copy the settings from `deployment/vercel.json` (build command `npm run build`, output `dist`).
4. Add environment variable:
   - `VITE_API_BASE_URL` = the Railway backend URL from step 1 (no trailing slash).
5. Deploy. Vercel assigns a URL like `https://culrag.vercel.app`.
6. Go back to Railway and set `FRONTEND_ORIGIN` to this Vercel URL, then redeploy the backend so CORS allows it.

Both platforms auto-deploy on every push to the connected branch (set it to `dev` or `main` in each platform's Git settings).

## 3. Local development

```bash
# Backend (from repo root, venv active)
uvicorn src.api:app --reload            # http://localhost:8000

# Frontend
cd culrag-frontend
npm install
npm run dev                             # http://localhost:3000
```

CORS already allows `localhost:3000` and `localhost:5173`; the frontend defaults to `http://localhost:8000` for the API, so no env vars are needed locally.

## 4. Smoke test checklist (after each deploy)

- [ ] `GET /api/health` returns `status: ok` and the expected `mode`
- [ ] Dashboard loads, form renders
- [ ] Submitting the form returns a recommendation card
- [ ] Like/Dislike stores a row in `data/feedback.json` (check Railway logs)
