# AgroMind Model Card

## Model Details

| Field | Value |
|---|---|
| Project | AgroMind — Beamdata Use Case |
| Team | Team 2, AIDC Bootcamp |
| Model status | Phase 1 baseline measured; Phase 2 QLoRA results reported on a separate evaluation set |
| Base model | `Qwen/Qwen2.5-VL-7B-Instruct` |
| Model type | Vision-language model (VLM) |
| Primary tasks | Crop identification and plant disease/pest recognition |
| Languages evaluated | Chinese prompt and labels |
| Serving framework | vLLM `0.27.1`, OpenAI-compatible API |
| Deployment | Kubernetes on NVIDIA RTX A6000 |
| License | Base model and dataset licenses require verification before publication |
| Card version | 0.2 — September 2026 |

## Model Summary

AgroMind uses `Qwen/Qwen2.5-VL-7B-Instruct` as its official baseline model. The system receives an agricultural image and a fixed text prompt, then returns the crop name and the visible disease or pest in a structured, comma-separated format.

Phase 1 evaluates the pretrained baseline without project-specific fine-tuning. The team's Phase 2 report describes QLoRA adaptation of the same base model and results on a separate 116-image evaluation split. The two phases have different evaluation sets and scoring methods; their percentages must not be compared as a direct improvement.

## Intended Use

### Primary use

- Identify the crop shown in an agricultural image.
- Predict a visible plant disease or pest.
- Support agricultural image understanding and question answering.
- Provide a research prototype for deployment and benchmarking on Beamdata infrastructure.

### Out-of-scope use

- It must not be treated as a definitive agricultural or laboratory diagnosis.
- It should not be used alone for pesticide selection, chemical dosage, or other safety-critical decisions.
- It is not validated for crops, diseases, regions, languages, or image conditions outside the evaluated dataset.

## Input and Output

### Input

Each request contains:

1. One agricultural image encoded as a Base64 data URL.
2. One fixed text prompt requesting the crop and disease/pest names.

Supported image MIME types are inferred from the file; unknown types default to `image/jpeg`.

### Evaluation prompt

```text
请识别图片中的作物和病虫害，按「作物，病害」格式回答；若为虫害，再补充具体虫种，按「作物，病害，虫种」。只回答名称，不要解释。
```

English meaning: identify the crop and disease or pest. Return `crop, disease`; for a pest case, return `crop, disease, pest`. Return names only without an explanation.

### Expected output

```text
crop,disease
```

or:

```text
crop,disease,pest
```

## Deployment Configuration

| Setting | Value |
|---|---|
| Precision | `float16` |
| Maximum model length | `20,000` tokens |
| GPU memory utilization | `0.85` |
| Temperature | `0` |
| Maximum output tokens | `64` |
| Request timeout | `180` seconds |
| GPU | NVIDIA RTX A6000, 49,140 MiB VRAM |
| API endpoint type | `/v1/chat/completions` |

The context limit was increased from 4,096 to 20,000 tokens after 74 requests exceeded the original limit. After this correction, all 500 evaluation requests completed successfully.

## Evaluation Data

- Evaluation size: 500 agricultural images.
- Raw crop-label count: 77.
- Raw disease/pest-label count: 117.
- The class distribution is highly imbalanced and long-tailed.
- Many crop and disease/pest classes contain only one example.
- Some labels contain whitespace inconsistencies or apparent duplicates.

The evaluation dataset is used for benchmarking. The exact Phase 2 training, validation, and test split must be recorded after QLoRA preparation to prevent data leakage.

## Phase 1 Baseline Results

All quality metrics use the complete 500-image evaluation set as the denominator. Invalid-format outputs are counted as incorrect.

| Metric | Count | Result |
|---|---:|---:|
| Successful API requests | 500/500 | 100.00% |
| Failed API requests | 0/500 | 0.00% |
| Valid-format outputs | 489/500 | 97.80% |
| Invalid-format outputs | 11/500 | 2.20% |
| Correct crop predictions | 234/500 | 46.80% |
| Correct disease/pest predictions | 41/500 | 8.20% |
| Correct combined diagnoses | 13/500 | 2.60% |

### Performance results

| Metric | Result |
|---|---:|
| Mean sequential latency | 1.1545 s |
| P50 sequential latency | 1.1520 s |
| P95 sequential latency | 1.7787 s |
| Peak observed throughput | 48.4451 requests/s at concurrency 16 |
| Peak GPU utilization | 100% |
| Peak VRAM usage | 44,897 MiB (approximately 91.36%) |
| Startup-to-readiness time | 190 s (3 min 10 s) |

The throughput result was measured with a small 20-request sample at each concurrency level and should not be interpreted as a stable production capacity limit without longer repeated load tests.

## Evaluation Method

The scorer normalizes punctuation and whitespace, then splits each output on commas. Only two-field (`crop,disease`) and three-field (`crop,disease,pest`) responses are valid. Crop and disease correctness use strict normalized exact-string matching.

