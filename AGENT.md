# AGENT.md – Rules for Cursor Agent in LLMPlayBench

## AGENT INSTRUCTIONS

You are an assistant working on this repository. Follow these rules:

1. **Respect OpenAI API format** → All endpoints must mirror the `/v1/responses` format.
2. **Keep small-model focus** → Target <1B parameter models (e.g., flan-t5-small).
3. **Always add warmup inference** after model load.
4. **Cache models in ./models** to avoid re-downloads.
5. **Auto CPU fallback** if CUDA unavailable or OOM.
6. **Logging**: Use Loguru for structured logs with rotation, retention, compression.
7. **Metrics**: Store in DB + expose via `/v1/metrics/*` endpoints.
8. **Frontend**: React + Vite + MUI (Material UI) as primary, with Tailwind utilities where helpful.
9. **Security**: Do not expose admin endpoints publicly without auth.
10. **Documentation**: Update README and API docs with any endpoint changes.
11. **CI/CD**: Use GitHub Actions for automated testing and deployment.

This document defines how the AI agent should generate and modify files for this repository.  
Follow these rules strictly to maintain project quality and consistency.  

---

## 1. Project Identity

- **Name:** LLMPlayBench  
- **Tagline:** Self-Hosted LLM Inference API + Benchmark Dashboard with Playground  
- This is both a **developer tool** and a **portfolio-quality showcase**.  
- Branding is important: maintain consistent name, colors, and folder structure.  

---

## 2. Repository Structure

Always keep the following structure:

llmplaybench/
├── backend/ # FastAPI backend
│ ├── app/
│ │ ├── main.py
│ │ ├── api/ # API routes & endpoints
│ │ │ ├── endpoints/ # Individual endpoint implementations
│ │ │ └── router.py # Main API router
│ │ ├── core/ # Core functionality
│ │ │ ├── config.py # Application configuration
│ │ │ ├── logging.py # Logging configuration
│ │ │ └── middleware.py # Application middleware
│ │ ├── models/ # Model definitions
│ │ ├── schemas/ # Data schemas
│ │ │ ├── api_schemas.py # API request/response models
│ │ │ └── db_models.py # Database models
│ │ └── services/ # Business logic
│ │   ├── benchmark_service.py # Model benchmarking
│ │   ├── db_service.py # Database operations
│ │   ├── metrics_service.py # Metrics collection
│ │   └── model_service.py # Model management
│ ├── migrations/ # Alembic migrations
│ │ ├── versions/ # Migration scripts
│ │ └── env.py # Migration environment
│ ├── alembic.ini # Alembic configuration
│ ├── logs/ # Application logs directory
│ └── tests/
├── frontend/ # React + Tailwind + MUI dashboard
│ ├── src/
│ │ ├── pages/ # Playground, Dashboard
│ │ ├── components/ # UI components
│ │ └── lib/ # utils, API client, logger
│ └── public/ # favicon, logo
├── branding/ # Logos, favicons, identity docs
│ ├── logo.svg
│ ├── logo.png
│ ├── favicon.svg
│ ├── favicon.png
│ └── branding.md
├── docs/ # Documentation
│ ├── API.md # API documentation
│ ├── PRODUCTION.md # Production deployment guide
│ └── AGENT.md
├── .github/ # GitHub Actions workflows
│ ├── workflows/ # CI/CD pipeline definitions
│ │ ├── ci-cd.yml # Main CI/CD workflow
│ │ ├── pr-check.yml # Pull request checks
│ │ ├── security.yml # Security scanning
│ │ ├── dependencies.yml # Dependency updates
│ │ └── docs.yml # Documentation publishing
│ ├── ISSUE_TEMPLATE/ # Issue and PR templates
│ └── CODEOWNERS # Code ownership configuration
├── docker-compose.yml  # includes dev/prod profiles for frontend services
├── README.md
├── CONTRIBUTING.md
├── TODO.md

---

## 3. Backend Rules

- Use **FastAPI** with structured routers (`api/` folder).  
- Implement **OpenAI-style endpoints**:
  - `/v1/responses`
  - `/v1/models`
  - `/v1/benchmarks`
  - `/v1/metrics/recent`
  - `/v1/metrics/summary`
  - `/v1/auth/token`
  - `/v1/auth/me`
  - `/v1/auth/status`
  - `/v1/auth/admin`
  - `/v1/admin/reload_model`
  - `/v1/admin/unload_model`
  - `/v1/clientlogs`
  - `/health`
