"""第 5 章映射：lessons/05_errors/exercise.py。"""

import pytest

from lessons._loader import load_exercise

exercise = load_exercise("05_errors")
ConfigurationError = exercise["ConfigurationError"]
parse_port = exercise["parse_port"]
temporary_value = exercise["temporary_value"]


def test_parse_port_translates_conversion_error_and_checks_range() -> None:
    assert parse_port("8000") == 8000

    with pytest.raises(ConfigurationError) as captured:
        parse_port("eight thousand")
    assert isinstance(captured.value.__cause__, ValueError)

    for value in ["0", "65536"]:
        with pytest.raises(ConfigurationError):
            parse_port(value)


def test_temporary_value_restores_existing_value_after_exception() -> None:
    values = {"mode": "normal"}

    with pytest.raises(RuntimeError), temporary_value(values, "mode", "testing"):
        assert values["mode"] == "testing"
        raise RuntimeError("body failed")

    assert values == {"mode": "normal"}


def test_temporary_value_removes_key_that_did_not_exist() -> None:
    values: dict[str, str] = {}
    with temporary_value(values, "mode", "testing"):
        assert values == {"mode": "testing"}
    assert values == {}
