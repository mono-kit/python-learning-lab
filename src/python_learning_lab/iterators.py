"""迭代协议、生成器和惰性计算。"""

from collections.abc import Iterable, Iterator


class Countdown(Iterator[int]):
    """迭代器同时实现 __iter__ 和 __next__。"""

    def __init__(self, start: int) -> None:
        self.current = start

    def __iter__(self) -> "Countdown":
        return self

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


def fibonacci(limit: int) -> Iterator[int]:
    """包含 yield 的函数返回生成器，并按需产生值。"""
    current, following = 0, 1
    while current <= limit:
        yield current
        current, following = following, current + following


def flatten(groups: Iterable[Iterable[int]]) -> Iterator[int]:
    """yield from 把产生值的工作委托给另一个可迭代对象。"""
    for group in groups:
        yield from group


def take(count: int, values: Iterable[int]) -> list[int]:
    """只消费可迭代对象的前 count 项。"""
    result: list[int] = []
    for value in values:
        if len(result) == count:
            break
        result.append(value)
    return result

