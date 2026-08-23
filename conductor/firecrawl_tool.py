"""Failure-tolerant Firecrawl v2 web search adapter."""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx

from utils.logger import logger


class FirecrawlTool:
    """Search the live web through Firecrawl without exposing its API key."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        client: Any = None,
        base_url: str = "https://api.firecrawl.dev",
    ) -> None:
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        self.base_url = base_url.rstrip("/")
        self._client = client

    @property
    def enabled(self) -> bool:
        return bool(self.api_key or self._client)

    def search(self, query: str, limit: int = 3) -> list[dict[str, str]]:
        """Return compact web results and degrade cleanly when unavailable."""
        if not self.enabled:
            return []

        try:
            owns_client = self._client is None
            client = self._client or httpx.Client(timeout=30.0)
            try:
                response = client.post(
                    f"{self.base_url}/v2/search",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "query": query[:500],
                        "limit": max(1, min(limit, 5)),
                        "sources": ["web"],
                    },
                )
            finally:
                if owns_client:
                    client.close()
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data", {}) if isinstance(payload, dict) else {}
            records = data.get("web", []) if isinstance(data, dict) else []
            return [
                {
                    "title": record.get("title") or record.get("url") or "Web result",
                    "url": record.get("url") or "",
                    "description": record.get("description") or "",
                }
                for record in records
                if isinstance(record, dict) and record.get("url")
            ]
        except Exception as exc:
            logger.warning("Firecrawl search failed; continuing without web results: %s", exc)
            return []
