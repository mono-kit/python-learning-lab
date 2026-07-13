"""在应用边界使用 Pydantic，而不是把校验散落在业务逻辑中。"""

from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from .models import User, UserCreate, UserPublic


def register_user(payload: Mapping[str, Any]) -> User:
    """验证不可信字典，随后构造系统拥有的 User。"""
    request = UserCreate.model_validate(payload)
    return User(**request.model_dump())


def public_user(user: User) -> UserPublic:
    return UserPublic.from_user(user)


def explain_validation_error(error: ValidationError) -> list[str]:
    """把结构化错误转换为适合终端或表单显示的中文路径信息。"""
    messages: list[str] = []
    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"])
        messages.append(f"{location}: {item['msg']}")
    return messages

