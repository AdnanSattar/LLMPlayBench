# Project Kickoff – LLMPlayBench

We are building **LLMPlayBench** – a self-hosted OpenAI-style inference API with a minimal benchmark dashboard and playground.

## Requirements

1. **Backend**
   - FastAPI service with OpenAI-compatible endpoints (`/v1/responses`, `/v1/models`, `/health`, `/metrics`).
   - Support for multiple Hugging Face small instruction-tuned LLMs (e.g., flan-t5-small, mpt-7b-instruct if hardware allows).
   - Model caching (`cache_dir="./models"`).
   - Warmup request after model load (dummy forward pass).
   - Auto-fallback to CPU if CUDA not available.
   - Metrics: latency, throughput, token count, error rates.

2. **Frontend**
   - React + Tailwind dashboard.
   - Pages:
     - **Playground** → send test prompts to backend, see responses.
     - **Metrics Dashboard** → visualize latency, throughput, memory with charts.
   - Modern look: Tailwind, shadcn/ui, lucide-react icons.

3. **Data & Persistence**
   - Lightweight DB for metrics (SQLite by default, easy swap to Redis/Postgres).
   - Store historical metrics for dashboard charts.

4. **Deployment**
   - Dockerized with separate `backend/`, `frontend/`, `branding/`.
   - Production-ready: logging, healthchecks, scaling hints.
   - `docker-compose.yml` for multi-service orchestration.

