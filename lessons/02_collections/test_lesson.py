"""第 2 章验收：独立验证本章 exercise.py 中的 invert。"""

from lessons._loader import load_exercise

invert = load_exercise("02_collections")["invert"]


def test_invert_groups_keys_without_mutating_input() -> None:
    source = {"a": 1, "b": 2, "c": 1}

    result = invert(source)

    assert result == {1: ["a", "c"], 2: ["b"]}
    assert source == {"a": 1, "b": 2, "c": 1}
    assert invert({}) == {}
