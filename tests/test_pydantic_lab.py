import pytest
from pydantic import ValidationError

from python_learning_lab.pydantic_lab.models import Role, UserCreate
from python_learning_lab.pydantic_lab.service import explain_validation_error, public_user, register_user
from python_learning_lab.pydantic_lab.settings import AppSettings


def valid_payload() -> dict[str, object]:
    return {
        "name": "  Ada   Lovelace ",
        "age": "36",
        "email": "ada@example.com",
        "role": "admin",
        "address": {"city": "London", "street": "St James's Square", "zip_code": "100001"},
        "tags": [" Python ", "MATH", "python"],
    }


def test_nested_model_conversion_and_normalization() -> None:
    user = UserCreate.model_validate(valid_payload())
    assert user.name == "Ada Lovelace"
    assert user.age == 36
    assert user.role is Role.ADMIN
    assert user.address.city == "London"
    assert user.tags == {"python", "math"}


def test_extra_fields_are_forbidden() -> None:
    payload = {**valid_payload(), "password": "should-not-be-accepted"}
    with pytest.raises(ValidationError) as captured:
        UserCreate.model_validate(payload)
    assert captured.value.errors()[0]["type"] == "extra_forbidden"


def test_model_validator_checks_multiple_fields() -> None:
    payload = {**valid_payload(), "age": 16}
    with pytest.raises(ValidationError, match="管理员必须年满 18 岁"):
        UserCreate.model_validate(payload)


def test_service_builds_internal_and_public_models() -> None:
    user = register_user(valid_payload())
    visible = public_user(user)
    data = visible.model_dump(mode="json")
    assert data["name"] == "Ada Lovelace"
    assert data["display_name"] == "Ada Lovelace (admin)"
    assert "email" not in data
    assert "address" not in data


def test_validation_errors_keep_field_paths() -> None:
    payload = {**valid_payload(), "address": {"city": "X", "street": "Y", "zip_code": "bad"}}
    with pytest.raises(ValidationError) as captured:
        UserCreate.model_validate(payload)
    assert explain_validation_error(captured.value)[0].startswith("address.zip_code:")


def test_settings_read_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LAB_DEBUG", "true")
    monkeypatch.setenv("LAB_PORT", "9000")
    settings = AppSettings()
    assert settings.debug is True
    assert settings.port == 9000

