import base64
import mimetypes
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import requests


API_URL = "http://localhost:30802/v1/chat/completions"
MODEL = "Qwen/Qwen2.5-VL-7B-Instruct"

IMAGES_DIR = Path("evaluation/images")
PROMPT_FILE = Path("prompts/diagnosis_prompt.txt")
RESULTS_FILE = Path("evaluation/results_qwen25_20000_final.csv")
OUTPUT_FILE = Path("evaluation/load_results_qwen25_20000.csv")

TEMPERATURE = 0
MAX_TOKENS = 64
TIMEOUT = 180

# Start conservatively
CONCURRENCY_LEVELS = [1, 2, 4, 8, 16]

# Number of requests per concurrency level
REQUESTS_PER_LEVEL = 100


def image_to_data_url(image_path):
    mime_type, _ = mimetypes.guess_type(image_path)

    if mime_type is None:
        mime_type = "image/jpeg"

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


def send_request(filename, prompt):
    image_path = IMAGES_DIR / filename

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_to_data_url(image_path)
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

    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=TIMEOUT
        )

        latency = time.perf_counter() - start

        return {
            "filename": filename,
            "latency_seconds": latency,
            "http_status": response.status_code,
            "success": response.status_code == 200,
            "error": ""
        }

    except Exception as e:
        latency = time.perf_counter() - start

        return {
            "filename": filename,
            "latency_seconds": latency,
            "http_status": None,
            "success": False,
            "error": str(e)
        }


def main():
    prompt = PROMPT_FILE.read_text(
        encoding="utf-8"
    ).strip()

    # Use only images that already succeeded in Phase 1.
    previous = pd.read_csv(RESULTS_FILE)

    successful = previous[
        previous["http_status"] == 200
    ]["filename"].tolist()

    filenames = successful[:REQUESTS_PER_LEVEL]

    print("========================================")
    print("AgroMind Load Benchmark")
    print("========================================")
    print(f"Images per level: {len(filenames)}")

    all_results = []

    for concurrency in CONCURRENCY_LEVELS:
        print(f"\nTesting concurrency = {concurrency}")

        level_start = time.perf_counter()

        level_results = []

        with ThreadPoolExecutor(
            max_workers=concurrency
        ) as executor:

            futures = [
                executor.submit(
                    send_request,
                    filename,
                    prompt
                )
                for filename in filenames
            ]

            for future in as_completed(futures):
                level_results.append(
                    future.result()
                )

        total_time = time.perf_counter() - level_start

        for result in level_results:
            result["concurrency"] = concurrency
            result["total_level_time_seconds"] = total_time

        all_results.extend(level_results)

        df = pd.DataFrame(level_results)

        successful_df = df[df["success"] == True]

        throughput = (
            len(successful_df) / total_time
            if total_time > 0
            else 0
        )

        if len(successful_df) > 0:
            p50 = successful_df[
                "latency_seconds"
            ].quantile(0.50)

            p95 = successful_df[
                "latency_seconds"
            ].quantile(0.95)

            mean = successful_df[
                "latency_seconds"
            ].mean()

        else:
            p50 = p95 = mean = float("nan")

        print(
            f"Successful: {len(successful_df)}/{len(df)}"
        )
        print(
            f"Throughput: {throughput:.2f} requests/sec"
        )
        print(
            f"Mean latency: {mean:.3f} sec"
        )
        print(
            f"p50 latency: {p50:.3f} sec"
        )
        print(
            f"p95 latency: {p95:.3f} sec"
        )

    pd.DataFrame(all_results).to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nSaved raw load results to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
