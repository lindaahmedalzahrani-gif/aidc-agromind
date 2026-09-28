"""
Configuration for the AgroMind RAG system.

Local development can use localhost defaults.
Kubernetes overrides these values through environment variables.
"""

import os


# ============================================================
# Base paths
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(
            __file__
        )
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data",
)


# ============================================================
# RAG storage
# ============================================================

KNOWLEDGE_BASE_PATH = os.getenv(
    "KNOWLEDGE_BASE_PATH",
    os.path.join(
        DATA_DIR,
        "knowledge_base.txt",
    ),
)


CHROMA_DB_PATH = os.getenv(
    "CHROMA_DB_PATH",
    os.path.join(
        BASE_DIR,
        "chroma_agromind",
    ),
)


REBUILD_VECTOR_DB = (
    os.getenv(
        "REBUILD_VECTOR_DB",
        "false",
    )
    .strip()
    .lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)


# ============================================================
# Embeddings
# ============================================================

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    (
        "sentence-transformers/"
        "paraphrase-multilingual-MiniLM-L12-v2"
    ),
)


# ============================================================
# LLM backend
# ============================================================

LLM_BACKEND = os.getenv(
    "LLM_BACKEND",
    "vllm",
)


# ============================================================
# Ollama local fallback
# ============================================================

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:1.5b",
)


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)


# ============================================================
# vLLM production backend
# ============================================================

VLLM_BASE_URL = os.getenv(
    "VLLM_BASE_URL",
    "http://localhost:30802/v1",
)


VLLM_MODEL_NAME = os.getenv(
    "VLLM_MODEL_NAME",
    "Qwen/Qwen2.5-VL-7B-Instruct",
)


# ============================================================
# Retrieval
# ============================================================

# A crop-condition pair normally has four Q&A entries.
# Free-text queries can therefore consider all four.
# Structured button queries filter down to one intent.
RETRIEVAL_K = int(
    os.getenv(
        "RETRIEVAL_K",
        "4",
    )
)


# ============================================================
# Generation
# ============================================================

TEMPERATURE = float(
    os.getenv(
        "TEMPERATURE",
        "0.3",
    )
)


TOP_P = float(
    os.getenv(
        "TOP_P",
        "0.9",
    )
)


NUM_CTX = int(
    os.getenv(
        "NUM_CTX",
        "2048",
    )
)


MAX_TOKENS = int(
    os.getenv(
        "MAX_TOKENS",
        "150",
    )
)