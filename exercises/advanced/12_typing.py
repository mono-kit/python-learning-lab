"""第 12 章练习：完成泛型缓存和保留签名的装饰器。"""

from collections.abc import Callable, Hashable
from functools import wraps
from typing import Generic, ParamSpec, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")
P = ParamSpec("P")
R = TypeVar("R")


class Cache(Generic[K, V]):
    def __init__(self) -> None:
        self._values: dict[K, V] = {}

    def put(self, key: K, value: V) -> None:
        self._values[key] = value

    def get(self, key: K) -> V | None:
        return self._values.get(key)


def traced(callback: Callable[[str], None]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            callback(function.__name__)
            return function(*args, **kwargs)

        return wrapper

    return decorate
