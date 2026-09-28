import os
import secrets
from typing import Any

import requests
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ============================================================
# Configuration
# ============================================================

MODEL_API_URL = os.getenv(
    "MODEL_API_URL",
    "http://agromind-serving:8000",
).rstrip("/")

RAG_API_URL = os.getenv(
    "RAG_API_URL",
    "http://agromind-rag:5000",
).rstrip("/")

DIAGNOSIS_MODEL = os.getenv(
    "DIAGNOSIS_MODEL",
    "agromind-diagnosis",
)

BASE_MODEL = os.getenv(
    "BASE_MODEL",
    "Qwen/Qwen2.5-VL-7B-Instruct",
)

API_KEY = os.getenv(
    "API_KEY",
    "",
)

REQUEST_TIMEOUT = int(
    os.getenv(
        "REQUEST_TIMEOUT",
        "180",
    )
)


# ============================================================
# FastAPI
# ============================================================

app = FastAPI(
    title="AgroMind API",
    version="2.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Authentication
# ============================================================

def require_api_key(
    authorization: str | None,
    x_api_key: str | None,
):
    supplied = None

    if authorization:
        parts = authorization.split(
            " ",
            1,
        )

        if (
            len(parts) == 2
            and
            parts[0].lower() == "bearer"
        ):
            supplied = parts[1]

    if not supplied and x_api_key:
        supplied = x_api_key

    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API key is not configured",
        )

    if (
        not supplied
        or
        not secrets.compare_digest(
            supplied,
            API_KEY,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )


# ============================================================
# Request models
# ============================================================

class DiagnoseRequest(BaseModel):
    image: str | None = None
    image_url: str | None = None
    lang: str = "en"
    prompt: str | None = None


class ChatRequest(BaseModel):
    crop: str
    disease: str

    # Optional now.
    #
    # Quick buttons send:
    #   question_type = cause / symptoms / management / crop_info
    #
    # Typed questions omit question_type and instead send:
    #   question = "Can this spread to nearby plants?"
    question_type: str | None = None

    lang: str = "en"

    question: str | None = None


# ============================================================
# Diagnosis prompts
# ============================================================

EN_DIAGNOSIS_PROMPT = (
    "Identify the crop and visible disease or pest. "
    "Answer only in the format: crop, disease. "
    "If it is a pest infestation, you may additionally return: "
    "crop, pest, pest species. "
    "Return names only. Do not explain."
)


ZH_DIAGNOSIS_PROMPT = (
    "请识别图片中的作物和病虫害，按「作物，病害」格式回答；"
    "若为虫害，再补充具体虫种，按「作物，病害，虫种」。"
    "只回答名称，不要解释。"
)


# ============================================================
# Health
# ============================================================

@app.get("/health")
def health():

    status: dict[str, Any] = {
        "status": "ok",
        "service": "agromind-api",
        "diagnosis_model": DIAGNOSIS_MODEL,
    }


    try:
        model_health = requests.get(
            f"{MODEL_API_URL}/health",
            timeout=5,
        )

        status["model_service"] = (
            "ok"
            if model_health.ok
            else "error"
        )

    except requests.RequestException:
        status["model_service"] = (
            "unreachable"
        )


    try:
        rag_health = requests.get(
            f"{RAG_API_URL}/health",
            timeout=5,
        )

        status["rag_service"] = (
            "ok"
            if rag_health.ok
            else "error"
        )

    except requests.RequestException:
        status["rag_service"] = (
            "unreachable"
        )


    return status


# ============================================================
# Diagnosis
#
# Always routes to:
#
#   agromind-diagnosis
#
# which is:
#
#   Qwen2.5-VL-7B + final LoRA adapter
# ============================================================

@app.post("/api/diagnose")
def diagnose(
    request: DiagnoseRequest,

    authorization: str | None = Header(
        default=None
    ),

    x_api_key: str | None = Header(
        default=None,
        alias="X-API-Key",
    ),
):

    require_api_key(
        authorization,
        x_api_key,
    )


    image = (
        request.image_url
        or
        request.image
    )


    if not image:
        raise HTTPException(
            status_code=400,
            detail=(
                "image or image_url is required"
            ),
        )


    # Allow:
    #
    # plain base64
    # data:image/...;base64,...
    # http://...
    # https://...
    #
    if not image.startswith(
        (
            "data:",
            "http://",
            "https://",
        )
    ):
        image = (
            "data:image/jpeg;base64,"
            + image
        )


    if request.prompt:
        prompt = request.prompt

    elif request.lang.lower().startswith(
        "zh"
    ):
        prompt = ZH_DIAGNOSIS_PROMPT

    else:
        prompt = EN_DIAGNOSIS_PROMPT


    payload = {
        "model": DIAGNOSIS_MODEL,

        "messages": [
            {
                "role": "user",

                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },

                    {
                        "type": "image_url",

                        "image_url": {
                            "url": image
                        },
                    },
                ],
            }
        ],

        "temperature": 0,

        "max_tokens": 64,
    }


    try:
        response = requests.post(
            (
                f"{MODEL_API_URL}"
                "/v1/chat/completions"
            ),

            json=payload,

            timeout=REQUEST_TIMEOUT,
        )

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,

            detail=(
                "Model service unavailable: "
                f"{exc}"
            ),
        )


    if not response.ok:
        raise HTTPException(
            status_code=502,

            detail={
                "message":
                    "Diagnosis model request failed",

                "upstream_status":
                    response.status_code,

                "upstream_response":
                    response.text[:1000],
            },
        )


    body = response.json()


    return {
        "model":
            DIAGNOSIS_MODEL,

        "diagnosis":
            body[
                "choices"
            ][0][
                "message"
            ][
                "content"
            ],

        "usage":
            body.get("usage"),
    }


