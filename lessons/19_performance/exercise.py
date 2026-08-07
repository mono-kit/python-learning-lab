"""第 19 章练习：实现可重复使用的测量工具。

完成后运行 ``pytest lessons/19_performance/test_lesson.py``。测试只检查调用次数、
参数转发、结果和报告结构，不会用不稳定的“必须比另一个实现快”作为正确性标准。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


@dataclass(frozen=True, slots=True)
class MemoryResult:
    current_bytes: int
    peak_bytes: int


def benchmark(function: Callable[[], object], *, number: int = 1000) -> float:
    """调用 function 指定次数并返回总秒数。"""

    # TODO: number 必须大于零；使用 timeit.Timer，不要自己写易受干扰的计时循环。
    raise NotImplementedError


def profile_text(function: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> str:
    """执行函数并返回按累计时间排序的 cProfile 文本。"""

    # TODO: 使用 cProfile.Profile、pstats.Stats 和内存中的文本流。
    raise NotImplementedError


def measure_peak_memory(
    function: Callable[P, R], *args: P.args, **kwargs: P.kwargs
) -> tuple[R, MemoryResult]:
    """执行函数，并同时返回原结果与 tracemalloc 当前值/峰值。"""

    # TODO: 无论函数成功还是抛出异常都必须停止本次启动的 tracemalloc。
    raise NotImplementedError
