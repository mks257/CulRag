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

Sanity rules (reject rows that fail):
- All macros ≥ 0; `calories` roughly ≈ 4·protein + 4·carbs + 9·fat (±25% — fiber and
  measurement variance make it inexact, but a 3× mismatch is a data bug).
- No duplicate `food_name` (exact match, case-insensitive).
- Values are per-100g, not per-serving. Mixing bases silently corrupts evaluation.

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
