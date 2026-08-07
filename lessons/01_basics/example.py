"""基础语法：值、变量、控制流、推导式和模式匹配。"""

from typing import Any


def describe_number(number: int) -> str:
    """使用 if/elif/else 对整数分类。"""
    if number < 0:
        return "负数"
    if number == 0:
        return "零"
    if number % 2 == 0:
        return "正偶数"
    return "正奇数"


def squares_of_even_numbers(numbers: list[int]) -> list[int]:
    """列表推导式等价于循环、判断和 append 的组合。"""
    return [number**2 for number in numbers if number % 2 == 0]


def unpack_person(person: tuple[str, int]) -> str:
    """序列解包把 tuple 中的两个值分别绑定到两个变量。"""
    name, age = person
    return f"{name} 今年 {age} 岁"


def classify_payload(payload: Any) -> str:
    """结构化模式匹配会同时检查数据形状和字段值。"""
    match payload:
        case {"type": "text", "content": str(content)}:
            return f"文本：{content}"
        case {"type": "image", "url": str(url)}:
            return f"图片：{url}"
        case [first, *rest]:
            return f"序列首项：{first}，剩余 {len(rest)} 项"
        case _:
            return "未知数据"


def truthy_name(name: str | None) -> str:
    """空字符串和 None 都是假值；非空字符串是真值。"""
    return name if name else "匿名用户"
