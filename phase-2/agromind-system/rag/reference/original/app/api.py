"""
AgroMind RAG - API Server for LeafGuard UI integration
"""

from flask import Flask, request, jsonify
from app.rag import initialize_rag, ask_rag

# Maps the UI's 4 question buttons to the exact phrasing used in the knowledge base
QUESTION_TEMPLATES = {
    "cause": "What causes this?",
    "symptoms": "What symptoms should I look for?",
    "management": "How can I manage it?",
    "crop_info": "Tell me more about this crop.",
}

CHINESE_QUESTION_TEMPLATES = {
    "cause": "病因是什么？",
    "symptoms": "应该注意哪些症状？",
    "management": "如何防治？",
    "crop_info": "介绍一下这种作物。",
}

app = Flask(__name__)
rag = None  # initialized in main()


@app.after_request
def add_cors_headers(response):
    # Allows the LeafGuard frontend (a different origin) to call this API from the browser
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/ask", methods=["POST"])
def api_ask():
    """
    Structured mode (matches the UI's 4 buttons):
        {"crop": "Cucumber", "disease": "Downy Mildew", "question_type": "cause", "lang": "en"}

    Free-text mode (fallback):
        {"question": "How can I manage cucumber downy mildew?"}
    """
    try:
        data = request.json or {}

        if "question_type" in data and "crop" in data and "disease" in data:
            crop = data["crop"]
            disease = data["disease"]
            q_type = data["question_type"]
            lang = data.get("lang", "en")

            templates = CHINESE_QUESTION_TEMPLATES if lang == "zh" else QUESTION_TEMPLATES
            if q_type not in templates:
                return jsonify({"error": f"Unknown question_type: {q_type}"}), 400

            question = f"{crop} {disease} {templates[q_type]}"
        elif "question" in data:
            question = data["question"]
        else:
            return jsonify({"error": "Provide either (crop, disease, question_type) or (question)"}), 400

        answer, sources = ask_rag(rag, question)

        if answer is None:
            return jsonify({"error": "Failed to generate an answer"}), 500

        return jsonify({
            "question": question,
            "answer": answer,
            "sources_count": len(sources),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    global rag
    rag = initialize_rag()

    print("\n" + "=" * 60)
    print("API Server starting")
    print("=" * 60)
    print("POST http://0.0.0.0:5000/api/ask")
    print("GET  http://0.0.0.0:5000/health")
    print()
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
