# AI DATA CENTER Bootcamp — AgroMind Phase 1 Benchmark Report

## 1. Executive Summary

- Model: Qwen/Qwen2.5-VL-7B-Instruct
- Deployment: vLLM on Kubernetes
- GPU: NVIDIA RTX A6000, 49,140 MiB VRAM
- Evaluation dataset: 500 agricultural images
- Successful inference coverage: 426/500 (85.20%)
- Crop accuracy: 45.31%
- Disease/pest accuracy: 7.75%
- Combined diagnosis accuracy: 2.58%
- Main deployment limitation: 74 requests exceeded the configured 4096-token maximum context length.

The Phase 1 benchmark successfully deployed the open-weight Qwen2.5-VL-7B-Instruct model through vLLM and Kubernetes and evaluated it against the provided AgroMind dataset.

The model was considerably stronger at identifying the crop than identifying the exact disease or pest. The model also frequently produced broad disease categories instead of the exact ground-truth disease label.

A separate infrastructure limitation was observed for 74 images whose image-derived input length exceeded the configured maximum context length of 4096 tokens.


## 2. Model and Deployment

- Model: Qwen/Qwen2.5-VL-7B-Instruct
- Serving framework: vLLM
- Kubernetes namespace: agromind-h100
- Deployment: agromind-vllm
- Service: agromind-serving
- API endpoint: /v1/chat/completions
- NodePort: 30802
- GPU: NVIDIA RTX A6000
- Total VRAM: 49,140 MiB
- Observed loaded-model VRAM: approximately 41,223 MiB
- Maximum model length: 4096
- Temperature: 0
- Maximum output tokens: 64

### Prompt

The same supplied AgroMind Chinese prompt was used for every evaluation image.

English meaning:

"Identify the crop and disease/pest shown in the image. Answer in the format 'crop, disease'. If it is a pest, also include the pest species. Return names only and do not provide an explanation."


## 3. Dataset and Evaluation Method

The provided AgroMind benchmark consisted of two dataset archives.

- Part 1: 250 images
- Part 2: 250 images
- Total: 500 images

Dataset validation found:

- Duplicate filenames: 0
- Missing crop labels: 0
- Missing disease labels: 0
- Missing referenced images: 0

The benchmark compared each model response against the supplied crop and disease ground-truth labels using normalized exact matching.

All requests used the same model, prompt, decoding settings, and evaluation procedure.


## 4. Model Quality Results

| Metric | Result |
|---|---:|
| Total images attempted | 500 |
| Successful inference responses | 426 |
| Inference success rate | 85.20% |
| Valid-output rate | 97.89% |
| Crop accuracy | 45.31% |
| Disease/pest accuracy | 7.75% |
| Combined diagnosis accuracy | 2.58% |

Accuracy metrics were calculated over successful inference responses.

### Observed Error Pattern

The model often identified the correct crop while predicting an incorrect disease.

Example:

- Ground truth: Citrus, Anthracnose
- Prediction: Citrus, Leaf Spot

The model also frequently produced broad disease categories such as "Leaf Spot" or the generic label "Disease" instead of the more specific ground-truth diagnosis.

### Representative Successful Predictions

The following examples show cases where both the crop and disease labels matched the ground truth.

| Image | Ground Truth | Model Prediction | Result |
|---|---|---|---|
| b24cb2c9_crop01.jpg | Grape — Powdery Mildew | Grape — Powdery Mildew | Correct |
| 屏幕截图 2026-05-31 144132.png | Rice — Rice Blast | Rice — Rice Blast | Correct |
| 微信图片_2026-06-03_101820_301.jpg | Peanut — Leaf Spot | Peanut — Leaf Spot | Correct |
| 微信图片_2026-06-02_172516_625.jpg | Corn — Leaf Spot | Corn — Leaf Spot | Correct |
| 微信图片_2026-06-02_163726_372.jpg | Tomato — Leaf Mold | Tomato — Leaf Mold | Correct |
| 微信图片_2026-06-02_173443_907.jpg | Chinese Cabbage — Downy Mildew | Chinese Cabbage — Downy Mildew | Correct |

### Representative Failure Cases

A common failure mode was identifying the crop correctly while confusing the exact disease.

| Image | Ground Truth | Model Prediction | Observation |
|---|---|---|---|
| b24cb2c9_crop02.jpg | Citrus — Anthracnose | Citrus — Leaf Spot | Correct crop, incorrect disease |
| b24cb2c9_crop03.jpg | Citrus — Scab | Citrus — Canker | Correct crop, incorrect disease |
| b24cb2c9_crop08.jpg | Corn — Rust | Corn — Leaf Spot | Correct crop, incorrect disease |
| 30f62513_crop03.jpg | Tomato — Early Blight | Tomato — Leaf Spot | Correct crop, incorrect disease |
| 屏幕截图 2026-05-31 141448.png | Apple — Anthracnose | Apple — Rot Disease | Correct crop, incorrect disease |
| 屏幕截图 2026-05-31 141619.png | Pear — Anthracnose | Citrus — Canker | Both crop and disease incorrect |
| 屏幕截图 2026-05-31 142601.png | Cucumber — Powdery Mildew | Cucurbit — Downy Mildew | Broad crop category and incorrect disease |
| 屏幕截图 2026-05-31 144528.png | Pepper — Anthracnose | Soybean — Leaf Spot | Both crop and disease incorrect |

