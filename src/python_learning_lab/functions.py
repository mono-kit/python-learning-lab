"""函数参数、闭包、高阶函数和装饰器。"""

from collections.abc import Callable
from functools import wraps
from time import perf_counter
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def format_user(user_id: int, /, name: str, *, active: bool = True) -> str:
    """`/` 前只能按位置传参，`*` 后只能按关键字传参。"""
    state = "启用" if active else "停用"
    return f"#{user_id} {name}（{state}）"


def total(*numbers: float) -> float:
    """*numbers 把任意数量的位置参数收集为 tuple。"""
    return sum(numbers)


def build_profile(name: str, **attributes: object) -> dict[str, object]:
    """**attributes 把额外关键字参数收集为 dict。"""
    return {"name": name, **attributes}


def make_multiplier(factor: int) -> Callable[[int], int]:
    """内部函数记住外层作用域中的 factor，这就是闭包。"""

    def multiply(number: int) -> int:
        return number * factor

    return multiply


def timed(function: Callable[P, R]) -> Callable[P, R]:
    """保持原函数类型和元数据的计时装饰器。"""

    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started = perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            elapsed = perf_counter() - started
            print(f"{function.__name__} took {elapsed:.6f}s")

    return wrapper
