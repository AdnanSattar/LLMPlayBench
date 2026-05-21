# LLMPlayBench

Self-hosted **OpenAI-style LLM inference API** with a **playground** and **benchmark dashboard**. Run small instruction-tuned models locally, measure latency and throughput, and experiment in the browser—Dockerized and portfolio-ready.

See [PRD.md](PRD.md) for product requirements.

---

## Features

- **Inference API** — `POST /v1/response` with model selection, temperature, `max_tokens`, and optional `system_prompt`
- **Playground** — Prompt testing with model dropdown and generation parameters (OpenAI Playground–style layout)
- **Metrics dashboard** — Latency over time, tokens/sec, summary stats, recent requests; auto-refresh every 5s
- **Multi-model registry** — T5 and causal LMs via Hugging Face Transformers (`cache_dir=./models`)
- **Benchmarking** — Per-request opt-in (`?benchmark=true`) or dedicated `GET /v1/benchmarks`; metrics only recorded when benchmarking runs
- **Caching** — Redis for responses and metrics (configurable TTL)
- **Auth** — API keys (`X-API-Key`) and JWT with read / write / admin scopes
- **Persistence** — PostgreSQL (default in Compose) or SQLite; Alembic migrations
- **Docker profiles** — `dev` (Vite HMR) and `prod` (Nginx static build)
- **CI/CD** — GitHub Actions for lint, test, build, security, and docs

---

## Supported models

| Model | Type | Params | Best for |
|-------|------|--------|----------|
| `google/flan-t5-small` | Encoder–decoder (T5) | 60M | Translation, Q&A, summarization |
| `HuggingFaceTB/SmolLM2-135M-Instruct` | Causal LM | 135M | Code, instructions |
| `facebook/MobileLLM-R1-140M` | Causal LM | 140M | Mobile / edge chat |
| `google/gemma-3-270m` | Causal LM | 270M | General reasoning |

All models support chat templates (causal LMs), temperature control, system prompts, and automatic CPU fallback when CUDA is unavailable.

**Details:** [docs/MODELS.md](docs/MODELS.md)

**Benchmarking:** Metrics appear on the dashboard only when benchmarking ran (`?benchmark=true` on `/v1/response`, or `RESPONSE_BENCH=true`). Otherwise requests are faster and are not stored as metrics.

**Generation defaults (causal LMs):** `repetition_penalty`, `no_repeat_ngram_size`, `top_p`, and `top_k` reduce repetition.

---

## Tech stack

| Layer | Stack |
|-------|--------|
| Backend | Python, FastAPI, Hugging Face Transformers, SQLAlchemy, Loguru |
| Data | PostgreSQL / SQLite, Redis (optional cache) |
| Frontend | React, Vite, MUI, Tailwind utilities, Recharts |
| Infra | Docker, docker-compose (`dev` / `prod` profiles) |
| CI | GitHub Actions |

---

## Quick start

### 1. Clone

```bash
git clone https://github.com/AdnanSattar/llmplaybench.git
cd llmplaybench
```

### 2. Run with Docker

Backend, Postgres, Redis, pgAdmin, and Redis Commander start by default. **Pick a frontend profile** for the UI:

```bash
# Development — Vite dev server with HMR
docker compose --profile dev up --build

# Production-like — Nginx serving the built frontend
docker compose --profile prod up --build
```

API-only (no UI):

```bash
docker compose up --build
```

### 3. Open services

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Dashboard / Playground | http://localhost:3000 |
| pgAdmin | http://localhost:8080 (`admin@admin.com` / `admin`) |
| Redis Commander | http://localhost:8081 (`admin` / `admin`) |

### 4. Authentication

Use **`X-API-Key`** (preferred) or a **Bearer JWT** from `POST /v1/auth/token`.

| Method | Dev examples | Production |
|--------|----------------|------------|
| API key | `read-dev-key`, `admin-dev-key` | Set `READ_API_KEY` / `ADMIN_API_KEY` in `backend/.env` |
| JWT | `admin` / `password` at `/v1/auth/token` | Change credentials and `SECRET_KEY` |

Change all defaults before deploying. See [docs/PRODUCTION.md](docs/PRODUCTION.md).

### 5. Example request

```bash
curl -X POST "http://localhost:8000/v1/response?benchmark=true" \
  -H "X-API-Key: read-dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "HuggingFaceTB/SmolLM2-135M-Instruct",
    "prompt": "Write a Python function to calculate fibonacci numbers",
    "system_prompt": "You are a helpful coding assistant.",
    "max_tokens": 200,
    "temperature": 0.3
  }'
```

More examples: [docs/MODELS.md](docs/MODELS.md).

---

## API endpoints

Base path: `/v1` (except health).

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | — | Health check |
| `GET` | `/v1/models` | — | List available models |
| `POST` | `/v1/response` | read | Generate text (`?benchmark=true` optional) |
| `GET` | `/v1/benchmarks` | — | Run benchmark for a model (`?model=...`) |
| `GET` | `/v1/metrics/recent` | read | Recent metrics window |
| `POST` | `/v1/metrics/recent` | read | Filtered metrics |
| `GET` | `/v1/metrics/summary` | read | Aggregated metrics |
| `POST` | `/v1/auth/token` | — | JWT access token |
| `GET` | `/v1/auth/me` | read | Current user |
| `POST` | `/v1/admin/reload_model` | admin | Reload model |
| `DELETE` | `/v1/admin/unload_model` | admin | Unload model |
| `POST` | `/v1/admin/clear_caches` | admin | Clear caches |
| `POST` | `/v1/clientlogs` | read | Frontend log ingestion |

