"""第 19 章：用 timeit、cProfile 和 tracemalloc 先测量再优化。"""

from __future__ import annotations

import cProfile
import io
import pstats
import tracemalloc
from collections.abc import Callable
from dataclasses import dataclass
from timeit import Timer
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


@dataclass(frozen=True, slots=True)
class MemoryResult:
    current_bytes: int
    peak_bytes: int


def benchmark(function: Callable[[], object], *, number: int = 1000) -> float:
    """返回多次调用的总秒数；比较时应使用相同 number 和输入。"""

    if number <= 0:
        raise ValueError("number 必须大于零")
    return Timer(function).timeit(number=number)


def profile_text(function: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> str:
    """返回按累计时间排序的 cProfile 文本。"""

    profiler = cProfile.Profile()
    profiler.runcall(function, *args, **kwargs)
    output = io.StringIO()
    pstats.Stats(profiler, stream=output).sort_stats("cumulative").print_stats()
    return output.getvalue()


def measure_peak_memory(
    function: Callable[P, R], *args: P.args, **kwargs: P.kwargs
) -> tuple[R, MemoryResult]:
    tracemalloc.start()
    try:
        result = function(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, MemoryResult(current, peak)


def main() -> None:
    values = list(range(10_000))
    sequence_time = benchmark(lambda: 9_999 in values)
    value_set = set(values)
    set_time = benchmark(lambda: 9_999 in value_set)
    print(f"list membership: {sequence_time:.6f}s")
    print(f"set membership:  {set_time:.6f}s")


if __name__ == "__main__":
    main()
