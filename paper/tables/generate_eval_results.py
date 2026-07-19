"""Regenerates eval_results.csv (Table 2 source) from the labeled query set.

Run from the repo root with the project venv active:
    python paper/tables/generate_eval_results.py

Fully reproducible offline baseline, by construction:
- Embedding: CRC32 bag-of-words (stable across processes, unlike built-in
  hash() which is salted per interpreter).
- Search: EXACT cosine k-NN with lexicographic tie-breaking, implemented
  below rather than via the Chroma HNSW index — approximate indexes break
  the many similarity ties these crude embeddings produce in
  non-deterministic order, which changed the table between runs.

For the production run: replace ExactRetriever with the real VectorRetriever
(OpenAI embeddings), where real-valued similarities make ties a non-issue,
and update EMBEDDING_LABEL.
"""

import csv
import json
import math
import sys
import zlib
from collections import Counter
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.evaluator import RAGEvaluator  # noqa: E402
EMBEDDING_DIM = 64
EMBEDDING_LABEL = "crc32-baseline"


def stable_hash_embed(text: str):
    """Deterministic (cross-process) bag-of-words embedding for offline runs."""
    vector = [0.0] * EMBEDDING_DIM
    for word, count in Counter(text.lower().split()).items():
        vector[zlib.crc32(word.encode()) % EMBEDDING_DIM] += count
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


class ExactRetriever:
    """Exact cosine k-NN over precomputed embeddings, deterministic tie-breaking."""

    def __init__(self, documents, metadatas):
        self._entries = sorted(
            (
                (meta["food_name"], stable_hash_embed(doc), doc, meta)
                for doc, meta in zip(documents, metadatas)
            ),
            key=lambda entry: entry[0],
        )

    def search(self, query, k=5):
        query_vec = stable_hash_embed(query)
        scored = [
            # Vectors are L2-normalized, so the dot product is cosine similarity.
            (sum(a * b for a, b in zip(query_vec, vec)), name, doc, meta)
            for name, vec, doc, meta in self._entries
        ]
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [
            {"id": name, "text": doc, "metadata": meta, "score": score}
            for score, name, doc, meta in scored[:k]
        ]


def main() -> None:
    df = pd.read_csv(REPO_ROOT / "data" / "sample_foods.csv")
    with open(REPO_ROOT / "data" / "eval_queries.json") as f:
        test_cases = json.load(f)

    documents = [
        f"{row.food_name}: {row.calories} kcal, protein {row.protein_g}g, "
        f"carbs {row.carbs_g}g, fat {row.fat_g}g, region {row.region}, "
        f"ayurvedic type {row.ayurvedic_type}, cooking method {row.cooking_method}"
        for row in df.itertuples()
    ]
    retriever = ExactRetriever(documents, df.to_dict("records"))

    report = RAGEvaluator().evaluate_retrieval(retriever, test_cases, k=5)

    out_path = Path(__file__).parent / "eval_results.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["query", "precision_at_5", "recall_at_5", "reciprocal_rank", "embedding"])
        for q in report["per_query"]:
            writer.writerow([
                q["query"], round(q["precision_at_k"], 3), round(q["recall_at_k"], 3),
                round(q["reciprocal_rank"], 3), EMBEDDING_LABEL,
            ])
        writer.writerow([
            "MEAN", round(report["mean_precision_at_k"], 3),
            round(report["mean_recall_at_k"], 3),
            round(report["mean_reciprocal_rank"], 3), EMBEDDING_LABEL,
        ])
    print(f"wrote {out_path}")
    print(f"means: P@5={report['mean_precision_at_k']:.3f} "
          f"R@5={report['mean_recall_at_k']:.3f} MRR={report['mean_reciprocal_rank']:.3f}")


if __name__ == "__main__":
    main()
