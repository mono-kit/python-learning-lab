import pytest

from learning_tests.loader import load_exercise


exercise = load_exercise("11_descriptors.py")
Account = exercise["Account"]
NonEmptyString = exercise["NonEmptyString"]


def test_descriptors_normalize_and_validate_values() -> None:
    account = Account("  Ada  ", 18)
    assert account.name == "Ada"
    assert account.age == 18

    account.age = 120
    assert account.age == 120

    with pytest.raises(ValueError):
        account.name = "  "
    with pytest.raises(ValueError):
        account.age = 121


def test_data_descriptor_wins_over_same_instance_dictionary_key() -> None:
    account = Account("Ada", 36)
    account.__dict__["age"] = 999
    assert account.age == 36


def test_descriptor_can_be_accessed_on_class() -> None:
    assert isinstance(Account.name, NonEmptyString)
