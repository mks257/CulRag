"""FastAPI backend exposing the CulRAG pipeline over HTTP.

Run locally with:
    uvicorn src.api:app --reload

Modes:
- Full mode (OPENAI_API_KEY set): real embeddings + LLM generation.
- Demo mode (no key): deterministic local hash embeddings and a
  retrieval-only recommendation composed from the top matching food, so the
  dashboard works end-to-end without any paid API. The active mode is
  reported by GET /api/health.
"""

from __future__ import annotations

import json
import logging
import math
import os
import threading
import uuid
import zlib
from collections import Counter
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.config import PROJECT_ROOT, get_config, setup_logging
from src.rag_pipeline import CulRAG

logger = logging.getLogger(__name__)

FEEDBACK_PATH = PROJECT_ROOT / "data" / "feedback.json"
KNOWLEDGE_BASE_PATH = PROJECT_ROOT / "data" / "sample_foods.csv"
DEMO_EMBEDDING_DIM = 64

# No cooking-time column exists in the IFCT-style data; estimate from the
# cooking method until the full dataset carries real prep times.
COOKING_TIME_BY_METHOD = {
    "Raw": 0,
    "Clarified": 10,
    "Shallow-fried": 15,
    "Roasted": 15,
    "Sauteed": 20,
    "Steamed": 20,
    "Boiled": 25,
    "Grilled": 25,
    "Pressure-cooked": 30,
    "Fermented": 30,
    "Simmered": 35,
}

_feedback_lock = threading.Lock()


# --------------------------------------------------------------------------
# Pydantic schemas
# --------------------------------------------------------------------------


class RecommendationRequest(BaseModel):
    """User preferences for a meal recommendation."""

    target_calories: int = Field(..., ge=1200, le=3000, description="Daily calorie target")
    vegetarian: bool = Field(True, description="Restrict to vegetarian foods")
    regional_preference: Optional[str] = Field(
        None, description="North, South, East, West, or Any"
    )
    ayurvedic_type: Optional[str] = Field(
        None, description="Vata, Pitta, Kapha, or Balanced"
    )
    allergies: Optional[List[str]] = Field(None, description="Allergen keywords to avoid")
    cooking_time_min: Optional[int] = Field(
        None, ge=0, le=120, description="Maximum cooking time in minutes"
    )


class Macros(BaseModel):
    protein_g: float
    carbs_g: float
    fat_g: float


class RecommendationResponse(BaseModel):
    """A single structured meal recommendation."""

    meal_name: str
    calories: int
    macros: Macros
    portion: str
    cooking_time: int
    region: str
    vegetarian: bool
    ayurvedic_type: str
    reasoning: str
    recommendation_id: str
    guardrails: Dict[str, Any] = Field(
        default_factory=dict, description="Constraint-check result for transparency"
    )


class FeedbackRequest(BaseModel):
    """User feedback on a previously returned recommendation."""

    recommendation_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)


class FeedbackResponse(BaseModel):
    status: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    mode: str
    indexed_foods: int


# --------------------------------------------------------------------------
# CulRAG bootstrap (initialized once at startup, not per request)
# --------------------------------------------------------------------------


def _demo_hash_embed(text: str) -> List[float]:
    """Deterministic (cross-process) bag-of-words embedding used when no OpenAI key is set."""
    vector = [0.0] * DEMO_EMBEDDING_DIM
    for word, count in Counter(text.lower().split()).items():
        vector[zlib.crc32(word.encode()) % DEMO_EMBEDDING_DIM] += count
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


