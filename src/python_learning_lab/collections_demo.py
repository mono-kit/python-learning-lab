"""Python 内置容器及其典型用途。"""


def unique_words(sentence: str) -> list[str]:
    """set 去重，sorted 返回新的有序 list。"""
    return sorted(set(sentence.lower().split()))


def word_frequency(words: list[str]) -> dict[str, int]:
    """字典把单词映射到出现次数。"""
    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts


def partition(numbers: list[int]) -> tuple[list[int], list[int]]:
    """一次返回多个值时，Python 实际返回一个 tuple。"""
    even = [number for number in numbers if number % 2 == 0]
    odd = [number for number in numbers if number % 2 != 0]
    return even, odd


def merge_preferences(defaults: dict[str, object], user: dict[str, object]) -> dict[str, object]:
    """后展开的字典覆盖同名键；原字典不会被修改。"""
    return {**defaults, **user}

