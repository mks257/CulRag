# CulRAG Dataset Improvement Update

Research report: current state of the food dataset, external datasets evaluated
(Hugging Face, Kaggle, GitHub), and a plan for scaling via real sources + grounded
synthetic data. Compiled 2026-07-20.

## 1. What's actually in the repo right now

| File | Content | Problem |
|---|---|---|
| `data/sample_foods.csv` | 50 hand-written Indian foods, full schema (region, vegetarian, 4 macros, fiber, ayurvedic_type, cooking_method) | This is the *entire* knowledge base the retriever indexes. 50 items can't demonstrate "systematic evaluation" — it's a fixture, not a dataset. |
| `data/ifct2017/IFCT2017.md` | Citation, licensing notes, and an acknowledgement string for IFCT 2017 | **No actual IFCT data file exists in the repo.** The paper's claimed ground truth (528 lab-measured foods) is currently a citation, not data. This is the single highest-priority gap — everything downstream (guardrail hallucination checks, macro sanity checks) is only as good as this table, and right now it isn't here. |
| `data/eval_queries.json` | 9 hand-labeled (query → relevant_foods) pairs | Already flagged in `evaluating-rag/SKILL.md` as a smoke test, not an evaluation. Needs to grow to 30+ before any number is publishable. |
| `ayurvedic_type` column | Dosha labels (Vata/Pitta/Kapha-pacifying etc.) on every food | **No cited source anywhere in the repo for these labels.** They read as authoritative but there's no traceable classical or secondary reference behind them — a paper-credibility risk, not just a data-quality one (see §5). |

No validation script exists yet (`building-food-data/SKILL.md` already flags this as
needed for Phase 3).

## 2. External datasets found — direct-use candidates

