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
        versions = text.split(".")
        if len(versions) != 3 or any(not version.isdigit() for version in versions):
            raise ValueError(f"无效版本：{text!r}")
        return cls(*(int(version) for version in versions))

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
