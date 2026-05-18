"""
Redis cache service for LLMPlayBench

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis connection
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,  # Automatically decode responses to Python strings
        socket_connect_timeout=2,  # Short timeout for connection attempts
        socket_timeout=5,  # Timeout for operations
    )
    # Test connection
    redis_client.ping()
    logger.info(f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
except redis.ConnectionError as e:
    logger.warning(f"Redis connection failed: {e}. Caching will be disabled.")
    redis_client = None
except Exception as e:
    logger.warning(f"Redis initialization error: {e}. Caching will be disabled.")
    redis_client = None


def is_cache_available() -> bool:
    """Check if Redis cache is available"""
    if redis_client is None:
        return False

    try:
        return redis_client.ping()
    except:
        return False


def get_cache(key: str) -> Optional[Any]:
    """
    Get a value from cache by key
    Returns None if key doesn't exist or cache is unavailable
    """
    if not is_cache_available():
        return None

    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logger.error(f"Cache get error for key '{key}': {e}")
        return None


def set_cache(key: str, value: Any, expire_seconds: int = 3600) -> bool:
    """
    Set a value in cache with optional expiration (default 1 hour)
    Returns True if successful, False otherwise
    """
    if not is_cache_available():
        return False

    try:
        serialized = json.dumps(value)
        return redis_client.set(key, serialized, ex=expire_seconds)
    except Exception as e:
        logger.error(f"Cache set error for key '{key}': {e}")
        return False


def delete_cache(key: str) -> bool:
    """Delete a key from cache"""
    if not is_cache_available():
        return False

    try:
        return bool(redis_client.delete(key))
    except Exception as e:
        logger.error(f"Cache delete error for key '{key}': {e}")
        return False


def clear_cache_pattern(pattern: str) -> int:
    """
    Clear all keys matching a pattern
    Returns number of keys deleted
    """
    if not is_cache_available():
        return 0

    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception as e:
        logger.error(f"Cache clear pattern error for '{pattern}': {e}")
        return 0


def get_cache_stats() -> Dict[str, Any]:
    """Get Redis cache statistics"""
    if not is_cache_available():
        return {"status": "unavailable"}

    try:
        info = redis_client.info()
        stats = {
            "status": "available",
            "used_memory": info.get("used_memory_human", "unknown"),
            "clients_connected": info.get("connected_clients", 0),
            "uptime_days": round(info.get("uptime_in_seconds", 0) / 86400, 1),
            "hit_rate": 0,
        }

        # Calculate hit rate if available
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        if hits + misses > 0:
            stats["hit_rate"] = round(hits / (hits + misses) * 100, 1)

        return stats
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        return {"status": "error", "message": str(e)}
