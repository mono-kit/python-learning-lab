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
        # TODO: 用正确泛型参数标注字典。
        self._values = {}

    def put(self, key: K, value: V) -> None:
        # TODO
        raise NotImplementedError

    def get(self, key: K) -> V | None:
        # TODO
        raise NotImplementedError


def traced(callback: Callable[[str], None]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # TODO: 记录函数名，再原样调用函数。
            raise NotImplementedError

        return wrapper

    return decorate
