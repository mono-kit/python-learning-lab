"""第 11 章：属性协议、描述器和 MRO。

数据描述器同时定义 ``__get__`` 和 ``__set__``，读取时优先于实例
``__dict__``。property 就是 Python 提供的数据描述器。
"""

from __future__ import annotations

from typing import Any, overload


class PositiveNumber:
    """复用非负或正数校验的数据描述器。"""

    def __init__(self, *, allow_zero: bool = False) -> None:
        self.allow_zero = allow_zero
        self.public_name = ""
        self.storage_name = ""

    def __set_name__(self, owner: type[Any], name: str) -> None:
        self.public_name = name
        self.storage_name = f"_{name}"

    @overload
    def __get__(self, instance: None, owner: type[Any] | None = None) -> PositiveNumber: ...

    @overload
    def __get__(self, instance: object, owner: type[Any] | None = None) -> float: ...

    def __get__(
        self, instance: object | None, owner: type[Any] | None = None
    ) -> PositiveNumber | float:
        if instance is None:
            return self
        return float(getattr(instance, self.storage_name))

    def __set__(self, instance: object, value: float) -> None:
        invalid = value < 0 if self.allow_zero else value <= 0
        if invalid:
            relation = "大于等于零" if self.allow_zero else "大于零"
            raise ValueError(f"{self.public_name} 必须{relation}")
        setattr(instance, self.storage_name, float(value))


class NonEmptyString:
    def __set_name__(self, owner: type[Any], name: str) -> None:
        self.public_name = name
        self.storage_name = f"_{name}"

    @overload
    def __get__(self, instance: None, owner: type[Any] | None = None) -> NonEmptyString: ...

    @overload
    def __get__(self, instance: object, owner: type[Any] | None = None) -> str: ...

    def __get__(
        self, instance: object | None, owner: type[Any] | None = None
    ) -> NonEmptyString | str:
        if instance is None:
            return self
        return str(getattr(instance, self.storage_name))

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

    @overload
    def __get__(self, instance: None, owner: type[Any] | None = None) -> BoundedInteger: ...

    @overload
    def __get__(self, instance: object, owner: type[Any] | None = None) -> int: ...

    def __get__(
        self, instance: object | None, owner: type[Any] | None = None
    ) -> BoundedInteger | int:
        if instance is None:
            return self
        return int(getattr(instance, self.storage_name))

    def __set__(self, instance: object, value: int) -> None:
        if not self.minimum <= value <= self.maximum:
            raise ValueError(f"{self.public_name} 必须在 {self.minimum} 到 {self.maximum} 之间")
        setattr(instance, self.storage_name, value)


class Account:
    name = NonEmptyString()
    age = BoundedInteger(18, 120)
    balance = PositiveNumber(allow_zero=True)

    def __init__(self, name: str, age: int, balance: float = 0) -> None:
        self.name = name
        self.age = age
        self.balance = balance


class Handler:
    def process(self, trace: list[str]) -> list[str]:
        trace.append("handler")
        return trace


class LoggingMixin(Handler):
    def process(self, trace: list[str]) -> list[str]:
        trace.append("logging")
        return super().process(trace)


class MetricsMixin(Handler):
    def process(self, trace: list[str]) -> list[str]:
        trace.append("metrics")
        return super().process(trace)


class Service(LoggingMixin, MetricsMixin, Handler):
    """每一层都调用 super()，调用顺序由 MRO 而不是父类名字决定。"""


def main() -> None:
    account = Account("  Ada  ", 36)
    account.__dict__["age"] = 999
    print(f"实例字典：{account.__dict__}")
    print(f"数据描述器仍返回内部值：{account.age}")
    print(f"MRO：{[item.__name__ for item in Service.__mro__]}")
    print(f"协作调用：{Service().process([])}")

    account = Account("Ada", 36)
    account.__dict__["name"] = "假的名字"
    print(account.__dict__)
    print(account.name)

    print(Service.__mro__)


if __name__ == "__main__":
    main()
