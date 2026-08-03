import pytest

from learning_tests.loader import load_exercise


Version = load_exercise("10_data_model.py")["Version"]


def test_version_parses_and_formats() -> None:
    version = Version.parse("2.10.3")
    assert (version.major, version.minor, version.patch) == (2, 10, 3)
    assert str(version) == "2.10.3"


def test_version_uses_numeric_order_and_hashing() -> None:
    assert Version.parse("2.10.0") > Version.parse("2.9.9")
    assert {Version.parse("1.2.3"), Version(1, 2, 3)} == {Version(1, 2, 3)}


@pytest.mark.parametrize("text", ["1", "1.2", "1.2.3.4", "1.two.3", "-1.2.3"])
def test_version_rejects_invalid_text(text: str) -> None:
    with pytest.raises(ValueError):
        Version.parse(text)


def test_version_does_not_compare_to_unrelated_type() -> None:
    version = Version(1, 0, 0)

    assert version.__lt__((1, 0, 0)) is NotImplemented
    with pytest.raises(TypeError):
        _ = version < (1, 0, 0)
