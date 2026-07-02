"""
Main FastAPI application.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .api.router import api_router
from .core.config import settings
from .core.logging import app_logger
from .core.middleware.middleware import RequestLoggingMiddleware
from .services.db_service import init_db
from .services.model_service import load_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    This is the new way to handle lifecycle events in FastAPI.
    """
    # Startup
    app_logger.info("Starting LLMPlayBench API")

    try:
        # Initialize database
        init_db()
        app_logger.info("Database initialized successfully")
        # Preload default model if configured
        default_model = getattr(settings, "DEFAULT_MODEL", None)
        default_quant = getattr(settings, "DEFAULT_QUANT", "int8")
        if default_model:
            try:
                app_logger.info(
                    "Preloading default model {} ({})", default_model, default_quant
                )
                load_model(default_model, default_quant)
                app_logger.info("Default model preloaded")
            except Exception as e:
                app_logger.exception("Failed to preload default model: {}", str(e))
    except Exception as e:
        app_logger.exception("Database initialization failed: {}", str(e))
        sys.exit(1)

    app_logger.info("LLMPlayBench API started successfully")

    yield  # Application is running here

    # Shutdown
    app_logger.info("Shutting down LLMPlayBench API")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="Self-Hosted LLM Inference API + Benchmark Dashboard",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "health", "description": "Service health checks"},
        {"name": "models", "description": "Model listing and management"},
        {"name": "responses", "description": "Text generation API (OpenAI-style)"},
        {"name": "metrics", "description": "Metrics retrieval and summaries"},
        {"name": "benchmarks", "description": "Benchmark runs"},
        {"name": "auth", "description": "Authentication endpoints"},
        {"name": "admin", "description": "Admin-only operations"},
    ],
)

# Add CORS middleware
origins = settings.BACKEND_CORS_ORIGINS
if isinstance(origins, str):
    origins = [o.strip() for o in origins.split(",") if o.strip()]

# Self-hosted deployments often use Tailscale/public IPs, not just localhost.
# Starlette returns 400 on OPTIONS when Origin is not allowed (see browser preflight).
_SELF_HOSTED_ORIGIN_RE = (
    r"^https?://" r"(localhost|127\.0\.0\.1|\d{1,3}(?:\.\d{1,3}){3})" r"(:\d+)?$"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=_SELF_HOSTED_ORIGIN_RE,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


# Exception handler for uncaught exceptions
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    app_logger.exception(f"Unhandled exception: {str(exc)}")
    return {"detail": "Internal server error"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
