# CulRAG: A Culturally Grounded Retrieval System for Indian Dietary Guidance

**Authors:** Kavya Sri Meka, Vartan [LAST NAME — @Vartan fill in]
**Target venue:** Frontiers in Artificial Intelligence (primary) · Computers/MDPI (fallback)
**Target length:** 8–10 pages, ~6,500 words, 4–6 figures/tables

<!--
MASTER FILE. Each section lives in its own .md for parallel editing;
this file is the assembly order + status tracker. To produce a single
document: concatenate in the order below (or import into Overleaf and
convert per-section).

  cat abstract.md introduction.md related_work.md methods.md \
      results.md discussion.md conclusion.md > _assembled.md

Status legend: DRAFT = substantive text · STUB = outline only
-->

| # | Section | File | Words | Owner | Status |
|---|---------|------|-------|-------|--------|
| — | Abstract | [abstract.md](abstract.md) | 150 | Kavya | DRAFT (metrics pending) |
| 1 | Introduction | [introduction.md](introduction.md) | 800 | Vartan | STUB |
| 2 | Related Work | [related_work.md](related_work.md) | 1200 | Vartan | STUB |
| 3 | Methods | [methods.md](methods.md) | 1500 | Kavya | **DRAFT** |
| 4 | Results | [results.md](results.md) | 1000 | Kavya | STUB (baseline numbers in) |
| 5 | Discussion | [discussion.md](discussion.md) | 1000 | Both | STUB |
| 6 | Conclusion | [conclusion.md](conclusion.md) | 400 | Kavya | STUB |
| — | References | [references.bib](references.bib) | 16 entries | Both | DRAFT (verify TODOs) |

## Figures & tables plan

| Item | Content | Source | Status |
|------|---------|--------|--------|
| Figure 1 | System architecture | `figures/01_architecture.py` | Script ready |
| Figure 2 | Per-query retrieval metrics | `figures/02_retrieval_metrics.py` | Script ready (baseline data) |
| Table 3 / Fig 3 | Hallucination-detection examples | `figures/03_hallucination.py` | Script ready (real examples) |
| Figure 4 | Regional food coverage | `figures/04_regional_coverage.py` | Script ready (real data) |
| Figure 5 | Constraint compliance | `figures/05_compliance.py` | Script ready (placeholder data) |
| Table 4 / Fig 6 | Example recommendations | `figures/06_examples.py` | Script ready (real examples) |
| Table 1 | Food DB sample (5 rows) | `tables/food_db_sample.csv` | Ready |
| Table 2 | Eval results per query | `tables/eval_results.csv` | Baseline in; replace with production run |

## Pre-submission checklist

- [ ] Replace every `[PLACEHOLDER]` with final numbers (grep for `PLACEHOLDER`)
- [ ] Resolve every `TODO verify` in references.bib against the linked sources
- [ ] Regenerate all figures from the full-dataset evaluation (`python figures/*.py`)
- [ ] Both authors read full assembled draft
- [ ] Word/page limits per venue guidelines
- [ ] Data availability + code availability statements
- [ ] Cover letter
