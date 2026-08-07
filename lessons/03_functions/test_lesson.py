"""第 3 章映射：lessons/03_functions/exercise.py。"""

import pytest

from lessons._loader import load_exercise

exercise = load_exercise("03_functions")
compose = exercise["compose"]
retry = exercise["retry"]


def test_compose_calls_functions_from_left_to_right() -> None:
    calls: list[str] = []

    def first(value: int) -> int:
        calls.append("first")
        return value + 1

    def second(value: int) -> int:
        calls.append("second")
        return value * 2

    assert compose(first, second)(3) == 8
    assert calls == ["first", "second"]


def test_retry_forwards_arguments_and_preserves_metadata() -> None:
    attempts = 0

    @retry(attempts=3)
    def unstable(value: int, *, bonus: int = 0) -> int:
        """Eventually return a value."""

        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RuntimeError("temporary")
        return value + bonus

    assert unstable(10, bonus=5) == 15
    assert attempts == 3
    assert unstable.__name__ == "unstable"
    assert unstable.__doc__ == "Eventually return a value."


def test_retry_validates_attempt_count_and_reraises_final_error() -> None:
    with pytest.raises(ValueError):
        retry(attempts=0)

    calls = 0

    @retry(attempts=2)
    def fail() -> None:
        nonlocal calls
        calls += 1
        raise LookupError("still broken")

    with pytest.raises(LookupError, match="still broken"):
        fail()
    assert calls == 2
