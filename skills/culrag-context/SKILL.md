# Skill: CulRAG Context

Background for any work on this project. Load alongside a task skill when the assistant
is new to the repo.

## The project in one paragraph

CulRAG is a research project building and evaluating a **Retrieval-Augmented Generation
system for personalized Indian dietary guidance**. It retrieves foods from a
culturally-adapted knowledge base (IFCT 2017 — Indian Food Composition Tables, 528 foods,
plus Ayurvedic properties) and uses an LLM to generate nutrition recommendations, with
guardrails that catch hallucinated foods and constraint violations. Target venue:
IEEE Access / Frontiers in AI. Timeline: 8 weeks. Team: Kavya (RAG/LLM lead),
Vartan (data lead).

## Research question

> Can RAG-based systems provide culturally-appropriate and nutritionally-accurate dietary
> guidance when grounded in Indian-specific food databases and Ayurvedic principles?

The paper's claimed contributions — every piece of work should serve one of these:
1. First systematic evaluation of **cultural grounding** in RAG nutrition systems
2. RAG optimized for **Indian cuisine** (IFCT 2017 foods)
3. Integration of **Ayurvedic principles** with modern nutrition science
4. Measured **hallucination rates** and **cultural relevance** in dietary recommendations

## Architecture (what exists in `src/`)

```
user query + constraints
        │
        ▼
CulRAG (src/rag_pipeline.py)  ── orchestrator: load_knowledge_base → retrieve → generate
        │
        ├── VectorRetriever (src/retriever.py)   — Pinecone (cloud) or Chroma (local fallback)
        ├── RAGChain (src/llm_chain.py)          — prompt templates → LLM → structured JSON meal rec
        ├── GuardrailChecker (src/guardrails.py) — vegetarian/calorie/allergy checks + hallucination detection
        └── RAGEvaluator (src/evaluator.py)      — precision@k, recall@k, MRR, safety metrics
Config: src/config.py + .env (see .env.example)
```

Around the pipeline:
- `src/api.py` — FastAPI server (`/api/recommend`, `/api/health`, `/api/feedback`);
  offline demo mode with hash embeddings (see `serving-api` skill)
- `culrag-frontend/` — React + Vite + Tailwind dashboard calling the API
- `deployment/` — Dockerfile, Railway/Vercel configs
- `paper/` — Paper 1 manuscript workspace: one .md per section, references.bib,
  figure scripts (see `writing-the-paper` skill); also `paper/protocol.md` +
  `paper/recruitment_kit/` — Paper 2 pilot-study protocol drafted for IRB review

## Data (what exists in `data/`)

- `data/sample_foods.csv` — ~50 Indian foods, the working dataset until the full IFCT
  import lands. Schema is the project's data contract (see `building-food-data` skill).
- `data/eval_queries.json` — hand-labeled (query → relevant_foods) pairs for retrieval eval.
- `data/ifct2017/IFCT2017.md` — IFCT 2017 citation, access, and licensing notes.
  **Licensing matters**: academic use with acknowledgement is fine; redistributing a
  compiled database may need NIN permission.

## Phases

1. ✅ Core RAG pipeline skeleton
2. ✅ Evaluation framework & metrics
3. ✅ 3A: API + frontend dashboard; ✅ 3B: paper scaffolding + Methods draft;
   deterministic baseline embeddings for offline runs
4. In progress: full IFCT dataset import (Vartan), production-embedding evaluation runs
   (current results.md numbers are hash-embedding placeholders), paper prose, Paper 2
   pilot study (IRB review)

## Conventions

- Python 3.13, venv at `.venv/`. Type hints + Google-style docstrings + logging everywhere.
- Vector DB must stay swappable: Pinecone ↔ Chroma behind `VectorRetriever`.
- Code must run without API keys where possible (Chroma local, mocked LLM in tests).
- Work happens on `dev`, merged to `main` via PR. Commit style: `[FEAT] Phase N - summary`.
