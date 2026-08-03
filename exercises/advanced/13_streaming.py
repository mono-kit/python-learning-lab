"""第 13 章练习：流式读取 JSONL 并按批次返回 Event。"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from pydantic import BaseModel, Field


class Event(BaseModel):
    name: str = Field(min_length=1)
    value: int


class InvalidRecord(ValueError):
    def __init__(self, path: Path, line_number: int, reason: str) -> None:
        self.path = path
        self.line_number = line_number
        self.reason = reason
        super().__init__(f"{path}:{line_number}: {reason}")


def validated_batches(path: Path, batch_size: int) -> Iterator[list[Event]]:
    """空行跳过；JSON 或模型错误转换为带行号的 InvalidRecord。"""

    # TODO: 参数应在函数调用时立即检查，文件内容应在消费时惰性读取。
    raise NotImplementedError
