"""Vector store abstraction supporting Chroma (local) and Pinecone (cloud) backends."""

from __future__ import annotations

import logging
import uuid
from typing import Any, Callable, Dict, List, Optional

from src.config import get_config

logger = logging.getLogger(__name__)

EmbeddingFunction = Callable[[str], List[float]]


class VectorRetriever:
    """Abstraction over a vector database used to index and search food documents.

    Supports two backends: ``"chroma"`` (local, no API key required beyond the
    embedding provider) and ``"pinecone"`` (cloud-hosted). The backend is chosen
    at construction time and all public methods behave identically regardless
    of which one is active.

    Example:
        >>> retriever = VectorRetriever(vector_db_type="chroma", index_name="culrag")
        >>> retriever.initialize_db()
        >>> retriever.index_documents(
        ...     documents=["Paneer Tikka: grilled paneer, high protein"],
        ...     metadatas=[{"food_name": "Paneer Tikka", "calories": 242}],
        ... )
        1
        >>> results = retriever.search("high protein vegetarian snack", k=3)
    """

    def __init__(
        self,
        vector_db_type: str = "chroma",
        index_name: str = "culrag",
        embedding_function: Optional[EmbeddingFunction] = None,
        persist_directory: Optional[str] = None,
        dimension: int = 1536,
    ) -> None:
        """Initializes the retriever without opening any connections yet.

        Args:
            vector_db_type: Either "chroma" or "pinecone".
            index_name: Name of the collection (Chroma) or index (Pinecone).
            embedding_function: Callable mapping text to an embedding vector.
                Defaults to OpenAI embeddings via :mod:`src.config`. Tests can
                inject a deterministic stub to avoid network/API calls.
            persist_directory: Directory for on-disk Chroma persistence. If
                None, an in-memory (ephemeral) Chroma client is used.
            dimension: Embedding vector dimension, required by Pinecone index
                creation.

        Raises:
            ValueError: If ``vector_db_type`` is not "chroma" or "pinecone".
        """
        if vector_db_type not in ("chroma", "pinecone"):
            raise ValueError(f"Unsupported vector_db_type: {vector_db_type!r}")

        self.vector_db_type = vector_db_type
        self.index_name = index_name
        self.persist_directory = persist_directory
        self.dimension = dimension
        self._embedding_function = embedding_function or self._default_embedding_function()
        self._client: Any = None
        self._collection: Any = None
        self._initialized = False

    def _default_embedding_function(self) -> EmbeddingFunction:
        """Builds an OpenAI-backed embedding function, created lazily.

        Returns:
            A callable that embeds a single string using the configured
            OpenAI embedding model.
        """
        config = get_config()

        def _embed(text: str) -> List[float]:
            from openai import OpenAI

            client = OpenAI(api_key=config.openai_api_key)
            response = client.embeddings.create(model=config.embedding_model, input=text)
            return response.data[0].embedding

        return _embed

    def initialize_db(self) -> None:
        """Connects to the configured vector database backend.

        For Chroma, creates (or opens) a persistent or in-memory client and
        collection. For Pinecone, connects with the configured API key and
        creates the index if it does not already exist.

        Raises:
            RuntimeError: If the backend client cannot be created (e.g.
                missing API key, connection failure).
        """
        try:
            if self.vector_db_type == "chroma":
                self._initialize_chroma()
            else:
                self._initialize_pinecone()
            self._initialized = True
            logger.info("Initialized %s vector DB (index=%s)", self.vector_db_type, self.index_name)
        except Exception as exc:
            raise RuntimeError(f"Failed to initialize {self.vector_db_type} vector DB: {exc}") from exc

    def _initialize_chroma(self) -> None:
        import chromadb

        if self.persist_directory:
            self._client = chromadb.PersistentClient(path=self.persist_directory)
        else:
            self._client = chromadb.EphemeralClient()
        self._collection = self._client.get_or_create_collection(name=self.index_name)

    def _initialize_pinecone(self) -> None:
        from pinecone import Pinecone, ServerlessSpec

        config = get_config()
        if not config.pinecone_api_key:
            raise RuntimeError("PINECONE_API_KEY is not set")

        self._client = Pinecone(api_key=config.pinecone_api_key)
        existing = [idx["name"] for idx in self._client.list_indexes()]
        if self.index_name not in existing:
            self._client.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=config.pinecone_environment or "us-east-1"),
            )
        self._collection = self._client.Index(self.index_name)

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            raise RuntimeError("VectorRetriever is not initialized. Call initialize_db() first.")

    def index_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
    ) -> int:
        """Embeds and stores documents in the vector database.

        Args:
            documents: List of text documents (e.g. food descriptions).
            metadatas: Parallel list of metadata dicts, one per document.
            ids: Optional parallel list of unique ids. Auto-generated (UUID4)
                if not provided.

        Returns:
            The number of documents successfully indexed.

        Raises:
            RuntimeError: If the retriever has not been initialized.
            ValueError: If ``documents`` and ``metadatas`` have different lengths.
        """
        self._ensure_initialized()
        if len(documents) != len(metadatas):
            raise ValueError("documents and metadatas must have the same length")
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]

        embeddings = [self._embedding_function(doc) for doc in documents]

        if self.vector_db_type == "chroma":
            self._collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
        else:
            vectors = [
                {"id": doc_id, "values": emb, "metadata": {**meta, "text": text}}
                for doc_id, emb, meta, text in zip(ids, embeddings, metadatas, documents)
            ]
            self._collection.upsert(vectors=vectors)

        logger.info("Indexed %d documents into %s", len(documents), self.index_name)
        return len(documents)

    def similarity_search(self, query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Runs a k-nearest-neighbors search given a precomputed embedding.

        Args:
            query_embedding: Embedding vector to search against.
            k: Number of nearest neighbors to return.

        Returns:
            A list of up to ``k`` result dicts, each with keys ``id``,
            ``text``, ``metadata``, and ``score`` (higher is more similar).

        Raises:
            RuntimeError: If the retriever has not been initialized.
        """
        self._ensure_initialized()

        if self.vector_db_type == "chroma":
            raw = self._collection.query(query_embeddings=[query_embedding], n_results=k)
            results = []
            for doc_id, doc, meta, distance in zip(
                raw["ids"][0], raw["documents"][0], raw["metadatas"][0], raw["distances"][0]
            ):
                results.append({"id": doc_id, "text": doc, "metadata": meta, "score": 1.0 - distance})
            return results

        raw = self._collection.query(vector=query_embedding, top_k=k, include_metadata=True)
        results = []
        for match in raw["matches"]:
            metadata = dict(match["metadata"])
            text = metadata.pop("text", "")
            results.append({"id": match["id"], "text": text, "metadata": metadata, "score": match["score"]})
        return results

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Embeds a text query and returns the top-k most similar documents.

        Args:
            query: Natural language search query (e.g. "high protein breakfast").
            k: Number of results to return.

        Returns:
            Same shape as :meth:`similarity_search`.

        Raises:
            RuntimeError: If the retriever has not been initialized.
        """
        self._ensure_initialized()
        query_embedding = self._embedding_function(query)
        return self.similarity_search(query_embedding, k=k)

    def get_stats(self) -> Dict[str, Any]:
        """Returns basic statistics about the index.

        Returns:
            Dict with keys ``index_name``, ``vector_db_type``, ``count``, and
            ``dimension``.

        Raises:
            RuntimeError: If the retriever has not been initialized.
        """
        self._ensure_initialized()

        if self.vector_db_type == "chroma":
            count = self._collection.count()
        else:
            stats = self._collection.describe_index_stats()
            count = stats.get("total_vector_count", 0)

        return {
            "index_name": self.index_name,
            "vector_db_type": self.vector_db_type,
            "count": count,
            "dimension": self.dimension,
        }

    def delete_index(self) -> None:
        """Deletes the underlying collection/index. Primarily used for test cleanup.

        Raises:
            RuntimeError: If the retriever has not been initialized.
        """
        self._ensure_initialized()

        if self.vector_db_type == "chroma":
            self._client.delete_collection(name=self.index_name)
        else:
            self._client.delete_index(self.index_name)

        self._initialized = False
        logger.info("Deleted index %s", self.index_name)
