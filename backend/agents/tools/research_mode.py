"""
Research mode system: mock / cached / live.
Controls how external research tools behave.
- mock: Return hardcoded mock data (no network calls)
- cached: Try cache first, then live, then save to cache
- live: Always call live APIs, save results to cache

Used by all research tools via the @research_tool decorator.
"""

import json
import os
import re
import logging
from pathlib import Path
from functools import wraps
from typing import Callable, Optional

from backend.config import settings

logger = logging.getLogger(__name__)

RESEARCH_MODE = settings.research_mode  # "mock" | "cached" | "live"
CACHE_DIR = Path(settings.cache_dir)


def _cache_path(source: str, key: str) -> Path:
    """
    Build a cache file path for a given source and key.

    Args:
        source: The research source name (e.g., "serper", "mca21").
        key: The lookup key (e.g., company name or query).

    Returns:
        Path object for the cache file.
    """
    sanitized_key = re.sub(r'[^\w\-]', '_', key.lower().strip())[:100]
    return CACHE_DIR / source / f"{sanitized_key}.json"


def save_to_cache(source: str, key: str, data: dict) -> None:
    """
    Save research results to the local file cache.

    Args:
        source: The research source name.
        key: The lookup key.
        data: The data dict to cache.
    """
    path = _cache_path(source, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"[Cache] Saved {source}/{key}")


def load_from_cache(source: str, key: str) -> Optional[dict]:
    """
    Load research results from local file cache.

    Args:
        source: The research source name.
        key: The lookup key.

    Returns:
        Cached dict or None if not found.
    """
    path = _cache_path(source, key)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            logger.info(f"[Cache] Hit {source}/{key}")
            return json.load(f)
    return None


def research_tool(source: str, mock_fn: Callable):
    """
    Decorator that wraps research functions with mock/cached/live mode handling.

    Args:
        source: Research source identifier for caching.
        mock_fn: Function that returns mock data when in mock mode.

    Returns:
        Decorated function that handles all three research modes.
    """
    def decorator(live_fn: Callable):
        @wraps(live_fn)
        def wrapper(*args, **kwargs):
            # Build cache key from first positional arg
            cache_key = str(args[0]) if args else "default"

            # Mode: mock
            if RESEARCH_MODE == "mock":
                logger.info(f"[Research] MOCK mode — {source}/{cache_key}")
                return mock_fn(*args, **kwargs)

            # Mode: cached — try cache first
            if RESEARCH_MODE == "cached":
                cached = load_from_cache(source, cache_key)
                if cached is not None:
                    return cached

            # Mode: live or cache miss — call live API
            try:
                result = live_fn(*args, **kwargs)
                # Save to cache for future use
                if isinstance(result, (dict, list)):
                    save_to_cache(source, cache_key, result if isinstance(result, dict) else {"data": result})
                elif isinstance(result, str):
                    save_to_cache(source, cache_key, {"text": result})
                return result
            except Exception as e:
                logger.error(f"[Research] Live call failed for {source}/{cache_key}: {e}")
                # Fallback to cache on live failure
                cached = load_from_cache(source, cache_key)
                if cached is not None:
                    logger.info(f"[Research] Using stale cache for {source}/{cache_key}")
                    return cached
                # Last resort: mock
                logger.warning(f"[Research] Falling back to mock for {source}/{cache_key}")
                return mock_fn(*args, **kwargs)

        return wrapper
    return decorator
