"""Unit tests for VectorRetriever using a local, ephemeral Chroma backend.

No external API calls are made: a deterministic hashing-based embedding
function stands in for the OpenAI embeddings used in production.
"""

import math
import uuid
from collections import Counter
from typing import List

import pandas as pd
import pytest

from src.retriever import VectorRetriever

EMBEDDING_DIM = 64


def fake_embed(text: str) -> List[float]:
    """Deterministic bag-of-words hashing embedding; no network calls."""
    vector = [0.0] * EMBEDDING_DIM
    words = text.lower().split()
    counts = Counter(words)
    for word, count in counts.items():
        idx = hash(word) % EMBEDDING_DIM
        vector[idx] += count

    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


@pytest.fixture
def sample_foods() -> List[dict]:
    df = pd.read_csv("data/sample_foods.csv")
    return df.to_dict("records")


@pytest.fixture
def retriever():
    r = VectorRetriever(
        vector_db_type="chroma",
        index_name=f"test_{uuid.uuid4().hex[:8]}",
        embedding_function=fake_embed,
        persist_directory=None,
    )
    r.initialize_db()
    yield r
    try:
        r.delete_index()
    except Exception:
        pass


def test_initialize_db(retriever):
    assert retriever._initialized is True
    stats = retriever.get_stats()
    assert stats["count"] == 0
    assert stats["vector_db_type"] == "chroma"


def test_index_documents(retriever, sample_foods):
    subset = sample_foods[:5]
    documents = [f"{row['food_name']}: {row['calories']} kcal" for row in subset]
    count = retriever.index_documents(documents, metadatas=subset)

    assert count == 5
    assert retriever.get_stats()["count"] == 5


def test_search_basic(retriever, sample_foods):
    subset = sample_foods[:10]
    documents = [f"{row['food_name']}: {row['calories']} kcal" for row in subset]
    retriever.index_documents(documents, metadatas=subset)

    results = retriever.search("high protein breakfast", k=5)

    assert len(results) == 5
    for result in results:
        assert set(result.keys()) == {"id", "text", "metadata", "score"}


def test_search_relevance(retriever):
    documents = [
        "Paneer Tikka: high protein grilled paneer snack",
        "Plain Rice: low protein boiled rice",
    ]
    metadatas = [{"food_name": "Paneer Tikka"}, {"food_name": "Plain Rice"}]
    retriever.index_documents(documents, metadatas=metadatas)

    results = retriever.search("high protein paneer snack", k=2)

    assert results[0]["metadata"]["food_name"] == "Paneer Tikka"


def test_metadata_preserved(retriever):
    metadata = {"food_name": "Masoor Dal", "calories": 116, "region": "North"}
    retriever.index_documents(["Masoor Dal: 116 kcal lentil curry"], metadatas=[metadata])

    results = retriever.search("lentil curry", k=1)

    assert results[0]["metadata"] == metadata


def test_empty_search(retriever):
    results = retriever.search("anything", k=5)
    assert results == []


def test_delete_index(retriever):
    retriever.index_documents(["Idli: steamed rice cake"], metadatas=[{"food_name": "Idli"}])
    retriever.delete_index()

    assert retriever._initialized is False
    with pytest.raises(RuntimeError):
        retriever.get_stats()
