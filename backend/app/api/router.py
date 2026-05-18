"""
API router configuration.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

from fastapi import APIRouter

from .endpoints import admin, auth, benchmarks, clientlogs, metrics, models, responses

# Create the main router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(responses.router, tags=["responses"])
api_router.include_router(models.router, tags=["models"])
api_router.include_router(benchmarks.router, tags=["benchmarks"])
api_router.include_router(metrics.router, tags=["metrics"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(admin.router, tags=["admin"])
api_router.include_router(clientlogs.router, tags=["clientlogs"])
