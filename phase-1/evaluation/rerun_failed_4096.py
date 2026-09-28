import pandas as pd
import requests
import base64
import mimetypes
import re
import time
from pathlib import Path

API_URL = "http://localhost:30802/v1/chat/completions"
MODEL = "Qwen/Qwen2.5-VL-7B-Instruct"

RESULTS_FILE = "evaluation/results_phase1_4096_original.csv"
IMAGES_DIR = Path("evaluation/images")
PROMPT_FILE = Path("prompts/diagnosis_prompt.txt")
OUTPUT_FILE = "evaluation/failed_requests_4096_detailed.csv"

TIMEOUT = 180

df = pd.read_csv(RESULTS_FILE)

# Original failed requests
failed = df[df["model_prediction"].isna()].copy()

prompt = PROMPT_FILE.read_text(encoding="utf-8").strip()

print(f"Failed requests to reproduce: {len(failed)}")

rows = []

for number, (_, row) in enumerate(failed.iterrows(), start=1):

    filename = row["filename"]
    image_path = IMAGES_DIR / filename

    print(f"[{number}/{len(failed)}] {filename}")

    if not image_path.exists():
        rows.append({
            "filename": filename,
            "http_status": None,
            "input_length": None,
            "max_context": None,
            "response_body": "IMAGE NOT FOUND"
        })
        continue

    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "image/jpeg"

    image_base64 = base64.b64encode(
        image_path.read_bytes()
    ).decode("utf-8")

    image_url = f"data:{mime_type};base64,{image_base64}"

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        "temperature": 0,
        "max_tokens": 64
    }

    try:
        start = time.time()

        response = requests.post(
            API_URL,
            json=payload,
            timeout=TIMEOUT
        )

        latency = time.time() - start

        body = response.text

        # Try to extract:
        # Input length (5154) exceeds model's maximum context length (4096)
        match = re.search(
            r"Input length\s*\(?(\d+)\)?.*?"
            r"maximum(?: model)? context length\s*\(?(\d+)\)?",
            body,
            re.IGNORECASE | re.DOTALL
        )

        input_length = int(match.group(1)) if match else None
        max_context = int(match.group(2)) if match else None

        prediction = None

        if response.status_code == 200:
            try:
                prediction = response.json()["choices"][0]["message"]["content"]
            except Exception:
                pass

        rows.append({
            "filename": filename,
            "http_status": response.status_code,
            "input_length": input_length,
            "max_context": max_context,
            "latency_seconds": latency,
            "model_prediction": prediction,
            "response_body": body
        })

        print(
            f"  HTTP={response.status_code}, "
            f"input={input_length}, "
            f"max={max_context}"
        )

    except Exception as e:

        rows.append({
            "filename": filename,
            "http_status": None,
            "input_length": None,
            "max_context": None,
            "latency_seconds": None,
            "model_prediction": None,
            "response_body": repr(e)
        })

        print("  ERROR:", repr(e))

    # Save after every request
    pd.DataFrame(rows).to_csv(
        OUTPUT_FILE,
        index=False
    )

print("\nFinished.")
print(f"Saved: {OUTPUT_FILE}")
