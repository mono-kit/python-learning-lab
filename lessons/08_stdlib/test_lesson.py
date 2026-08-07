"""第 8 章映射：lessons/08_stdlib/exercise.py。"""

from pathlib import Path

import pytest

from lessons._loader import load_exercise

exercise = load_exercise("08_stdlib")
count_words = exercise["count_words"]
group_by_initial = exercise["group_by_initial"]
save_json = exercise["save_json"]
load_json = exercise["load_json"]
pages = exercise["pages"]
fibonacci_recursive = exercise["fibonacci_recursive"]


def test_counter_and_defaultdict_tasks() -> None:
    assert count_words("Python makes PYTHON fun") == {
        "python": 2,
        "makes": 1,
        "fun": 1,
    }
    assert group_by_initial(["Ada", "Alice", "Bob"]) == {
        "a": ["Ada", "Alice"],
        "b": ["Bob"],
    }


def test_json_round_trip_uses_pathlib(tmp_path: Path) -> None:
    path = tmp_path / "data.json"
    data = {"message": "你好", "values": [1, 2]}
    save_json(path, data)
    assert load_json(path) == data
    assert "你好" in path.read_text(encoding="utf-8")


def test_islice_pages_keep_partial_final_batch() -> None:
    assert pages(iter([1, 2, 3, 4, 5]), 2) == [(1, 2), (3, 4), (5,)]
    with pytest.raises(ValueError):
        pages([1], 0)


def test_recursive_fibonacci_is_cached() -> None:
    fibonacci_recursive.cache_clear()
    assert fibonacci_recursive(10) == 55
    before = fibonacci_recursive.cache_info()
    assert fibonacci_recursive(10) == 55
    after = fibonacci_recursive.cache_info()
    assert after.hits == before.hits + 1

    with pytest.raises(ValueError):
        fibonacci_recursive(-1)
