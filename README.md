# LLMPlayBench

✨ Self-Hosted LLM Inference API + Benchmark Dashboard with Playground

LLMPlayBench is a **self-hosted, OpenAI-style inference API** with a **minimal playground and benchmark dashboard**.  
Run small instruction-tuned LLMs locally, measure performance metrics, and experiment interactively—all in one lightweight, production-ready stack.

---

## 🚀 Features

- **OpenAI-Compatible Responses API** – Serve local models with `/v1/responses`
- **Playground UI** – Interactively test prompts in a clean, React dashboard
- **Benchmarking & Metrics** – Track latency, token throughput, and average response time
- **Multi-Model Support** – Load and switch between multiple LLMs
- **Warmup & Caching** – Faster inference, reduced startup lag, Redis response caching
- **Self-Hosted & Lightweight** – Runs on your own infra with Docker
- **Authentication** – API key and JWT token support for securing endpoints
- **Database Migrations** – Alembic migrations for schema versioning
- **Production-Ready Logging** – Structured logs with rotation and retention
- **UI Components** – Error boundaries, consistent loading/empty states, accessibility features
- **CI/CD Pipeline** – GitHub Actions workflows for testing, building, and deployment

## 🤖 Supported Models

LLMPlayBench supports multiple small language models optimized for local inference:

### T5-Based Models (Encoder-Decoder)

- **google/flan-t5-small** - Google's instruction-tuned T5 model (60M parameters)
- **google/flan-t5-base** - Larger T5 model (220M parameters)

### Causal Language Models (Decoder-Only)

- **HuggingFaceTB/SmolLM2-135M-Instruct** - Hugging Face's small instruction-tuned model (135M parameters)
- **facebook/MobileLLM-R1-140M** - Meta's mobile-optimized model (140M parameters)
- **google/gemma-3-270m** - Google's Gemma model optimized for efficiency (270M parameters)

All models support:

- **Chat Templates** - Proper conversation formatting for instruction-tuned models
- **Temperature Control** - Adjustable randomness in generation
- **System Prompts** - Context-aware responses
- **CPU Fallback** - Automatic fallback when GPU unavailable

Performance notes

- **Benchmarking behavior**: Metrics are only recorded when benchmarking is enabled. By default it's disabled for faster requests. Enable per-request with `?benchmark=true` or globally with env `RESPONSE_BENCH=true`. When off, responses are not saved to metrics and won't appear on the Dashboard.
- **Redis Caching** is enabled by default for model responses and metrics. This significantly reduces response time for identical requests and database load for metrics queries. Configure with `USE_REDIS_CACHE=true|false` and `REDIS_CACHE_TTL=3600` (seconds).
- For **causal LMs** we apply sensible defaults to reduce repetition (`repetition_penalty`, `no_repeat_ngram_size`, `top_p`, `top_k`).

---

## 📊 Tech Stack

- **Backend:** FastAPI, Hugging Face Transformers, SQLite/Postgres (metrics), Redis (caching), Loguru (logging)
- **Frontend:** React, Tailwind, Recharts (dashboard & playground), loglevel (logging)
- **Containerization:** Docker + Docker Compose
- **Authentication:** JWT tokens and API keys
- **Database:** SQLAlchemy ORM with Alembic migrations
- **Monitoring:** Dashboard with charts (latency, tokens/sec, error rate)
- **CI/CD:** GitHub Actions for automated testing, building, and deployment

---

## 📦 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/AdnanSattar/llmplaybench.git
cd llmplaybench
```

### 2. Run with Docker

```bash
docker compose up --build
```

### 3. Access the Services

- API → [http://localhost:8000](http://localhost:8000)
- Dashboard → [http://localhost:3000](http://localhost:3000)
- API Documentation → [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Authentication

Default API keys are provided in the `.env` files:

- Admin API key: `admin-dev-key`
- Read-only API key: `read-dev-key`

For JWT tokens, use the `/v1/auth/token` endpoint with:

- Username: `admin`
- Password: `password`

⚠️ **Security Note:** Change these values in production!

### 5. Model Usage Examples

#### Using T5 Models (Encoder-Decoder)

```bash
curl -X POST "http://localhost:8000/v1/response" \
  -H "Authorization: Bearer read-dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/flan-t5-small",
    "prompt": "Translate to French: Hello, how are you?",
    "max_tokens": 50,
    "temperature": 0.7
  }'
