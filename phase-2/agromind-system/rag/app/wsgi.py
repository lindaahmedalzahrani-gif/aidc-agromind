"""
Production WSGI entrypoint for AgroMind RAG.

Initializes:
- supported knowledge-base pairs
- persistent Chroma retriever
- Qwen/vLLM RAG chain

Then exposes the Flask application to Gunicorn.
"""

import app.api as api_module

from app.api import app, load_supported_pairs
from app.rag import initialize_rag


print("=" * 60)
print("Starting AgroMind RAG production service")
print("=" * 60)

api_module.supported_pairs = load_supported_pairs()
api_module.rag = initialize_rag()

print(
    f"Knowledge-base pairs: "
    f"{len(api_module.supported_pairs)}"
)

print("AgroMind RAG production service ready.")

application = app
