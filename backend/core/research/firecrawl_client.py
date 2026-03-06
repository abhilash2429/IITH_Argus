"""
Firecrawl client wrapper with retries, normalization, and structured logs.
"""

from __future__ import annotations

from typing import Any

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from backend.config import settings
from backend.core.structured_logging import get_logger

logger = get_logger(__name__)


class FirecrawlClient:
    """
    Thin production-safe wrapper over firecrawl-py SDK.
    """

    def __init__(self) -> None:
        self.max_pages = settings.max_firecrawl_pages_per_search
        self.api_key = settings.firecrawl_api_key
        if not self.api_key:
            raise RuntimeError("FIRECRAWL_API_KEY is required for live research mode")
        try:
            from firecrawl import FirecrawlApp
        except Exception as exc:
            raise RuntimeError("firecrawl-py is not installed") from exc
        self.app = FirecrawlApp(api_key=self.api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        retry=retry_if_exception_type(Exception),
    )
    def search(
        self,
        query: str,
        *,
        num_results: int | None = None,
        scrape_options: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        limit = int(num_results or self.max_pages)
        normalized_scrape_options = scrape_options or {"formats": ["markdown"]}
        logger.info("firecrawl.search.start", query=query[:120], limit=limit)
        try:
            # firecrawl-py v2+ signature
            response = self.app.search(
                query,
                limit=limit,
                scrape_options=normalized_scrape_options,
            )
        except TypeError:
            # firecrawl-py v1 fallback
            params = {
                "limit": limit,
                "scrapeOptions": normalized_scrape_options,
            }
            response = self.app.search(query, params=params)
        data = getattr(response, "data", None)
        if data is None:
            data = getattr(response, "web", None)
        if data is None and isinstance(response, dict):
            data = response.get("data") or response.get("web")
        if data is None:
            data = response
        normalized = [self._normalize_result(r) for r in (data or [])]
        logger.info("firecrawl.search.complete", query=query[:120], count=len(normalized))
        return normalized

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        retry=retry_if_exception_type(Exception),
    )
    def scrape(self, url: str, *, formats: list[str] | None = None) -> dict[str, Any]:
        chosen_formats = formats or ["markdown", "links"]
        logger.info("firecrawl.scrape.start", url=url[:120])
        try:
            # firecrawl-py v2+ signature
            response = self.app.scrape(url, formats=chosen_formats)
        except TypeError:
            # firecrawl-py v1 fallback
            response = self.app.scrape_url(url, params={"formats": chosen_formats})
        result = getattr(response, "data", response) or {}
        logger.info("firecrawl.scrape.complete", url=url[:120])
        return self._normalize_result(result)

    def crawl(self, url: str, *, max_depth: int = 2, limit: int = 20) -> list[dict[str, Any]]:
        logger.info("firecrawl.crawl.start", url=url[:120], max_depth=max_depth, limit=limit)
        try:
            # firecrawl-py v2+ signature
            response = self.app.crawl(
                url,
                max_discovery_depth=max_depth,
                limit=limit,
                scrape_options={"formats": ["markdown"]},
                timeout=120,
            )
        except TypeError:
            # firecrawl-py v1 fallback
            params = {
                "crawlerOptions": {"maxDepth": max_depth, "limit": limit},
                "pageOptions": {"formats": ["markdown"]},
            }
            response = self.app.crawl_url(url, params=params, wait_until_done=True, timeout=120)
        pages = getattr(response, "data", []) or []
        normalized = [self._normalize_result(p) for p in pages]
        logger.info("firecrawl.crawl.complete", url=url[:120], pages=len(normalized))
        return normalized

    def map_domain(self, url: str, *, search: str | None = None) -> list[str]:
        try:
            # firecrawl-py v2+ signature
            response = self.app.map(url, search=search)
        except TypeError:
            # firecrawl-py v1 fallback
            params: dict[str, Any] = {}
            if search:
                params["search"] = search
            response = self.app.map_url(url, params=params)
        links = getattr(response, "links", None)
        if links is None and isinstance(response, dict):
            links = response.get("links")
        out = links or []
        logger.info("firecrawl.map.complete", url=url[:120], links=len(out))
        return out

    @staticmethod
    def _normalize_result(item: Any) -> dict[str, Any]:
        def _from_metadata(metadata: Any) -> tuple[str, str, str]:
            if not metadata:
                return "", "", ""
            if isinstance(metadata, dict):
                return (
                    metadata.get("sourceURL")
                    or metadata.get("source_url")
                    or metadata.get("url")
                    or "",
                    metadata.get("title") or "",
                    metadata.get("description") or "",
                )
            return (
                getattr(metadata, "sourceURL", "")
                or getattr(metadata, "source_url", "")
                or getattr(metadata, "url", ""),
                getattr(metadata, "title", "") or "",
                getattr(metadata, "description", "") or "",
            )

        if isinstance(item, dict):
            meta = item.get("metadata") or {}
            meta_url, meta_title, meta_desc = _from_metadata(meta)
            return {
                "url": item.get("url") or meta_url,
                "title": item.get("title") or meta_title,
                "description": item.get("description") or meta_desc,
                "markdown": item.get("markdown") or item.get("content") or item.get("raw_content") or "",
                "metadata": meta,
            }
        # Best-effort for SDK object types
        metadata = getattr(item, "metadata", {}) or {}
        meta_url, meta_title, meta_desc = _from_metadata(metadata)
        return {
            "url": getattr(item, "url", "") or meta_url,
            "title": getattr(item, "title", "") or meta_title,
            "description": getattr(item, "description", "") or meta_desc,
            "markdown": getattr(item, "markdown", "")
            or getattr(item, "content", "")
            or getattr(item, "raw_content", ""),
            "metadata": metadata,
        }