Interactive reference: http://localhost:8000/docs

---

## Architecture

```text
                        +-------------------------------+
                        |           Browser              |
                        |   React + Vite + MUI UI        |
                        +-------------------------------+
                                      |
                                      | HTTP (JSON)
                                      v
          +-------------------+   dev: Vite (HMR)   +-------------------+
          |  frontend-dev     | <-----------------> |  Developer Laptop |
          |  (profile=dev)    |                     +-------------------+
          +-------------------+
                 | prod build (static)
                 v
          +-------------------+         HTTP (static assets)
          |   frontend (Nginx)| <---------------------------------+
          |   (profile=prod)  |                                   |
          +-------------------+                                   |
                 |                                               |
                 | HTTP (API)                                    |
                 v                                               |
          +-------------------------------------------------------------+
          |                      FastAPI Backend                         |
          |  /health  /v1/models  /v1/response  /v1/metrics/*  /v1/benchmarks|
          |  Auth: X-API-Key + JWT (scopes) | Loguru | SQLAlchemy         |
          +-------------------------------------------------------------+
                 |                    |                      |
           SQL (metrics)          Redis (cache)        ./models (HF cache)
                 |                    |                      |
                 v                    v                      v
          +-----------+        +------------+        +----------------+
          | Postgres  |        |  Redis     |        |  model weights |
          | or SQLite |        |            |        |                |
          +-----------+        +------------+        +----------------+
```

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Mermaid system and sequence diagrams
- [docs/WIREFRAMES.md](docs/WIREFRAMES.md) — Dashboard, Playground, Settings layouts

---

## Project structure

```text
llmplaybench/
├── backend/                 # FastAPI app
│   ├── app/
│   │   ├── api/endpoints/   # Routes (response, models, metrics, …)
│   │   ├── core/            # Config, auth, logging, middleware
│   │   ├── schemas/         # Pydantic + DB models
│   │   └── services/        # Model, metrics, benchmark, cache
│   ├── migrations/          # Alembic
│   └── manage_db.py
├── frontend/                # React + Vite dashboard & playground
│   └── src/
│       ├── pages/           # Dashboard, Playground
│       └── components/
├── branding/                # Logo, favicon, colors
├── docs/
│   ├── ARCHITECTURE.md
│   ├── MODELS.md
│   ├── PRODUCTION.md
│   └── WIREFRAMES.md
├── .github/workflows/       # CI/CD
├── docker-compose.yml
├── PRD.md
├── AGENT.md
└── TODO.md
```

---

## Environment configuration

### Backend (`backend/.env`)

```bash
PROJECT_NAME=LLMPlayBench
SECRET_KEY=your_production_secret_key
ADMIN_API_KEY=your_admin_key
READ_API_KEY=your_read_key
DATABASE_URL=postgresql://llm_user:llm_pass@postgres:5432/llm_metrics
CACHE_DIR=./models
DEFAULT_MODEL=google/flan-t5-small
LOG_LEVEL=INFO

# Benchmarking & generation
RESPONSE_BENCH=false
REPETITION_PENALTY=1.2
NO_REPEAT_NGRAM_SIZE=3
TOP_P=0.9
TOP_K=50

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
USE_REDIS_CACHE=true
REDIS_CACHE_TTL=3600
```

### Frontend (`frontend/.env` or Compose env)

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=read-dev-key
VITE_LOG_LEVEL=info
```

---

## Local development (without Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database migrations

```bash
cd backend
python manage_db.py upgrade
python manage_db.py create "Description"
```

### Test models

```bash
cd backend
python test_new_models.py
```

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [PRD.md](PRD.md) | Product requirements |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and request flows |
| [docs/MODELS.md](docs/MODELS.md) | Model guide and curl examples |
| [docs/PRODUCTION.md](docs/PRODUCTION.md) | Production deployment |
| [docs/WIREFRAMES.md](docs/WIREFRAMES.md) | UI wireframes |
| [AGENT.md](AGENT.md) | Cursor / agent workflow |
| [TODO.md](TODO.md) | Implementation checklist |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guide |

---

## CI/CD

GitHub Actions workflows under `.github/workflows/`:

- `ci-cd.yml` — Lint, test, build, deploy
- `pr-check.yml` — Pull request validation
- `security.yml` — Dependency and image scanning
- `dependencies.yml` — Automated dependency updates
- `docs.yml` — Documentation publish

Configure repository secrets (`DOCKERHUB_*`, `SSH_*`, etc.) before enabling deployment jobs.

---

## Roadmap

- Streaming responses (SSE / WebSocket)
- Concurrency limits, timeouts, circuit breaker
- Background queue for batch inference
- Prometheus `/metrics` and Grafana
- OpenTelemetry tracing
- Multi-model side-by-side benchmarks
- Cloud deployment templates (AWS / GCP / Azure)
- Admin UI for model lifecycle

---

## Author

**Adnan Sattar**

- Email: adnansattar09@gmail.com
- GitHub: [AdnanSattar](https://github.com/AdnanSattar)
- LinkedIn: [adnansattar09](https://www.linkedin.com/in/adnansattar09/)

---

## License

MIT License © 2025 Adnan Sattar