```

#### Using Causal LM Models (Chat Format)

```bash
curl -X POST "http://localhost:8000/v1/response" \
  -H "Authorization: Bearer read-dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "HuggingFaceTB/SmolLM2-135M-Instruct",
    "prompt": "Write a Python function to calculate fibonacci numbers",
    "system_prompt": "You are a helpful coding assistant. Provide clean, well-documented code.",
    "max_tokens": 200,
    "temperature": 0.3
  }'
```

#### Mobile-Optimized Model

```bash
curl -X POST "http://localhost:8000/v1/response" \
  -H "Authorization: Bearer read-dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "facebook/MobileLLM-R1-140M",
    "prompt": "Explain quantum computing in simple terms",
    "max_tokens": 150
  }'
```

---

## 🛠️ Project Structure

```shell
llmplaybench/
├── backend/              # FastAPI backend
│   ├── app/              # Application code
│   │   ├── api/          # API routes and endpoints
│   │   ├── core/         # Core configuration and security
│   │   │   ├── logging.py  # Loguru configuration
│   │   │   └── middleware.py # Request middleware
│   │   ├── models/       # Model definitions
│   │   ├── schemas/      # API and DB schemas
│   │   └── services/     # Business logic services
│   ├── migrations/       # Database migrations
│   ├── .env              # Environment configuration
│   └── requirements.txt  # Python dependencies
├── frontend/             # React frontend
│   ├── src/              # Source code
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities and API client
│   │   │   └── logger.js # Frontend logging
│   │   ├── pages/        # Main page components
│   │   └── styles/       # CSS styles
│   ├── .env              # Environment configuration
│   └── package.json      # JavaScript dependencies
├── branding/             # Logo and branding assets
├── docs/                 # Documentation
│   ├── API.md            # API documentation
│   └── PRODUCTION.md     # Production deployment guide
├── .github/              # GitHub Actions workflows
│   ├── workflows/        # CI/CD pipeline definitions
│   └── ISSUE_TEMPLATE/   # Issue and PR templates
├── docker-compose.yml    # Multi-service orchestration
└── README.md             # This file
```

---

## 🧭 Architecture (ASCII Overview)

```shell
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
          |  - /health  - /v1/models  - /v1/responses                   |
          |  - /v1/metrics/recent  - /v1/metrics/summary  - /v1/benchmarks|
          |  Auth: API Key + JWT (scopes) | Loguru | SQLAlchemy         |
          +-------------------------------------------------------------+
                 |                    |                      |
                 |                    |                      |
           SQL (metrics)          Cache (opt)          Model files
                 |                    |                      |
                 v                    v                      v
          +-----------+        +------------+        +----------------+
          | Postgres  |        |  Redis     |        | ./models cache |
          | or SQLite |        | (optional) |        | (HF downloads) |
          +-----------+        +------------+        +----------------+