The scorer does not currently apply case folding, synonym mapping, semantic matching, or automatic removal of explanatory labels. Therefore, a semantically reasonable answer may still be scored as incorrect if it does not match the ground-truth label exactly.

## Limitations

- Crop identification is substantially stronger than fine-grained disease and pest recognition.
- Visually similar diseases may be confused.
- Performance may degrade with blurry images, poor lighting, occlusion, unusual viewpoints, or multiple plants in one image.
- The long-tailed and imbalanced dataset increases metric uncertainty.
- Minor label-quality issues may reduce strict exact-match scores.
- The current evaluation uses Chinese prompts and labels; performance in Arabic or English has not yet been established.
- The 20,000-token context supports the current data but reduces theoretical KV-cache concurrency compared with the original 4,096-token configuration.
- Results from this 500-image dataset may not generalize to real farms, other regions, or unseen crop diseases.

## Safety and Responsible Use

Model predictions must be presented as decision support, not confirmed diagnoses. Low-confidence, unclear, or high-impact cases should be reviewed by a qualified agricultural specialist. Users should not apply pesticides or take costly interventions based only on the model output.

Images and labels must be collected and processed according to applicable privacy, ownership, and licensing requirements. Evaluation should be expanded across crop types, disease classes, image conditions, and relevant user groups before production use.

## Phase 2 — QLoRA Fine-Tuning Record

The following values are transcribed from the team's `phase2_report (1).md`; underlying run logs and artifacts have not yet been checked against the report. Phase 2 uses 116 held-out images, whereas the Phase 1 baseline above uses 500 images. The Phase 2 report also uses regex-based JSON extraction instead of the Phase 1 comma-separated strict scorer.

| Item | Reported value |
|---|---|
| Fine-tuned model | QLoRA adapter on `Qwen/Qwen2.5-VL-7B-Instruct` |
| Training / validation / evaluation | 300 / 86 / 116 images (reported totals sum to 502; split provenance to verify) |
| Epochs | 3 |
| Learning rate | `2e-4` (student variation) |
| Batch size / gradient accumulation | 1 / 8 (effective batch size 8) |
| LoRA rank / alpha / dropout | 16 / 32 / 0.05 |
| Target modules | `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` |
| Quantization for training | 4-bit QLoRA; deployed inference quantization not established |
| Training GPU / duration | NVIDIA GeForce RTX 5070 Ti / approximately 30 minutes |
| Adapter path in report | `./agro_qlora_output_variation`; verify actual artifact and team naming |
| Random seed, dataset version, dependency versions | Not stated in report |

### Reported results on the Phase 2 evaluation set (N = 116)

| Metric | Base model | QLoRA baseline | Student variation |
|---|---:|---:|---:|
| Crop accuracy | 81.03% | 92.24% | 93.10% |
| Disease/pest accuracy | 2.59% | 50.86% | 56.03% |
| Combined diagnosis accuracy | 1.72% | 48.28% | 54.31% |
| Valid-output rate | 100.00% | 100.00% | 100.00% |
| Inference failure rate | 0.00% | 0.00% | 0.00% |

On this reported 116-image evaluation, the student variation exceeded the QLoRA baseline by 6.03 percentage points in combined diagnosis accuracy. This comparison applies only within the Phase 2 evaluation. Phase 2 latency, throughput, concurrency, VRAM and inference cost are not reported.

### Provenance checks before final submission

- The project belongs to **Team 2**. The Phase 2 report's `team3-qlora-variation-lr2e4` identifier is inconsistent with the team name; verify the adapter's actual identifier before publishing or renaming an artifact.
- The report's three split counts total 502 images. Confirm dataset size, split membership, and the statement about specimen/field grouping against split files.
- Confirm the 116-image predictions and scoring script, plus the inference configuration used for all three Phase 2 models.

## Reproducibility

- Repository: <https://github.com/FayAlaamri/Team2-H100-Agromind.git>
- Phase 1 branch: `phase-1`
- Verified Phase 1 commit: `a9efb2db50a204515a60ce96e18344c1eeb230bc`
- Deployment manifests: `phase-1/k8s/`
- Evaluation scripts and results: `phase-1/evaluation/`
- Evaluation prompt: `phase-1/prompts/diagnosis_prompt.txt`
- Reports and evidence: `phase-1/reports/`

For final submission, update the repository commit, dataset version or hash, verified adapter/checkpoint and dependency versions. Record English and Arabic performance as not evaluated (the prompt and labels tested here were Chinese); confirm license, container image, recommended production GPU, measured concurrency and inference cost.

## Citation and Contact

Developed by Team 2 for the AIDC Bootcamp AgroMind — Beamdata Use Case. Project owner: Shan Gao.

For questions, contact the Team 2 project members through the bootcamp communication channel.
