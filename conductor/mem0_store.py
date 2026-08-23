"""Cloud-persistent conversation memory backed by Mem0 Platform."""

from __future__ import annotations

import logging
import os
from typing import Any, Optional


logger = logging.getLogger(__name__)


class Mem0Store:
    """Small failure-tolerant adapter around the Mem0 Platform client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        user_id: Optional[str] = None,
        client: Any = None,
    ) -> None:
        self.user_id = user_id or os.getenv("MEM0_USER_ID", "john-cramer")
        self.agent_id = os.getenv("MEM0_AGENT_ID", "ara-conductor")
        self._client = client

        key = api_key or os.getenv("MEM0_API_KEY")
        if self._client is None and key:
            try:
                from mem0 import MemoryClient

                self._client = MemoryClient(api_key=key)
            except Exception as exc:
                logger.warning("Mem0 initialization failed; continuing without memory: %s", exc)

    @property
    def enabled(self) -> bool:
        """Whether a Mem0 client is available for this process."""
        return self._client is not None

    def search(self, query: str, limit: int = 5) -> list[str]:
        """Return relevant remembered facts without interrupting chat on failure."""
        if not self._client:
            return []

        try:
            payload = self._client.search(
                query,
                filters={"user_id": self.user_id},
            )
            records = payload.get("results", []) if isinstance(payload, dict) else payload
            if not isinstance(records, list):
                return []
            return [
                record["memory"]
                for record in records
                if isinstance(record, dict) and record.get("memory")
            ][:limit]
        except Exception as exc:
            logger.warning("Mem0 search failed; continuing without retrieved memory: %s", exc)
            return []

    def add_turn(self, user_text: str, assistant_text: str, provider: str) -> bool:
        """Persist one user/assistant exchange, returning whether it was accepted."""
        if not self._client:
            return False

        try:
            self._client.add(
                messages=[
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": assistant_text},
                ],
                user_id=self.user_id,
                metadata={
                    "agent_id": self.agent_id,
                    "provider": provider,
                    "source": "conductor-voice",
                },
            )
            return True
        except Exception as exc:
            logger.warning("Mem0 write failed; response will still be returned: %s", exc)
            return False
