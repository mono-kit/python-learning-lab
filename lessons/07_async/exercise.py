"""第 7 章练习：TaskGroup 并发与 ``async for``。"""

import asyncio
from collections.abc import AsyncIterable, Awaitable, Callable, Sequence
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


async def run_concurrently(items: Sequence[T], worker: Callable[[T], Awaitable[R]]) -> list[R]:
    """并发执行 ``worker``，同时让结果保持输入顺序。"""

    tasks: list[asyncio.Task[R]] = []
    async with asyncio.TaskGroup() as group:
        for item in items:
            tasks.append(group.create_task(worker(item)))
    return [task.result() for task in tasks]


async def collect_async(values: AsyncIterable[T]) -> list[T]:
    """使用 ``async for`` 收集异步可迭代对象。"""

    result: list[T] = []
    async for value in values:
        result.append(value)
    return result
