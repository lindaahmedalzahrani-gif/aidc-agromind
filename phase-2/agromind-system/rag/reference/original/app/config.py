"""
Configuration for AgroMind RAG System
"""

import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
KNOWLEDGE_BASE_PATH = os.path.join(DATA_DIR, "knowledge_base.txt")
CHROMA_DB_PATH = os.path.join(BASE_DIR, "chroma_agromind")

# Embedding model (unchanged regardless of LLM backend)
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# ============================================================
# LLM BACKEND SWITCH
# Change this one line when the vLLM deployment is ready:
#   "ollama" -> local test model (current default)
#   "vllm"   -> the real Qwen2.5-VL-7B-Instruct served via vLLM
# ============================================================
LLM_BACKEND = "vllm"

# --- Ollama settings (used when LLM_BACKEND = "ollama") ---
OLLAMA_MODEL = "qwen2.5:1.5b"
OLLAMA_BASE_URL = "http://localhost:11434"

# --- vLLM settings (used when LLM_BACKEND = "vllm") ---
# Matches the Phase 1 revised deployment: same model, same endpoint pattern.
VLLM_BASE_URL = "http://localhost:30802/v1"
VLLM_MODEL_NAME = "Qwen/Qwen2.5-VL-7B-Instruct"

# RAG Settings
CHUNK_SIZE = 50
CHUNK_OVERLAP = 0
RETRIEVAL_K = 5

# LLM Settings
TEMPERATURE = 0.3
TOP_P = 0.9
NUM_CTX = 2048
MAX_TOKENS = 150
