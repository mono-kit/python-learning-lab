"""第 23 章：有界并发 HTTP 请求与流式响应。"""

from __future__ import annotations

import asyncio
import hashlib
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
