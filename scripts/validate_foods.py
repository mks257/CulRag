#!/usr/bin/env python3
"""Validate a CulRAG food dataset (and optionally the eval query set) against the data contract.

The single validation gate referenced by `skills/building-food-data/SKILL.md`:
run it on every dataset change so nobody validates 500+ rows by eye. Designed
for CI — exits non-zero if any hard error is found (warnings do not fail).

Usage:
    python scripts/validate_foods.py
    python scripts/validate_foods.py --foods data/sample_foods.csv --queries data/eval_queries.json
    python scripts/validate_foods.py --foods data/indian_foods_full.csv --strict

Checks (hard errors unless noted):
  - All contract columns present, in order.
  - No duplicate food_name (case-insensitive).
  - vegetarian is a boolean.
  - region in the allowed set; ayurvedic_type matches the dosha grammar.
  - All macros and calories are non-negative numbers.
  - ayurvedic_type_source (if present) is one of the allowed provenance values.
  - Calorie sanity: kcal vs. 4*protein + 4*carbs + 9*fat. Warn above 25%
    deviation; hard-error only on a >3x mismatch (a genuine data bug, per the
    data-contract skill). --strict promotes the 25% warning to an error.
  - Eval grounding (when --queries is given): every relevant_food exists
    verbatim in the dataset (the evaluator does exact string matching).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent

CONTRACT_COLUMNS = [
    "food_name", "region", "vegetarian", "calories",
    "protein_g", "carbs_g", "fat_g", "fiber_g",
    "ayurvedic_type", "cooking_method",
]
MACRO_COLUMNS = ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g"]

ALLOWED_REGIONS = {"North", "South", "East", "West", "Pan-India"}
ALLOWED_DOSHAS = {"Vata", "Pitta", "Kapha"}
ALLOWED_DOSHA_EFFECTS = {"pacifying", "aggravating"}
ALLOWED_SOURCE_VALUES = {"llm-inferred", "classical-text", "secondary-compilation"}

CALORIE_WARN_RATIO = 0.25   # relative deviation that triggers a warning
CALORIE_ERROR_FACTOR = 3.0  # absolute factor that triggers a hard error


class Report:
    """Accumulates validation errors and warnings."""

    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def ok(self) -> bool:
        return not self.errors


def _valid_ayurvedic_type(value: str) -> bool:
    """True if value is 'Tridoshic' or '<Dosha>-<pacifying|aggravating>'."""
    if value == "Tridoshic":
        return True
    if "-" not in value:
        return False
    dosha, _, effect = value.partition("-")
    return dosha in ALLOWED_DOSHAS and effect in ALLOWED_DOSHA_EFFECTS


def validate_foods(foods_path: Path, strict: bool, report: Report) -> pd.DataFrame | None:
    """Validates the food dataset, returning the DataFrame (or None if unreadable)."""
    try:
        df = pd.read_csv(foods_path)
    except Exception as exc:  # noqa: BLE001 - surface any read failure as one error
        report.error(f"Cannot read {foods_path}: {exc}")
        return None

    # Column contract: required columns present and in the contract order.
    actual_leading = list(df.columns[: len(CONTRACT_COLUMNS)])
    if actual_leading != CONTRACT_COLUMNS:
        report.error(
            "Column contract violated.\n"
            f"  expected first {len(CONTRACT_COLUMNS)} columns: {CONTRACT_COLUMNS}\n"
            f"  got:                                {actual_leading}"
        )
        return df  # further per-column checks would be noise if the schema is wrong

    # Duplicate names (case-insensitive).
    lowered = df["food_name"].str.lower()
    dupes = lowered[lowered.duplicated()].unique()
    for name in dupes:
        report.error(f"Duplicate food_name (case-insensitive): {name!r}")

    for row in df.itertuples():
        name = row.food_name

        if str(row.region) not in ALLOWED_REGIONS:
            report.error(f"{name}: region {row.region!r} not in {sorted(ALLOWED_REGIONS)}")

        if not isinstance(row.vegetarian, (bool,)) and str(row.vegetarian) not in ("True", "False"):
            report.error(f"{name}: vegetarian {row.vegetarian!r} is not a boolean")

        for col in MACRO_COLUMNS:
            val = getattr(row, col)
            if not isinstance(val, (int, float)) or pd.isna(val) or val < 0:
                report.error(f"{name}: {col} {val!r} is not a non-negative number")

        if not _valid_ayurvedic_type(str(row.ayurvedic_type)):
            report.error(f"{name}: ayurvedic_type {row.ayurvedic_type!r} does not match the dosha grammar")

        # Calorie sanity (only when macros are usable numbers).
        try:
            implied = 4 * row.protein_g + 4 * row.carbs_g + 9 * row.fat_g
            stated = row.calories
            if stated > 0 and implied > 0:
                ratio = stated / implied
                deviation = abs(stated - implied) / implied
                if ratio > CALORIE_ERROR_FACTOR or ratio < 1 / CALORIE_ERROR_FACTOR:
                    report.error(
                        f"{name}: calories {stated} vs implied {implied:.0f} "
                        f"(>{CALORIE_ERROR_FACTOR:.0f}x mismatch — likely a data bug)"
                    )
                elif deviation > CALORIE_WARN_RATIO:
                    msg = (f"{name}: calories {stated} deviate {deviation:.0%} from implied "
                           f"{implied:.0f} (4P+4C+9F)")
                    report.error(msg) if strict else report.warn(msg)
        except TypeError:
            pass  # already reported by the macro-type check above

    # Optional provenance column.
    if "ayurvedic_type_source" in df.columns:
        bad = set(df["ayurvedic_type_source"].dropna().unique()) - ALLOWED_SOURCE_VALUES
        if bad:
            report.error(f"ayurvedic_type_source has unknown values {sorted(bad)}; "
                         f"allowed: {sorted(ALLOWED_SOURCE_VALUES)}")
    else:
        report.warn("No ayurvedic_type_source column — dosha labels have no recorded provenance "
                    "(see IMPROVEMENT_UPDATE.md §4)")

    return df


def validate_queries(queries_path: Path, foods: pd.DataFrame, report: Report) -> None:
    """Checks that every relevant_food in the eval set exists verbatim in the dataset."""
    try:
        with open(queries_path) as f:
            cases = json.load(f)
    except Exception as exc:  # noqa: BLE001
        report.error(f"Cannot read {queries_path}: {exc}")
        return

    known = set(foods["food_name"])
    for i, case in enumerate(cases):
        if "query" not in case or "relevant_foods" not in case:
            report.error(f"Query #{i}: missing 'query' or 'relevant_foods'")
            continue
        if not case["relevant_foods"]:
            report.error(f"Query {case['query']!r}: empty relevant_foods")
        for food in case["relevant_foods"]:
            if food not in known:
                report.error(
                    f"Query {case['query']!r}: relevant food {food!r} not found verbatim "
                    "in the dataset (exact-match evaluation would silently score it wrong)"
                )
    print(f"  eval set: {len(cases)} queries checked against {len(known)} foods")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a CulRAG food dataset.")
    parser.add_argument("--foods", type=Path, default=REPO_ROOT / "data" / "sample_foods.csv")
    parser.add_argument("--queries", type=Path, default=REPO_ROOT / "data" / "eval_queries.json",
                        help="Eval query set to check for grounding (pass 'none' to skip)")
    parser.add_argument("--strict", action="store_true",
                        help="Promote calorie-deviation warnings (>25%%) to errors")
    args = parser.parse_args()

    report = Report()
    print(f"Validating {args.foods} ...")
    foods = validate_foods(args.foods, args.strict, report)

    if foods is not None and str(args.queries).lower() != "none" and Path(args.queries).exists():
        validate_queries(args.queries, foods, report)

    for w in report.warnings:
        print(f"  WARN  {w}")
    for e in report.errors:
        print(f"  ERROR {e}")

    n_rows = 0 if foods is None else len(foods)
    if report.ok():
        print(f"\nPASS — {n_rows} foods, {len(report.warnings)} warning(s), 0 errors.")
        return 0
    print(f"\nFAIL — {n_rows} foods, {len(report.warnings)} warning(s), {len(report.errors)} error(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
