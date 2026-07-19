# Skill: Writing the Paper

For drafting the CulRAG paper (target: IEEE Access / Frontiers in AI) with claims that
survive review.

## Structure (IEEE Access style)

1. Abstract — problem, approach, headline numbers, one-line contribution
2. Introduction — why cultural grounding in dietary RAG matters; the research question;
   numbered contributions (the 4 from `culrag-context`)
3. Related Work — built FROM `RELATED_WORK.md` ledger entries, grouped by the claim table
   in the `deep-research` skill
4. Method — architecture (pipeline diagram), knowledge base construction (IFCT + Ayurvedic
   labels), guardrail design
5. Experimental Setup — dataset stats, eval query set, metrics definitions (cite standard
   defs), baselines, LLM/config provenance
6. Results — retrieval quality table, safety metrics table, ablations
7. Discussion & Limitations
8. Conclusion

## Claims discipline — every claim must hold

- **Every number traces to a run.** A result in the paper = a script + config + date that
  reproduces it (see `evaluating-rag` provenance rules). No number from a notebook cell
  that no longer exists.
- **Claim only what was measured.** "Reduces hallucinations by X% vs. no-RAG baseline on
  our 30-query eval set" — not "eliminates hallucinations". Rates always come with N.
- **Scope every claim.** Our eval is Indian foods, our query set, our labelers. Say so.
  Overclaiming generality is the top reviewer complaint.
- **The "first" claim** must be worded to survive the counterexamples logged in
  RELATED_WORK.md: "To our knowledge, the first systematic evaluation of…" plus explicit
  differentiation from near-misses.
- **Ayurveda framing:** cultural-appropriateness signal, NOT medical/nutritional evidence.
  Never imply health efficacy of dosha classifications — that's both scientifically
  unsupported and an ethics-review red flag.
- **Composite-dish nutrition values are estimates** (see `building-food-data`) — the
  limitations section must say so.

## Required sections reviewers will check

- **Limitations:** small eval set size, exact-string matching in retrieval eval,
  LLM non-determinism, single-culture scope, Ayurvedic label subjectivity.
- **Ethics/safety:** dietary advice is health-adjacent — state the system is research,
  not medical advice; describe guardrails as harm mitigation, not guarantees.
- **Data availability:** IFCT licensing (see `data/ifct2017/IFCT2017.md`) — we can cite
  and acknowledge; redistributing the compiled DB may need NIN permission. The
  acknowledgement string to use is in that file.
- **Reproducibility:** repo link, config files, eval scripts, model versions.

## Writing mechanics

- One claim per sentence in the abstract and intro; a reviewer skims those first.
- Tables: metric definitions cited, N stated, best results bold, config in caption.
- Every figure/table referenced in text; every citation from the verified ledger only.
- Draft order: Results tables first (forces the experiments to be done), then Method,
  then Related Work, Intro and Abstract LAST.
