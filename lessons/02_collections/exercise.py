"""第 2 章练习：使用字典按值归组。"""


def invert(mapping: dict[str, int]) -> dict[int, list[str]]:
    """把值相同的键归组，例如 {'a': 1, 'b': 1} -> {1: ['a', 'b']}。"""
    result: dict[int, list[str]] = {}

    for item in mapping.items():
        key, value = item
        result.setdefault(value, []).append(key)

    return result
