"""第 23 章练习：有界并发请求和异步流式下载。"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True, slots=True)
class FetchResult:
    url: str
    status: int | None = None
    payload: Any = None
    error: str | None = None


async def fetch_many(
    urls: Sequence[str],
    client: httpx.AsyncClient,
    *,
    max_concurrency: int = 5,
) -> list[FetchResult]:
    """保持输入顺序，区分 HTTP、timeout、transport 和 JSON 错误。"""

    # TODO: 复用第 14 章的 Semaphore 与 TaskGroup 知识。
    raise NotImplementedError


async def stream_sha256(client: httpx.AsyncClient, url: str) -> str:
    """逐块读取响应并返回 SHA-256 十六进制摘要。"""

    # TODO: 使用 client.stream() 和 response.aiter_bytes()。
    raise NotImplementedError
