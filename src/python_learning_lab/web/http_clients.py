"""第 22～24 章：HTTPX、并发请求、流式响应和重试策略。"""

from __future__ import annotations

import asyncio
import hashlib
from collections.abc import Sequence
from dataclasses import dataclass, field
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


@dataclass(frozen=True, slots=True)
class FetchResult:
    url: str
    status: int | None = None
    payload: Any = None
    error: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.error is None


async def fetch_many(
    urls: Sequence[str],
    client: httpx.AsyncClient,
    *,
    max_concurrency: int = 5,
) -> list[FetchResult]:
    """限制并发并保持输入顺序；外层取消仍会正常传播。"""

    if max_concurrency <= 0:
        raise ValueError("max_concurrency 必须大于零")
    semaphore = asyncio.Semaphore(max_concurrency)

    async def fetch(url: str) -> FetchResult:
        async with semaphore:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return FetchResult(url=url, status=response.status_code, payload=response.json())
            except httpx.TimeoutException as error:
                return FetchResult(url=url, error=f"timeout: {error}")
            except httpx.HTTPStatusError as error:
                return FetchResult(
                    url=url,
                    status=error.response.status_code,
                    error=f"http: {error.response.status_code}",
                )
            except httpx.RequestError as error:
                return FetchResult(url=url, error=f"transport: {type(error).__name__}")
            except ValueError as error:
                return FetchResult(url=url, status=response.status_code, error=f"json: {error}")

    tasks: list[asyncio.Task[FetchResult]] = []
    async with asyncio.TaskGroup() as group:
        for url in urls:
            tasks.append(group.create_task(fetch(url)))
    return [task.result() for task in tasks]


async def stream_sha256(client: httpx.AsyncClient, url: str) -> str:
    """逐块计算响应摘要，不把整个 body 一次放入内存。"""

    digest = hashlib.sha256()
    async with client.stream("GET", url) as response:
        response.raise_for_status()
        async for chunk in response.aiter_bytes():
            digest.update(chunk)
    return digest.hexdigest()


RFC_IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE", "PUT", "DELETE"})


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """业务客户端的有界重试策略；不负责真正休眠或发送请求。"""

    max_attempts: int = 3
    retryable_methods: frozenset[str] = field(
        default_factory=lambda: frozenset({"GET", "HEAD", "OPTIONS"})
    )
    retryable_statuses: frozenset[int] = field(
        default_factory=lambda: frozenset({429, 502, 503, 504})
    )
    base_delay: float = 0.1
    max_delay: float = 2.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts 至少为 1")
        if self.base_delay < 0 or self.max_delay < 0:
            raise ValueError("退避时间不能为负数")
        if self.base_delay > self.max_delay:
            raise ValueError("base_delay 不能大于 max_delay")

    def should_retry(
        self,
        method: str,
        status: int,
        *,
        attempt: int,
        idempotency_key: str | None = None,
    ) -> bool:
        """``attempt`` 是刚完成的尝试序号，从 1 开始。"""

        if attempt < 1:
            raise ValueError("attempt 从 1 开始")
        method = method.upper()
        has_idempotency_key = bool(idempotency_key and idempotency_key.strip())
        replayable = method in self.retryable_methods or has_idempotency_key
        return attempt < self.max_attempts and replayable and status in self.retryable_statuses

    def backoff_delay(self, *, attempt: int, jitter: float = 0.0) -> float:
        """返回下一次尝试前的指数退避；jitter 由可注入随机源产生。"""

        if attempt < 1:
            raise ValueError("attempt 从 1 开始")
        if jitter < 0:
            raise ValueError("jitter 不能为负数")
        delay = self.base_delay * float(2 ** (attempt - 1)) + jitter
        return min(self.max_delay, delay)
