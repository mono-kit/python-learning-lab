"""第 22 章练习：实现可复用、可测试的同步 JSON 客户端。"""

from __future__ import annotations

from typing import Any

import httpx


class InvalidJSONResponse(ValueError):
    pass


class SyncJSONClient:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def get_object(self, path: str) -> dict[str, Any]:
        """请求 path，检查状态码，并且只接受 JSON object。"""

        # TODO: 使用注入的 client；不要在每次调用时创建新 Client。
        raise NotImplementedError
