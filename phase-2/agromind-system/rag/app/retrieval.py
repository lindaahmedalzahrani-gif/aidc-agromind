"""
Structured retrieval module for AgroMind RAG.

The knowledge base is indexed as one Chroma document per Q&A entry.

Each document receives metadata such as:

    crop
    condition
    language
    intent
    pair_key
    intent_key

This allows AgroMind to constrain retrieval to the exact verified
crop + condition pair before performing semantic similarity search.

The Chroma vector database is persisted across Pod restarts.

Behavior:
- If a valid existing database is present, load it.
- If no database exists, build it from the knowledge base.
- If REBUILD_VECTOR_DB=true, clear the database contents and rebuild it.

Important:
CHROMA_DB_PATH may be a Kubernetes-mounted directory, so we never
delete the mount point itself. We only delete its contents.
"""

import os
import re
import shutil

from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from app.config import (
    KNOWLEDGE_BASE_PATH,
    CHROMA_DB_PATH,
    EMBEDDING_MODEL,
    RETRIEVAL_K,
    REBUILD_VECTOR_DB,
)


# ============================================================
# Label normalization
# ============================================================

def normalize_pair_value(value):
    """
    Normalize crop and condition labels.

    Examples:

        Blossom-End Rot
        blossom_end_rot
        Blossom end rot

    all become:

        blossom end rot
    """

    value = str(value).strip().lower()

    for character in (
        "-",
        "_",
        "–",
        "—",
    ):
        value = value.replace(
            character,
            " ",
        )

    return " ".join(
        value.split()
    )


# ============================================================
# Crop aliases
# ============================================================

CROP_ALIASES = {
    "tomatoes":
        "tomato",

    "tomato plant":
        "tomato",

    "peppers":
        "pepper",

    "chili":
        "pepper",

    "chilli":
        "pepper",

    "chili pepper":
        "pepper",

    "chilli pepper":
        "pepper",

    "cucumbers":
        "cucumber",

    "aubergine":
        "eggplant",

    "aubergines":
        "eggplant",

    "maize":
        "corn",

    "napa cabbage":
        "chinese cabbage",

    "cow pea":
        "cowpea",

    "long bean":
        "cowpea",

    "yardlong bean":
        "cowpea",
}


def canonicalize_crop(value):
    normalized = normalize_pair_value(
        value
    )

    return CROP_ALIASES.get(
        normalized,
        normalized,
    )


# ============================================================
# Diagnosis aliases
# ============================================================

DIAGNOSIS_ALIASES = {

    # Mites
    "spider mite":
        "mites",

    "spider mites":
        "mites",

    "red spider mite":
        "mites",

    "red spider mites":
        "mites",

    "two spotted spider mite":
        "mites",

    "two spotted spider mites":
        "mites",

    "mite infestation":
        "mites",


    # Blossom end rot
    "blossom end rot disorder":
        "blossom end rot",

    "blossom end rot disease":
        "blossom end rot",


    # Whiteflies
    "whitefly":
        "whiteflies",

    "white fly":
        "whiteflies",

    "white flies":
        "whiteflies",

    "whitefly infestation":
        "whiteflies",


    # Aphids
    "aphid":
        "aphids",

    "aphid infestation":
        "aphids",


    # Thrips
    "thrip":
        "thrips",

    "thrips infestation":
        "thrips",


    # Mildews
    "powdery mildew disease":
        "powdery mildew",

    "downy mildew disease":
        "downy mildew",


    # Anthracnose
    "anthracnose disease":
        "anthracnose",


    # Viral disease
    "virus":
        "viral disease",

    "virus disease":
        "viral disease",

    "viral infection":
        "viral disease",


    # Bacterial disease
    "bacterial infection":
        "bacterial disease",


    # Bacterial spot
    "bacterial spot disease":
        "bacterial spot",


    # Root rot
    "root rot disease":
        "root rot",


    # Phytophthora root/crown rot
    "phytophthora root rot":
        "phytophthora root and crown rot",

    "phytophthora crown rot":
        "phytophthora root and crown rot",

    "phytophthora root crown rot":
        "phytophthora root and crown rot",


    # Citrus leafminer
    "citrus leaf miner":
        "citrus leafminer",


    # Fall armyworm
    "fall army worm":
        "fall armyworm",


    # Clubroot
    "club root":
        "clubroot",


    # Chinese aliases
    "红蜘蛛":
        "螨",

    "叶螨":
        "螨",

    "蜘蛛螨":
        "螨",
}


def canonicalize_diagnosis(value):
    normalized = normalize_pair_value(
        value
    )

    return DIAGNOSIS_ALIASES.get(
        normalized,
        normalized,
    )