# ============================================================
# RAG chat
#
# Structured quick-button request:
#
# {
#   "crop": "Pepper",
#   "disease": "Anthracnose",
#   "question_type": "management",
#   "lang": "en"
# }
#
#
# Free-text request:
#
# {
#   "crop": "Pepper",
#   "disease": "Anthracnose",
#   "question": "Can this spread to nearby plants?",
#   "lang": "en"
# }
# ============================================================

@app.post("/api/chat")
def chat(
    request: ChatRequest,

    authorization: str | None = Header(
        default=None
    ),

    x_api_key: str | None = Header(
        default=None,
        alias="X-API-Key",
    ),
):

    require_api_key(
        authorization,
        x_api_key,
    )


    # Must provide either:
    #
    # question_type
    #
    # OR
    #
    # a typed question.
    #
    if (
        not request.question_type
        and
        not (
            request.question
            and
            request.question.strip()
        )
    ):
        raise HTTPException(
            status_code=400,

            detail=(
                "Either question_type "
                "or question is required"
            ),
        )


    # exclude_none=True is important.
    #
    # Typed questions will NOT send:
    #
    #   question_type: null
    #
    # to the RAG service.
    #
    payload = request.model_dump(
        exclude_none=True
    )


    try:
        response = requests.post(
            f"{RAG_API_URL}/api/ask",

            json=payload,

            timeout=REQUEST_TIMEOUT,
        )

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,

            detail=(
                "RAG service unavailable: "
                f"{exc}"
            ),
        )


    if not response.ok:
        raise HTTPException(
            status_code=502,

            detail={
                "message":
                    "RAG request failed",

                "upstream_status":
                    response.status_code,

                "upstream_response":
                    response.text[:1000],
            },
        )


    return response.json()


# ============================================================
# OpenAI-compatible model listing
# ============================================================

@app.get("/v1/models")
def models(
    authorization: str | None = Header(
        default=None
    ),

    x_api_key: str | None = Header(
        default=None,
        alias="X-API-Key",
    ),
):

    require_api_key(
        authorization,
        x_api_key,
    )


    try:
        response = requests.get(
            f"{MODEL_API_URL}/v1/models",

            timeout=10,
        )

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,

            detail=(
                "Model service unavailable: "
                f"{exc}"
            ),
        )


    if not response.ok:
        raise HTTPException(
            status_code=502,

            detail=(
                "Unable to retrieve models"
            ),
        )


    return response.json()


# ============================================================
# OpenAI-compatible chat completions proxy
# ============================================================

@app.post("/v1/chat/completions")
def chat_completions(
    payload: dict[str, Any],

    authorization: str | None = Header(
        default=None
    ),

    x_api_key: str | None = Header(
        default=None,
        alias="X-API-Key",
    ),
):

    require_api_key(
        authorization,
        x_api_key,
    )


    requested_model = payload.get(
        "model",
        DIAGNOSIS_MODEL,
    )


    allowed_models = {
        DIAGNOSIS_MODEL,
        BASE_MODEL,
    }


    if requested_model not in allowed_models:
        raise HTTPException(
            status_code=400,

            detail=(
                "Model is not allowed"
            ),
        )


    payload["model"] = (
        requested_model
    )


    try:
        response = requests.post(
            (
                f"{MODEL_API_URL}"
                "/v1/chat/completions"
            ),

            json=payload,

            timeout=REQUEST_TIMEOUT,
        )

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,

            detail=(
                "Model service unavailable: "
                f"{exc}"
            ),
        )


    try:
        body = response.json()

    except ValueError:
        body = {
            "upstream_response":
                response.text
        }


    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,

            detail=body,
        )


    return body