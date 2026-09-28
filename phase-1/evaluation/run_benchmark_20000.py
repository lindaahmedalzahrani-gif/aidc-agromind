import argparse
import base64
import csv
import mimetypes
import time
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm


# ---------------------------------------------------------
# Fixed benchmark configuration
# ---------------------------------------------------------

API_URL = "http://localhost:30802/v1/chat/completions"
MODEL = "Qwen/Qwen2.5-VL-7B-Instruct"

LABELS_FILE = Path("evaluation/labels.csv")
IMAGES_DIR = Path("evaluation/images")
PROMPT_FILE = Path("prompts/diagnosis_prompt.txt")

RESULTS_FILE = Path("evaluation/results_qwen25_20000.csv")

TEMPERATURE = 0
MAX_TOKENS = 64
REQUEST_TIMEOUT = 180


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def image_to_data_url(image_path):
    """
    Convert a local image into a base64 data URL
    that can be sent to the OpenAI-compatible vLLM API.
    """

    mime_type, _ = mimetypes.guess_type(image_path)

    if mime_type is None:
        mime_type = "image/jpeg"

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


def load_completed_filenames(results_file):
    """
    If results.csv already exists, read the filenames
    already completed so the benchmark can resume.
    """

    if not results_file.exists():
        return set()

    try:
        previous_results = pd.read_csv(results_file)

        if "filename" not in previous_results.columns:
            return set()

        return set(previous_results["filename"].dropna().astype(str))

    except Exception:
        return set()


def create_results_file_if_needed(results_file):
    """
    Create results.csv with the required header.
    """

    if results_file.exists():
        return

    fieldnames = [
        "filename",
        "true_crop",
        "true_disease",
        "true_disease_type",
        "model_prediction",
        "latency_seconds",
        "http_status",
        "error",
    ]

    with open(results_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()


def save_result(results_file, result):
    """
    Append one result immediately.

    This protects us from losing all progress if
    the benchmark is interrupted.
    """

    with open(results_file, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=result.keys())
        writer.writerow(result)


# ---------------------------------------------------------
# Single image inference
# ---------------------------------------------------------

def run_inference(image_path, prompt):
    image_url = image_to_data_url(image_path)

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }

    start = time.perf_counter()

    response = requests.post(
        API_URL,
        json=payload,
        timeout=REQUEST_TIMEOUT
    )

    latency = time.perf_counter() - start

    response.raise_for_status()

    result = response.json()

    prediction = result["choices"][0]["message"]["content"].strip()

    return prediction, latency, response.status_code


# ---------------------------------------------------------
# Main benchmark
# ---------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process this many remaining images."
    )

    args = parser.parse_args()

    print("========================================")
    print("AgroMind Phase 1 Benchmark")
    print("========================================")

    print(f"Model: {MODEL}")
    print(f"Endpoint: {API_URL}")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Max tokens: {MAX_TOKENS}")
    print()

    # Load dataset
    df = pd.read_csv(LABELS_FILE)

    print(f"Total evaluation images: {len(df)}")

    # Load fixed prompt
    prompt = PROMPT_FILE.read_text(
        encoding="utf-8"
    ).strip()

    # Prepare results file
    create_results_file_if_needed(RESULTS_FILE)

    completed = load_completed_filenames(RESULTS_FILE)

    if completed:
        print(f"Already completed: {len(completed)}")

    remaining_df = df[
        ~df["filename"].astype(str).isin(completed)
    ].copy()

    if args.limit is not None:
        remaining_df = remaining_df.head(args.limit)

    print(f"Images to process now: {len(remaining_df)}")
    print()

    if len(remaining_df) == 0:
        print("Nothing to process.")
        return

    success_count = 0
    error_count = 0

    for _, row in tqdm(
        remaining_df.iterrows(),
        total=len(remaining_df),
        desc="Benchmarking"
    ):

        filename = str(row["filename"])
        image_path = IMAGES_DIR / filename

        true_crop = row.get("crop", "")
        true_disease = row.get("disease", "")
        true_disease_type = row.get("disease_type", "")

        prediction = ""
        latency = ""
        http_status = ""
        error = ""

        try:
            if not image_path.exists():
                raise FileNotFoundError(
                    f"Image not found: {image_path}"
                )

            prediction, latency, http_status = run_inference(
                image_path,
                prompt
            )

            success_count += 1

        except Exception as e:
            error = str(e)
            error_count += 1

        result = {
            "filename": filename,
            "true_crop": true_crop,
            "true_disease": true_disease,
            "true_disease_type": true_disease_type,
            "model_prediction": prediction,
            "latency_seconds": latency,
            "http_status": http_status,
            "error": error,
        }

        # Save immediately after every image
        save_result(RESULTS_FILE, result)

    print()
    print("========================================")
    print("Benchmark run finished")
    print("========================================")
    print(f"Successful requests: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