- Hugging Face integration:
  - Use `transformers` library with `cache_dir="./models"`.
  - Perform a **warmup dummy forward pass** after model load.
  - Implement **auto-fallback to CPU** if CUDA not available.
  - Keep `/v1/response` fast by skipping benchmarks by default. Support opt-in via `?benchmark=true` or env `RESPONSE_BENCH=true`.
  - Apply generation defaults for causal LMs (`repetition_penalty`, `no_repeat_ngram_size`, `top_p`, `top_k`) to reduce repetition.
- Metrics:
  - Log latency, tokens/sec, and errors.
  - Store in SQLite by default or Postgres in production.
- Logging:
  - Use Loguru for structured logging
  - Configure file rotation, retention, and compression
  - Log with context (request_id, user, etc.)
  - Support JSON format for machine parsing
- Always separate concerns:
  - `api/endpoints/` for API routes
  - `core/` for application configuration
  - `schemas/` for data models
  - `services/` for business logic
  - `models/` for model definitions

---

## 4. Frontend Rules

- **React + Vite + MUI (Material UI)** with Tailwind utilities.  
- Pages:
  - **Playground:** text input, send requests to `/v1/responses`, show output.  
  - **Dashboard:** charts for metrics (latency, throughput, error rate).  
- Components should be modular, reusable, and clean.  
- Use MUI components (Grid, Card, Table, Select, Skeleton) and theme.  
- Include favicon + logo in `public/`.  
- Frontend logging:
  - Use loglevel for client-side logging
  - Support remote logging to backend
  - Capture unhandled errors and rejections

---

## 5. Docker & Deployment

- Each service (`backend`, `frontend`) has its own Dockerfile.  
- Use `docker-compose.yml` to orchestrate services.  
- Expose:
  - Backend API on `8000`
  - Frontend on `3000`
- Add healthcheck to backend service.  
- Use multi-stage Docker builds for smaller images.  
- Configure proper logging:
  - JSON format logs
  - Volume mounts for logs
  - Log rotation and retention

---

## 6. Documentation

Always keep docs updated.

Required now:

- `README.md` – setup, run, deploy.  
- `PRD.md` – product requirements (repo root).  
- `TODO.md` – development checklist.  
- `backend/README.md` – backend API, auth, env, migrations.  

Optional (recommended):

- `docs/API.md` – API reference with examples.  
- `docs/PRODUCTION.md` – production deployment guide.  
- `branding/branding.md` – colors, typography, logo usage.  

---

## 7. CI/CD and Testing

- Use GitHub Actions for CI/CD pipelines:
  - Build and test backend
  - Build and test frontend
  - Build and push Docker images
  - Run linting and type checking
  - Deploy to staging/production environments
- Write tests for critical components:
  - Backend API endpoints
  - Services and utilities
  - Frontend components
  - Integration tests
- Required GitHub Secrets:
  - `DOCKERHUB_USERNAME`: Docker Hub username
  - `DOCKERHUB_TOKEN`: Docker Hub access token
  - `SSH_PRIVATE_KEY`: SSH private key for deployment
  - `SSH_KNOWN_HOSTS`: Known hosts configuration for SSH
  - `SSH_USER`: Username for SSH connection
  - `SSH_HOST`: Host for SSH connection

---

## 8. Coding Standards

- Write **clean, production-grade code** (docstrings, typing).  
- Use **Black** (Python) and **Prettier** (JS/TS) formatting.  
- Always add comments to complex sections.  
- Prefer clarity over cleverness.  
- Include author information in all files:

  ```
  Author: Adnan Sattar
  Email: <adnansattar09@gmail.com>
  GitHub: <https://github.com/AdnanSattar>
  LinkedIn: <https://www.linkedin.com/in/adnansattar09/>
  ```

---

## 9. Rules for Cursor Agent

- Always place files in the correct directory.  
- Do not overwrite existing files unless explicitly asked.  
- When editing code, **preserve comments and docstrings**.
- If unclear, **ask for clarification before generating**.  
- Always update AGENT.md and TODO.md after significant changes.
- When generating code, follow repo structure.
- Prefer FastAPI for backend API.
- Use Hugging Face Transformers for model inference.
- Use SQLAlchemy for DB access (SQLite/Postgres).
- Use React + Vite + MUI (with Tailwind utilities) for frontend.
- Add type hints in Python.
- Ensure Dockerfiles are production-ready (non-root user, healthcheck).
- Do not commit secrets. Use `.env` for config.
- When asked to "improve performance," focus on caching, batching, efficient device usage.
- When asked to "improve UI," prefer MUI components/theme; use Tailwind utilities sparingly.

---

✅ Following this `AGENT.md` ensures consistency, clarity, and production-quality code.
