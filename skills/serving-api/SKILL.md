# Skill: Serving the API

For work on the FastAPI server — it EXISTS at `src/api.py` (416 lines), with tests in
`tests/test_api.py`. Read the file before changing it; this skill maps it.

## What exists

Endpoints (all under `/api`):
- `GET /api/health` → `HealthResponse` — pipeline status + indexed-food count
- `POST /api/recommend` → `RecommendationResponse` — body: `RecommendationRequest`
  (query + constraints); builds constraints dict for `GuardrailChecker`, filters
  retrieved foods, returns structured recommendation
- `POST /api/feedback` → `FeedbackResponse` — appends user feedback to a local file
  (`append_feedback`)

Pydantic models: `RecommendationRequest`, `Macros`, `RecommendationResponse`,
`FeedbackRequest`, `FeedbackResponse`, `HealthResponse` — mirror them, don't invent a
second schema. Startup is a FastAPI `lifespan` handler that loads the pipeline once.

**Demo mode:** the API can run fully offline using `_demo_hash_embed` (deterministic
hash embeddings) and `_demo_recommendation` — no API keys. This powers the frontend
dashboard (`culrag-frontend/`, React + Vite; calls these `/api/*` routes) and local dev.
Demo-mode output is pipeline validation only — never quote its numbers as results.

## Rules

1. **The API never bypasses guardrails.** Recommendations go through the constraint
   checks; the guardrail signal stays in the response.
2. **Validate at the boundary.** Pydantic enforces types; keep caps on query length and
   list sizes — `/api/recommend` can call paid LLM APIs.
3. Errors: LLM/API failures return an error status with a plain message; never a
   fabricated recommendation, no stack traces or key material in responses.
4. Endpoint or model changes are breaking changes for `culrag-frontend/src/types/` and
   `tests/test_api.py` — update all three together.
5. Research demo, not production: no real auth or rate limiting; don't expose beyond
   localhost / the demo deployment without adding both.
6. Deployment configs live in `deployment/` (Dockerfile, railway.json, vercel.json) —
   see `deployment/README.md`.

## Run

```
.venv\Scripts\python.exe -m uvicorn src.api:app --reload
```

Tests (offline, like all tests): `.venv\Scripts\python.exe -m pytest tests/test_api.py -v`