### Output-Format Failures

Most successful requests followed the required compact `crop, disease` response format. However, 9 of the 426 successful inference responses did not follow the expected format.

Examples included responses such as:

- `作物：大豆 / 病害：大豆根腐病 / 虫害：大豆蚜虫`
  - English: `Crop: Soybean / Disease: Soybean Root Rot / Pest: Soybean Aphid`
- `无`
  - English: `None`

These responses contain potentially useful information but do not comply with the required output structure and were therefore counted as invalid-format responses.

## 5. Infrastructure Benchmark

### Startup

Observed pod-to-ready startup time:

- 210 seconds
- approximately 3 minutes 30 seconds

This measurement includes container startup, model initialization, vLLM engine startup, and Kubernetes readiness.

### Sequential Evaluation Latency

| Metric | Result |
|---|---:|
| Mean latency | 0.886 s |
| p50 latency | 0.913 s |
| p95 latency | 1.389 s |

### Load Test

100 successful requests were executed at each concurrency level.

| Concurrency | Success | Throughput | Mean latency | p50 | p95 |
|---:|---:|---:|---:|---:|---:|
| 1 | 100/100 | 1.47 req/s | 0.678 s | 0.706 s | 1.317 s |
| 2 | 100/100 | 10.27 req/s | 0.192 s | 0.183 s | 0.236 s |
| 4 | 100/100 | 19.24 req/s | 0.204 s | 0.192 s | 0.266 s |
| 8 | 100/100 | 34.60 req/s | 0.222 s | 0.209 s | 0.289 s |
| 16 | 100/100 | 53.42 req/s | 0.271 s | 0.259 s | 0.365 s |

### GPU Measurements

- GPU: NVIDIA RTX A6000
- Total VRAM: 49,140 MiB
- Observed VRAM usage with model loaded: 41,223 MiB
- Peak observed GPU utilization under load: 100%
- Peak observed power draw: 283.84 W

### GPU Measurements

- GPU: NVIDIA RTX A6000
- Total VRAM: 49,140 MiB
- Observed VRAM usage with model loaded: 41,223 MiB
- Peak observed GPU utilization under load: 100%
- Peak observed power draw: 283.84 W

### Estimated Inference Energy and Cost

During the concurrency-16 benchmark, the maximum observed GPU power draw was 283.84 W and measured throughput was 53.42 requests per second.

Using these measurements:

- Approximate time for 1,000 requests: 18.72 seconds
- Estimated GPU energy per 1,000 requests: approximately 0.001476 kWh
- Estimated GPU energy per 1,000,000 requests: approximately 1.476 kWh

Using an assumed electricity tariff of **0.18 SAR/kWh**:

- Estimated GPU electricity cost per hour: **0.0511 SAR**
- Estimated GPU electricity cost per 1,000 requests: **0.000266 SAR**
- Estimated GPU electricity cost per 1,000,000 requests: **0.2657 SAR**

The 0.18 SAR/kWh electricity tariff is an assumption used for this estimate and should be replaced if the deployment environment has a different applicable tariff.

This estimate represents GPU electricity only. It does not include CPU, system memory, storage, networking, cooling, server capital cost/depreciation, maintenance, or idle infrastructure consumption.

## 6. Key Limitation


## 6. Key Limitation

74 of 500 evaluation requests returned HTTP 400 before inference.

A representative server response was:

Input length 5154 exceeded the configured maximum model context length of 4096.

Therefore:

- 426 images successfully reached inference.
- 74 images were not assigned model-quality scores.
- The failure is treated as a deployment/input-processing limitation rather than an incorrect disease prediction.

Potential future work may investigate image preprocessing, image-resolution controls, or a larger context configuration.


## 7. Conclusion

The Phase 1 deployment was reproducible and successfully served Qwen2.5-VL-7B-Instruct through vLLM and Kubernetes on an NVIDIA RTX A6000.

The deployment demonstrated strong infrastructure throughput under concurrent requests, but the untuned model showed limited fine-grained agricultural disease-recognition performance. Crop recognition was substantially stronger than exact disease identification.

The benchmark also identified a concrete infrastructure limitation: 14.8% of the supplied images exceeded the configured 4096-token maximum context length and were rejected before inference.

These findings provide a baseline for the next AgroMind phase and establish measurable areas for future model and serving improvements.
