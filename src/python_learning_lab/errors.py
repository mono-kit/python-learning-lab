"""异常处理和上下文管理器。"""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class ConfigurationError(ValueError):
    """针对配置错误建立更精确的异常类型。"""


def parse_port(value: str) -> int:
    """把底层 ValueError 转换成领域异常，并保留异常链。"""
    try:
        port = int(value)
    except ValueError as error:
        raise ConfigurationError("端口必须是整数") from error

    if not 1 <= port <= 65535:
        raise ConfigurationError("端口必须在 1 到 65535 之间")
    return port


def read_optional_text(path: Path) -> str | None:
    """只捕获能够处理的异常；其他错误继续向上传播。"""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


@contextmanager
def temporary_value(mapping: dict[str, str], key: str, value: str) -> Iterator[None]:
    """无论 with 代码块是否异常，finally 都恢复原始状态。"""
    sentinel = object()
    previous: str | object = mapping.get(key, sentinel)
    mapping[key] = value
    try:
        yield
    finally:
        if previous is sentinel:
            mapping.pop(key, None)
        else:
            mapping[key] = str(previous)

