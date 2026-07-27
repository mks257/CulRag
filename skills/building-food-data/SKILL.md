# Skill: Building Food Data

For creating, extending, or cleaning the food knowledge base — the dataset the retriever
indexes and the guardrails treat as ground truth.

## The data contract (schema of `data/sample_foods.csv`)

Every food row MUST have all columns, in this order:

| Column | Type | Rule |
|---|---|---|
| `food_name` | str | Common English/Indian name, unique, e.g. `Masoor Dal`, `Dosa (plain)` |
| `region` | str | One of: `North`, `South`, `East`, `West` (dominant region of the dish) |
| `vegetarian` | bool | `True`/`False`. Indian context: expect ~95% True |
| `calories` | float | kcal per 100g, from IFCT 2017 where available |
| `protein_g` | float | g per 100g |
| `carbs_g` | float | g per 100g |
| `fat_g` | float | g per 100g |
| `fiber_g` | float | g per 100g |
| `ayurvedic_type` | str | Dosha effect: `Vata/Pitta/Kapha-pacifying`, `-aggravating`, or `Tridoshic` |
| `cooking_method` | str | e.g. `Pressure-cooked`, `Steamed`, `Shallow-fried`, `Deep-fried`, `Raw` |
| `ayurvedic_type_source` | str | Provenance of the dosha label: `llm-inferred`, `classical-text`, or `secondary-compilation`. Makes the cultural signal auditable (see below). |

`region` allowed values: `North`, `South`, `East`, `West`, `Pan-India`.

Sanity rules (reject rows that fail) — enforced by `scripts/validate_foods.py`:
- All macros ≥ 0; `calories` roughly ≈ 4·protein + 4·carbs + 9·fat. The validator
  warns above 25% deviation and hard-errors only on a >3× mismatch (a real data bug).
- No duplicate `food_name` (exact match, case-insensitive).
- Values are per-100g, not per-serving. Mixing bases silently corrupts evaluation.
- Run `python scripts/validate_foods.py` after ANY change; it also checks that every
  `relevant_foods` entry in `data/eval_queries.json` exists verbatim in the dataset.

## Ground truth source: IFCT 2017

- 528 lab-measured Indian raw foods, ~151 nutrient components. Citation and licensing in
  `data/ifct2017/IFCT2017.md` — read it before redistributing anything derived.
- Use IFCT values for raw ingredients. For composite dishes (biryani, dosa), derive from
  ingredient proportions and note the derivation — these are estimates, and the paper must
  not claim lab accuracy for them.
- A third-party machine-readable `ifct2017` package exists; verify its values against the
  official NIN PDFs before trusting it, and check its license.

## Ayurvedic labels

Dosha classifications are traditional, not lab-measured. Source them from consistent
classical references, keep a note of which source per food, and never present them as
nutritional fact in the data or the paper — they are a *cultural grounding* signal.

Provenance is recorded per-row in `ayurvedic_type_source`. The current
`sample_foods.csv` labels are all `llm-inferred` (assigned from general knowledge, not a
cited classical text) — this is disclosed honestly rather than presented as authoritative
(see `IMPROVEMENT_UPDATE.md` §4). When a row's label is verified against a classical or
vetted secondary source, change its `ayurvedic_type_source` to `classical-text` /
`secondary-compilation` and log the source in `DATA_SOURCES.md`. Do this before scaling
past the current 50 rows — provenance is far cheaper to build in than to retrofit.

## Workflow for adding foods

1. Pick foods that improve coverage: underrepresented regions, cooking methods, or the
   non-vegetarian minority — check current distribution with pandas first.
2. Fill every column per the contract; validate with the sanity rules.
3. If a food is referenced in `data/eval_queries.json`, the `food_name` spelling must
   match EXACTLY — the evaluator does exact string matching.
4. After any dataset change, re-run retrieval eval (`evaluating-rag` skill) so metric
   shifts are attributable.

## Scaling to the full IFCT import (Phase 3)

- Keep `sample_foods.csv` untouched as the small fixture for tests and notebooks.
- The full dataset gets its own file; same contract, same validation script.
- Write ONE validation script (`scripts/validate_foods.py` when it exists) that both
  datasets pass through — don't validate by eye at 500+ rows.
