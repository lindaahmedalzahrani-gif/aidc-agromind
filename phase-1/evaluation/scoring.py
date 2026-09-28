
import json
import re
from pathlib import Path

import pandas as pd


RESULTS_FILE = Path("evaluation/results.csv")
SCORED_FILE = Path("evaluation/scored_results.csv")
SUMMARY_FILE = Path("evaluation/metrics_summary.json")


def normalize_text(value):
    if pd.isna(value):
        return ""

    value = str(value).strip()

    # Normalize common Chinese/English punctuation
    value = value.replace("，", ",")
    value = value.replace("、", ",")
    value = value.replace("：", ":")
    value = value.replace("\n", " ")

    # Remove repeated spaces
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def parse_prediction(prediction):
    """
    Expected format:
        crop,disease

    or for pest cases:
        crop,disease,pest
    """

    prediction = normalize_text(prediction)

    if not prediction:
        return "", "", "", False

    parts = [
        part.strip()
        for part in prediction.split(",")
        if part.strip()
    ]

    if len(parts) == 2:
        return parts[0], parts[1], "", True

    if len(parts) == 3:
        return parts[0], parts[1], parts[2], True

    return "", "", "", False


def main():
    df = pd.read_csv(RESULTS_FILE)

    print("========================================")
    print("AgroMind Phase 1 Scoring")
    print("========================================")

    print(f"Total benchmark records: {len(df)}")

    # Successful inference = HTTP 200 + prediction exists
    successful_mask = (
        (df["http_status"] == 200)
        & df["model_prediction"].notna()
    )

    successful_df = df[successful_mask].copy()
    failed_df = df[~successful_mask].copy()

    print(f"Successful inferences: {len(successful_df)}")
    print(f"Failed inferences: {len(failed_df)}")

    inference_success_rate = (
        len(successful_df) / len(df)
        if len(df) > 0
        else 0
    )

    scored_rows = []

    for _, row in successful_df.iterrows():

        pred_crop, pred_disease, pred_pest, valid_format = (
            parse_prediction(row["model_prediction"])
        )

        true_crop = normalize_text(row["true_crop"])
        true_disease = normalize_text(row["true_disease"])

        crop_correct = (
            pred_crop == true_crop
            if valid_format
            else False
        )

        disease_correct = (
            pred_disease == true_disease
            if valid_format
            else False
        )

        combined_correct = (
            crop_correct and disease_correct
        )

        scored_rows.append({
            **row.to_dict(),

            "predicted_crop": pred_crop,
            "predicted_disease": pred_disease,
            "predicted_pest": pred_pest,

            "valid_format": valid_format,
            "crop_correct": crop_correct,
            "disease_correct": disease_correct,
            "combined_correct": combined_correct,
        })

    scored_df = pd.DataFrame(scored_rows)

    # ----------------------------
    # Quality metrics
    # ----------------------------

    valid_output_rate = (
        scored_df["valid_format"].mean()
        if len(scored_df) > 0
        else 0
    )

    crop_accuracy = (
        scored_df["crop_correct"].mean()
        if len(scored_df) > 0
        else 0
    )

    disease_accuracy = (
        scored_df["disease_correct"].mean()
        if len(scored_df) > 0
        else 0
    )

    combined_accuracy = (
        scored_df["combined_correct"].mean()
        if len(scored_df) > 0
        else 0
    )

    # ----------------------------
    # Latency metrics
    # ----------------------------

    latency = pd.to_numeric(
        scored_df["latency_seconds"],
        errors="coerce"
    ).dropna()

    p50_latency = latency.quantile(0.50)
    p95_latency = latency.quantile(0.95)
    mean_latency = latency.mean()

    # ----------------------------
    # Print results
    # ----------------------------

    print("\n===== COVERAGE =====")
    print(
        f"Inference success rate: "
        f"{inference_success_rate:.2%}"
    )

    print("\n===== MODEL QUALITY =====")
    print(
        f"Valid-output rate:      "
        f"{valid_output_rate:.2%}"
    )
    print(
        f"Crop accuracy:          "
        f"{crop_accuracy:.2%}"
    )
    print(
        f"Disease accuracy:       "
        f"{disease_accuracy:.2%}"
    )
    print(
        f"Combined accuracy:      "
        f"{combined_accuracy:.2%}"
    )

    print("\n===== LATENCY =====")
    print(
        f"Mean latency: "
        f"{mean_latency:.3f} s"
    )
    print(
        f"p50 latency:  "
        f"{p50_latency:.3f} s"
    )
    print(
        f"p95 latency:  "
        f"{p95_latency:.3f} s"
    )

    # ----------------------------
    # Save scored results
    # ----------------------------

    scored_df.to_csv(
        SCORED_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    summary = {
        "total_images": int(len(df)),
        "successful_inferences": int(len(successful_df)),
        "failed_inferences": int(len(failed_df)),

        "inference_success_rate": float(
            inference_success_rate
        ),

        "valid_output_rate": float(
            valid_output_rate
        ),

        "crop_accuracy": float(
            crop_accuracy
        ),

        "disease_accuracy": float(
            disease_accuracy
        ),

        "combined_accuracy": float(
            combined_accuracy
        ),

        "mean_latency_seconds": float(
            mean_latency
        ),

        "p50_latency_seconds": float(
            p50_latency
        ),

        "p95_latency_seconds": float(
            p95_latency
        ),

        "known_phase1_limitation": (
            "74 requests exceeded the configured "
            "4096-token maximum context length."
        ),
    }

    with open(
        SUMMARY_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            summary,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("\nSaved:")
    print(f"  {SCORED_FILE}")
    print(f"  {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
