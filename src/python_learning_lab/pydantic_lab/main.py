"""通过 `python -m python_learning_lab.pydantic_lab.main` 运行。"""

from pydantic import ValidationError

from .service import explain_validation_error, public_user, register_user
from .settings import AppSettings


VALID_PAYLOAD = {
    "name": "  Ada   Lovelace ",
    "age": "36",
    "email": "ada@example.com",
    "role": "admin",
    "address": {"city": "London", "street": "St James's Square", "zip_code": "100001"},
    "tags": [" Python ", "MATH", "python"],
}


def main() -> None:
    settings = AppSettings()
    print(f"{settings.app_name} running on {settings.host}:{settings.port}")

    user = register_user(VALID_PAYLOAD)
    print(user.model_dump_json(indent=2))
    print(public_user(user).model_dump_json(indent=2))

    invalid = {**VALID_PAYLOAD, "email": "not-an-email", "age": -1}
    try:
        register_user(invalid)
    except ValidationError as error:
        print("校验失败：")
        for message in explain_validation_error(error):
            print(f"- {message}")


if __name__ == "__main__":
    main()