5. **Branding**
   - Project name: **LLMPlayBench**.
   - Branding folder with `logo.svg`, `logo.png`, `favicon.svg`, `favicon.png`.
   - Colors: Deep Blue (#1E3A8A), Electric Cyan (#06B6D4), Warm Gray (#F3F4F6).
   - Fonts: Inter (UI), JetBrains Mono (code).

6. **Docs**
   - `README.md` → setup, run, deploy.
   - `PRD.md` → product requirements.
   - `AGENT.md` → rules for Cursor agent.
   - `TODO.md` → implementation checklist.
   - `BRANDING.md` → visual identity.

## Deliverables

- Full project scaffold with `backend/`, `frontend/`, `branding/`, `docs/`.
- Ready-to-run with `docker compose up`.
- Developer-friendly, portfolio showcase quality.

## TODO Checklist

### Backend (FastAPI)

- [x] Setup FastAPI app structure
- [x] Implement `/v1/health` endpoint
- [x] Implement `/v1/models` endpoint
- [x] Implement `/v1/responses` endpoint
- [x] Integrate Hugging Face Transformers for real model inference
- [x] Add warmup request after model load
- [x] Implement multi-model registry and selection
- [x] Add CPU fallback logic
- [x] Add metrics collection (latency, tokens/sec, errors)
- [x] Save metrics to DB (SQLAlchemy + Postgres/SQLite)
- [x] Add `/v1/metrics` endpoint (JSON + Prometheus-ready)
- [x] Structure backend into modular components (api, core, schemas, services)
- [x] Implement benchmarking service with multi-run averaging
- [x] Add author information to all files
- [x] Implement authentication middleware with API keys and JWT
- [x] Set up Alembic migrations for database schema versioning
- [x] Implement admin endpoints for model management
- [x] Add structured JSON logging with Loguru (rotation, retention, compression)
- [x] Add client logs endpoint for frontend logging
- [x] Make benchmarking optional: default off for /v1/response, enable with `?benchmark=true` or env `RESPONSE_BENCH=true`
- [x] Add generation defaults for causal LMs to reduce repetition (repetition_penalty, no_repeat_ngram_size, top_p, top_k)

### Frontend (React + Tailwind)

- [x] Basic playground UI (prompt + response)
- [x] Add model selector dropdown
- [x] Add latency/tokens/sec metrics visualization
- [x] Add request log table (last N requests)
- [x] Connect metrics API for live charts
- [x] Build Playground page with model settings
- [x] Build Dashboard page with metrics visualization
- [x] Implement Layout with header and footer
- [x] Add API client for backend communication
- [x] Polish UI with Tailwind components
- [x] Configure branding colors in Tailwind
- [x] Add fonts (Inter for UI, JetBrains Mono for code)
- [x] Implement frontend logging with loglevel
- [x] Migrate UI shell to MUI ThemeProvider and CssBaseline (enterprise look)
- [x] Refactor Dashboard to MUI Grid/Cards with Skeleton empty states
- [x] Refactor ModelSelector to MUI Select
- [x] Refactor RequestList to MUI Table
- [x] Add toasts: playground errors (500/timeout/model not loaded), backend unhealthy, stale metrics, docs nudges
- [x] Ensure HMR on Windows/Docker with polling env (CHOKIDAR_USEPOLLING, WATCHPACK_POLLING, VITE_FORCE_HMR)

#### UX & Accessibility

- [x] Ensure WCAG AA color contrast across light/dark themes
- [x] Keyboard navigation and focus states for interactive controls
- [x] Reduced motion preference support for animations/transitions
- [x] Compact density toggle for enterprise dashboard feel
- [x] Toast/snackbar error handling for API failures
- [x] Error boundaries for critical UI regions
- [x] Consistent empty and loading states across components

### Database

- [x] Define schema for requests + metrics
- [x] Implement database models with SQLAlchemy
- [x] Create database service for operations
- [x] Add migration support with Alembic

### Deployment / Infra

- [x] Dockerfile for backend
- [x] Dockerfile for frontend
- [x] docker-compose.yml with services (backend, frontend, db, pgadmin)
- [x] Add healthcheck commands in Dockerfiles
- [x] Non-root user in Dockerfiles (best practice)
- [x] Configure logging volume or external log driver
- [x] Set up GitHub Actions CI/CD pipeline
- [x] Configure Docker Hub or GitHub Container Registry
- [x] Configure GitHub repository secrets for CI/CD
- [x] Add Docker Compose profiles (`dev`, `prod`) for frontend-dev and frontend
- [x] Migrate from pip to uv for dependency management
- [x] Replace requirements.txt with pyproject.toml
- [x] Add uv helper script for common commands

### Documentation

- [x] README.md (basic)
- [x] PRD.md
- [x] AGENT.md
- [x] CURSOR_RULES.md
- [x] Backend README with API docs
- [x] Frontend README with component documentation
- [x] CONTRIBUTING.md
- [x] Expand README with setup instructions, screenshots
- [x] Write API.md with request/response examples
- [x] Create PRODUCTION.md with deployment guide
- [x] Document CI/CD workflows and required secrets
- [x] Authentication middleware (API key/JWT) - Implemented with both API keys and JWT tokens
- [x] Alembic migrations for DB schema versioning - Added with migration management script
- [x] Admin endpoints for model management - Added endpoints to reload and unload models
- [x] Production-ready logging with Loguru - Rotation, retention, compression, structured format
- [x] Frontend logging with loglevel - Client-side logging with remote capture
- [x] CI/CD pipeline with GitHub Actions - Automated testing, building, and deployment

## Future Recommendations

- [ ] Prometheus + Grafana integration (Add compose services + export metrics)
- [ ] Tests (pytest for backend, jest for frontend)
- [ ] Production-grade model hosting (model pool, SQS job queue)
- [x] Store and display generated responses in metrics dashboard
- [x] Add previous responses history to Playground with restore functionality
- [x] Add top-p and top-k controls to Playground UI
- [x] Filter out metrics records when benchmark is off (0.000s latency)
- [x] Optimize Redis caching to only cache where really needed

## API Endpoints Status

- [x] /v1/response — main inference (OpenAI Responses-style)
- [x] /v1/models — list available models + quant modes
- [x] /v1/benchmarks — run/return benchmark
- [x] /v1/metrics/recent — return recent persisted metrics for dashboard
- [x] /v1/metrics/summary — aggregated metrics (avg latency per model, tokens/sec)
- [x] /v1/admin/reload_model — admin endpoint to load/unload models (protected)
- [x] /v1/admin/unload_model — admin endpoint to unload models (protected)
- [x] /v1/auth/token — authentication endpoints for JWT tokens
- [x] /v1/auth/me — get current user info
- [x] /v1/auth/status — check authentication status
- [x] /v1/auth/admin — admin-only test endpoint
- [x] /v1/clientlogs — endpoint for frontend logs
- [ ] /metrics — Prometheus scrapeable metrics endpoint
- [x] Include prompt and response fields in metrics API responses

## Best-practices & Production notes

- Model cache persistence: mount models_cache volume to /app/models (compose above). This avoids re-downloads and speeds warm restarts.
- Healthchecks: GET /health verifies service is alive. Compose uses healthcheck for container orchestration.
- Logging: Use Loguru for structured logs (JSON) with rotation, retention, and compression. Configure for container logging.
- Frontend Logging: Use loglevel with remote logging to centralize all logs in backend.
- Scaling: For scale, run multiple backend replicas behind a load balancer; each container can load different models or share models if memory allows. Consider a separate model server pool (1 container per heavy model) and a router service that routes model requests.
- Memory/OOM mitigation: implement per-request model memory check; if GPU OOM on load, fallback to CPU automatically. Also add max_model_load_concurrency.
- Secrets: Keep secrets out of .env in prod (use secrets manager).
- Monitoring: Export metrics to Prometheus (endpoint /metrics) and visualize in Grafana for long-term monitoring. For the dashboard, you can read from Postgres + Redis.
- CI/CD: Build Docker images in CI (GitHub Actions) and push to registry, then deploy via Kubernetes / ECS.
- Security: Add API keys (Auth middleware) before exposing on public networks. Limit rate per user and consider request size limits.

## GitHub Actions CI/CD Required Secrets

The following secrets need to be configured in your GitHub repository for the CI/CD pipeline to work:

- `DOCKERHUB_USERNAME`: Your Docker Hub username for pushing images
- `DOCKERHUB_TOKEN`: Your Docker Hub access token (not your password)
- `SSH_PRIVATE_KEY`: SSH private key for deployment to production server
- `SSH_KNOWN_HOSTS`: SSH known hosts configuration for secure connections
- `SSH_USER`: Username for SSH connection to production server
- `SSH_HOST`: Hostname or IP address of production server

To configure these secrets:

1. Go to your GitHub repository
2. Navigate to "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Add each secret with its corresponding value
