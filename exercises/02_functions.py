from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def compose(first: Callable[[T], T], second: Callable[[T], T]) -> Callable[[T], T]:
    """返回一个新函数，新函数先调用 first，再调用 second。"""
    # TODO: 返回闭包
    raise NotImplementedError


def retry(attempts: int):
    """编写一个装饰器：函数抛出异常时最多重试 attempts 次。"""
    # TODO: 需要三层函数和一个循环
    raise NotImplementedError

