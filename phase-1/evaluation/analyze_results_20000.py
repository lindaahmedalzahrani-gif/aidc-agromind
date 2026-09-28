import pandas as pd

df = pd.read_csv("evaluation/scored_results_qwen25_20000.csv")

print("========================================")
print("AgroMind Result Analysis")
print("========================================")

print("\nTotal scored:", len(df))

print("\n===== COUNTS =====")
print("Valid format:", df["valid_format"].sum())
print("Crop correct:", df["crop_correct"].sum())
print("Disease correct:", df["disease_correct"].sum())
print("Combined correct:", df["combined_correct"].sum())


print("\n===== 10 FULLY CORRECT EXAMPLES =====")

correct = df[df["combined_correct"] == True]

print(
    correct[
        [
            "filename",
            "true_crop",
            "true_disease",
            "model_prediction"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


print("\n===== 10 CROP CORRECT / DISEASE WRONG =====")

crop_only = df[
    (df["crop_correct"] == True)
    & (df["disease_correct"] == False)
]

print(
    crop_only[
        [
            "filename",
            "true_crop",
            "true_disease",
            "predicted_crop",
            "predicted_disease"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


print("\n===== 10 WRONG CROP EXAMPLES =====")

wrong_crop = df[df["crop_correct"] == False]

print(
    wrong_crop[
        [
            "filename",
            "true_crop",
            "true_disease",
            "predicted_crop",
            "predicted_disease"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


print("\n===== INVALID FORMAT EXAMPLES =====")

invalid = df[df["valid_format"] == False]

print(
    invalid[
        [
            "filename",
            "true_crop",
            "true_disease",
            "model_prediction"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


print("\n===== MOST COMMON TRUE DISEASES =====")

print(
    df["true_disease"]
    .value_counts()
    .head(15)
    .to_string()
)


print("\n===== MOST COMMON MODEL DISEASE PREDICTIONS =====")

print(
    df["predicted_disease"]
    .value_counts()
    .head(15)
    .to_string()
)
