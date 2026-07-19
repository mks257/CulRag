# Skill: Evaluating RAG

For measuring the system — the numbers that go in the paper. Two separate concerns,
never conflated:

1. **Retrieval quality** — does the vector search surface the right foods?
2. **Recommendation safety** — does the LLM output hallucinate or violate constraints?

## Retrieval metrics (`src/evaluator.py`, class `RAGEvaluator`)

- `precision_at_k(retrieved, relevant, k)` — fraction of top-k that are relevant
- `recall_at_k(retrieved, relevant, k)` — fraction of relevant found in top-k
- MRR — reciprocal rank of the first relevant hit, averaged over queries
- Report at k=5 by default; matching is **exact food_name string match** against the
  labeled set — spelling drift between dataset and labels silently zeroes the metrics.

Ground truth lives in `data/eval_queries.json`:

```json
{ "query": "South Indian breakfast dish",
  "relevant_foods": ["Idli", "Dosa (plain)", "Uttapam", "Upma"] }
```

Rules for the eval set:
- Every `relevant_foods` entry must exist verbatim in the food dataset. Verify with a
  script, not by eye, after any dataset or query change.
- Label relevance from the DATA, not from what the retriever returns — labeling from
  retriever output is circular and inflates every metric.
- Cover the paper's claims: regional queries, Ayurvedic (dosha) queries, macro/nutrition
  queries, cooking-method queries, and negative cases (non-veg minority). Currently
  9 queries — grow this to 30+ before reporting numbers in the paper; 9 is a smoke test,
  not an evaluation.

## Safety metrics

Aggregated from `GuardrailChecker` output over a batch of `CulRAG.recommend()` calls:
- **Hallucination rate** — fraction of recommendations naming foods absent from the
  knowledge base, or with macros far off DB values
- **Constraint-violation rate** — vegetarian / calorie-range / allergy violations

These require real LLM calls (cost money, non-deterministic). Fix the model, temperature,
and prompt version per run; log every prompt+output; report N (number of calls) with
every rate. A rate without N is not a result.

## Honest-numbers rules

- Never evaluate on queries used to tune prompts or retrieval params. Hold out.
- Any change to dataset, embeddings, k, or prompt = re-run the FULL eval; never mix
  numbers from different configurations in one table.
- Record with every reported number: dataset version/size, embedding model, k, LLM model,
  temperature, N queries, date. The paper's tables need exactly this provenance.
- A metric that goes UP after a change you can't explain is a bug until proven otherwise
  (usually label leakage or name-matching drift).

## Where eval runs

`notebooks/02_retrieval_evaluation.ipynb` for exploration; promote anything reported in
the paper to a script so it's reproducible with one command.
