"""
AgroMind RAG API

Internal Kubernetes service used by the AgroMind application API.

Endpoints:
    GET  /health
    POST /api/ask

Both structured and free-text requests:

1. normalize the crop and diagnosis;
2. verify that the pair exists in the AgroMind KB;
3. restrict Chroma retrieval to that exact pair;
4. generate an answer only from the filtered context.
"""

from flask import (
    Flask,
    jsonify,
    request,
)

from app.rag import (
    initialize_rag,
    ask_rag,
)

from app.retrieval import (
    load_supported_pairs as load_pairs_from_kb,
    canonicalize_crop,
    canonicalize_diagnosis,
)


# ============================================================
# UI question templates
# ============================================================

QUESTION_TEMPLATES = {
    "cause":
        "What causes this?",

    "symptoms":
        "What symptoms should I look for?",

    "management":
        "How can I manage it?",

    "crop_info":
        "Tell me more about this crop.",
}


CHINESE_QUESTION_TEMPLATES = {
    "cause":
        "病因是什么？",

    "symptoms":
        "应该注意哪些症状？",

    "management":
        "如何防治？",

    "crop_info":
        "介绍一下这种作物。",
}


# ============================================================
# Flask
# ============================================================

app = Flask(
    __name__
)

app.json.ensure_ascii = False

rag = None
supported_pairs = set()


# ============================================================
# Supported KB pair index
# ============================================================

def load_supported_pairs():
    """
    Wrapper kept here so existing wsgi.py startup code continues
    to work without changes.
    """

    return (
        load_pairs_from_kb()
    )


def pair_is_supported(
    crop,
    disease,
):

    pair = (
        canonicalize_crop(
            crop
        ),

        canonicalize_diagnosis(
            disease
        ),
    )


    return (
        pair
        in supported_pairs
    )


# ============================================================
# Unsupported response
# ============================================================

def unsupported_pair_response(
    crop,
    disease,
    question,
    lang,
):

    if lang == "zh":

        answer = (
            "AgroMind 知识库目前没有"
            f"关于「{crop} | {disease}」"
            "的已验证条目。"
        )

    else:

        answer = (
            "The AgroMind knowledge base "
            "does not currently contain a "
            "verified entry for "
            f"{crop} | {disease}."
        )


    return jsonify(
        {
            "question":
                question,

            "answer":
                answer,

            "supported":
                False,

            "sources_count":
                0,
        }
    ), 200


# ============================================================
# CORS
# ============================================================

@app.after_request
def add_cors_headers(
    response,
):

    response.headers[
        "Access-Control-Allow-Origin"
    ] = "*"

    response.headers[
        "Access-Control-Allow-Methods"
    ] = "GET, POST, OPTIONS"

    response.headers[
        "Access-Control-Allow-Headers"
    ] = "Content-Type"

    return response


# ============================================================
# Health
# ============================================================

@app.route(
    "/health",
    methods=["GET"],
)
def health():

    return jsonify(
        {
            "status":
                "ok",

            "knowledge_base_pairs":
                len(
                    supported_pairs
                ),
        }
    ), 200


# ============================================================
# Ask RAG
# ============================================================

