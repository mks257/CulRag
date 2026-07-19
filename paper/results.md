# 5. Results

<!-- Target: ~1000 words. Status: STUB with baseline numbers.
IMPORTANT: numbers below are the OFFLINE BASELINE (CRC32 bag-of-words embedding,
exact cosine k-NN, 50-food dev subset, 9 queries), regenerated reproducibly by
paper/tables/generate_eval_results.py. They validate the pipeline, NOT semantic
retrieval quality. Replace after the production-embedding + full-IFCT run.
(Note: earlier notebook runs used Python's salted hash() through Chroma's HNSW
index and were NOT reproducible across processes — do not quote those numbers.) -->

## 5.1 Retrieval quality

<!-- [TABLE 2 GOES HERE: from paper/tables/eval_results.csv] -->
<!-- [FIGURE 2 GOES HERE: per-query retrieval metrics bar chart] -->

Offline baseline (crc32 embedding, exact k-NN, k=5, n=9 queries — reproducible):
- Mean Precision@5: 0.133   [PLACEHOLDER — replace with production-embedding run]
- Mean Recall@5:    0.185   [PLACEHOLDER]
- Mean MRR:         0.211   [PLACEHOLDER]

<!-- Narrative to write once real numbers exist:
- Which query categories retrieve well (explicit attributes: region, cooking method)
  vs. poorly (implicit semantics: "comfort food", "iron rich")?
- Ablation: hash embedding vs. text-embedding-3-small (the injectable embedding
  function makes this a one-line change). -->

## 5.2 Hallucination detection

<!-- [TABLE 3 GOES HERE: example recommendations with guardrail verdicts — see figures/03_hallucination.py] -->
<!-- Show 3-4 rows: a clean pass; an unknown-food flag; a macro-deviation flag;
a constraint violation. We already have real examples from the Phase 3A smoke test
(e.g., "Paneer Tikka with Dal" macro deviations flagged at 150-6150%). -->

Findings to fill:
- Hallucination rate across [PLACEHOLDER: N] pipeline runs: [PLACEHOLDER]%
- False-flag analysis: how often does the 30% macro-deviation threshold flag
  *correct* multi-food meals? (Known behavior: per-100g KB values vs. whole-meal
  macros — discuss threshold calibration.)

## 5.3 Constraint compliance

<!-- [FIGURE 5 GOES HERE: compliance stacked bar] -->
<!-- Pass rates by check type: vegetarian / calorie window / allergens.
Data source: RAGEvaluator.evaluate_batch() over the eval query set. -->

## 5.4 Qualitative examples

<!-- [TABLE 4 / FIGURE 6 GOES HERE: 2-3 worked examples] -->
<!-- Include one dashboard screenshot (Phase 3A) showing the guardrail banner
surfacing a violation to the user — transparency as a feature. -->

<!-- @Kavya: fill 5.1-5.3 after the full-dataset evaluation run.
     @Vartan: qualitative example selection once full KB is integrated. -->
