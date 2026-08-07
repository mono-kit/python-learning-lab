"""第 8 章练习：组合 pathlib、json、collections、itertools 和 functools。"""

import json
from collections import Counter, defaultdict
from collections.abc import Iterable
from functools import lru_cache
from itertools import islice
from pathlib import Path


def count_words(text: str) -> Counter[str]:
    return Counter(text.lower().split())


def group_by_initial(names: list[str]) -> dict[str, list[str]]:
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for name in names:
        groups[name[0].lower()].append(name)
    return dict(groups)


def save_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def pages(values: Iterable[int], size: int) -> list[tuple[int, ...]]:
    if size < 1:
        raise ValueError("size 必须大于零")

    iterator = iter(values)
    result: list[tuple[int, ...]] = []
    while batch := tuple(islice(iterator, size)):
        result.append(batch)
    return result


@lru_cache(maxsize=None)  # noqa: UP033 - 本章专门练习 lru_cache
def fibonacci_recursive(number: int) -> int:
    if number < 0:
        raise ValueError("number 不能为负数")
    if number < 2:
        return number
    return fibonacci_recursive(number - 1) + fibonacci_recursive(number - 2)
