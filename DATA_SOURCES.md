# Data Sources Ledger

Provenance and licensing for every dataset in this repo. Keep this current — the
paper's data-availability statement is built from it, and several candidate sources
(see `IMPROVEMENT_UPDATE.md`) carry licensing caveats that must survive into publication.

## In the repo now

### `data/sample_foods.csv` (50 foods)
- **Origin:** Hand-authored development fixture. Nutrition values are realistic
  per-100g approximations consistent with IFCT 2017 ranges; they are **not** extracted
  from the official IFCT tables and must not be presented as lab-measured.
- **`ayurvedic_type`:** `llm-inferred` for all 50 rows (assigned from general knowledge,
  not a cited classical source). Recorded per-row in the `ayurvedic_type_source` column
  so the cultural signal is auditable rather than presented as authoritative
  (see `IMPROVEMENT_UPDATE.md` §4).
- **License:** Repository license (project-authored content).
- **Validation:** `python scripts/validate_foods.py` (schema + macro sanity + eval grounding).

### `data/eval_queries.json` (30 queries)
- **Origin:** Hand-authored, labeled from dataset attributes (region, dosha, macros,
  cooking method), not from retriever output (avoids circularity). Every `relevant_foods`
  entry is verified to exist verbatim in `sample_foods.csv` by `scripts/validate_foods.py`.
- **License:** Repository license.

### `data/ifct2017/IFCT2017.md`
- **Origin:** Citation, access, and licensing notes for IFCT 2017 (Longvah et al., 2017,
  National Institute of Nutrition). **No IFCT data file is present** — this is the
  highest-priority data gap (`IMPROVEMENT_UPDATE.md` §1).
- **License:** NIN permits academic use with acknowledgement; redistributing a compiled
  electronic database may require written NIN permission. Resolve before committing any
  IFCT-derived table to this public repo.

## Evaluated but NOT yet imported (pending licensing decision — Vartan, data lead)

| Source | What | License note | Status |
|---|---|---|---|
| Indian Nutrient Databank (INDB), Anuvaad | 1,014 recipes + 1,095 items, IFCT-derived | CC BY per peer-reviewed paper — verify | Candidate primary source (`IMPROVEMENT_UPDATE.md` §2) |
| IFCT2017 Kaggle mirror | 528 foods, third-party machine-readable | Unverified — spot-check vs. NIN PDF + confirm license | Candidate to close the IFCT gap |
| Indian Food 101 (Kaggle) | 255 dishes, metadata (state/course/flavor), no macros | Community dataset, unclear license | Metadata enrichment only |
| USDA FoodData Central | 300K+ foods | Public domain | Generic-RAG baseline (ablation), not cultural KB |

**Rule:** every nutrition number in a committed dataset must trace to IFCT, INDB, or an
explicit auditable ingredient-sum derivation — never to an unaided LLM estimate
(`IMPROVEMENT_UPDATE.md` §5).
