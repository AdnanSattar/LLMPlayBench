"""
Model cache service for LLMPlayBench

This service integrates Redis caching with the model service to cache model responses
and reduce duplicate inference requests.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import hashlib
import json
import logging
from typing import Any, Dict, Optional, Tuple

from app.services.cache_service import get_cache, is_cache_available, set_cache

logger = logging.getLogger(__name__)

# Cache key prefixes
MODEL_RESPONSE_PREFIX = "model_response:"
MODEL_METRICS_PREFIX = "model_metrics:"


def _create_response_cache_key(
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: Optional[float],
    system_prompt: Optional[str],
    top_p: Optional[float],
    top_k: Optional[int],
    quantization: str = "int8",
) -> str:
    """
    Create a unique cache key for a model response based on input parameters

    Args:
        model: Model name/ID
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        system_prompt: Optional system prompt
        top_p: Optional nucleus sampling parameter
        top_k: Optional top-k sampling parameter
        quantization: Model quantization level

    Returns:
        A unique cache key string
    """
    # Create a dictionary of parameters that affect the response
    params = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system_prompt": system_prompt,
        "top_p": top_p,
        "top_k": top_k,
        "quantization": quantization,
    }

    # Convert to a stable string representation and hash it
    params_str = json.dumps(params, sort_keys=True)
    key_hash = hashlib.md5(params_str.encode()).hexdigest()

    return f"{MODEL_RESPONSE_PREFIX}{key_hash}"


def get_cached_response(
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: Optional[float] = None,
    system_prompt: Optional[str] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    quantization: str = "int8",
) -> Optional[Dict[str, Any]]:
    """
    Get a cached model response if available

    Only caches deterministic responses (temperature=0) or frequently used prompts
    to avoid cache pollution with random responses.

    Args:
        model: Model name/ID
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        system_prompt: Optional system prompt
        top_p: Optional nucleus sampling parameter
        top_k: Optional top-k sampling parameter
        quantization: Model quantization level

    Returns:
        Cached response dict or None if not in cache
    """
    if not is_cache_available():
        return None

    # Only cache deterministic responses (temperature=0) or short common prompts
    # to avoid cache pollution with random responses
    should_cache = (temperature == 0.0) or (  # Deterministic responses
        len(prompt) < 100
        and prompt.strip().lower()
        in {
            "hello",
            "hi",
            "hey",
            "test",
            "hello world",  # Common greetings
            "what is your name",
            "who are you",
            "help",  # Common questions
            "tell me a joke",
            "how are you",  # Common requests
        }
    )

    if not should_cache:
        return None

    cache_key = _create_response_cache_key(
        model,
        prompt,
        max_tokens,
        temperature,
        system_prompt,
        top_p,
        top_k,
        quantization,
    )

    try:
        cached_data = get_cache(cache_key)
        if cached_data:
            logger.info(f"Cache hit for response: {cache_key}")
            return cached_data
        logger.debug(f"Cache miss for response: {cache_key}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving cached response: {e}")
        return None


def cache_model_response(
    model: str,
    prompt: str,
    max_tokens: int,
    response_text: str,
    response_data: Dict[str, Any],
    temperature: Optional[float] = None,
    system_prompt: Optional[str] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    quantization: str = "int8",
    cache_ttl: int = 3600,  # 1 hour default
) -> bool:
    """
    Cache a model response for future reuse

    Only caches deterministic responses (temperature=0) or frequently used prompts
    to avoid cache pollution with random responses.

    Args:
        model: Model name/ID
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        response_text: The generated text response
        response_data: Complete response data dictionary
        temperature: Sampling temperature
        system_prompt: Optional system prompt
        top_p: Optional nucleus sampling parameter
        top_k: Optional top-k sampling parameter
        quantization: Model quantization level
        cache_ttl: Time-to-live in seconds for the cache entry

    Returns:
        True if caching was successful, False otherwise
    """
    if not is_cache_available():
        return False

    # Only cache deterministic responses (temperature=0) or short common prompts
    # to avoid cache pollution with random responses
    should_cache = (temperature == 0.0) or (  # Deterministic responses
        len(prompt) < 100
        and prompt.strip().lower()
        in {
            "hello",
            "hi",
            "hey",
            "test",
            "hello world",  # Common greetings
            "what is your name",
            "who are you",
            "help",  # Common questions
            "tell me a joke",
            "how are you",  # Common requests
        }
    )

    if not should_cache:
        return False

    cache_key = _create_response_cache_key(
        model,
        prompt,
        max_tokens,
        temperature,
        system_prompt,
        top_p,
        top_k,
        quantization,
    )

    try:
        success = set_cache(cache_key, response_data, expire_seconds=cache_ttl)
        if success:
            logger.info(f"Cached model response: {cache_key}")
        return success
    except Exception as e:
        logger.error(f"Error caching model response: {e}")
        return False


def _create_metrics_cache_key(model: str, metric_type: str) -> str:
    """
    Create a cache key for model metrics

    Args:
        model: Model name/ID
        metric_type: Type of metric (e.g., 'latency', 'throughput')

    Returns:
        A cache key string
    """
    return f"{MODEL_METRICS_PREFIX}{model}:{metric_type}"


def get_cached_metrics(model: str, metric_type: str) -> Optional[Dict[str, Any]]:
    """
    Get cached metrics for a model if available

    Args:
        model: Model name/ID
        metric_type: Type of metric (e.g., 'latency', 'throughput')

    Returns:
        Cached metrics dict or None if not in cache
    """
    if not is_cache_available():
        return None

    cache_key = _create_metrics_cache_key(model, metric_type)

    try:
        cached_data = get_cache(cache_key)
        if cached_data:
            logger.info(f"Cache hit for metrics: {cache_key}")
            return cached_data
        return None
    except Exception as e:
        logger.error(f"Error retrieving cached metrics: {e}")
        return None


def cache_model_metrics(
    model: str, metric_type: str, metrics_data: Dict[str, Any], cache_ttl: int = 300
) -> bool:
    """
    Cache model metrics for a short period

    Only caches metrics that have actual data (total_requests > 0) to avoid
    caching empty results for long periods.

    Args:
        model: Model name/ID
        metric_type: Type of metric (e.g., 'latency', 'throughput')
        metrics_data: The metrics data to cache
        cache_ttl: Time-to-live in seconds for the cache entry (default 5 minutes)

    Returns:
        True if caching was successful, False otherwise
    """
    if not is_cache_available():
        return False

    # Only cache metrics that have actual data
    has_data = False

    # Check if this is a summary with actual data
    if metric_type == "summary" and isinstance(metrics_data, dict):
        total_requests = metrics_data.get("total_requests", 0)
        has_data = total_requests > 0
    else:
        # For other metric types, check if there's any data
        has_data = bool(metrics_data)

    # Adjust TTL based on data presence
    # Empty results get shorter TTL to avoid stale cache
    adjusted_ttl = cache_ttl if has_data else 60  # 1 minute for empty results

    cache_key = _create_metrics_cache_key(model, metric_type)

    try:
        success = set_cache(cache_key, metrics_data, expire_seconds=adjusted_ttl)
        if success:
            logger.info(f"Cached model metrics: {cache_key}, TTL: {adjusted_ttl}s")
        return success
    except Exception as e:
        logger.error(f"Error caching model metrics: {e}")
        return False
