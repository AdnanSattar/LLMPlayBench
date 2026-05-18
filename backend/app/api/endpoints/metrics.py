"""
Metrics API endpoint.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from ...core.security.auth import User, get_read_user
from ...schemas.api_schemas import MetricsRequest, MetricsResponse
from ...services.metrics_service import get_metrics_summary, get_recent_metrics

router = APIRouter()


@router.get("/metrics/recent", response_model=MetricsResponse)
def recent_metrics(
    model: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_read_user),
):
    """Get recent metrics entries."""
    metrics = get_recent_metrics(model=model, limit=limit)
    return {"metrics": metrics}


@router.post("/metrics/recent", response_model=MetricsResponse)
def filtered_metrics(
    request: MetricsRequest, current_user: User = Depends(get_read_user)
):
    """Get filtered metrics based on request parameters."""
    metrics = get_recent_metrics(
        model=request.model,
        limit=request.limit,
        from_timestamp=request.from_timestamp,
        to_timestamp=request.to_timestamp,
    )
    return {"metrics": metrics}


@router.get("/metrics/summary")
def metrics_summary(
    model: Optional[str] = None, current_user: User = Depends(get_read_user)
):
    """Get summary metrics (avg latency, tokens/sec, etc.)."""
    return get_metrics_summary(model=model)
