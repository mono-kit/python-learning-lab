"""第 5 章练习：异常转换、异常链和可靠清理。"""

from collections.abc import Iterator
from contextlib import contextmanager


class ConfigurationError(ValueError):
    """表示调用方提供了无效配置。"""


def parse_port(value: str) -> int:
    """解析 1～65535 的端口，并保留底层转换异常。"""

    try:
        port = int(value)
    except ValueError as error:
        raise ConfigurationError("端口必须是整数") from error

    if not 1 <= port <= 65535:
        raise ConfigurationError("端口必须在 1 到 65535 之间")
    return port


@contextmanager
def temporary_value(mapping: dict[str, str], key: str, value: str) -> Iterator[None]:
    """在 ``with`` 内临时设置值，退出时恢复调用前状态。"""

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
