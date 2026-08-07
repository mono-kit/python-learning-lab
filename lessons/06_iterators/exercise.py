"""第 6 章练习：迭代协议、委托迭代和精确消费。"""

from collections.abc import Iterable, Iterator


class Countdown(Iterator[int]):
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
    """惰性地产出所有严格小于 ``limit`` 的斐波那契数。"""

    current, following = 0, 1
    while current < limit:
        yield current
        current, following = following, current + following


def flatten(groups: Iterable[Iterable[int]]) -> Iterator[int]:
    """按顺序惰性地产出所有分组中的元素。"""

    for group in groups:
        yield from group


def take(count: int, values: Iterable[int]) -> list[int]:
    """精确消费至多 ``count`` 项，不额外读取下一项。"""

    if count < 0:
        raise ValueError("count 不能为负数")

    result: list[int] = []
    iterator = iter(values)
    for _ in range(count):
        try:
            result.append(next(iterator))
        except StopIteration:
            break
    return result
