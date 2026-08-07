"""第 22 章：可复用、可测试的同步 HTTPX 客户端。"""

from __future__ import annotations

from typing import Any, cast

import httpx


class InvalidJSONResponse(ValueError):
    """响应是 JSON，但不是当前客户端契约要求的 JSON object。"""


class SyncJSONClient:
    """复用外部传入的 ``httpx.Client``，不擅自决定其生命周期。"""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def get_object(self, path: str) -> dict[str, Any]:
        response = self._client.get(path)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or not all(isinstance(key, str) for key in payload):
            raise InvalidJSONResponse("expected a JSON object")
        return cast(dict[str, Any], payload)
