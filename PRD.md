# 📄 PRD: LLMPlayBench – Self-Hosted LLM Inference & Benchmark Dashboard

## 1. Overview

**LLMPlayBench** is a **self-hosted developer tool** that provides:

- A unified API for running **LLM inference locally** (OpenAI-style endpoints).  
- A **minimal metrics dashboard** to track latency, throughput, and errors.  
- A **playground UI** for quick experimentation with prompts.  

The goal is to provide a **job-ready, production-adjacent portfolio project** that demonstrates how to host, benchmark, and interact with LLMs in a developer-friendly way.

---

## 2. Goals

- ✅ Offer **OpenAI-compatible REST API** endpoints for LLM inference.  
- ✅ Provide **basic benchmarking metrics** (latency, throughput, error rate).  
- ✅ Include a **minimal but clear frontend** for prompt testing + monitoring.  
- ✅ Be **self-contained** (Dockerized, minimal dependencies).  
- ✅ Showcase **scalable architecture** with room for future extensions.  

---

## 3. Non-Goals

- ❌ Does not focus on **distributed GPU scaling** (future extension possible).  

---

## 4. Target Audience

- **Developers & ML Engineers** who want to self-host open models.  
- **Students / Learners** who want to understand LLM inference internals.  
- **Hiring managers / recruiters** evaluating technical portfolio projects.  

---

## 5. Functional Requirements

### 5.1 Backend API (FastAPI)

- **Endpoints**
  - `GET /health` → health check.
  - `GET /v1/models` → list available models (`id`, `size`, `status`).
  - `POST /v1/responses` → generate text completions (OpenAI-style schema; streaming planned).
  - Per-request benchmarking is optional (query param `benchmark=true`). Default behavior skips benchmarks for faster latency.
  - `GET /v1/metrics/recent` → recent metrics window (avg latency, tokens/sec, error rate).
  - `GET /v1/metrics/summary` → aggregated metrics across timeframe/by model.
  - `POST /v1/benchmarks` → run benchmark(s) against selected model(s).
- **Features**
  - Hugging Face `transformers` loader with `cache_dir="./models"`.
  - Warm-up dummy forward pass after model load.
  - Auto CPU fallback if CUDA unavailable.
  - Generation defaults for causal LMs to reduce repetition: repetition penalty, no-repeat n-gram, top-p and top-k sampling.
  - Structured request logging (latency, tokens, error flag, request_id).
  - Authentication: API Key and JWT support with scopes (read/write/admin).
  - Temperature and max_tokens respected in generation and benchmarking.
  - Instruction-tuned flow: support optional system prompt in requests.

### 5.2 Metrics & Storage

- SQLAlchemy models with Postgres (prod) or SQLite (dev) persistence.  
- Redis for response and metrics caching.  
- Schema:
  - `request_id`  
  - `model`  
  - `latency_ms`  
  - `tokens_generated`  
  - `error_flag`  
  - `timestamp`  
  - additional aggregates materialized as needed

### 5.3 Model Registry & Runtime

- Model registry entries include: `id`, `revision`, `quantization`, `device`, `cache_dir`.  
- Warmup strategy executed after load to reduce first-token latency.  
- Automatic CPU fallback on CUDA unavailability or OOM.

### 5.4 Frontend (React + Vite + MUI + Tailwind utilities)

- **Playground Page**
  - Text input box + model dropdown.  
  - Button → send request → display response.
  - temperature setting
  - max and min token limits
  - playground as OpenAI Playground keep it as ferenace
- **Dashboard Page**
  - Line chart: latency over time.  
  - Bar chart: tokens/sec distribution.  
  - Stats counters: avg latency, total requests, error rate.  
  - Auto-refresh every 5s.  

### 5.5 Deployment

- **Dockerized architecture**:
  - `backend` (FastAPI + Uvicorn).
  - `frontend-dev` (Vite dev server with HMR; profile `dev`).
  - `frontend` (Nginx serving production build; profile `prod`).
  - `db` (SQLite in dev; Postgres in compose for production-like runs).

- `docker-compose.yml` with profiles for `dev` and `prod` workflows.

---

## 6. Non-Functional Requirements

- **Performance**: <500ms overhead beyond model inference, with Redis caching for repeated requests.  
- **Scalability**: Support multiple models via config.  
- **Reliability**: Graceful error handling if model missing / GPU OOM.  
- **Security**: API Key and JWT supported; scope-based access (read/write/admin).  
- **Portability**: Run on laptop with CPU or server with GPU.  

---

## 7. Success Metrics

- ✅ A developer can **pull the repo, run docker-compose up, and query models within 5 minutes**.  
- ✅ The dashboard updates **in real-time** with metrics.  
- ✅ Playground allows **model switching and prompt testing** without editing code.  

---

## 8. Future Roadmap

- 🔁 Streaming responses (SSE/websocket) for live tokens.
- 🧭 Concurrency controls, request timeouts, backoff/retry policy, circuit breaker.
- 🧳 Background queue for batch inference and benchmarking.
- 📈 Advanced metrics (GPU utilization, memory), Prometheus `/metrics`, Grafana dashboards.
- 🔎 OpenTelemetry tracing and log/trace correlation.
- 🌍 Multi-model benchmarking (side-by-side comparisons).
- 🚀 Cloud deployment templates (AWS/GCP/Azure).
- 🎛️ Admin UI for model lifecycle management.

---

## 9. Tech Stack

- **Backend**: Python, FastAPI, Hugging Face Transformers, SQLAlchemy, Postgres/SQLite.  
- **Frontend**: React, Vite, MUI (Material UI) with Tailwind utilities; charts TBD.  
- **Infra**: Docker, docker-compose with `dev`/`prod` profiles.  
- **Dev Tools**: Cursor IDE, GitHub Actions CI/CD.  

---

## 10. Project Deliverables

- `README.md` → Setup + usage guide.  
- `AGENT.md` → Cursor IDE instructions.  
- `TODO.md` → Development checklist.  
- `PRD.md` → Product requirements (this doc).  
- `docs/ARCHITECTURE.md` → System architecture and request flows.  
- `docs/WIREFRAMES.md` → UI wireframes for Dashboard and Playground.  
- `/branding/` → Logos, favicon, typography/colors.  
- **Backend code** → API + model service.  
- **Frontend code** → Dashboard + Playground.  
- **Docker setup** → `Dockerfile`, `docker-compose.yml`.  

---
