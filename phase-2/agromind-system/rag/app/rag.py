"""
AgroMind RAG System

Connects:

    metadata-filtered Chroma retrieval
        ↓
    verified crop-condition context
        ↓
    Qwen2.5-VL served through vLLM
        ↓
    grounded agricultural answer

Supported backends:
    - vLLM   -> production / Kubernetes
    - Ollama -> optional local development fallback
"""

from langchain.prompts import PromptTemplate

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

from app.retrieval import (
    initialize_retriever,
    search,
)


# ============================================================
# AgroMind grounded prompt
# ============================================================

AGROMIND_RAG_PROMPT = PromptTemplate(
    input_variables=[
        "context",
        "question",
        "crop",
        "condition",
        "language",
    ],

    template="""
You are AgroMind, an agricultural knowledge assistant.

The requested verified diagnosis is:

Crop:
{crop}

Condition:
{condition}

Language:
{language}

Use ONLY the AgroMind knowledge-base context below to answer
the user's question.

IMPORTANT RULES:

1. The retrieved context has already been filtered to the
   requested crop and condition.

2. Do not invent agricultural information.

3. Do not provide causes, symptoms, treatments, pesticides,
   dosages, management steps, or crop information unless they
   are supported by the context.

4. Do not add recommendations that are absent from the context.

5. If the context does not contain enough information to answer
   the question, say so clearly.

6. If the requested language is Chinese, answer in Chinese.

7. If the requested language is English, answer in English.

8. Keep the answer concise, practical, and directly related to
   the user's question.

Retrieved AgroMind context:
----------------------------
{context}
----------------------------

User question:
{question}

AgroMind answer:
""".strip(),
)


# ============================================================
# LLM initialization
# ============================================================

def initialize_llm():

    print(
        f"Initializing model "
        f"(backend: {LLM_BACKEND})..."
    )


    # --------------------------------------------------------
    # Ollama local fallback
    # --------------------------------------------------------

    if LLM_BACKEND == "ollama":

        from langchain_community.llms import (
            Ollama
        )


        print(
            f"Connecting to Ollama at "
            f"{OLLAMA_BASE_URL}"
        )


        try:

            llm = Ollama(
                model=
                    OLLAMA_MODEL,

                base_url=
                    OLLAMA_BASE_URL,

                temperature=
                    TEMPERATURE,

                top_p=
                    TOP_P,

                num_ctx=
                    NUM_CTX,
            )


            llm.invoke(
                "Hello"
            )


            print(
                "Connected to Ollama."
            )


            return llm


        except Exception as exc:

            print(
                f"Ollama connection error: "
                f"{exc}"
            )

            raise


    # --------------------------------------------------------
    # vLLM production backend
    # --------------------------------------------------------

    elif LLM_BACKEND == "vllm":

        from langchain_community.chat_models import (
            ChatOpenAI
        )


        print(
            "Connecting to vLLM chat endpoint:"
        )

        print(
            f"  {VLLM_BASE_URL}"
        )

        print(
            "Model:"
        )

        print(
            f"  {VLLM_MODEL_NAME}"
        )


        try:

            llm = ChatOpenAI(
                openai_api_key=
                    "not-needed",

                openai_api_base=
                    VLLM_BASE_URL,

                model_name=
                    VLLM_MODEL_NAME,

                temperature=
                    TEMPERATURE,

                max_tokens=
                    MAX_TOKENS,

                model_kwargs={
                    "top_p":
                        TOP_P,
                },
            )


            llm.invoke(
                "Hello"
            )


            print(
                "Connected to vLLM."
            )


            return llm


        except Exception as exc:

            print(
                f"vLLM connection error: "
                f"{exc}"
            )


            print(
                "Expected Kubernetes endpoint:"
            )

            print(
                "  http://agromind-serving:8000/v1"
            )


            raise


    else:

        raise ValueError(
            f"Unknown LLM_BACKEND: "
            f"{LLM_BACKEND}"
        )


# ============================================================
# Full initialization
# ============================================================

def initialize_rag():
    """
    Initialize:

        embeddings
            ↓
        structured Chroma DB
            ↓
        Qwen/vLLM

    Retrieval itself is created dynamically per request because
    each request has its own crop-condition metadata filter.
    """

    print()

    print(
        "=" * 60
    )

    print(
        "Initializing AgroMind RAG"
    )

    print(
        "=" * 60
    )


    vectordb = (
        initialize_retriever()
    )


    llm = (
        initialize_llm()
    )


    rag = {
        "vectordb":
            vectordb,

        "llm":
            llm,
    }


    print(
        "Metadata-filtered RAG ready."
    )

    print(
        "=" * 60
    )

    print(
        "AgroMind RAG is ready."
    )

    print(
        "=" * 60
    )

    print()


    return rag


# ============================================================
# LLM response extraction
# ============================================================

def extract_message_text(
    result,
):

    if isinstance(
        result,
        str,
    ):
        return result.strip()


    content = getattr(
        result,
        "content",
        None,
    )


    if isinstance(
        content,
        str,
    ):
        return content.strip()


    return str(
        result
    ).strip()


# ============================================================
# Query execution
# ============================================================

def ask_rag(
    rag,
    question,
    crop,
    condition,
    language="en",
    intent=None,
):
    """
    Perform metadata-filtered retrieval followed by grounded
    generation.

    Structured quick-button request:
        filters by crop + condition + language + intent.

    Free-text request:
        filters by crop + condition + language,
        then semantically ranks that pair's four Q&A entries.
    """

    print()

    print(
        f"Question: {question}"
    )

    print(
        f"Crop: {crop}"
    )

    print(
        f"Condition: {condition}"
    )

    print(
        f"Language: {language}"
    )

    print(
        f"Intent: {intent or 'free-text'}"
    )

    print(
        "-" * 60
    )


    try:

        source_documents = search(
            vectordb=
                rag["vectordb"],

            query=
                question,

            crop=
                crop,

            condition=
                condition,

            language=
                language,

            intent=
                intent,

            k=
                RETRIEVAL_K,
        )


        print(
            f"Filtered sources found: "
            f"{len(source_documents)}"
        )


        if not source_documents:

            return (
                (
                    "The AgroMind knowledge base "
                    "does not contain enough verified "
                    "information for this question."
                ),
                [],
            )


        context = "\n\n".join(
            document.page_content
            for document
            in source_documents
        )


        prompt = (
            AGROMIND_RAG_PROMPT.format(
                context=
                    context,

                question=
                    question,

                crop=
                    crop,

                condition=
                    condition,

                language=
                    language,
            )
        )


        result = (
            rag["llm"].invoke(
                prompt
            )
        )


        answer = (
            extract_message_text(
                result
            )
        )


        print()

        print(
            "Answer:"
        )

        print(
            answer
        )


        print()

        print(
            f"Retrieved sources: "
            f"{len(source_documents)}"
        )


        for index, document in enumerate(
            source_documents[:5],
            start=1,
        ):

            preview = (
                document.page_content
                .replace(
                    "\n",
                    " ",
                )
                [:220]
            )


            metadata = (
                document.metadata
            )


            print(
                f"  {index}. "
                f"[{metadata.get('crop')} | "
                f"{metadata.get('condition')} | "
                f"{metadata.get('intent')}] "
                f"{preview}..."
            )


        return (
            answer,
            source_documents,
        )


    except Exception as exc:

        print(
            f"RAG query error: "
            f"{exc}"
        )


        return (
            None,
            [],
        )