# ============================================================
# Intent detection
# ============================================================

ENGLISH_INTENTS = {
    "what causes this?":
        "cause",

    "what symptoms should i look for?":
        "symptoms",

    "how can i manage it?":
        "management",

    "tell me more about this crop.":
        "crop_info",
}


CHINESE_INTENTS = {
    "病因是什么？":
        "cause",

    "应该注意哪些症状？":
        "symptoms",

    "如何防治？":
        "management",

    "介绍一下这种作物。":
        "crop_info",
}


def detect_intent(
    question,
    language,
):
    question = str(
        question
    ).strip()

    if language == "zh":
        return CHINESE_INTENTS.get(
            question,
            "other",
        )

    return ENGLISH_INTENTS.get(
        question.lower(),
        "other",
    )


# ============================================================
# Metadata keys
# ============================================================

def make_pair_key(
    crop,
    condition,
    language,
):
    return (
        f"{canonicalize_crop(crop)}"
        "|||"
        f"{canonicalize_diagnosis(condition)}"
        "|||"
        f"{language}"
    )


def make_intent_key(
    crop,
    condition,
    language,
    intent,
):
    return (
        f"{make_pair_key(crop, condition, language)}"
        "|||"
        f"{intent}"
    )


# ============================================================
# Knowledge-base parser
# ============================================================

HEADER_PATTERN = re.compile(
    r"^\[\s*(.*?)\s*\|\s*(.*?)\s*\]"
    r"\s*(Q:|问：|问:)\s*(.*?)\s*$"
)


