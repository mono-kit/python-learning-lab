"""Pydantic 模型、字段约束、嵌套数据和校验器。"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Self
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    computed_field,
    field_validator,
    model_validator,
)


class Role(StrEnum):
    MEMBER = "member"
    ADMIN = "admin"


class Address(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    city: str = Field(min_length=1, max_length=80)
    street: str = Field(min_length=1, max_length=120)
    zip_code: str = Field(pattern=r"^\d{6}$")


class UserCreate(BaseModel):
    """接收注册输入的模型；禁止调用者传入未声明字段。"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=50)
    age: int = Field(ge=0, le=150)
    email: EmailStr
    role: Role = Role.MEMBER
    address: Address
    tags: set[str] = Field(default_factory=set)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """标准类型校验后，把连续空白折叠成一个空格。"""
        return " ".join(value.split())

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: Any) -> Any:
        """在 set 转换前统一字符串的大小写并去除空白。"""
        if isinstance(value, (list, tuple, set)):
            return {str(item).strip().lower() for item in value if str(item).strip()}
        return value

    @model_validator(mode="after")
    def admin_must_be_adult(self) -> Self:
        if self.role is Role.ADMIN and self.age < 18:
            raise ValueError("管理员必须年满 18 岁")
        return self


class User(UserCreate):
    """系统保存的用户；ID 和创建时间由程序生成。"""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UserPublic(BaseModel):
    """面向外部的输出模型，刻意不暴露地址等内部字段。"""

    id: UUID
    name: str
    role: Role
    created_at: datetime

    @computed_field
    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.role.value})"

    @classmethod
    def from_user(cls, user: User) -> "UserPublic":
        return cls.model_validate(user, from_attributes=True)
