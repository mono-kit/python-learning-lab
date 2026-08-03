"""第 10 章练习：实现 Version 数据模型。"""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering


@total_ordering
@dataclass(frozen=True, slots=True)
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, text: str) -> Version:
        """解析严格的 major.minor.patch；无效输入抛出 ValueError。"""

        # TODO: 检查段数、是否为十进制数字，并返回 Version。
        raise NotImplementedError

    def __lt__(self, other: object) -> bool:
        # TODO: 非 Version 返回 NotImplemented，Version 按三元组比较。
        raise NotImplementedError

    def __str__(self) -> str:
        # TODO: 返回 major.minor.patch。
        raise NotImplementedError
