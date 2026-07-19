# Skill: Running Experiments

For producing the paper's Results section: baselines, ablations, and comparison runs.
`evaluating-rag` defines the metrics; this skill defines WHAT to run and how to keep
runs comparable.

## The experiment matrix (minimum for the paper)

| System | What it shows |
|---|---|
| **CulRAG (full)** | Our system: cultural KB + retrieval + guardrails |
| **No-RAG baseline** | Same LLM, same prompt, NO retrieved context — isolates the value of retrieval |
| **Generic-RAG baseline** | Retrieval from a non-cultural food KB (e.g. USDA-style generic foods) — isolates the value of *cultural* grounding, this is the paper's core claim |
| **No-guardrails ablation** | Full pipeline minus GuardrailChecker — shows guardrails' contribution to safety metrics |

Every system runs the SAME eval query set, same LLM model, same temperature, same k.
Only one variable differs per comparison — otherwise the numbers claim nothing.

## Run protocol

1. Every run gets a config record: `{run_id, date, system_variant, llm_model, temperature,
   k, embedding_model, dataset_version, n_queries}`. Save it next to the outputs —
   `results/<run_id>/config.json` + raw outputs + computed metrics.
2. Raw LLM outputs are saved, not just metrics. Reviewers ask for examples; you also
   re-score old runs when metric definitions change, without re-paying for LLM calls.
3. LLM non-determinism: temperature 0 where the comparison allows it; otherwise ≥3
   repeats and report mean ± range. Never report a single stochastic run as the number.
4. Cost control: smoke-test every experiment script on 3 queries before the full run.
5. A run that errors partway is discarded, not patched — partial batches bias rates.

## Ablation discipline

- Change ONE component per ablation. "CulRAG minus Ayurvedic metadata" is one ablation;
  "minus Ayurveda and different k" is two runs.
- Negative/neutral results are results — they go in the paper (or its limitations), not
  in the bin. A generic-RAG baseline that ties us is exactly what reviewers will suspect
  if we don't report it.

## Where things live

- Experiment scripts: `scripts/` (one script per experiment, runnable end-to-end with
  one command; notebooks are for exploration only, nothing in the paper comes from an
  unversioned notebook cell).
- Outputs: `results/<run_id>/` — gitignore raw LLM outputs if large; commit configs and
  metric summaries always.
