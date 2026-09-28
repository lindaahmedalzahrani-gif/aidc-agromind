"""
RAG System - connects retrieval with the LLM
Supports two backends: Ollama (local testing) and vLLM (production, Qwen2.5-VL-7B)
"""

from langchain.chains import RetrievalQA
from app.config import (
    LLM_BACKEND,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    VLLM_BASE_URL,
    VLLM_MODEL_NAME,
    TEMPERATURE,
    TOP_P,
    NUM_CTX,
    MAX_TOKENS,
    RETRIEVAL_K,
)
from app.retrieval import initialize_retriever


def initialize_llm():
    print(f"Initializing model (backend: {LLM_BACKEND})...")

    if LLM_BACKEND == "ollama":
        from langchain_community.llms import Ollama
        print(f"(Make sure Ollama is running on {OLLAMA_BASE_URL})")
        try:
            llm = Ollama(
                model=OLLAMA_MODEL,
                base_url=OLLAMA_BASE_URL,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                num_ctx=NUM_CTX
            )
            llm("Hello")
            print("Connected to Ollama.")
            return llm
        except Exception as e:
            print(f"Connection error: {e}")
            print("Is Ollama running? Try: systemctl status ollama")
            raise

    elif LLM_BACKEND == "vllm":
        # Uses the CHAT completions endpoint (/v1/chat/completions), not the
        # raw text-completions endpoint. This matters a lot for an Instruct
        # model: chat completions respects the model's chat template and its
        # end-of-turn token, so the model stops cleanly after answering
        # instead of continuing to generate fabricated follow-up turns.
        from langchain_community.chat_models import ChatOpenAI
        print(f"(Connecting to vLLM chat endpoint at {VLLM_BASE_URL})")
        try:
            llm = ChatOpenAI(
                openai_api_key="not-needed",
                openai_api_base=VLLM_BASE_URL,
                model_name=VLLM_MODEL_NAME,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                max_tokens=MAX_TOKENS,
            )
            llm.predict("Hello")
            print("Connected to vLLM.")
            return llm
        except Exception as e:
            print(f"Connection error: {e}")
            print(f"Is the vLLM deployment running and reachable at {VLLM_BASE_URL}?")
            print("Check: kubectl get pods -n agromind-h100")
            raise

    else:
        raise ValueError(f"Unknown LLM_BACKEND: {LLM_BACKEND}")


def initialize_rag_chain(vectordb, llm):
    print("Building RAG chain...")

    rag = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectordb.as_retriever(
            search_type="similarity",
            search_kwargs={"k": RETRIEVAL_K}
        ),
        return_source_documents=True,
        verbose=False
    )

    print("RAG chain ready.")
    return rag


def initialize_rag():
    print("Initializing...")
    print("=" * 60)

    vectordb = initialize_retriever()
    llm = initialize_llm()
    rag = initialize_rag_chain(vectordb, llm)

    print("=" * 60)
    print("RAG is ready.")
    print("=" * 60)

    return rag


def ask_rag(rag, question):
    print(f"Question: {question}")
    print("-" * 60)

    try:
        result = rag({"query": question})
        answer = result["result"]
        print(f"Answer:\n{answer}")

        if result.get("source_documents"):
            print(f"Sources ({len(result['source_documents'])} documents):")
            for i, doc in enumerate(result["source_documents"][:3], 1):
                preview = doc.page_content[:100].replace("\n", " ")
                print(f"   {i}. {preview}...")

        return answer, result.get("source_documents", [])

    except Exception as e:
        print(f"Error: {e}")
        return None, []