@app.route(
    "/api/ask",
    methods=[
        "POST",
        "OPTIONS",
    ],
)
def api_ask():

    if request.method == "OPTIONS":

        return "", 204


    try:

        data = (
            request.get_json(
                silent=True
            )
            or {}
        )


        # ====================================================
        # Structured quick-button request
        # ====================================================

        if (
            "question_type"
            in data

            and
            "crop"
            in data

            and
            "disease"
            in data
        ):

            raw_crop = str(
                data["crop"]
            ).strip()


            raw_disease = str(
                data["disease"]
            ).strip()


            question_type = str(
                data[
                    "question_type"
                ]
            ).strip()


            lang = str(
                data.get(
                    "lang",
                    "en",
                )
            ).strip().lower()


            lang = (
                "zh"
                if lang == "zh"
                else "en"
            )


            if (
                not raw_crop
                or
                not raw_disease
            ):

                return jsonify(
                    {
                        "error": (
                            "crop and disease "
                            "cannot be empty"
                        )
                    }
                ), 400


            crop = (
                canonicalize_crop(
                    raw_crop
                )
            )


            disease = (
                canonicalize_diagnosis(
                    raw_disease
                )
            )


            templates = (
                CHINESE_QUESTION_TEMPLATES
                if lang == "zh"
                else QUESTION_TEMPLATES
            )


            if (
                question_type
                not in templates
            ):

                return jsonify(
                    {
                        "error": (
                            "Unknown question_type: "
                            f"{question_type}"
                        )
                    }
                ), 400


            display_question = (
                f"{crop} "
                f"{disease} "
                f"{templates[question_type]}"
            )


            if not pair_is_supported(
                crop,
                disease,
            ):

                return (
                    unsupported_pair_response(
                        crop=
                            raw_crop,

                        disease=
                            raw_disease,

                        question=
                            display_question,

                        lang=
                            lang,
                    )
                )


            rag_question = (
                display_question
            )


            answer, sources = (
                ask_rag(
                    rag=
                        rag,

                    question=
                        rag_question,

                    crop=
                        crop,

                    condition=
                        disease,

                    language=
                        lang,

                    intent=
                        question_type,
                )
            )


        # ====================================================
        # Free-text follow-up request
        # ====================================================

        elif "question" in data:

            user_question = str(
                data[
                    "question"
                ]
            ).strip()


            if not user_question:

                return jsonify(
                    {
                        "error":
                            "question cannot be empty"
                    }
                ), 400


            if (
                "crop"
                not in data

                or
                "disease"
                not in data
            ):

                return jsonify(
                    {
                        "error": (
                            "Free-text questions require "
                            "crop and disease context"
                        )
                    }
                ), 400


            raw_crop = str(
                data[
                    "crop"
                ]
            ).strip()


            raw_disease = str(
                data[
                    "disease"
                ]
            ).strip()


            lang = str(
                data.get(
                    "lang",
                    "en",
                )
            ).strip().lower()


            lang = (
                "zh"
                if lang == "zh"
                else "en"
            )


            if (
                not raw_crop
                or
                not raw_disease
            ):

                return jsonify(
                    {
                        "error": (
                            "crop and disease "
                            "cannot be empty"
                        )
                    }
                ), 400


            crop = (
                canonicalize_crop(
                    raw_crop
                )
            )


            disease = (
                canonicalize_diagnosis(
                    raw_disease
                )
            )


            if not pair_is_supported(
                crop,
                disease,
            ):

                return (
                    unsupported_pair_response(
                        crop=
                            raw_crop,

                        disease=
                            raw_disease,

                        question=
                            user_question,

                        lang=
                            lang,
                    )
                )


            display_question = (
                user_question
            )


            rag_question = (
                f"{crop} "
                f"{disease} "
                f"{user_question}"
            )


            answer, sources = (
                ask_rag(
                    rag=
                        rag,

                    question=
                        rag_question,

                    crop=
                        crop,

                    condition=
                        disease,

                    language=
                        lang,

                    intent=
                        None,
                )
            )


        # ====================================================
        # Invalid request
        # ====================================================

        else:

            return jsonify(
                {
                    "error": (
                        "Provide either "
                        "(crop, disease, question_type) "
                        "or "
                        "(crop, disease, question)"
                    )
                }
            ), 400


        # ====================================================
        # Generation failure
        # ====================================================

        if answer is None:

            return jsonify(
                {
                    "error": (
                        "Failed to generate an answer"
                    )
                }
            ), 500


        # ====================================================
        # Successful grounded answer
        # ====================================================

        return jsonify(
            {
                "question":
                    display_question,

                "answer":
                    answer,

                "supported":
                    True,

                "sources_count":
                    len(
                        sources
                    ),
            }
        ), 200


    except Exception as exc:

        print(
            f"[RAG API] Error: "
            f"{exc}"
        )


        return jsonify(
            {
                "error":
                    str(
                        exc
                    )
            }
        ), 500


# ============================================================
# Startup
# ============================================================

def main():

    global rag
    global supported_pairs


    supported_pairs = (
        load_supported_pairs()
    )


    rag = (
        initialize_rag()
    )


    print()

    print(
        "=" * 60
    )

    print(
        "AgroMind RAG API starting"
    )

    print(
        "=" * 60
    )


    print(
        f"Knowledge-base pairs: "
        f"{len(supported_pairs)}"
    )


    print(
        "POST http://0.0.0.0:5000/api/ask"
    )


    print(
        "GET  http://0.0.0.0:5000/health"
    )


    print()


    app.run(
        host=
            "0.0.0.0",

        port=
            5000,

        debug=
            False,
    )


if __name__ == "__main__":

    main()