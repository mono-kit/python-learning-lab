"""第 14 章练习：实现有界并发执行器。"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
R = TypeVar("R")


@dataclass(frozen=True, slots=True)
class WorkResult(Generic[R]):
    value: R | None = None
    error: str | None = None
    timed_out: bool = False


async def run_limited(
    items: Sequence[T],
    worker: Callable[[T], Awaitable[R]],
    *,
    max_concurrency: int = 3,
    timeout: float | None = None,
) -> list[WorkResult[R]]:
    """保持输入顺序；限制并发；普通失败和超时转换成 WorkResult。"""

    if max_concurrency <= 0:
        raise ValueError("max_concurrency 必须大于零")
    if timeout is not None and timeout <= 0:
        raise ValueError("timeout 必须大于零")

    semaphore = asyncio.Semaphore(max_concurrency)

    async def execute(item: T) -> WorkResult[R]:
        async with semaphore:
            try:
                if timeout is None:
                    result = await worker(item)
                else:
                    async with asyncio.timeout(timeout):
                        result = await worker(item)
                return WorkResult(value=result)
            except TimeoutError:
                return WorkResult(error="timeout", timed_out=True)
            except Exception as error:  # noqa: BLE001
                return WorkResult(error=f"{type(error).__name__}: {error}")

    tasks: list[asyncio.Task[WorkResult[R]]] = []

    async with asyncio.TaskGroup() as group:
        for item in items:
            tasks.append(group.create_task(execute(item)))

    return [task.result() for task in tasks]
