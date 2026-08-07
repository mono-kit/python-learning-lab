"""第 14 章：取消、超时、并发上限和结构化并发。"""

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

    @property
    def succeeded(self) -> bool:
        return self.error is None and not self.timed_out


async def run_limited(
    items: Sequence[T],
    worker: Callable[[T], Awaitable[R]],
    *,
    max_concurrency: int = 3,
    timeout: float | None = None,
) -> list[WorkResult[R]]:
    """按输入顺序返回结果，同时限制正在执行的 worker 数量。

    普通异常被转换成结果；``CancelledError`` 不会被吞掉，因为它继承
    ``BaseException``。取消外层任务时，TaskGroup 会等待所有子任务清理完成。
    """

    if max_concurrency <= 0:
        raise ValueError("max_concurrency 必须大于零")
    if timeout is not None and timeout <= 0:
        raise ValueError("timeout 必须大于零")

    semaphore = asyncio.Semaphore(max_concurrency)

    async def execute(item: T) -> WorkResult[R]:
        async with semaphore:
            try:
                if timeout is None:
                    value = await worker(item)
                else:
                    async with asyncio.timeout(timeout):
                        value = await worker(item)
                return WorkResult(value=value)
            except TimeoutError:
                return WorkResult(error="timeout", timed_out=True)
            # 任务执行器的契约就是把普通工作失败转换为结果；取消仍会继续传播。
            except Exception as error:  # noqa: BLE001
                return WorkResult(error=f"{type(error).__name__}: {error}")

    tasks: list[asyncio.Task[WorkResult[R]]] = []
    async with asyncio.TaskGroup() as group:
        for item in items:
            tasks.append(group.create_task(execute(item)))
    return [task.result() for task in tasks]


async def fail_fast(awaitables: Sequence[Awaitable[R]]) -> list[R]:
    """演示 TaskGroup：任一任务失败会取消仍在运行的兄弟任务。"""

    tasks: list[asyncio.Task[R]] = []

    async def wait_for(awaitable: Awaitable[R]) -> R:
        return await awaitable

    async with asyncio.TaskGroup() as group:
        for awaitable in awaitables:
            tasks.append(group.create_task(wait_for(awaitable)))
    return [task.result() for task in tasks]


async def main() -> None:
    async def square(number: int) -> int:
        await asyncio.sleep(0)
        return number**2

    print(await run_limited([1, 2, 3, 4], square, max_concurrency=2))


if __name__ == "__main__":
    asyncio.run(main())
