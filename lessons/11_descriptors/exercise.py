"""第 11 章练习：编写可复用的数据描述器。"""

from typing import Any


class NonEmptyString:
    def __set_name__(self, owner: type[Any], name: str) -> None:
        self.public_name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance: object | None, owner: type[Any] | None = None):
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance: object, value: str) -> None:
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{self.public_name} 不能为空")
        setattr(instance, self.storage_name, normalized)


class BoundedInteger:
    def __init__(self, minimum: int, maximum: int) -> None:
        self.minimum = minimum
        self.maximum = maximum

    def __set_name__(self, owner: type[Any], name: str) -> None:
        self.public_name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance: object | None, owner: type[Any] | None = None):
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance: object, value: int) -> None:
        if not self.minimum <= value <= self.maximum:
            raise ValueError(f"{self.public_name} 必须在 {self.minimum} 到 {self.maximum} 之间")
        setattr(instance, self.storage_name, value)


class Account:
    name = NonEmptyString()
    age = BoundedInteger(18, 120)

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age
