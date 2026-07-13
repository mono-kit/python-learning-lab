from pathlib import Path

import pytest

from python_learning_lab.async_demo import fetch_users
from python_learning_lab.basics import classify_payload, describe_number, squares_of_even_numbers
from python_learning_lab.collections_demo import merge_preferences, partition, unique_words, word_frequency
from python_learning_lab.errors import ConfigurationError, parse_port, temporary_value
from python_learning_lab.functions import build_profile, format_user, make_multiplier, total
from python_learning_lab.iterators import Countdown, fibonacci, flatten, take
from python_learning_lab.oop import Circle, Drawing, Employee, Rectangle
from python_learning_lab.stdlib_demo import load_json, pages, save_json


def test_control_flow_and_comprehensions() -> None:
    assert [describe_number(number) for number in (-1, 0, 2, 3)] == ["负数", "零", "正偶数", "正奇数"]
    assert squares_of_even_numbers([1, 2, 3, 4]) == [4, 16]
    assert classify_payload({"type": "text", "content": "你好"}) == "文本：你好"


def test_collections() -> None:
    assert unique_words("Python makes PYTHON fun") == ["fun", "makes", "python"]
    assert word_frequency(["a", "b", "a"]) == {"a": 2, "b": 1}
    assert partition([1, 2, 3, 4]) == ([2, 4], [1, 3])
    defaults = {"theme": "light", "page_size": 10}
    assert merge_preferences(defaults, {"theme": "dark"}) == {"theme": "dark", "page_size": 10}
    assert defaults["theme"] == "light"


def test_function_parameter_styles_and_closure() -> None:
    assert format_user(7, "Ada", active=False) == "#7 Ada（停用）"
    assert total(1, 2.5, 3) == 6.5
    assert build_profile("Ada", language="Python") == {"name": "Ada", "language": "Python"}
    double = make_multiplier(2)
    assert double(9) == 18


def test_objects_and_composition() -> None:
    drawing = Drawing("demo")
    drawing.add(Circle(1))
    drawing.add(Rectangle(2, 3))
    assert drawing.total_area == pytest.approx(3.141592653589793 + 6)
    employee = Employee.from_text("Ada:3")
    assert (employee.name, employee.level) == ("Ada", 3)


def test_errors_and_context_manager() -> None:
    assert parse_port("8000") == 8000
    with pytest.raises(ConfigurationError):
        parse_port("eight thousand")

    values = {"mode": "normal"}
    with temporary_value(values, "mode", "testing"):
        assert values["mode"] == "testing"
    assert values["mode"] == "normal"


def test_iterators_and_generators() -> None:
    assert list(Countdown(3)) == [3, 2, 1]
    assert list(fibonacci(10)) == [0, 1, 1, 2, 3, 5, 8]
    assert list(flatten([[1, 2], [], [3]])) == [1, 2, 3]
    assert take(3, fibonacci(100)) == [0, 1, 1]


async def test_async_concurrency() -> None:
    users = await fetch_users([1, 2, 3])
    assert [user["id"] for user in users] == [1, 2, 3]


def test_path_json_and_batching(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    save_json(target, {"message": "你好"})
    assert load_json(target) == {"message": "你好"}
    assert pages([1, 2, 3, 4, 5], 2) == [(1, 2), (3, 4), (5,)]

