"""第 14 章练习：实现有界并发执行器。"""

from __future__ import annotations

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

    # TODO: 使用 Semaphore、asyncio.timeout 和 TaskGroup。
    raise NotImplementedError
