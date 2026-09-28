"""
Retrieval Module - searches the knowledge base
"""

from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from app.config import (
    KNOWLEDGE_BASE_PATH,
    CHROMA_DB_PATH,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RETRIEVAL_K,
)
import os


def load_knowledge_base():
    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        raise FileNotFoundError(f"Knowledge base not found: {KNOWLEDGE_BASE_PATH}")

    loader = TextLoader(KNOWLEDGE_BASE_PATH, encoding="utf-8")
    docs = loader.load()
    return docs


def split_documents(docs):
    splitter = CharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separator="\n\n"
    )
    return splitter.split_documents(docs)


def create_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True}
    )


def create_vectordb(docs_split, embeddings):
    if os.path.exists(CHROMA_DB_PATH):
        import shutil
        shutil.rmtree(CHROMA_DB_PATH)

    vectordb = Chroma.from_documents(
        docs_split,
        embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    vectordb.persist()
    return vectordb


def initialize_retriever():
    print("Loading knowledge base...")
    docs = load_knowledge_base()
    print(f"Loaded {len(docs)} document(s).")

    print("Splitting documents...")
    docs_split = split_documents(docs)
    print(f"Split into {len(docs_split)} chunks.")

    print("Creating embeddings...")
    embeddings = create_embeddings()
    print("Embedding model loaded.")

    print("Storing in ChromaDB...")
    vectordb = create_vectordb(docs_split, embeddings)
    print(f"Stored at: {CHROMA_DB_PATH}")

    return vectordb


def search(vectordb, query, k=RETRIEVAL_K):
    results = vectordb.similarity_search(query, k=k)
    return results
