"""第 1 章练习：控制流与 FizzBuzz。"""


def fizz_buzz(limit: int) -> list[str]:
    """返回 1..limit；3 的倍数用 Fizz，5 的倍数用 Buzz，两者用 FizzBuzz。"""
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
