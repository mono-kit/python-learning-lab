"""第 1 章映射：lessons/01_basics/exercise.py 中的 fizz_buzz。"""

from lessons._loader import load_exercise

fizz_buzz = load_exercise("01_basics")["fizz_buzz"]


def test_fizz_buzz_covers_control_flow_boundaries() -> None:
    assert fizz_buzz(0) == []
    assert fizz_buzz(15) == [
        "1",
        "2",
        "Fizz",
        "4",
        "Buzz",
        "Fizz",
        "7",
        "8",
        "Fizz",
        "Buzz",
        "11",
        "Fizz",
        "13",
        "14",
        "FizzBuzz",
    ]