class RAGService:
    """Holds the singleton CulRAG instance and adapts it for HTTP responses."""

    def __init__(self) -> None:
        self.culrag: Optional[CulRAG] = None
        self.demo_mode: bool = True

    def startup(self) -> None:
        """Loads and indexes the knowledge base. Called once at app startup."""
        config = get_config()
        self.demo_mode = not bool(config.openai_api_key)

        self.culrag = CulRAG(
            vector_db_type="chroma",
            llm_model=config.llm_model,
            knowledge_base_path=str(KNOWLEDGE_BASE_PATH),
        )
        if self.demo_mode:
            logger.warning("No OPENAI_API_KEY found - running in demo mode (local embeddings, no LLM)")
            self.culrag.retriever._embedding_function = _demo_hash_embed
        self.culrag.index_documents()
        logger.info("CulRAG ready (%d foods indexed, demo_mode=%s)",
                    len(self.culrag.knowledge_base), self.demo_mode)

    @property
    def indexed_foods(self) -> int:
        return len(self.culrag.knowledge_base) if self.culrag else 0

    @staticmethod
    def _build_query(request: RecommendationRequest) -> str:
        """Turns structured preferences into a retrieval query string."""
        parts = []
        if request.vegetarian:
            parts.append("vegetarian")
        if request.regional_preference and request.regional_preference.lower() != "any":
            parts.append(f"{request.regional_preference} Indian")
        if request.ayurvedic_type and request.ayurvedic_type.lower() != "balanced":
            parts.append(f"{request.ayurvedic_type}-pacifying")
        parts.append("meal")
        per_meal = request.target_calories // 3
        parts.append(f"around {per_meal} calories")
        return " ".join(parts)

    @staticmethod
    def _constraints(request: RecommendationRequest) -> Dict[str, Any]:
        per_meal = request.target_calories // 3
        constraints: Dict[str, Any] = {
            "vegetarian": request.vegetarian,
            # Per-meal window: a third of the daily target, +/- 50%.
            "target_calories": (per_meal * 0.5, per_meal * 1.5),
        }
        if request.allergies:
            constraints["allergies"] = request.allergies
        if request.regional_preference:
            constraints["regional_preference"] = request.regional_preference
        if request.cooking_time_min is not None:
            constraints["max_cooking_time"] = request.cooking_time_min
        return constraints

    @staticmethod
    def _cooking_time(metadata: Dict[str, Any]) -> int:
        return COOKING_TIME_BY_METHOD.get(str(metadata.get("cooking_method", "")), 30)

    def _filter_retrieved(
        self, retrieved: List[Dict[str, Any]], request: RecommendationRequest
    ) -> List[Dict[str, Any]]:
        """Hard-filters on vegetarian/allergy/time; soft-prefers the requested region."""
        filtered = []
        allergies = [a.lower() for a in (request.allergies or [])]
        for item in retrieved:
            meta = item.get("metadata", {})
            if request.vegetarian and not _truthy(meta.get("vegetarian", True)):
                continue
            name = str(meta.get("food_name", "")).lower()
            if any(allergen in name for allergen in allergies):
                continue
            if request.cooking_time_min is not None and self._cooking_time(meta) > request.cooking_time_min:
                continue
            filtered.append(item)

        # Soft region preference: narrow to matching (or pan-Indian) foods when
        # possible, but never let a region choice empty the result set.
        region = (request.regional_preference or "").lower()
        if region and region != "any":
            region_matches = [
                item for item in filtered
                if str(item["metadata"].get("region", "")).lower() in (region, "pan-india")
            ]
            if region_matches:
                filtered = region_matches
        return filtered

    def _demo_recommendation(
        self, retrieved: List[Dict[str, Any]], request: RecommendationRequest
    ) -> Dict[str, Any]:
        """Retrieval-only recommendation used when no LLM key is configured."""
        if not retrieved:
            raise HTTPException(
                status_code=404,
                detail="No foods in the knowledge base satisfy those constraints.",
            )
        top = retrieved[0]["metadata"]
        return {
            "meal_name": top.get("food_name", "Unknown"),
            "calories": int(top.get("calories", 0)),
            "macros": {
                "protein_g": float(top.get("protein_g", 0)),
                "carbs_g": float(top.get("carbs_g", 0)),
                "fat_g": float(top.get("fat_g", 0)),
            },
            "portion": "1 standard serving (100g)",
            "reasoning": (
                f"Top retrieval match for your preferences. {top.get('food_name')} is a "
                f"{'vegetarian' if _truthy(top.get('vegetarian', True)) else 'non-vegetarian'} "
                f"{top.get('region', 'Indian')} Indian dish ({top.get('ayurvedic_type', 'Tridoshic')}), "
                f"prepared by {str(top.get('cooking_method', 'cooking')).lower()}. "
                "Demo mode: generated from the knowledge base without an LLM."
            ),
        }

    def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        """Runs the pipeline and adapts the result to the response schema.

        Raises:
            HTTPException: 503 if the pipeline is not ready or retrieval
                fails; 502 if LLM generation fails; 404 if no foods match.
        """
        if self.culrag is None:
            raise HTTPException(status_code=503, detail="RAG pipeline not initialized")

        query = self._build_query(request)
        constraints = self._constraints(request)
        logger.info("Recommend query=%r constraints=%s", query, constraints)

        try:
            retrieved = self.culrag.retrieve(query, k=10)
        except RuntimeError as exc:
            logger.error("Retrieval failed: %s", exc)
            raise HTTPException(status_code=503, detail=f"Retrieval failed: {exc}") from exc

        retrieved = self._filter_retrieved(retrieved, request)

        if self.demo_mode:
            recommendation = self._demo_recommendation(retrieved, request)
        else:
            recommendation = self.culrag.generate(query, retrieved, constraints)
            if "error" in recommendation:
                logger.error("LLM generation failed: %s", recommendation["error"])
                raise HTTPException(status_code=502, detail=recommendation["error"])

        guardrail_result = self.culrag.guardrails.run_all_checks(
            recommendation, constraints, self.culrag.knowledge_base
        )

        top_meta = retrieved[0]["metadata"] if retrieved else {}
        macros = recommendation.get("macros", {})
        return RecommendationResponse(
            meal_name=str(recommendation.get("meal_name", "Unknown")),
            calories=int(recommendation.get("calories", 0)),
            macros=Macros(
                protein_g=float(macros.get("protein_g", 0)),
                carbs_g=float(macros.get("carbs_g", 0)),
                fat_g=float(macros.get("fat_g", 0)),
            ),
            portion=str(recommendation.get("portion", "1 serving")),
            cooking_time=self._cooking_time(top_meta),
            region=str(top_meta.get("region", "Pan-India")),
            vegetarian=_truthy(top_meta.get("vegetarian", request.vegetarian)),
            ayurvedic_type=str(top_meta.get("ayurvedic_type", "Tridoshic")),
            reasoning=str(recommendation.get("reasoning", "")),
            recommendation_id=str(uuid.uuid4()),
            guardrails=guardrail_result,
        )


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "yes")


