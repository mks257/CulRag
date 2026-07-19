# 6. Discussion

<!-- Target: ~1000 words. Status: OUTLINE STUB — both authors. -->

## 6.1 What worked

<!-- ~200 words.
- Metadata-preserving indexing: structured attributes survive retrieval, enabling
  exact-value guardrail checks instead of text re-parsing.
- Separation of retrieval and safety evaluation localized failures precisely.
- Injectable dependencies (embeddings, LLM clients) made the whole pipeline
  testable offline — 42 unit tests, no API costs in CI.
- Transparent guardrails surfaced to end users (dashboard banner) rather than
  silently filtering. -->

## 6.2 Limitations

<!-- ~250 words. BE HONEST — reviewers will check.
- Development KB is 50 foods; full IFCT integration in progress.
- 9 hand-labeled eval queries; ground truth authored by the developers (bias risk).
- Baseline numbers use deterministic hash embeddings (pipeline validation only).
- Hallucination detection is rule-based; the 30% macro-deviation threshold
  over-flags composed meals (per-100g KB values vs. whole-meal totals) —
  quantify the false-flag rate in 5.2.
- Ayurvedic classifications are coarse (single label per food) and not
  clinically validated.
- No user study yet; no comparison against registered dietitians. -->

## 6.3 Comparison to related approaches

<!-- ~250 words.
- vs. Graph-RAG for Indian Thali [@thaligraphrag2026]: they use structured graphs;
  we show a simpler vector-RAG + guardrails pipeline is viable and easier to
  reproduce; discuss trade-offs (multi-hop reasoning vs. engineering cost).
- vs. USDA-anchored systems [@khamesian2025nutrigen; @metaplate2025]: cultural
  grounding as the differentiator; note their evaluation methodology we adopted.
- vs. learned safety critics: auditability argument for rule-based checks in
  regulated domains. -->

## 6.4 Implications

<!-- ~150 words.
- Cultural adaptation is an architecture question, not just a data question:
  region/Ayurvedic metadata changed retrieval, prompting, AND validation.
- The demo-mode pattern (identical code path, offline dependencies) is a
  reusable recipe for health-AI systems that must be tested without exposing
  real users or spending API budget. -->

## 6.5 Future work

<!-- ~150 words.
- Full IFCT 2017 + 200+ regional recipes (in progress, @Vartan).
- Pilot user study via the released dashboard (feedback collection already built).
- Embedding ablations; fine-tuned nutrition-domain embeddings.
- Learned hallucination detection calibrated against the rule-based baseline.
- Extension to other under-served cuisines. -->
