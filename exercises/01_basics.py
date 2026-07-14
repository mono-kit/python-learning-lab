def fizz_buzz(limit: int) -> list[str]:
    """返回 1..limit；3 的倍数用 Fizz，5 的倍数用 Buzz，两者用 FizzBuzz。"""
    # TODO: 使用 for、if/elif/else 和 append
    result: list[str] = []
    for number in range(1, limit + 1):
        if number % 15 == 0:
            result.append("FizzBuzz")
        elif number % 3 == 0:
            result.append("Fizz")
        elif number % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(number))
    return result


def invert(mapping: dict[str, int]) -> dict[int, list[str]]:
    """把值相同的键归组，例如 {'a': 1, 'b': 1} -> {1: ['a', 'b']}。"""
    # TODO: 使用 dict.setdefault 或 collections.defaultdict

    result: dict[int, list[str]] = {}

    for item in mapping.items():
        key, value = item
        result.setdefault(value, []).append(key)

    return result


if __name__ == "__main__":
    assert fizz_buzz(0) == []
    assert fizz_buzz(5) == ["1", "2", "Fizz", "4", "Buzz"]
    assert fizz_buzz(15)[-1] == "FizzBuzz"

    assert invert({}) == {}
    assert invert({"a": 1}) == {1: ["a"]}
    assert invert({"a": 1, "b": 2, "c": 1}) == {
        1: ["a", "c"],
        2: ["b"],
    }

    print("01_basics 全部验证通过")

