"""第 6 章映射：lessons/06_iterators/exercise.py。"""

from collections.abc import Iterator

import pytest

from lessons._loader import load_exercise

exercise = load_exercise("06_iterators")
Countdown = exercise["Countdown"]
flatten = exercise["flatten"]
take = exercise["take"]


def test_countdown_is_its_own_iterator_and_stays_exhausted() -> None:
    countdown = Countdown(3)
    assert iter(countdown) is countdown
    assert list(countdown) == [3, 2, 1]
    with pytest.raises(StopIteration):
        next(countdown)


def test_flatten_is_lazy_and_preserves_order() -> None:
    flattened = flatten([[1, 2], [], [3]])
    assert isinstance(flattened, Iterator)
    assert list(flattened) == [1, 2, 3]


def test_take_does_not_consume_one_item_too_many() -> None:
    iterator = iter([10, 20, 30])
    assert take(2, iterator) == [10, 20]
    assert next(iterator) == 30
    assert take(5, [1, 2]) == [1, 2]

    with pytest.raises(ValueError):
        take(-1, [1, 2])
