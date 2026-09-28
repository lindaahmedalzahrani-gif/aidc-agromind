import os
import pandas as pd

PART1_LABELS = "data/raw/part1/labels.csv"
PART2_LABELS = "data/raw/part2/labels.csv"
IMAGES_DIR = "evaluation/images"
OUTPUT_LABELS = "evaluation/labels.csv"


def main():
    print("Loading dataset labels...")

    part1 = pd.read_csv(PART1_LABELS)
    part2 = pd.read_csv(PART2_LABELS)

    print(f"Part 1 rows: {len(part1)}")
    print(f"Part 2 rows: {len(part2)}")

    combined = pd.concat([part1, part2], ignore_index=True)

    print(f"Combined rows: {len(combined)}")

    duplicate_count = combined["filename"].duplicated().sum()
    missing_crop = combined["crop"].isna().sum()
    missing_disease = combined["disease"].isna().sum()

    print(f"Duplicate filenames: {duplicate_count}")
    print(f"Missing crop labels: {missing_crop}")
    print(f"Missing disease labels: {missing_disease}")

    missing_images = []

    for filename in combined["filename"]:
        image_path = os.path.join(IMAGES_DIR, filename)

        if not os.path.exists(image_path):
            missing_images.append(filename)

    print(f"Missing referenced images: {len(missing_images)}")

    if missing_images:
        print("Example missing images:")
        for filename in missing_images[:10]:
            print(" -", filename)

    combined.to_csv(
        OUTPUT_LABELS,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nSaved merged labels to: {OUTPUT_LABELS}")

    if (
        len(combined) == 500
        and duplicate_count == 0
        and len(missing_images) == 0
    ):
        print("✅ Dataset validation passed.")
    else:
        print("⚠️ Dataset validation found issues. Check the results above.")


if __name__ == "__main__":
    main()
