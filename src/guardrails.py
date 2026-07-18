"""Constraint validation and basic hallucination detection for RAG recommendations."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Fallback keyword list used when no knowledge base is available for a
# vegetarian check. Indian-context sample data is ~95% vegetarian, so
# non-veg items are the exception worth flagging explicitly.
NON_VEGETARIAN_KEYWORDS = ["chicken", "mutton", "fish", "egg", "prawn", "shrimp", "meat", "beef", "pork"]

# Relative macro deviation (vs. the matched knowledge-base entry) above which
# a recommendation is flagged as a possible hallucination.
MACRO_DEVIATION_THRESHOLD = 0.3


class GuardrailChecker:
    """Validates LLM-generated meal recommendations against user constraints.

    Example:
        >>> checker = GuardrailChecker()
        >>> result = checker.run_all_checks(recommendation, {
        ...     "vegetarian": True,
        ...     "target_calories": (1500, 2000),
        ...     "allergies": ["peanuts"],
        ... })
        >>> result["passed"]
        True
    """

    def __init__(self, llm_model: str = "gpt-4", knowledge_base: Optional[List[Dict[str, Any]]] = None) -> None:
        """Initializes the checker.

        Args:
            llm_model: Reserved for future LLM-assisted checks (e.g. semantic
                hallucination detection); not currently used for rule-based checks.
            knowledge_base: Optional default list of food records (dicts with
                at least ``food_name``, ``vegetarian``, ``calories``,
                ``protein_g``, ``carbs_g``, ``fat_g``) used by
                :meth:`detect_hallucinations` when no override is passed.
        """
        self.llm_model = llm_model
        self.knowledge_base = knowledge_base or []

    def check_vegetarian(
        self, recommendation: Dict[str, Any], user_constraints: Dict[str, Any]
    ) -> Optional[str]:
        """Checks whether a recommendation respects a vegetarian constraint.

        Args:
            recommendation: LLM recommendation dict with at least ``meal_name``.
            user_constraints: Constraints dict; only acts if
                ``user_constraints.get("vegetarian")`` is truthy.

        Returns:
            A violation message string if a non-vegetarian food is detected,
            otherwise None.
        """
        if not user_constraints.get("vegetarian"):
            return None

        meal_name = str(recommendation.get("meal_name", "")).lower()

        for entry in self.knowledge_base:
            food_name = str(entry.get("food_name", "")).lower()
            if food_name and food_name in meal_name and not _to_bool(entry.get("vegetarian", True)):
                return f"Non-vegetarian food detected: {entry.get('food_name')}"

        for keyword in NON_VEGETARIAN_KEYWORDS:
            if keyword in meal_name:
                return f"Non-vegetarian keyword detected in meal name: '{keyword}'"

        return None

    def check_calories(
        self, recommendation: Dict[str, Any], target_range: Tuple[float, float]
    ) -> Optional[str]:
        """Checks whether the recommended calorie count falls within a target range.

        Args:
            recommendation: LLM recommendation dict with a ``calories`` field.
            target_range: ``(min_calories, max_calories)`` inclusive bounds.

        Returns:
            A violation message if calories are missing or out of range,
            otherwise None.
        """
        calories = recommendation.get("calories")
        if calories is None:
            return "No calorie value present in recommendation"

        low, high = target_range
        if not (low <= calories <= high):
            return f"Calories {calories} outside target range ({low}, {high})"

        return None

    def check_allergies(
        self, recommendation: Dict[str, Any], allergies_list: List[str]
    ) -> List[str]:
        """Checks the recommendation text for mentions of allergens.

        Args:
            recommendation: LLM recommendation dict. Text fields checked are
                ``meal_name`` and ``reasoning``.
            allergies_list: List of allergen keywords to search for (e.g.
                ``["peanuts", "shellfish"]``).

        Returns:
            A list of violation messages, one per matched allergen. Empty if
            none are found.
        """
        text = f"{recommendation.get('meal_name', '')} {recommendation.get('reasoning', '')}".lower()
        violations = []
        for allergen in allergies_list:
            if allergen.lower() in text:
                violations.append(f"Potential allergen detected: {allergen}")
        return violations

    def detect_hallucinations(
        self, recommendation: Dict[str, Any], knowledge_base: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Flags foods or macros that don't correspond to the knowledge base.

        Splits ``meal_name`` on common separators ("with", "and", ",") into
        candidate food components, then checks each against the knowledge
        base by substring match. Components with no match are flagged as
        unknown foods. If a component does match, its macros are compared
        against the recommendation's overall macros and flagged if they
        deviate by more than :data:`MACRO_DEVIATION_THRESHOLD`.

        Args:
            recommendation: LLM recommendation dict.
            knowledge_base: List of food records to validate against. Falls
                back to ``self.knowledge_base`` if not provided.

        Returns:
            A list of hallucination flag strings. Empty if none are found.
        """
        kb = knowledge_base if knowledge_base is not None else self.knowledge_base
        if not kb:
            logger.warning("No knowledge base provided; skipping hallucination detection")
            return []

        meal_name = str(recommendation.get("meal_name", ""))
        components = [c.strip() for c in re.split(r"\bwith\b|\band\b|,", meal_name, flags=re.IGNORECASE) if c.strip()]
        if not components:
            components = [meal_name]

        flags: List[str] = []
        kb_names = [str(entry.get("food_name", "")).lower() for entry in kb]

        for component in components:
            component_lower = component.lower()
            matched_entry = next(
                (entry for entry, name in zip(kb, kb_names) if name and (name in component_lower or component_lower in name)),
                None,
            )
            if matched_entry is None:
                flags.append(f"hallucination: unknown_food '{component}'")
                continue

            macros = recommendation.get("macros", {})
            for macro_key, kb_key in (("protein_g", "protein_g"), ("carbs_g", "carbs_g"), ("fat_g", "fat_g")):
                rec_value = macros.get(macro_key)
                kb_value = matched_entry.get(kb_key)
                if rec_value is None or kb_value in (None, 0):
                    continue
                deviation = abs(rec_value - float(kb_value)) / float(kb_value)
                if deviation > MACRO_DEVIATION_THRESHOLD:
                    flags.append(
                        f"hallucination: {component} {macro_key} deviates {deviation:.0%} from knowledge base"
                    )

        return flags

    def run_all_checks(
        self,
        recommendation: Dict[str, Any],
        constraints_dict: Dict[str, Any],
        knowledge_base: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Runs every applicable check and aggregates the results.

        Args:
            recommendation: LLM recommendation dict to validate.
            constraints_dict: May include ``vegetarian`` (bool),
                ``target_calories`` (tuple), and ``allergies`` (list).
            knowledge_base: Optional override for hallucination detection.

        Returns:
            Dict with keys ``passed`` (bool), ``violations`` (list of str),
            ``flags`` (list of str), and ``confidence`` (float in [0, 1]).
        """
        violations: List[str] = []
        flags: List[str] = []

        if "error" in recommendation:
            return {
                "passed": False,
                "violations": [f"LLM generation error: {recommendation['error']}"],
                "flags": [],
                "confidence": 0.0,
            }

        veg_violation = self.check_vegetarian(recommendation, constraints_dict)
        if veg_violation:
            violations.append(veg_violation)

        target_calories = constraints_dict.get("target_calories")
        if target_calories:
            cal_violation = self.check_calories(recommendation, target_calories)
            if cal_violation:
                violations.append(cal_violation)

        allergies = constraints_dict.get("allergies")
        if allergies:
            violations.extend(self.check_allergies(recommendation, allergies))

        flags.extend(self.detect_hallucinations(recommendation, knowledge_base))

        confidence = max(0.0, 1.0 - 0.25 * len(violations) - 0.1 * len(flags))

        result = {
            "passed": len(violations) == 0,
            "violations": violations,
            "flags": flags,
            "confidence": round(confidence, 2),
        }
        logger.info("Guardrail check result: %s", result)
        return result


def _to_bool(value: Any) -> bool:
    """Coerces common truthy/falsy representations (including CSV strings) to bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return bool(value)
