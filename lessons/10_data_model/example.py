"""第 10 章：Python 数据模型。

Python 的运算符和内置函数会转成特殊方法调用。例如 ``a + b`` 会尝试
``a.__add__(b)``，``len(container)`` 会调用 ``container.__len__()``。

运行本模块：``python lessons/10_data_model/example.py``。
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from decimal import Decimal
from functools import total_ordering


class CurrencyMismatch(ValueError):
    """两个金额的币种不兼容。"""


@total_ordering
@dataclass(frozen=True, slots=True)
class Money:
    """不可变金额值对象，可安全地作为 set 元素或 dict 键。"""

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        normalized = self.currency.strip().upper()
        if len(normalized) != 3:
            raise ValueError("币种必须是三个字母")
        object.__setattr__(self, "currency", normalized)

    def __add__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        self._require_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._require_same_currency(other)
        return self.amount < other.amount

    def __format__(self, format_spec: str) -> str:
        spec = format_spec or ".2f"
        return f"{format(self.amount, spec)} {self.currency}"

    def _require_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise CurrencyMismatch(f"不能混合 {self.currency} 和 {other.currency}")


@total_ordering
@dataclass(frozen=True, slots=True)
class Version:
    """可解析、比较和哈希的语义版本核心三元组。"""

    major: int
    minor: int
    patch: int

    def __post_init__(self) -> None:
        if min(self.major, self.minor, self.patch) < 0:
            raise ValueError("版本号不能为负数")

    @classmethod
    def parse(cls, text: str) -> Version:
        parts = text.split(".")
        if len(parts) != 3 or any(not part.isdigit() for part in parts):
            raise ValueError(f"无效版本：{text!r}")
        return cls(*(int(part) for part in parts))

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __format__(self, format_spec: str) -> str:
        text = str(self)
        return format(text, format_spec) if format_spec else text


@dataclass(frozen=True, slots=True)
class StockItem:
    product_id: str
    quantity: int

    def __post_init__(self) -> None:
        if not self.product_id:
            raise ValueError("product_id 不能为空")
        if self.quantity < 0:
            raise ValueError("quantity 不能为负数")


class Inventory(Mapping[str, StockItem]):
    """只读容器；继承 Mapping 后只需实现三个最小方法。"""

    def __init__(self, items: Iterator[StockItem] | list[StockItem]) -> None:
        self._items = {item.product_id: item for item in items}

    def __getitem__(self, product_id: str) -> StockItem:
        return self._items[product_id]

    def __iter__(self) -> Iterator[str]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)


def main() -> None:
    wallet = {Money(Decimal("10.00"), "cny"), Money(Decimal(10), "CNY")}
    print(f"相等对象在 set 中只保留一个：{wallet}")
    print(f"金额相加：{Money(Decimal('12.5'), 'CNY') + Money(Decimal('7.5'), 'CNY')}")
    print(f"版本排序：{sorted(map(Version.parse, ['2.10.0', '2.9.9']))}")


if __name__ == "__main__":
    main()
