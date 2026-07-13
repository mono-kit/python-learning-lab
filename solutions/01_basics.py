from collections import defaultdict


def fizz_buzz(limit: int) -> list[str]:
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
    result: defaultdict[int, list[str]] = defaultdict(list)
    for key, value in mapping.items():
        result[value].append(key)
    return dict(result)

