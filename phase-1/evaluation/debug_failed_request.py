import base64
import mimetypes
from pathlib import Path

import pandas as pd
import requests


API_URL = "http://localhost:30802/v1/chat/completions"
MODEL = "Qwen/Qwen2.5-VL-7B-Instruct"

RESULTS_FILE = Path("evaluation/results.csv")
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
    df = pd.read_csv(RESULTS_FILE)

    failed = df[df["error"].fillna("").ne("")]

    print("Failed requests:", len(failed))

    if len(failed) == 0:
        print("No failed requests.")
        return

    row = failed.iloc[0]

    filename = row["filename"]
    image_path = IMAGES_DIR / filename

    print("\nTesting failed image:")
    print(filename)
    print("Image path:", image_path)
    print("Exists:", image_path.exists())

    prompt = PROMPT_FILE.read_text(
        encoding="utf-8"
    ).strip()

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

    response = requests.post(
        API_URL,
        json=payload,
        timeout=180
    )

    print("\nHTTP status:")
    print(response.status_code)

    print("\nServer response:")
    print(response.text)


if __name__ == "__main__":
    main()
