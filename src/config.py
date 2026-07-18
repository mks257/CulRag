"""Centralized configuration for CulRAG, loaded from environment variables."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Config:
    """Runtime configuration for the CulRAG system.

    Attributes:
        openai_api_key: API key for OpenAI (embeddings + optional LLM).
        anthropic_api_key: API key for Anthropic (optional LLM).
        pinecone_api_key: API key for Pinecone, required only when
            ``vector_db_type == "pinecone"``.
        pinecone_environment: Pinecone environment/region name.
        pinecone_index_name: Name of the Pinecone index to use.
        vector_db_type: Which vector store backend to use, "chroma" (local,
            default, no API key needed) or "pinecone" (cloud).
        chroma_persist_dir: Directory where the local Chroma index is stored.
        embedding_model: OpenAI embedding model name.
        llm_model: Default chat/completion model name.
        debug: Enables verbose logging when true.
    """

    openai_api_key: str | None = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: str | None = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    pinecone_api_key: str | None = field(default_factory=lambda: os.getenv("PINECONE_API_KEY"))
    pinecone_environment: str | None = field(default_factory=lambda: os.getenv("PINECONE_ENVIRONMENT"))
    pinecone_index_name: str = field(default_factory=lambda: os.getenv("PINECONE_INDEX_NAME", "culrag"))
    vector_db_type: str = field(default_factory=lambda: os.getenv("VECTOR_DB_TYPE", "chroma"))
    chroma_persist_dir: str = field(
        default_factory=lambda: os.getenv("CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "data" / "chroma"))
    )
    embedding_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "False").lower() == "true")


def get_config() -> Config:
    """Builds a :class:`Config` from the current environment."""
    return Config()


def setup_logging(debug: bool = False) -> None:
    """Configures root logging for the project.

    Args:
        debug: When true, sets the log level to DEBUG instead of INFO.
    """
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
