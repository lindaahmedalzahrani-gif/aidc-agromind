# 🌱 AgroMind

AgroMind is an AI-powered plant diagnosis system that analyzes plant images to identify crops, diseases, and pests, then provides helpful agricultural guidance through a Retrieval-Augmented Generation (RAG) system.

The project was developed as part of the **AI Data Center Operations Bootcamp**.

## System Overview

AgroMind combines vision-language AI, model serving, RAG, Kubernetes, and monitoring into one deployed system.

### How It Works

1. The user uploads a plant image through the web interface.
2. The request is sent to the AgroMind API.
3. **Qwen2.5-VL-7B-Instruct**, served using **vLLM**, analyzes the image.
4. A **QLoRA adapter** improves the model for plant diagnosis.
5. For follow-up questions, the system uses **RAG** with a verified agricultural knowledge base.
6. The services run on **Kubernetes** and are monitored using **Prometheus and Grafana**.

## Architecture

```text
User
  │
  ▼
Web UI
  │
  ▼
AgroMind API
  │
  ├──► vLLM + Qwen2.5-VL + QLoRA
  │       └── Plant Image Diagnosis
  │
  └──► RAG Service
          └── Agricultural Knowledge Base

Kubernetes → Deployment & Service Management
Prometheus → Metrics Collection
Grafana    → Monitoring & Visualization
```

## Model

**Base Model:** Qwen/Qwen2.5-VL-7B-Instruct

The model was adapted using **QLoRA** for plant image diagnosis.

Final evaluation:

- Crop identification accuracy: **93.10%**
- Disease/Pest identification accuracy: **56.03%**
- Combined crop + disease/pest accuracy: **54.31%**

## Serving & Performance

The model is served using **vLLM** on an NVIDIA RTX A6000 GPU.

Phase 1 load testing achieved:

- **500/500 successful requests**
- **97.8% valid model outputs**
- Mean latency: **1.15 seconds**
- P95 latency: **1.78 seconds**
- Peak throughput: **48.45 requests/second**

The model uses a **20,000-token context length** to support large vision-language requests.

## RAG

AgroMind includes a Retrieval-Augmented Generation system for agricultural follow-up questions.

The knowledge base contains crop, disease, pest, and treatment information that was generated and then verified using reliable agricultural sources before being added to the system.

## Infrastructure

The final system includes:

- **Kubernetes** for deployment and service management
- **vLLM** for GPU model serving
- **FastAPI** for the application API
- **RAG** for agricultural knowledge retrieval
- **Prometheus** for metrics collection
- **Grafana** for dashboards and monitoring
- **Docker** for containerization

## Repository Structure

```text
phase-1/
├── evaluation/       # Model benchmarking and evaluation
├── k8s/              # Initial Kubernetes deployment
├── prompts/          # Diagnosis prompts
└── reports/          # Benchmark reports and evidence

phase-2/
├── adapters/         # QLoRA adapter configuration
├── agromind-system/
│   ├── api/          # AgroMind API
│   ├── k8s/          # Kubernetes manifests
│   ├── monitoring/   # Monitoring configuration
│   ├── rag/          # RAG service and knowledge base
│   └── ui/           # Web interface
├── configs/          # Training configuration
├── evidence/         # Deployment and training evidence
└── reports/          # Model documentation
```

> Large datasets, model weights, generated vector databases, and sensitive environment files are excluded from this repository.

## Team

**Team 2 – AgroMind**

- Linda Alzahrani
- Wasan
- Fai
- Najd

## Technologies

Python · Qwen2.5-VL · QLoRA · vLLM · FastAPI · RAG · ChromaDB · Docker · Kubernetes · Prometheus · Grafana · React
