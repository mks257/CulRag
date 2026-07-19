# Skill: Serving the API

For the planned FastAPI server exposing CulRAG as endpoints (Phase 2+ item; fastapi and
uvicorn are already in requirements.txt). Build this ONLY when the pipeline works
end-to-end — the API is a thin wrapper, not the product.

## Shape

- One file to start: `src/api.py`. Split only when it outgrows one file.
- Endpoints:
  - `POST /recommend` — body: `{query: str, constraints: {...}}` (constraints dict format
    from `src/guardrails.py`); returns the structured recommendation JSON from `RAGChain`
    PLUS the guardrail report (`passed`, `violations`, `flags`, `confidence`). Never strip
    the guardrail report — the safety signal is the point of the system.
  - `GET /health` — returns vector DB status from `VectorRetriever.get_stats()`.
- Request/response models: Pydantic (v2 is installed) — mirror the constraints dict and
  recommendation JSON exactly; don't invent a second schema.

## Rules

1. **Validate at the boundary.** Pydantic models enforce types; additionally cap query
   length and constraint list sizes. This endpoint calls paid LLM APIs — an unvalidated
   input is an unbounded bill.
2. **The API never bypasses guardrails.** `CulRAG.recommend()` with checks, always.
3. Startup: load knowledge base + init retriever ONCE in a FastAPI lifespan handler, not
   per-request. Chroma local by default; Pinecone via env config.
4. Errors: LLM/API failures return 503 with a plain message; never a fabricated
   recommendation. Log full detail server-side, return no stack traces or key material.
5. This is a research demo, not production: no auth beyond an optional shared token from
   `.env`, no rate limiting beyond an in-process counter. Say so in the README when the
   API lands. Add real auth only if it's ever exposed beyond localhost.
6. Include a disclaimer field in every response: research system, not medical advice —
   consistent with the paper's ethics section.

## Run

```
.venv\Scripts\python.exe -m uvicorn src.api:app --reload
```

Test: `tests/test_api.py` with FastAPI's `TestClient`, LLM call mocked — offline like all
other tests.
