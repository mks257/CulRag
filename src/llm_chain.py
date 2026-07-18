"""LLM integration layer: builds prompts and generates structured meal recommendations."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from src.config import get_config

logger = logging.getLogger(__name__)

RECOMMENDATION_SCHEMA_HINT = """{
  "meal_name": "string",
  "calories": number,
  "macros": {"protein_g": number, "carbs_g": number, "fat_g": number},
  "portion": "string",
  "reasoning": "string"
}"""


class RAGChain:
    """Combines retrieved food context with an LLM to produce meal recommendations.

    Example:
        >>> chain = RAGChain(model="gpt-4", temperature=0.7)
        >>> prompt = chain.create_prompt("high protein breakfast", retrieved_docs)
        >>> result = chain.generate_recommendation("high protein breakfast", retrieved_docs)
    """

    def __init__(self, model: str = "gpt-4", temperature: float = 0.7) -> None:
        """Initializes the chain.

        Args:
            model: LLM model name. Names starting with "claude" route to
                Anthropic; anything else routes to OpenAI's chat completions.
            temperature: Sampling temperature passed to the LLM provider.
        """
        self.model = model
        self.temperature = temperature
        self._config = get_config()

    def create_prompt(
        self,
        query: str,
        retrieved_foods: List[Dict[str, Any]],
        user_constraints: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Builds the LLM prompt from the user query and retrieved food context.

        Args:
            query: The user's natural-language request (e.g. "high protein
                vegetarian breakfast under 500 calories").
            retrieved_foods: Retriever results, each with ``text`` and
                ``metadata`` keys (see :meth:`src.retriever.VectorRetriever.search`).
            user_constraints: Optional dict of constraints (vegetarian,
                allergies, regional_preference, etc.) to weave into the prompt.

        Returns:
            The fully formatted prompt string.
        """
        context_lines = []
        for item in retrieved_foods:
            meta = item.get("metadata", {})
            context_lines.append(
                f"- {meta.get('food_name', item.get('text', 'unknown'))}: "
                f"{meta.get('calories', '?')} kcal, "
                f"protein {meta.get('protein_g', '?')}g, "
                f"carbs {meta.get('carbs_g', '?')}g, "
                f"fat {meta.get('fat_g', '?')}g, "
                f"region {meta.get('region', 'unknown')}, "
                f"ayurvedic type {meta.get('ayurvedic_type', 'unknown')}"
            )
        context_block = "\n".join(context_lines) or "(no foods retrieved)"

        constraints_block = ""
        if user_constraints:
            constraints_block = f"\nUser constraints: {json.dumps(user_constraints)}\n"

        return f"""You are a culturally-aware Indian nutrition assistant. Using ONLY the
foods listed below, recommend a meal that answers the user's request. Do not
invent foods that are not in the list. Reference Ayurvedic properties when
relevant.

User request: "{query}"
{constraints_block}
Available foods (from the knowledge base):
{context_block}

Respond with a single JSON object matching exactly this schema, no extra text:
{RECOMMENDATION_SCHEMA_HINT}
"""

    def _call_openai(self, prompt: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self._config.openai_api_key)
        response = client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""

    def _call_anthropic(self, prompt: str) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=self._config.anthropic_api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if hasattr(block, "text"))

    def generate_recommendation(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        user_constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generates a structured meal recommendation via the LLM.

        Args:
            query: The user's natural-language request.
            retrieved_docs: Retriever results used as grounding context.
            user_constraints: Optional dietary constraints dict.

        Returns:
            Parsed recommendation dict (see :meth:`format_response`). On LLM
            or parsing failure, returns a dict with an ``"error"`` key instead
            of raising, so callers can degrade gracefully.
        """
        prompt = self.create_prompt(query, retrieved_docs, user_constraints)
        logger.debug("Generated prompt: %s", prompt)

        try:
            if self.model.lower().startswith("claude"):
                raw_output = self._call_anthropic(prompt)
            else:
                raw_output = self._call_openai(prompt)
        except Exception as exc:
            logger.error("LLM call failed: %s", exc)
            return {"error": f"LLM call failed: {exc}"}

        logger.debug("Raw LLM output: %s", raw_output)
        return self.format_response(raw_output)

    def format_response(self, raw_llm_output: str) -> Dict[str, Any]:
        """Parses raw LLM text into the structured recommendation schema.

        Args:
            raw_llm_output: The raw string returned by the LLM, expected to
                contain a JSON object optionally wrapped in prose or code
                fences.

        Returns:
            The parsed dict on success, matching the schema documented in
            :data:`RECOMMENDATION_SCHEMA_HINT`. If parsing fails, returns
            ``{"error": ..., "raw_output": raw_llm_output}``.
        """
        match = re.search(r"\{.*\}", raw_llm_output, re.DOTALL)
        if not match:
            logger.warning("No JSON object found in LLM output")
            return {"error": "No JSON object found in LLM output", "raw_output": raw_llm_output}

        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            logger.warning("Failed to parse LLM output as JSON: %s", exc)
            return {"error": f"Invalid JSON: {exc}", "raw_output": raw_llm_output}

        return parsed
