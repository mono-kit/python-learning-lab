"""第 11 章练习：编写可复用的数据描述器。"""

from typing import Any


class NonEmptyString:
    def __set_name__(self, owner: type[Any], name: str) -> None:
        # TODO: 保存公开名和实际存储名。
        pass

    def __get__(self, instance: object | None, owner: type[Any] | None = None):
        # TODO: 类访问返回描述器本身，实例访问返回已保存的字符串。
        raise NotImplementedError

    def __set__(self, instance: object, value: str) -> None:
        # TODO: strip 后不能为空，再写入实际存储名。
        raise NotImplementedError


class BoundedInteger:
    def __init__(self, minimum: int, maximum: int) -> None:
        self.minimum = minimum
        self.maximum = maximum

    def __set_name__(self, owner: type[Any], name: str) -> None:
        # TODO
        pass

    def __get__(self, instance: object | None, owner: type[Any] | None = None):
        # TODO
        raise NotImplementedError

    def __set__(self, instance: object, value: int) -> None:
        # TODO: 包含上下边界。
        raise NotImplementedError


class Account:
    name = NonEmptyString()
    age = BoundedInteger(18, 120)

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age
