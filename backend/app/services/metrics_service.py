"""
Metrics collection and retrieval service.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import time
import uuid
from typing import Any, Dict, List, Optional

from ..core.config import settings
from ..core.logging import app_logger
from ..schemas.db_models import RequestMetric
from .db_service import get_session
from .model_cache_service import cache_model_metrics, get_cached_metrics


def save_request_metric(
    model: str,
    prompt: str,
    latency_s: float,
    tokens: int,
    tokens_per_sec: float,
    quant: str = "int8",
    response: str = None,
    temperature: float = None,
    top_p: float = None,
    top_k: int = None,
    system_prompt: str = None,
    benchmarked: bool = True,
):
    """
    Save request metrics to database.

    Args:
        model: Model name
        prompt: Input prompt
        latency_s: Inference latency in seconds
        tokens: Number of tokens generated
        tokens_per_sec: Tokens per second throughput
        quant: Quantization level
        response: Generated response text
        temperature: Temperature parameter for generation
        top_p: Top-p (nucleus sampling) parameter
        top_k: Top-k sampling parameter
        system_prompt: System prompt for instruction-tuned models
    """
    # Generate unique request ID
    request_id = f"req-{uuid.uuid4()}"

    app_logger.debug(
        "Saving request metric",
        request_id=request_id,
        model=model,
        latency_s=latency_s,
        tokens=tokens,
        tokens_per_sec=tokens_per_sec,
    )

    # Create metric entry
    db = get_session()
    try:
        metric = RequestMetric(
            request_id=request_id,
            timestamp=int(time.time()),
            model=model,
            prompt=prompt,
            prompt_length=len(prompt),
            response=response,
            latency_s=latency_s,
            tokens=tokens,
            tokens_per_sec=tokens_per_sec,
            quantization=quant,
            benchmarked=benchmarked,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            system_prompt=system_prompt,
        )
        db.add(metric)
        db.commit()
        app_logger.debug("Request metric saved successfully", request_id=request_id)
    except Exception as e:
        app_logger.error(
            "Failed to save request metric", request_id=request_id, error=str(e)
        )
        db.rollback()
        raise
    finally:
        db.close()


def get_recent_metrics(
    model: Optional[str] = None,
    limit: int = 100,
    from_timestamp: Optional[int] = None,
    to_timestamp: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Get recent metrics from database.

    Args:
        model: Filter by model name (optional)
        limit: Maximum number of entries to return
        from_timestamp: Filter by start timestamp (optional)
        to_timestamp: Filter by end timestamp (optional)

    Returns:
        List of metric entries
    """
    app_logger.debug(
        "Fetching recent metrics",
        model=model,
        limit=limit,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp,
    )

    db = get_session()
    try:
        # Start with base query
        query = (
            db.query(RequestMetric)
            .filter(RequestMetric.benchmarked == True)
            .order_by(RequestMetric.timestamp.desc())
        )

        # Apply filters
        if model:
            query = query.filter(RequestMetric.model == model)

        if from_timestamp:
            query = query.filter(RequestMetric.timestamp >= from_timestamp)

        if to_timestamp:
            query = query.filter(RequestMetric.timestamp <= to_timestamp)

        # Apply limit
        metrics = query.limit(limit).all()

        app_logger.debug("Retrieved metrics from database", count=len(metrics))

        # Convert to dictionaries
        return [metric.to_dict() for metric in metrics]
    except Exception as e:
        app_logger.error("Failed to fetch recent metrics", error=str(e))
        raise
    finally:
        db.close()


def get_metrics_summary(model: Optional[str] = None) -> Dict[str, Any]:
    """
    Get metrics summary (averages).
    Uses Redis cache if available to avoid repeated database queries.

    Args:
        model: Filter by model name (optional)

    Returns:
        Dictionary with summary metrics
    """
    app_logger.debug("Fetching metrics summary", model=model)

    # Try to get from cache first if Redis caching is enabled
    if getattr(settings, "USE_REDIS_CACHE", True):
        cache_key = "summary" if not model else f"summary:{model}"
        cached_metrics = get_cached_metrics(model or "all", "summary")
        if cached_metrics:
            app_logger.info("Using cached metrics summary", model=model, cache_hit=True)
            return cached_metrics

    db = get_session()
    try:
        # Start with base query
        query = db.query(RequestMetric).filter(RequestMetric.benchmarked == True)

        # Apply model filter if provided
        if model:
            query = query.filter(RequestMetric.model == model)

        # Get all matching entries
        metrics = query.all()
        app_logger.debug("Retrieved metrics for summary", count=len(metrics))

        # Calculate averages if we have metrics
        if metrics:
            avg_latency = max(0.0, sum(m.latency_s for m in metrics) / len(metrics))
            avg_tokens = max(0.0, sum(m.tokens for m in metrics) / len(metrics))
            avg_tps = max(0.0, sum(m.tokens_per_sec for m in metrics) / len(metrics))

            # Group by model
            models = {}
            for m in metrics:
                if m.model not in models:
                    models[m.model] = []
                models[m.model].append(m)

            # Calculate per-model averages
            model_stats = {}
            for model_name, model_metrics in models.items():
                model_stats[model_name] = {
                    "avg_latency": max(
                        0.0,
                        sum(m.latency_s for m in model_metrics) / len(model_metrics),
                    ),
                    "avg_tokens": max(
                        0.0, sum(m.tokens for m in model_metrics) / len(model_metrics)
                    ),
                    "avg_tps": max(
                        0.0,
                        sum(m.tokens_per_sec for m in model_metrics)
                        / len(model_metrics),
                    ),
                    "count": len(model_metrics),
                }

            result = {
                "total_requests": len(metrics),
                "overall_avg_latency": avg_latency,
                "overall_avg_tokens": avg_tokens,
                "overall_avg_tps": avg_tps,
                "models": model_stats,
            }
            app_logger.debug(
                "Metrics summary calculated",
                total_requests=len(metrics),
                models_count=len(model_stats),
            )

            # Cache the results if Redis caching is enabled
            if getattr(settings, "USE_REDIS_CACHE", True):
                cache_model_metrics(
                    model or "all",
                    "summary",
                    result,
                    cache_ttl=getattr(
                        settings, "METRICS_CACHE_TTL", 300
                    ),  # 5 minutes default
                )

            return result
        else:
            app_logger.debug("No metrics found for summary")
            result = {
                "total_requests": 0,
                "overall_avg_latency": 0,
                "overall_avg_tokens": 0,
                "overall_avg_tps": 0,
                "models": {},
            }

            # Cache empty results too (but with shorter TTL)
            if getattr(settings, "USE_REDIS_CACHE", True):
                cache_model_metrics(
                    model or "all",
                    "summary",
                    result,
                    cache_ttl=60,  # 1 minute for empty results
                )

            return result
    except Exception as e:
        app_logger.error("Failed to fetch metrics summary", error=str(e))
        raise
    finally:
        db.close()
