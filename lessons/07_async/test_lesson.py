"""第 7 章映射：lessons/07_async/exercise.py。"""

import asyncio
from collections.abc import AsyncIterator

from lessons._loader import load_exercise

exercise = load_exercise("07_async")
run_concurrently = exercise["run_concurrently"]
collect_async = exercise["collect_async"]


async def test_run_concurrently_starts_all_work_and_preserves_input_order() -> None:
    started: list[int] = []
    all_started = asyncio.Event()

    async def worker(value: int) -> int:
        started.append(value)
        if len(started) == 3:
            all_started.set()
        await asyncio.wait_for(all_started.wait(), timeout=0.2)
        return value * 10

    results = await run_concurrently([3, 1, 2], worker)

    assert set(started) == {1, 2, 3}
    assert results == [30, 10, 20]


async def test_collect_async_awaits_each_anext_result() -> None:
    async def values() -> AsyncIterator[int]:
        yield 1
        await asyncio.sleep(0)
        yield 2

    assert await collect_async(values()) == [1, 2]
