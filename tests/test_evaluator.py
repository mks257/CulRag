"""Unit tests for RAGEvaluator. Fully offline: no vector DB or LLM calls."""

from src.evaluator import RAGEvaluator


class FakeRetriever:
    """Minimal stand-in for VectorRetriever.search(), no embeddings involved."""

    def __init__(self, responses):
        self._responses = responses

    def search(self, query, k=5):
        return self._responses[query][:k]


class FakeCulRAG:
    """Minimal stand-in for CulRAG.recommend(), no LLM calls involved."""

    def __init__(self, responses):
        self._responses = responses

    def recommend(self, query, user_constraints=None):
        return self._responses[query]


def _doc(food_name):
    return {"metadata": {"food_name": food_name}}


def test_precision_at_k_full_hit():
    evaluator = RAGEvaluator()
    assert evaluator.precision_at_k(["A", "B"], ["A", "B"], k=2) == 1.0


def test_precision_at_k_partial_hit():
    evaluator = RAGEvaluator()
    assert evaluator.precision_at_k(["A", "X"], ["A", "B"], k=2) == 0.5


def test_precision_at_k_empty_retrieved():
    evaluator = RAGEvaluator()
    assert evaluator.precision_at_k([], ["A"], k=5) == 0.0


def test_recall_at_k_full_recall():
    evaluator = RAGEvaluator()
    assert evaluator.recall_at_k(["A", "B", "C"], ["A", "B"], k=3) == 1.0


def test_recall_at_k_partial_recall():
    evaluator = RAGEvaluator()
    assert evaluator.recall_at_k(["A"], ["A", "B"], k=1) == 0.5


def test_recall_at_k_empty_relevant():
    evaluator = RAGEvaluator()
    assert evaluator.recall_at_k(["A"], [], k=1) == 0.0


def test_reciprocal_rank_first_hit():
    evaluator = RAGEvaluator()
    assert evaluator.reciprocal_rank(["A", "B"], ["A"]) == 1.0


def test_reciprocal_rank_third_hit():
    evaluator = RAGEvaluator()
    assert evaluator.reciprocal_rank(["X", "Y", "A"], ["A"]) == 1 / 3


def test_reciprocal_rank_no_hit():
    evaluator = RAGEvaluator()
    assert evaluator.reciprocal_rank(["X", "Y"], ["A"]) == 0.0


def test_evaluate_retrieval_aggregates_across_queries():
    evaluator = RAGEvaluator()
    retriever = FakeRetriever(
        {
            "q1": [_doc("A"), _doc("B")],
            "q2": [_doc("X"), _doc("A")],
        }
    )
    test_cases = [
        {"query": "q1", "relevant_foods": ["A"]},
        {"query": "q2", "relevant_foods": ["A"]},
    ]

    report = evaluator.evaluate_retrieval(retriever, test_cases, k=2)

    assert len(report["per_query"]) == 2
    assert report["per_query"][0]["reciprocal_rank"] == 1.0
    assert report["per_query"][1]["reciprocal_rank"] == 0.5
    assert report["mean_reciprocal_rank"] == 0.75


def test_evaluate_recommendation_normal_case():
    evaluator = RAGEvaluator()
    recommendation_result = {
        "recommendation": {"meal_name": "Idli"},
        "guardrails": {"passed": True, "violations": [], "flags": [], "confidence": 0.9},
    }

    metrics = evaluator.evaluate_recommendation(recommendation_result)

    assert metrics == {
        "passed": True,
        "num_violations": 0,
        "num_hallucination_flags": 0,
        "confidence": 0.9,
    }


def test_evaluate_recommendation_error_case():
    evaluator = RAGEvaluator()
    metrics = evaluator.evaluate_recommendation({"error": "retrieval failed"})

    assert metrics["passed"] is False
    assert metrics["error"] == "retrieval failed"


def test_evaluate_batch_aggregates():
    evaluator = RAGEvaluator()
    culrag = FakeCulRAG(
        {
            "q1": {"guardrails": {"passed": True, "violations": [], "flags": [], "confidence": 0.9}},
            "q2": {"guardrails": {"passed": False, "violations": ["v"], "flags": ["f"], "confidence": 0.4}},
        }
    )
    test_cases = [{"query": "q1"}, {"query": "q2"}]

    report = evaluator.evaluate_batch(culrag, test_cases)

    assert report["pass_rate"] == 0.5
    assert report["hallucination_rate"] == 0.5
    assert report["mean_confidence"] == 0.65


def test_generate_report_contains_key_metrics():
    evaluator = RAGEvaluator()
    results = {
        "per_query": [{}],
        "mean_precision_at_k": 0.8,
        "mean_recall_at_k": 0.6,
        "mean_reciprocal_rank": 1.0,
        "k": 5,
    }

    report = evaluator.generate_report(results)

    assert "Precision@5: 0.800" in report
    assert "Recall@5:    0.600" in report
