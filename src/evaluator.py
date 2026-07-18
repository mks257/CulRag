"""Evaluation metrics for CulRAG: retrieval quality and recommendation safety.

Two concerns are evaluated separately, matching the paper's research question:
- Retrieval quality: precision@k, recall@k, and mean reciprocal rank (MRR)
  against a hand-labeled set of (query, relevant_foods) pairs.
- Recommendation safety: hallucination rate and constraint-violation rate,
  aggregated from :class:`~src.guardrails.GuardrailChecker` output across a
  batch of :meth:`~src.rag_pipeline.CulRAG.recommend` calls.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RAGEvaluator:
    """Computes retrieval and recommendation-safety metrics for CulRAG.

    Example:
        >>> evaluator = RAGEvaluator()
        >>> test_cases = [
        ...     {"query": "South Indian breakfast", "relevant_foods": ["Idli", "Dosa (plain)"]},
        ... ]
        >>> report = evaluator.evaluate_retrieval(retriever, test_cases, k=5)
        >>> report["mean_precision_at_k"]
    """

    @staticmethod
    def precision_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
        """Fraction of the top-k retrieved items that are relevant.

        Args:
            retrieved: Ranked list of retrieved food names (best first).
            relevant: Ground-truth set of relevant food names.
            k: Cutoff rank to evaluate at.

        Returns:
            Precision@k in [0, 1]. Returns 0.0 if ``retrieved`` is empty.
        """
        top_k = retrieved[:k]
        if not top_k:
            return 0.0
        relevant_set = set(relevant)
        hits = sum(1 for item in top_k if item in relevant_set)
        return hits / len(top_k)

    @staticmethod
    def recall_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
        """Fraction of all relevant items captured within the top-k retrieved.

        Args:
            retrieved: Ranked list of retrieved food names (best first).
            relevant: Ground-truth set of relevant food names.
            k: Cutoff rank to evaluate at.

        Returns:
            Recall@k in [0, 1]. Returns 0.0 if ``relevant`` is empty.
        """
        if not relevant:
            return 0.0
        top_k = set(retrieved[:k])
        relevant_set = set(relevant)
        hits = len(top_k & relevant_set)
        return hits / len(relevant_set)

    @staticmethod
    def reciprocal_rank(retrieved: List[str], relevant: List[str]) -> float:
        """Reciprocal rank of the first relevant item in the retrieved list.

        Args:
            retrieved: Ranked list of retrieved food names (best first).
            relevant: Ground-truth set of relevant food names.

        Returns:
            ``1 / rank`` of the first hit (1-indexed), or 0.0 if no relevant
            item appears in ``retrieved`` at all.
        """
        relevant_set = set(relevant)
        for rank, item in enumerate(retrieved, start=1):
            if item in relevant_set:
                return 1.0 / rank
        return 0.0

    def evaluate_retrieval(
        self, retriever: Any, test_cases: List[Dict[str, Any]], k: int = 5
    ) -> Dict[str, Any]:
        """Runs a labeled test set through a retriever and scores the results.

        Args:
            retriever: An object exposing ``search(query, k) -> List[Dict]``
                where each result has a ``metadata`` dict containing
                ``food_name`` (see :class:`~src.retriever.VectorRetriever`).
            test_cases: List of dicts with ``query`` (str) and
                ``relevant_foods`` (List[str]) keys.
            k: Number of results to retrieve and evaluate per query.

        Returns:
            Dict with ``per_query`` (list of per-case metrics) and aggregate
            keys ``mean_precision_at_k``, ``mean_recall_at_k``, ``mean_reciprocal_rank``.
        """
        per_query = []
        for case in test_cases:
            query = case["query"]
            relevant = case["relevant_foods"]
            results = retriever.search(query, k=k)
            retrieved_names = [r["metadata"].get("food_name", r.get("text", "")) for r in results]

            per_query.append(
                {
                    "query": query,
                    "retrieved": retrieved_names,
                    "relevant": relevant,
                    "precision_at_k": self.precision_at_k(retrieved_names, relevant, k),
                    "recall_at_k": self.recall_at_k(retrieved_names, relevant, k),
                    "reciprocal_rank": self.reciprocal_rank(retrieved_names, relevant),
                }
            )

        n = len(per_query) or 1
        result = {
            "per_query": per_query,
            "mean_precision_at_k": sum(q["precision_at_k"] for q in per_query) / n,
            "mean_recall_at_k": sum(q["recall_at_k"] for q in per_query) / n,
            "mean_reciprocal_rank": sum(q["reciprocal_rank"] for q in per_query) / n,
            "k": k,
        }
        logger.info(
            "Retrieval eval: P@%d=%.3f R@%d=%.3f MRR=%.3f (n=%d queries)",
            k, result["mean_precision_at_k"], k, result["mean_recall_at_k"],
            result["mean_reciprocal_rank"], len(per_query),
        )
        return result

    def evaluate_recommendation(self, recommendation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts safety metrics from a single :meth:`CulRAG.recommend` output.

        Args:
            recommendation_result: The dict returned by
                :meth:`~src.rag_pipeline.CulRAG.recommend`, containing a
                ``guardrails`` key.

        Returns:
            Dict with ``passed`` (bool), ``num_violations`` (int),
            ``num_hallucination_flags`` (int), and ``confidence`` (float).
            If the input has a top-level ``"error"`` key (retrieval failure),
            returns ``{"passed": False, "num_violations": 0,
            "num_hallucination_flags": 0, "confidence": 0.0, "error": ...}``.
        """
        if "error" in recommendation_result:
            return {
                "passed": False,
                "num_violations": 0,
                "num_hallucination_flags": 0,
                "confidence": 0.0,
                "error": recommendation_result["error"],
            }

        guardrails = recommendation_result.get("guardrails", {})
        return {
            "passed": guardrails.get("passed", False),
            "num_violations": len(guardrails.get("violations", [])),
            "num_hallucination_flags": len(guardrails.get("flags", [])),
            "confidence": guardrails.get("confidence", 0.0),
        }

    def evaluate_batch(
        self, culrag: Any, test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Runs a batch of queries through a live CulRAG instance and aggregates safety metrics.

        Args:
            culrag: A :class:`~src.rag_pipeline.CulRAG` instance (or any object
                exposing ``recommend(query, constraints) -> Dict``).
            test_cases: List of dicts with ``query`` (str) and optional
                ``constraints`` (Dict) keys.

        Returns:
            Dict with ``per_query`` (list of per-case safety metrics) and
            aggregate keys ``pass_rate``, ``hallucination_rate`` (fraction of
            recommendations with at least one flag), and ``mean_confidence``.
        """
        per_query = []
        for case in test_cases:
            query = case["query"]
            constraints = case.get("constraints")
            result = culrag.recommend(query, user_constraints=constraints)
            metrics = self.evaluate_recommendation(result)
            per_query.append({"query": query, **metrics})

        n = len(per_query) or 1
        hallucinated = sum(1 for q in per_query if q["num_hallucination_flags"] > 0)
        result = {
            "per_query": per_query,
            "pass_rate": sum(1 for q in per_query if q["passed"]) / n,
            "hallucination_rate": hallucinated / n,
            "mean_confidence": sum(q["confidence"] for q in per_query) / n,
        }
        logger.info(
            "Batch eval: pass_rate=%.2f hallucination_rate=%.2f mean_confidence=%.2f (n=%d)",
            result["pass_rate"], result["hallucination_rate"], result["mean_confidence"], len(per_query),
        )
        return result

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Formats an evaluation result dict as a human-readable text report.

        Args:
            results: Output of :meth:`evaluate_retrieval` or :meth:`evaluate_batch`.

        Returns:
            A multi-line summary string.
        """
        lines = ["CulRAG Evaluation Report", "=" * 24]

        if "mean_precision_at_k" in results:
            k = results.get("k", "?")
            lines.append(f"Retrieval (k={k}):")
            lines.append(f"  Mean Precision@{k}: {results['mean_precision_at_k']:.3f}")
            lines.append(f"  Mean Recall@{k}:    {results['mean_recall_at_k']:.3f}")
            lines.append(f"  Mean Reciprocal Rank: {results['mean_reciprocal_rank']:.3f}")

        if "pass_rate" in results:
            lines.append("Recommendation safety:")
            lines.append(f"  Pass rate: {results['pass_rate']:.1%}")
            lines.append(f"  Hallucination rate: {results['hallucination_rate']:.1%}")
            lines.append(f"  Mean confidence: {results['mean_confidence']:.2f}")

        lines.append(f"\nEvaluated {len(results.get('per_query', []))} queries.")
        return "\n".join(lines)
