# Skill: RAG Pipeline

For work on retrieval, generation, or guardrails — the code in `src/`.

## Component map

| File | Class | Job |
|---|---|---|
| `src/rag_pipeline.py` | `CulRAG` | Orchestrator: `load_knowledge_base()`, `retrieve()`, `generate()`, `recommend()` |
| `src/retriever.py` | `VectorRetriever` | Vector DB abstraction: `index_documents()`, `search()`; Pinecone or Chroma |
| `src/llm_chain.py` | `RAGChain` | Prompt build + LLM call + structured JSON output |
| `src/guardrails.py` | `GuardrailChecker` | Constraint checks + hallucination detection |
| `src/config.py` | — | Env/config loading (`.env`, see `.env.example`) |

## ⚠️ Installed versions are NEWER than the original plan

The venv (Python 3.13) has current-generation libraries. The original prompts referenced
2023-era APIs — do NOT copy code patterns from them or from old tutorials:

- **langchain 1.x** — legacy chains (`RetrievalQA`, `langchain.chains`) are gone/moved.
  Use `langchain-core` primitives (runnables, prompt templates) or plain SDK calls.
- **openai 2.x** — client style is `OpenAI().chat.completions.create(...)` /
  `client.embeddings.create(...)`; old `openai.ChatCompletion` is long dead.
- **anthropic 0.117** — `Anthropic().messages.create(...)`.
- **`pinecone` (v9), NOT `pinecone-client`** — the package was renamed; import `pinecone`,
  use the `Pinecone(api_key=...)` class, serverless index spec.
- **chromadb 1.x**, **pandas 3.x**, **numpy 2.x**.

When editing a `src/` file, read it first — match the API style already in the file, and
if it uses a dead API, fixing that is part of the task.

## Design rules

1. **Vector DB stays swappable.** Pinecone (cloud) and Chroma (local) both work behind
   `VectorRetriever`. New features must work on Chroma with no API key — that's what
   tests and teammates without keys use.
2. **Retrieval works before generation.** Debug retrieval quality standalone (notebook
   `02_retrieval_evaluation.ipynb`) before blaming the LLM.
3. **Document format:** `{text: "<food_name>", metadata: {calories: ..., region: ...,
   vegetarian: ..., ayurvedic_type: ...}}`. Metadata must survive indexing — guardrails
   read it to verify LLM claims.
4. **Structured output.** `RAGChain` returns JSON: `meal_name`, `calories`, `macros`
   {protein_g, carbs_g, fat_g}, `portion`, `reasoning`. Parse defensively — LLM output
   is a trust boundary; never `eval`, always validate fields before guardrails consume them.
5. **Guardrails are the paper's safety metric.** `GuardrailChecker` output
   (`passed`, `violations`, `flags`, `confidence`) feeds hallucination-rate numbers in
   `RAGEvaluator`. Changing its output shape breaks the evaluator — change both together.
6. **Hallucination detection = check against the knowledge base**: food not in the DB →
   flag; macros far from DB values → flag. The knowledge base is ground truth, not the LLM.
7. Error handling for API failures (timeouts, rate limits) with logging; no silent
   fallbacks that fabricate a recommendation.

## Testing

- `tests/test_retriever.py`, `tests/test_evaluator.py` — pytest, Chroma-local, no API
  keys, `sample_foods.csv` as fixture data. Keep it that way.
- Run: `F:\culrag\.venv\Scripts\python.exe -m pytest tests/ -v`
- New pipeline behavior gets a test that runs offline (mock the LLM call).