| Dataset | Size | What it has | License / caveat | Fit for CulRAG |
|---|---|---|---|---|
| **[Indian Nutrient Databank (INDB)](https://www.anuvaad.org.in/indian-nutrient-databank/)** — Anuvaad Solutions | 1,014 recipes + 1,095 individual food items, per-100g and per-serving | Regional recipes across India, built from IFCT 2017 + NIVI 2004 + UK COFID + USDA FDC | Open-access, downloadable as Excel; STATA processing code on [GitHub](https://github.com/lindsayjaacks/Indian-Nutrient-Databank-INDB-); published under CC BY (per the peer-reviewed paper) | **Best single upgrade available.** This is what the IFCT-derivation work should be built on — it already did the ingredient→recipe macro summation that would otherwise need redoing. |
| **[Indian Food 101](https://www.kaggle.com/datasets/nehaprabhavalkar/indian-food-101)** (Kaggle) | 255 dishes | `diet`, `prep_time`, `cook_time`, `flavor_profile`, `course`, `state`, `region` — **no macros** | Public Kaggle dataset, unclear formal license — treat as CC-BY-ish community data | Not a nutrition source. Use to **enrich** existing rows with state/course/flavor metadata via name-matching, not to add new foods. |
| **[Indian Food Nutritional Values (2025)](https://www.kaggle.com/datasets/batthulavinay/indian-food-nutrition)** | 250+ dishes | Calories, macros, and some micronutrients (iron, calcium, vitamins) | Explicitly derived from INDB — a secondary copy, not an independent source | Use only for spot-checking INDB values, not as a second ground truth. |
| **[Indian Recipes: Nutrition & Cooking Method (2026)](https://www.kaggle.com/datasets/kashyap077/indian-recipes-ingredients-nutrition-and-cooking)** | 725 dishes | Recipe ↔ nutrient profile, built by fuzzy-matching a recipe corpus against a nutrition source | Kaggle community dataset | Good precedent for the *fuzzy-matching methodology* needed to merge INDB with recipe-metadata sources like Indian Food 101. |
| **[IFCT2017 Kaggle mirror](https://www.kaggle.com/datasets/gijoe707/ifct2017)** | 528 foods | Third-party machine-readable copy of the actual IFCT tables | **Unverified** — `data/ifct2017/IFCT2017.md` already warns to verify source/licensing before reuse; applies directly here | Use to fill the gap in §1, but spot-check a sample against the official NIN PDF before trusting it as lab-accurate. |

## 3. Reference / methodology sources (not for direct import, but genuinely useful)

- **[FKG.in](https://arxiv.org/abs/2409.00830)** (Ashoka University) — a knowledge graph of
  9,600–25,000+ Indian recipes built with a semi-automated, human-in-the-loop LLM
  curation pipeline. Already in `RELATED_WORK.md` (entries 1–2). The follow-up paper
  ([Enhancing FKG.in](https://arxiv.org/html/2412.05248v2)) describes a **three-agent
  pipeline**: an aggregator that merges IFCT + INDB + Nutritionix in priority order, an
  LLM agent (GPT-3.5) that resolves ingredient ambiguity and multilingual naming, and a
  calculator that sums ingredient composition into recipe-level nutrition. They openly
  admit two weaknesses: no cooking-retention-factor correction, and verification is
  "human-dependent and slow." This is the blueprint for composite-dish derivation work
  here, and a chance to do the retention-factor part better — worth a footnote in
  `paper/methods.md`.
- **[USDA FoodData Central](https://fdc.nal.usda.gov/)** — 300K+ foods, free API and bulk
  download. Not culturally relevant on its own, but it's exactly the kind of **generic,
  non-cultural knowledge base** the `running-experiments/SKILL.md` "Generic-RAG baseline"
  ablation needs — the comparison that isolates whether cultural grounding specifically
  (not just retrieval) drives the results. NutriGen and MetaPlate (already in
  `RELATED_WORK.md`, entries 4–5) both use USDA this way.
- **["What's Not on the Plate?"](https://arxiv.org/html/2509.16286v1)** (2025) — not a
  dataset, a critique. It argues food-computing datasets (including implicitly things
  like FKG.in) are built from scraped, web-standardized recipes and miss
  vernacular/tribal foodways, with unclear consent/attribution when scraping recipe
  blogs. Two implications: (1) a citable motivating reference for the "cultural
  grounding" contribution claim in the paper — evidence the gap being addressed is real
  and recently documented; (2) if future data sourcing scrapes recipe sites the way
  FKG.in did, the same consent/attribution caution applies — worth a line in the paper's
  ethics section.

## 4. Ayurvedic dosha data — the honest finding: there isn't a usable one

A specific search for a structured, food-level dosha dataset found none. What exists
instead:
- Datasets like [DoshaMitra](https://github.com/letsdoitbycode/DoshaMitra) and the
  [Prakriti200 questionnaire dataset](https://arxiv.org/html/2510.06262v1) classify
  **people's constitution** (Vata/Pitta/Kapha body type) from survey answers — wrong
  unit of analysis, not food properties.
- A GitHub JSON dataset of 700+ Ayurvedic herbs exists but covers herbs, not everyday
  foods.

This means the `ayurvedic_type` column in `sample_foods.csv` is currently unsourced, and
no drop-in replacement exists to source it from. Two honest paths, mutually exclusive
per-row, not blended silently:
1. **Manual classification from a cited classical source** (e.g., a specific Ayurvedic
   nutrition text or a vetted secondary compilation) — slow, defensible, small scale.
2. **LLM-assisted classification, explicitly marked as such** — a new column like
   `ayurvedic_type_source: "llm-inferred"` vs `"classical-text"`, with a confidence
   field, and an explicit statement in the paper's limitations section that this is a
   cultural-framing signal, not verified fact (`writing-the-paper/SKILL.md` already
   contains this framing rule — the data needs a column to make it auditable).

## 5. Synthetic data — where it's appropriate and where it's a trap

**Good uses (grounded synthetic data):**
- **Composite-dish nutrition** — derive from real ingredient-level IFCT/INDB values via
  the aggregator→LLM-resolve→sum pattern above, not from an LLM guessing calorie counts
  directly. Every derived value should carry its ingredient breakdown so it's auditable.
- **Eval query expansion** — the current 9 queries need to become 30–50. The right tool
  is the [RAGAS](https://docs.ragas.io/) synthetic testset pattern: generate queries
  *from the actual food dataset* (not from imagination), then run a faithfulness/
  grounding check that rejects any generated query-answer pair not traceable to a real
  row. This is the 2025–2026 consensus pattern across the synthetic-RAG-data literature
  reviewed — "every synthetic answer must be grounded in its cited context," with a
  judge step that rejects ungrounded generations.
- **Guardrail test fixtures** — synthetic "bad" recommendations (a hallucinated food
  name, a plausible-but-wrong macro value) are exactly the right thing to synthesize,
  since the detector is being tested, not the fake food's validity.

**The trap:** don't synthesize new *ground-truth nutrition facts* wholesale (e.g., asking
an LLM to invent macros for 500 foods it wasn't given data for) — that's the
hallucination failure mode the guardrails exist to catch, just moved one step upstream
into the dataset itself. Every nutrition number in the dataset needs to trace to IFCT,
INDB, or an explicit ingredient-sum derivation — never to an LLM's unaided estimate.

## 6. Recommended plan, in order

1. **Pull the real IFCT 2017 table** — either from the Kaggle mirror (spot-checked
   against 20–30 rows of the official NIN PDF) or by contacting NIN directly per the
   licensing note already in the repo. Closes gap #1.
2. **Pull INDB** (Anuvaad, 1,014 recipes) as the second primary source — already
   IFCT-derived and recipe-level, saving the composite-dish derivation work for those
   1,014 dishes.
3. **Merge/dedupe** the two on food name (case-insensitive, following the fuzzy-match
   precedent from the kashyap077 dataset), keeping `sample_foods.csv`'s existing 50 rows
   as the reviewed core.
4. **Enrich with Indian Food 101** metadata (state, course, flavor_profile) by name
   match — free extra columns, zero nutrition risk since it's metadata-only.
5. **For any dish still missing** (not in IFCT or INDB): apply the FKG.in-style
   pipeline — LLM decomposes into ingredients, sum IFCT/INDB values, flag for human
   spot-check (aim for ~10% audited, per the FKG.in paper's own admitted weak spot on
   verification).
6. **Ayurvedic labels**: pick one classical/secondary source and cite it, OR keep
   LLM-inferred labels but add the source/confidence column from §4. Do this before
   scaling past 50 rows — much harder to retrofit provenance onto 500 unsourced labels
   than to build it in now.
7. **Validate everything** against the schema in `skills/building-food-data/SKILL.md`
   with one script (`scripts/validate_foods.py`, not yet written).
8. **Expand `eval_queries.json`** using grounded synthetic generation against the new
   dataset, covering the query-type matrix already defined in
   `skills/evaluating-rag/SKILL.md` (regional, dosha, macro, cooking-method, non-veg
   negative cases).
9. **Log every new source** — add a `DATA_SOURCES.md` ledger (same pattern as
   `RELATED_WORK.md`) recording each dataset's URL, license, and what it was used for,
   since three of the candidates above (Kaggle mirrors, FKG.in) carry licensing caveats
   that need to survive into the paper's data-availability section.
