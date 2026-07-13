"""类、继承、组合、数据类和结构化子类型。"""

from dataclasses import dataclass, field
from math import pi
from typing import Protocol


class Shape(Protocol):
    """任何拥有 area 属性的对象都符合这个协议。"""

    @property
    def area(self) -> float: ...


class Circle:
    """普通类：通过 property 管理属性访问。"""

    def __init__(self, radius: float) -> None:
        self.radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value <= 0:
            raise ValueError("半径必须大于零")
        self._radius = value

    @property
    def area(self) -> float:
        return pi * self.radius**2

    def __repr__(self) -> str:
        return f"Circle(radius={self.radius!r})"


@dataclass(slots=True)
class Rectangle:
    """dataclass 自动生成初始化、比较和 repr 等方法。"""

    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("长和宽必须大于零")

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass
class Drawing:
    """Drawing 拥有 Shape；这是组合，而不是继承。"""

    name: str
    shapes: list[Shape] = field(default_factory=list)

    def add(self, shape: Shape) -> None:
        self.shapes.append(shape)

    @property
    def total_area(self) -> float:
        return sum(shape.area for shape in self.shapes)


class Employee:
    """用类方法提供具名构造方式。"""

    company = "Python Lab"

    def __init__(self, name: str, level: int) -> None:
        self.name = name
        self.level = level

    @classmethod
    def from_text(cls, text: str) -> "Employee":
        name, level = text.split(":")
        return cls(name=name, level=int(level))