def append_feedback(entry: Dict[str, Any], path: Optional[Path] = None) -> None:
    """Appends a feedback entry to the JSON store (thread-safe, MVP-grade).

    Args:
        entry: Feedback record to persist.
        path: Target JSON file; created with ``{"feedback": []}`` if absent.
            Defaults to the module-level ``FEEDBACK_PATH`` (resolved at call
            time so tests can redirect it).
    """
    if path is None:
        path = FEEDBACK_PATH
    with _feedback_lock:
        if path.exists():
            with open(path) as f:
                store = json.load(f)
        else:
            store = {"feedback": []}
        store["feedback"].append(entry)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(store, f, indent=2)


# --------------------------------------------------------------------------
# App wiring
# --------------------------------------------------------------------------

service = RAGService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(get_config().debug)
    service.startup()
    yield


app = FastAPI(
    title="CulRAG API",
    description="Culturally grounded RAG for Indian dietary guidance",
    version="0.1.0",
    lifespan=lifespan,
)

_cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]
if os.getenv("FRONTEND_ORIGIN"):
    _cors_origins.append(os.environ["FRONTEND_ORIGIN"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health check with pipeline status."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        mode="demo" if service.demo_mode else "full",
        indexed_foods=service.indexed_foods,
    )


@app.post("/api/recommend", response_model=RecommendationResponse)
def recommend(request: RecommendationRequest) -> RecommendationResponse:
    """Generates a meal recommendation from user preferences."""
    response = service.recommend(request)
    logger.info("Recommended %r (id=%s)", response.meal_name, response.recommendation_id)
    return response


@app.post("/api/feedback", response_model=FeedbackResponse)
def feedback(request: FeedbackRequest) -> FeedbackResponse:
    """Stores user feedback for a recommendation."""
    entry = {
        "id": str(uuid.uuid4()),
        "recommendation_id": request.recommendation_id,
        "rating": request.rating,
        "comment": request.comment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        append_feedback(entry)
    except OSError as exc:
        logger.error("Failed to persist feedback: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to store feedback") from exc
    logger.info("Stored feedback %s (rating=%d)", entry["id"], request.rating)
    return FeedbackResponse(status="success")
