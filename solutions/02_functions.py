from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")


def compose(first: Callable[[T], T], second: Callable[[T], T]) -> Callable[[T], T]:
    def composed(value: T) -> T:
        return second(first(value))

    return composed


def retry(attempts: int):
    if attempts < 1:
        raise ValueError("attempts 必须大于零")

    def decorator(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(attempts):
                try:
                    return function(*args, **kwargs)
                except Exception:
                    if attempt == attempts - 1:
                        raise
            raise AssertionError("unreachable")

        return wrapper

    return decorator

