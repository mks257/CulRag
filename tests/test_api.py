"""Unit tests for the FastAPI backend. CulRAG is faked - no vector DB or LLM calls.

The TestClient is used WITHOUT entering its context manager, so the app's
lifespan (which indexes the real knowledge base) never runs; each test wires
a FakeCulRAG into the service directly.
"""

import json

import pytest
from fastapi.testclient import TestClient

import src.api as api
from src.api import app


def _food(name, **overrides):
    metadata = {
        "food_name": name,
        "calories": 150,
        "protein_g": 8.0,
        "carbs_g": 20.0,
        "fat_g": 4.0,
        "region": "South",
        "vegetarian": True,
        "ayurvedic_type": "Tridoshic",
        "cooking_method": "Steamed",
    }
    metadata.update(overrides)
    return {"id": name, "text": name, "metadata": metadata, "score": 0.9}


class FakeGuardrails:
    def run_all_checks(self, recommendation, constraints, knowledge_base):
        return {"passed": True, "violations": [], "flags": [], "confidence": 0.95}


class FakeCulRAG:
    def __init__(self, retrieved=None, retrieve_error=None):
        self._retrieved = retrieved if retrieved is not None else [_food("Idli")]
        self._retrieve_error = retrieve_error
        self.knowledge_base = [r["metadata"] for r in self._retrieved]
        self.guardrails = FakeGuardrails()

    def retrieve(self, query, k=5):
        if self._retrieve_error:
            raise RuntimeError(self._retrieve_error)
        return self._retrieved

    def generate(self, query, retrieved_docs, user_constraints=None):
        raise AssertionError("generate() must not be called in demo mode")


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "FEEDBACK_PATH", tmp_path / "feedback.json")
    monkeypatch.setattr(api.service, "culrag", FakeCulRAG())
    monkeypatch.setattr(api.service, "demo_mode", True)
    return TestClient(app)


VALID_REQUEST = {
    "target_calories": 1800,
    "vegetarian": True,
    "regional_preference": "South",
    "ayurvedic_type": "Pitta",
    "allergies": ["peanuts"],
    "cooking_time_min": 30,
}


def test_health_check(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["mode"] == "demo"
    assert body["indexed_foods"] == 1
    assert "timestamp" in body


def test_recommend_success(client):
    response = client.post("/api/recommend", json=VALID_REQUEST)

    assert response.status_code == 200
    body = response.json()
    assert body["meal_name"] == "Idli"
    assert body["calories"] == 150
    assert body["macros"] == {"protein_g": 8.0, "carbs_g": 20.0, "fat_g": 4.0}
    assert body["region"] == "South"
    assert body["vegetarian"] is True
    assert body["cooking_time"] == 20
    assert body["recommendation_id"]
    assert body["guardrails"]["passed"] is True


def test_recommend_missing_field(client):
    response = client.post("/api/recommend", json={"vegetarian": True})
    assert response.status_code == 422


def test_recommend_invalid_calories(client):
    response = client.post("/api/recommend", json={**VALID_REQUEST, "target_calories": 500})
    assert response.status_code == 422


def test_recommend_filters_non_vegetarian(client, monkeypatch):
    retrieved = [
        _food("Chicken Curry", vegetarian=False),
        _food("Dhokla", region="West"),
    ]
    monkeypatch.setattr(api.service, "culrag", FakeCulRAG(retrieved=retrieved))

    response = client.post("/api/recommend", json=VALID_REQUEST)

    assert response.status_code == 200
    assert response.json()["meal_name"] == "Dhokla"


def test_recommend_filters_allergens(client, monkeypatch):
    retrieved = [_food("Peanut Chikki"), _food("Idli")]
    monkeypatch.setattr(api.service, "culrag", FakeCulRAG(retrieved=retrieved))

    response = client.post("/api/recommend", json={**VALID_REQUEST, "allergies": ["peanut"]})

    assert response.status_code == 200
    assert response.json()["meal_name"] == "Idli"


def test_recommend_no_matching_foods(client, monkeypatch):
    retrieved = [_food("Chicken Curry", vegetarian=False)]
    monkeypatch.setattr(api.service, "culrag", FakeCulRAG(retrieved=retrieved))

    response = client.post("/api/recommend", json=VALID_REQUEST)

    assert response.status_code == 404


def test_recommend_retrieval_failure(client, monkeypatch):
    monkeypatch.setattr(api.service, "culrag", FakeCulRAG(retrieve_error="embedding API down"))

    response = client.post("/api/recommend", json=VALID_REQUEST)

    assert response.status_code == 503
    assert "embedding API down" in response.json()["detail"]


def test_recommend_respects_cooking_time(client, monkeypatch):
    retrieved = [
        _food("Rajma (Kidney Bean Curry)", cooking_method="Simmered"),  # 35 min
        _food("Poha", cooking_method="Sauteed"),  # 20 min
    ]
    monkeypatch.setattr(api.service, "culrag", FakeCulRAG(retrieved=retrieved))

    response = client.post("/api/recommend", json={**VALID_REQUEST, "cooking_time_min": 25})

    assert response.status_code == 200
    assert response.json()["meal_name"] == "Poha"


def test_recommend_prefers_requested_region(client, monkeypatch):
    retrieved = [
        _food("Paratha (plain)", region="North"),
        _food("Idli", region="South"),
    ]
    monkeypatch.setattr(api.service, "culrag", FakeCulRAG(retrieved=retrieved))

    response = client.post("/api/recommend", json={**VALID_REQUEST, "regional_preference": "South"})

    assert response.status_code == 200
    body = response.json()
    assert body["meal_name"] == "Idli"
    assert body["region"] == "South"


def test_recommend_region_never_empties_results(client, monkeypatch):
    retrieved = [_food("Paratha (plain)", region="North")]
    monkeypatch.setattr(api.service, "culrag", FakeCulRAG(retrieved=retrieved))

    response = client.post("/api/recommend", json={**VALID_REQUEST, "regional_preference": "East"})

    assert response.status_code == 200
    assert response.json()["meal_name"] == "Paratha (plain)"


def test_feedback_success(client, tmp_path):
    response = client.post(
        "/api/feedback",
        json={"recommendation_id": "abc-123", "rating": 5, "comment": "Great recommendation!"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    with open(tmp_path / "feedback.json") as f:
        store = json.load(f)
    assert len(store["feedback"]) == 1
    entry = store["feedback"][0]
    assert entry["recommendation_id"] == "abc-123"
    assert entry["rating"] == 5
    assert entry["comment"] == "Great recommendation!"
    assert entry["timestamp"]


def test_feedback_appends_multiple(client, tmp_path):
    for rating in (4, 2):
        client.post("/api/feedback", json={"recommendation_id": "x", "rating": rating})

    with open(tmp_path / "feedback.json") as f:
        store = json.load(f)
    assert [e["rating"] for e in store["feedback"]] == [4, 2]


def test_feedback_invalid_rating(client):
    response = client.post("/api/feedback", json={"recommendation_id": "x", "rating": 6})
    assert response.status_code == 422


def test_service_not_initialized(client, monkeypatch):
    monkeypatch.setattr(api.service, "culrag", None)

    response = client.post("/api/recommend", json=VALID_REQUEST)

    assert response.status_code == 503
