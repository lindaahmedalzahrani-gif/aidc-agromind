import base64
import mimetypes
import time
from pathlib import Path

import pandas as pd
import requests


API_URL = "http://localhost:30802/v1/chat/completions"
MODEL = "Qwen/Qwen2.5-VL-7B-Instruct"

LABELS_FILE = Path("evaluation/labels.csv")
IMAGES_DIR = Path("evaluation/images")
PROMPT_FILE = Path("prompts/diagnosis_prompt.txt")


def image_to_data_url(image_path):
    mime_type, _ = mimetypes.guess_type(image_path)

    if mime_type is None:
        mime_type = "image/jpeg"

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


def main():
    # Load labels
    df = pd.read_csv(LABELS_FILE)

    # Start with only the first benchmark image
    row = df.iloc[0]

    filename = row["filename"]
    true_crop = row["crop"]
    true_disease = row["disease"]

    image_path = IMAGES_DIR / filename

    # Load the fixed AgroMind prompt
    prompt = PROMPT_FILE.read_text(encoding="utf-8").strip()

    print("Testing image:", filename)
    print("Expected crop:", true_crop)
    print("Expected disease:", true_disease)

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
        "temperature": 0,
        "max_tokens": 64
    }

    start = time.perf_counter()

    response = requests.post(
        API_URL,
        json=payload,
        timeout=180
    )

    latency = time.perf_counter() - start

    print("\nHTTP status:", response.status_code)

    response.raise_for_status()

    result = response.json()

    prediction = result["choices"][0]["message"]["content"]

    print("\nModel prediction:")
    print(prediction)

    print("\nLatency:")
    print(f"{latency:.3f} seconds")


if __name__ == "__main__":
    main()