def parse_knowledge_base():
    """
    Convert knowledge_base.txt into structured Document objects.

    Example source:

        [Pepper | Mites] Q: How can I manage it?
        A: ...

    becomes one Chroma Document with metadata:

        crop=pepper
        condition=mites
        language=en
        intent=management
    """

    if not os.path.exists(
        KNOWLEDGE_BASE_PATH
    ):
        raise FileNotFoundError(
            f"Knowledge base not found: "
            f"{KNOWLEDGE_BASE_PATH}"
        )

    with open(
        KNOWLEDGE_BASE_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        lines = file.readlines()


    documents = []

    index = 0


    while index < len(lines):

        line = lines[
            index
        ].strip()

        match = HEADER_PATTERN.match(
            line
        )


        if not match:

            index += 1
            continue


        raw_crop = (
            match.group(1).strip()
        )

        raw_condition = (
            match.group(2).strip()
        )

        marker = (
            match.group(3)
        )

        question = (
            match.group(4).strip()
        )


        language = (
            "zh"
            if marker.startswith("问")
            else "en"
        )


        # Find the following non-empty answer line.
        answer = ""

        answer_index = (
            index + 1
        )


        while (
            answer_index
            < len(lines)
        ):

            candidate = lines[
                answer_index
            ].strip()


            if not candidate:
                answer_index += 1
                continue


            if (
                candidate.startswith(
                    "A:"
                )
            ):
                answer = candidate[
                    2:
                ].strip()

            elif (
                candidate.startswith(
                    "答："
                )
            ):
                answer = candidate[
                    2:
                ].strip()

            elif (
                candidate.startswith(
                    "答:"
                )
            ):
                answer = candidate[
                    2:
                ].strip()


            break


        if not answer:

            print(
                "[RAG] Warning: "
                "no answer found for "
                f"{raw_crop} | "
                f"{raw_condition} | "
                f"{question}"
            )

            index += 1
            continue


        crop = (
            canonicalize_crop(
                raw_crop
            )
        )

        condition = (
            canonicalize_diagnosis(
                raw_condition
            )
        )

        intent = (
            detect_intent(
                question,
                language,
            )
        )


        pair_key = (
            make_pair_key(
                crop,
                condition,
                language,
            )
        )


        intent_key = (
            make_intent_key(
                crop,
                condition,
                language,
                intent,
            )
        )


        if language == "zh":

            page_content = (
                f"[{raw_crop} | "
                f"{raw_condition}]\n"
                f"问题：{question}\n"
                f"答案：{answer}"
            )

        else:

            page_content = (
                f"[{raw_crop} | "
                f"{raw_condition}]\n"
                f"Question: {question}\n"
                f"Answer: {answer}"
            )


        document = Document(
            page_content=
                page_content,

            metadata={
                "crop":
                    crop,

                "condition":
                    condition,

                "language":
                    language,

                "intent":
                    intent,

                "pair_key":
                    pair_key,

                "intent_key":
                    intent_key,

                "display_crop":
                    raw_crop,

                "display_condition":
                    raw_condition,
            },
        )


        documents.append(
            document
        )


        index = (
            answer_index + 1
        )


    return documents


def load_supported_pairs():
    """
    Return all canonical crop-condition pairs represented
    by the structured KB documents.
    """

    documents = (
        parse_knowledge_base()
    )

    pairs = set()


    for document in documents:

        pairs.add(
            (
                document.metadata[
                    "crop"
                ],

                document.metadata[
                    "condition"
                ],
            )
        )


    print(
        f"[RAG] Loaded "
        f"{len(pairs)} supported KB pairs."
    )

    return pairs


# ============================================================
# Embeddings
# ============================================================

def create_embeddings():

    return HuggingFaceEmbeddings(
        model_name=
            EMBEDDING_MODEL,

        encode_kwargs={
            "normalize_embeddings":
                True
        },
    )


# ============================================================
# Existing DB detection
# ============================================================

def existing_vectordb_available():

    if not os.path.isdir(
        CHROMA_DB_PATH
    ):
        return False


    try:

        entries = os.listdir(
            CHROMA_DB_PATH
        )

    except OSError:

        return False


    if not entries:
        return False


    return (
        "chroma.sqlite3"
        in entries
    )


# ============================================================
# Clear DB contents safely
# ============================================================

def clear_directory_contents(
    path,
):

    os.makedirs(
        path,
        exist_ok=True,
    )


    for name in os.listdir(
        path
    ):

        item = os.path.join(
            path,
            name,
        )


        if (
            os.path.isdir(item)
            and
            not os.path.islink(item)
        ):

            shutil.rmtree(
                item
            )

        else:

            os.remove(
                item
            )


# ============================================================
# Chroma load / create
# ============================================================

def load_vectordb(
    embeddings,
):

    print(
        f"Loading existing ChromaDB from: "
        f"{CHROMA_DB_PATH}"
    )


    return Chroma(
        persist_directory=
            CHROMA_DB_PATH,

        embedding_function=
            embeddings,
    )


def create_vectordb(
    documents,
    embeddings,
):

    os.makedirs(
        CHROMA_DB_PATH,
        exist_ok=True,
    )


    vectordb = (
        Chroma.from_documents(
            documents=
                documents,

            embedding=
                embeddings,

            persist_directory=
                CHROMA_DB_PATH,
        )
    )


    vectordb.persist()


    return vectordb


def rebuild_vectordb(
    embeddings,
):

    print(
        "Rebuilding structured ChromaDB..."
    )


    clear_directory_contents(
        CHROMA_DB_PATH
    )


    documents = (
        parse_knowledge_base()
    )


    print(
        f"Parsed "
        f"{len(documents)} "
        "structured Q&A documents."
    )


    vectordb = (
        create_vectordb(
            documents,
            embeddings,
        )
    )


    print(
        f"Stored at: "
        f"{CHROMA_DB_PATH}"
    )


    return vectordb


# ============================================================
# Initialization
# ============================================================

def initialize_retriever():

    print(
        "Initializing AgroMind retriever..."
    )


    print(
        f"Embedding model: "
        f"{EMBEDDING_MODEL}"
    )


    embeddings = (
        create_embeddings()
    )


    print(
        "Embedding model loaded."
    )


    if (
        existing_vectordb_available()
        and
        not REBUILD_VECTOR_DB
    ):

        vectordb = (
            load_vectordb(
                embeddings
            )
        )


        print(
            "Existing ChromaDB loaded."
        )


        return vectordb


    return rebuild_vectordb(
        embeddings
    )


# ============================================================
# Filtered search
# ============================================================

def search(
    vectordb,
    query,
    crop,
    condition,
    language,
    intent=None,
    k=RETRIEVAL_K,
):
    """
    Search ONLY documents belonging to the requested verified pair.

    Structured button requests also filter by intent.

    Free-text requests search across the four Q&A entries belonging
    to the same crop-condition pair.
    """

    crop = canonicalize_crop(
        crop
    )

    condition = (
        canonicalize_diagnosis(
            condition
        )
    )

    language = (
        "zh"
        if language == "zh"
        else "en"
    )


    if intent:

        filter_value = (
            make_intent_key(
                crop,
                condition,
                language,
                intent,
            )
        )

        metadata_filter = {
            "intent_key":
                filter_value
        }

    else:

        filter_value = (
            make_pair_key(
                crop,
                condition,
                language,
            )
        )

        metadata_filter = {
            "pair_key":
                filter_value
        }


    documents = (
        vectordb.similarity_search(
            query=
                query,

            k=
                k,

            filter=
                metadata_filter,
        )
    )


    return documents