```

See detailed diagrams in:

- docs/ARCHITECTURE.md — Mermaid system and sequence diagrams
- docs/WIREFRAMES.md — Dashboard, Playground, Settings wireframes

---

## 🧰 Development Tools

- **PgAdmin** - Database management UI at <http://localhost:8080> (<admin@admin.com> / admin)
- **Redis Commander** - Redis management UI at <http://localhost:8081> (admin / admin)
- **Swagger UI** - API docs at <http://localhost:8000/docs>
- **ReDoc** - Alternative API docs at <http://localhost:8000/redoc>

## 📈 API Endpoints

- `GET /health` - Health check endpoint
- `POST /v1/response` - Generate text from model
- `GET /v1/models` - List available models
- `GET /v1/benchmarks` - Run benchmark on model
- `GET /v1/metrics/recent` - Get recent metrics (auth required)
- `POST /v1/metrics/recent` - Filter metrics by criteria (auth required)
- `GET /v1/metrics/summary` - Get aggregated metrics (auth required)
- `POST /v1/auth/token` - Get JWT access token
- `POST /v1/admin/reload_model` - Admin endpoint to reload model (admin auth required)
- `DELETE /v1/admin/unload_model` - Admin endpoint to unload model (admin auth required)
- `POST /v1/clientlogs` - Endpoint for frontend logs (auth required)

For detailed API documentation, see [docs/API.md](docs/API.md).

---

## 🔒 Environment Configuration

### Backend (.env)

```shell
PROJECT_NAME=LLMPlayBench
SECRET_KEY=your_production_secret_key
ADMIN_API_KEY=admin_api_key
READ_API_KEY=read_api_key
DATABASE_URL=postgresql://user:pass@postgres:5432/llm_metrics
CACHE_DIR=./models
DEFAULT_MODEL=google/flan-t5-small
LOG_LEVEL=INFO

# Performance settings
RESPONSE_BENCH=false
REPETITION_PENALTY=1.2
NO_REPEAT_NGRAM_SIZE=3
TOP_P=0.9
TOP_K=50

# Redis caching
REDIS_HOST=redis
REDIS_PORT=6379
USE_REDIS_CACHE=true
REDIS_CACHE_TTL=3600
```

### Frontend (.env)

```shell
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=read_api_key
VITE_LOG_LEVEL=info
VITE_REMOTE_LOGGING_ENABLED=true
```

---

## 🧪 Development

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

### Database Migrations

```bash
cd backend
python manage_db.py upgrade   # Apply migrations
python manage_db.py create "Description"  # Create new migration
```

### Testing New Models

```bash
cd backend
python test_new_models.py    # Test all supported models
```

---

## 🚀 CI/CD Pipeline

LLMPlayBench uses GitHub Actions for continuous integration and deployment. The following workflows are included:

- **Main CI/CD Pipeline** (`ci-cd.yml`): Lints code, runs tests, builds Docker images, and deploys to production
- **Pull Request Checks** (`pr-check.yml`): Validates pull requests before merging
- **Security Checks** (`security.yml`): Scans dependencies and Docker images for vulnerabilities
- **Dependency Updates** (`dependencies.yml`): Automatically updates dependencies and creates PRs
- **Documentation** (`docs.yml`): Builds and publishes documentation to GitHub Pages

### Required Secrets

The following secrets must be configured in your GitHub repository for the CI/CD pipeline:

- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Your Docker Hub access token
- `SSH_PRIVATE_KEY`: SSH private key for deployment
- `SSH_KNOWN_HOSTS`: Known hosts configuration for SSH
- `SSH_USER`: Username for SSH connection
- `SSH_HOST`: Host for SSH connection

To configure these secrets:

1. Go to your repository settings
2. Navigate to "Secrets and variables" > "Actions"
3. Add each required secret

---

## 📝 Documentation

- [API Documentation](docs/API.md) - Detailed API reference
- [Models Guide](docs/MODELS.md) - Complete guide to supported models
- [Production Deployment Guide](docs/PRODUCTION.md) - Guide for production deployment
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project

---

## 🚀 Roadmap

- [ ] Prometheus + Grafana integration
- [x] CI/CD pipeline with GitHub Actions
- [ ] Test suite for backend and frontend
- [ ] Production-grade model hosting with model pooling
- [ ] ONNX Runtime integration for faster inference

---

## 👨‍💻 Author

Adnan Sattar

- Email: <adnansattar09@gmail.com>
- GitHub: [AdnanSattar](https://github.com/AdnanSattar)
- LinkedIn: [adnansattar09](https://www.linkedin.com/in/adnansattar09/)

---

## 📄 License

MIT License © 2025 Adnan Sattar
