"""Main orchestrator tying together retrieval, generation, and guardrails."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from src.config import get_config, setup_logging
from src.guardrails import GuardrailChecker
from src.llm_chain import RAGChain
from src.retriever import VectorRetriever

logger = logging.getLogger(__name__)


class CulRAG:
    """End-to-end culturally-grounded RAG system for Indian dietary guidance.

    Wires together :class:`~src.retriever.VectorRetriever`,
    :class:`~src.llm_chain.RAGChain`, and :class:`~src.guardrails.GuardrailChecker`
    into a single pipeline: load foods -> index -> retrieve -> generate -> validate.

    Example:
        >>> culrag = CulRAG(vector_db_type="chroma", llm_model="gpt-4",
        ...                  knowledge_base_path="data/sample_foods.csv")
        >>> culrag.index_documents()
        >>> result = culrag.recommend("high-protein vegetarian breakfast")
        >>> result["recommendation"]["meal_name"]
    """

    def __init__(
        self,
        vector_db_type: str = "chroma",
        llm_model: str = "gpt-4",
        knowledge_base_path: Optional[str] = None,
        index_name: str = "culrag",
        persist_directory: Optional[str] = None,
    ) -> None:
        """Initializes the pipeline and optionally loads a knowledge base.

        Args:
            vector_db_type: Either "chroma" (local) or "pinecone" (cloud).
            llm_model: Model name passed through to :class:`RAGChain`.
            knowledge_base_path: Optional CSV path to load immediately via
                :meth:`load_knowledge_base`.
            index_name: Name of the vector collection/index to use.
            persist_directory: Optional on-disk directory for Chroma persistence.

        Raises:
            RuntimeError: If ``knowledge_base_path`` is given but cannot be loaded.
        """
        setup_logging(get_config().debug)

        self.retriever = VectorRetriever(
            vector_db_type=vector_db_type, index_name=index_name, persist_directory=persist_directory
        )
        self.chain = RAGChain(model=llm_model)
        self.guardrails = GuardrailChecker(llm_model=llm_model)

        self.knowledge_base: List[Dict[str, Any]] = []
        self._documents: List[str] = []
        self._metadatas: List[Dict[str, Any]] = []

        if knowledge_base_path:
            self.load_knowledge_base(knowledge_base_path)

    def load_knowledge_base(self, csv_path: str) -> int:
        """Loads an Indian foods CSV into memory as documents + metadata.

        Args:
            csv_path: Path to a CSV with at least a ``food_name`` column
                (see ``data/sample_foods.csv`` for the expected schema).

        Returns:
            The number of food records loaded.

        Raises:
            RuntimeError: If the CSV cannot be read or parsed.
        """
        import pandas as pd

        try:
            df = pd.read_csv(csv_path)
        except Exception as exc:
            raise RuntimeError(f"Failed to load knowledge base from {csv_path}: {exc}") from exc

        self.knowledge_base = df.to_dict("records")
        self.guardrails.knowledge_base = self.knowledge_base
        self._metadatas = self.knowledge_base
        self._documents = [self._food_to_text(row) for row in self.knowledge_base]

        logger.info("Loaded %d foods from %s", len(self.knowledge_base), csv_path)
        return len(self.knowledge_base)

    @staticmethod
    def _food_to_text(row: Dict[str, Any]) -> str:
        """Renders a food record as a natural-language string for embedding."""
        veg = "vegetarian" if str(row.get("vegetarian", "True")).strip().lower() in ("true", "1", "yes") else "non-vegetarian"
        return (
            f"{row.get('food_name', 'Unknown food')}: {row.get('calories', '?')} kcal, "
            f"protein {row.get('protein_g', '?')}g, carbs {row.get('carbs_g', '?')}g, "
            f"fat {row.get('fat_g', '?')}g, fiber {row.get('fiber_g', '?')}g, "
            f"{veg}, region {row.get('region', 'unknown')}, "
            f"ayurvedic type {row.get('ayurvedic_type', 'unknown')}, "
            f"cooking method {row.get('cooking_method', 'unknown')}"
        )

    def index_documents(self) -> int:
        """Initializes the vector DB and indexes the loaded knowledge base.

        Returns:
            The number of documents indexed.

        Raises:
            RuntimeError: If no knowledge base has been loaded yet, or if
                indexing fails (e.g. embedding API failure).
        """
        if not self._documents:
            raise RuntimeError("No knowledge base loaded. Call load_knowledge_base() first.")

        self.retriever.initialize_db()
        try:
            return self.retriever.index_documents(self._documents, self._metadatas)
        except Exception as exc:
            raise RuntimeError(f"Failed to index documents: {exc}") from exc

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieves the top-k most relevant foods for a query.

        Args:
            query: Natural language query.
            k: Number of results to retrieve.

        Returns:
            List of result dicts (see :meth:`VectorRetriever.search`).

        Raises:
            RuntimeError: If retrieval fails (e.g. embedding API failure).
        """
        try:
            return self.retriever.search(query, k=k)
        except Exception as exc:
            raise RuntimeError(f"Retrieval failed: {exc}") from exc

    def generate(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        user_constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generates a structured recommendation from retrieved context.

        Args:
            query: Natural language query.
            retrieved_docs: Output of :meth:`retrieve`.
            user_constraints: Optional dietary constraints dict.

        Returns:
            Recommendation dict, or ``{"error": ...}`` on LLM failure (does
            not raise; see :meth:`RAGChain.generate_recommendation`).
        """
        return self.chain.generate_recommendation(query, retrieved_docs, user_constraints)

    def recommend(
        self,
        user_query: str,
        user_constraints: Optional[Dict[str, Any]] = None,
        k: int = 5,
    ) -> Dict[str, Any]:
        """Runs the full retrieve -> generate -> validate pipeline.

        Args:
            user_query: Natural language request, e.g. "high-protein
                vegetarian breakfast".
            user_constraints: Optional dict with keys such as ``vegetarian``,
                ``target_calories``, ``allergies``, ``regional_preference``.
            k: Number of foods to retrieve as context.

        Returns:
            Dict with keys ``recommendation`` (from :meth:`generate`),
            ``retrieved_foods`` (from :meth:`retrieve`), and ``guardrails``
            (from :class:`GuardrailChecker.run_all_checks`). If retrieval
            fails, returns ``{"error": ...}`` instead.
        """
        try:
            retrieved = self.retrieve(user_query, k=k)
        except RuntimeError as exc:
            logger.error("recommend() aborted: %s", exc)
            return {"error": str(exc)}

        recommendation = self.generate(user_query, retrieved, user_constraints)
        guardrail_result = self.guardrails.run_all_checks(
            recommendation, user_constraints or {}, self.knowledge_base
        )

        return {
            "recommendation": recommendation,
            "retrieved_foods": retrieved,
            "guardrails": guardrail_result,
        }
