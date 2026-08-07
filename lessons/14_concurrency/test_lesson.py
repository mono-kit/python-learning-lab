import asyncio

from lessons._loader import load_exercise

exercise = load_exercise("14_concurrency")
run_limited = exercise["run_limited"]


async def test_run_limited_preserves_order_and_concurrency_limit() -> None:
    active = 0
    maximum = 0

    async def worker(number: int) -> int:
        nonlocal active, maximum
        active += 1
        maximum = max(maximum, active)
        try:
            await asyncio.sleep(0)
            return number**2
        finally:
            active -= 1

    results = await run_limited([3, 1, 2], worker, max_concurrency=2)
    assert [result.value for result in results] == [9, 1, 4]
    assert maximum == 2


async def test_run_limited_separates_failure_and_timeout() -> None:
    async def worker(value: str) -> str:
        if value == "fail":
            raise RuntimeError("broken")
        if value == "slow":
            await asyncio.sleep(0.05)
        return value

    results = await run_limited(["ok", "fail", "slow"], worker, max_concurrency=3, timeout=0.005)

    assert results[0].value == "ok"
    assert "RuntimeError" in results[1].error
    assert results[2].timed_out is True
